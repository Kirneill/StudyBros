import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const API_START_TIMEOUT_MS = 15_000;
const HEALTH_REQUEST_TIMEOUT_MS = 1_000;
const HEALTH_POLL_INTERVAL_MS = 250;

export function getVenvPythonPath(codeDir, platform = process.platform) {
  const executable =
    platform === "win32"
      ? path.join(".venv", "Scripts", "python.exe")
      : path.join(".venv", "bin", "python");
  return path.join(codeDir, executable);
}

export function buildApiLaunch(codeDir, platform = process.platform) {
  return {
    command: getVenvPythonPath(codeDir, platform),
    args: [
      "-m",
      "uvicorn",
      "api.main:app",
      "--host",
      "127.0.0.1",
      "--port",
      "8000",
    ],
    cwd: codeDir,
  };
}

export function buildNextArgs(forwardedArgs = []) {
  return ["dev", "--webpack", ...forwardedArgs];
}

export function isHealthyApiResponse(status, payload) {
  return status === 200 && payload?.status === "ok";
}

export function createShutdown(cleanup) {
  let shutdownPromise;
  return () => {
    shutdownPromise ??= Promise.resolve().then(cleanup);
    return shutdownPromise;
  };
}

export function resolveApiTarget(configuredUrl) {
  const rawUrl = configuredUrl?.trim() || DEFAULT_API_BASE_URL;
  let url;
  try {
    url = new URL(rawUrl);
  } catch {
    throw new Error(`API_URL must be an absolute HTTP(S) URL; received "${rawUrl}".`);
  }
  if (!["http:", "https:"].includes(url.protocol)) {
    throw new Error(`API_URL must use HTTP or HTTPS; received "${rawUrl}".`);
  }

  url.search = "";
  url.hash = "";
  const baseUrl = url.toString().replace(/\/+$/, "");
  const effectivePort = url.port || (url.protocol === "https:" ? "443" : "80");
  const isLocal =
    ["127.0.0.1", "localhost"].includes(url.hostname.toLowerCase()) &&
    effectivePort === "8000";

  return {
    baseUrl,
    healthUrl: `${baseUrl}/api/health`,
    isLocal,
  };
}

export function decideApiStartup(apiTarget, isHealthy) {
  if (isHealthy) {
    return "reuse";
  }
  return apiTarget.isLocal ? "start-local" : "fail-remote";
}

export function buildOwnedSpawnOptions(cwd, env, platform = process.platform) {
  return {
    cwd,
    env,
    stdio: "inherit",
    windowsHide: true,
    detached: platform !== "win32",
  };
}

export function getTerminationPlan(pid, platform = process.platform) {
  if (platform === "win32") {
    return {
      kind: "taskkill",
      command: "taskkill",
      args: ["/PID", String(pid), "/T", "/F"],
    };
  }
  return { kind: "process-group", pid: -pid };
}

function hasExited(child) {
  return child.exitCode !== null || child.signalCode !== null;
}

function delay(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function probeApiHealth(healthUrl) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), HEALTH_REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(healthUrl, { signal: controller.signal });
    const payload = await response.json().catch(() => null);
    return isHealthyApiResponse(response.status, payload);
  } catch {
    return false;
  } finally {
    clearTimeout(timeout);
  }
}

function waitForExit(child) {
  if (hasExited(child)) {
    return Promise.resolve({ code: child.exitCode, signal: child.signalCode, error: null });
  }
  return new Promise((resolve) => {
    child.once("exit", (code, signal) => resolve({ code, signal, error: null }));
    child.once("error", (error) => resolve({ code: null, signal: null, error }));
  });
}

async function waitForApi(child, getSpawnError, healthUrl) {
  const deadline = Date.now() + API_START_TIMEOUT_MS;

  while (Date.now() < deadline) {
    const spawnError = getSpawnError();
    if (spawnError) {
      throw new Error(`Could not launch the backend: ${spawnError.message}`);
    }
    if (hasExited(child)) {
      throw new Error(
        `The backend exited before becoming healthy (exit code ${child.exitCode ?? "unknown"}).`,
      );
    }
    if (await probeApiHealth(healthUrl)) {
      return;
    }
    await delay(HEALTH_POLL_INTERVAL_MS);
  }

  throw new Error(
    `The backend did not become healthy at ${healthUrl} within ${
      API_START_TIMEOUT_MS / 1_000
    } seconds.`,
  );
}

async function terminateChildTree(child) {
  if (!child?.pid) {
    return;
  }

  const plan = getTerminationPlan(child.pid);
  if (plan.kind === "taskkill") {
    if (hasExited(child)) {
      return;
    }
    const taskkill = spawn(
      plan.command,
      plan.args,
      { stdio: "ignore", windowsHide: true },
    );
    await waitForExit(taskkill);
    return;
  }

  const killGroup = (signal) => {
    try {
      process.kill(plan.pid, signal);
      return true;
    } catch (error) {
      if (error.code === "ESRCH") {
        return false;
      }
      throw error;
    }
  };

  if (killGroup("SIGTERM")) {
    await delay(2_000);
    killGroup("SIGKILL");
  }
}

function exitCodeFor(result) {
  if (result.error) {
    return 1;
  }
  if (typeof result.code === "number") {
    return result.code;
  }
  if (result.signal === "SIGINT") {
    return 130;
  }
  return result.signal === "SIGTERM" ? 143 : 1;
}

async function run() {
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const frontendDir = path.resolve(scriptDir, "..");
  const codeDir = path.resolve(frontendDir, "..");
  const nextBin = path.join(frontendDir, "node_modules", "next", "dist", "bin", "next");
  const ownedChildren = [];
  const apiTarget = resolveApiTarget(process.env.API_URL);
  const stopOwnedChildren = createShutdown(async () => {
    await Promise.all(ownedChildren.map((child) => terminateChildTree(child)));
  });

  const handleSignal = (signal) => {
    void stopOwnedChildren().finally(() => {
      process.exit(signal === "SIGINT" ? 130 : 143);
    });
  };

  process.once("SIGINT", handleSignal);
  process.once("SIGTERM", handleSignal);

  try {
    let apiChild = null;
    const apiDecision = decideApiStartup(
      apiTarget,
      await probeApiHealth(apiTarget.healthUrl),
    );

    if (apiDecision === "reuse") {
      console.log(`StudyBros API is already healthy at ${apiTarget.healthUrl}; reusing it.`);
    } else if (apiDecision === "fail-remote") {
      throw new Error(
        `The configured API at ${apiTarget.healthUrl} is not healthy. ` +
          "Refusing to start a local API that the frontend would not use.",
      );
    } else {
      const apiLaunch = buildApiLaunch(codeDir);
      if (!existsSync(apiLaunch.command)) {
        throw new Error(
          `StudyBros backend Python was not found at ${apiLaunch.command}.\n` +
            `Create the environment from ${codeDir} and install it with:\n` +
            `  python -m venv .venv\n` +
            `  .venv\\Scripts\\python.exe -m pip install -e ".[dev]"`,
        );
      }

      console.log(`Starting StudyBros API for ${apiTarget.baseUrl}...`);
      apiChild = spawn(
        apiLaunch.command,
        apiLaunch.args,
        buildOwnedSpawnOptions(apiLaunch.cwd, process.env),
      );
      ownedChildren.push(apiChild);

      let apiSpawnError = null;
      apiChild.once("error", (error) => {
        apiSpawnError = error;
      });

      await waitForApi(apiChild, () => apiSpawnError, apiTarget.healthUrl);
      console.log("StudyBros API is healthy.");
    }

    if (!existsSync(nextBin)) {
      throw new Error(
        `Next.js was not found at ${nextBin}. Run "npm install" in ${frontendDir}.`,
      );
    }

    const frontendChild = spawn(
      process.execPath,
      [nextBin, ...buildNextArgs(process.argv.slice(2))],
      buildOwnedSpawnOptions(
        frontendDir,
        {
          ...process.env,
          API_URL: apiTarget.baseUrl,
        },
      ),
    );
    ownedChildren.push(frontendChild);

    const exits = [
      waitForExit(frontendChild).then((result) => ({ source: "frontend", result })),
    ];
    if (apiChild) {
      exits.push(waitForExit(apiChild).then((result) => ({ source: "api", result })));
    }

    const firstExit = await Promise.race(exits);
    if (firstExit.result.error) {
      throw new Error(
        `Could not launch the ${firstExit.source}: ${firstExit.result.error.message}`,
      );
    }
    if (firstExit.source === "api") {
      console.error("StudyBros API stopped; shutting down the frontend.");
    }

    return exitCodeFor(firstExit.result);
  } finally {
    try {
      await stopOwnedChildren();
    } finally {
      process.removeListener("SIGINT", handleSignal);
      process.removeListener("SIGTERM", handleSignal);
    }
  }
}

const isDirectRun =
  process.argv[1] !== undefined &&
  pathToFileURL(path.resolve(process.argv[1])).href === import.meta.url;

if (isDirectRun) {
  run()
    .then((code) => {
      process.exitCode = code;
    })
    .catch((error) => {
      console.error(`StudyBros development startup failed:\n${error.message}`);
      process.exitCode = 1;
    });
}
