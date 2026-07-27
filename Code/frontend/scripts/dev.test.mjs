import assert from "node:assert/strict";
import path from "node:path";
import test from "node:test";

import {
  buildApiLaunch,
  buildNextArgs,
  buildOwnedSpawnOptions,
  createShutdown,
  decideApiStartup,
  getVenvPythonPath,
  getTerminationPlan,
  isHealthyApiResponse,
  resolveApiTarget,
} from "./dev.mjs";

test("selects the virtualenv Python executable for Windows", () => {
  assert.equal(
    getVenvPythonPath("C:\\studybros\\Code", "win32"),
    path.join("C:\\studybros\\Code", ".venv", "Scripts", "python.exe"),
  );
});

test("selects the virtualenv Python executable for POSIX", () => {
  assert.equal(
    getVenvPythonPath("/opt/studybros/Code", "linux"),
    path.join("/opt/studybros/Code", ".venv", "bin", "python"),
  );
});

test("builds a bounded local API launch command", () => {
  assert.deepEqual(buildApiLaunch("/opt/studybros/Code", "linux"), {
    command: path.join("/opt/studybros/Code", ".venv", "bin", "python"),
    args: [
      "-m",
      "uvicorn",
      "api.main:app",
      "--host",
      "127.0.0.1",
      "--port",
      "8000",
    ],
    cwd: "/opt/studybros/Code",
  });
});

test("keeps Webpack enabled while forwarding npm arguments", () => {
  assert.deepEqual(buildNextArgs(["--hostname", "127.0.0.1", "--port", "3001"]), [
    "dev",
    "--webpack",
    "--hostname",
    "127.0.0.1",
    "--port",
    "3001",
  ]);
});

test("accepts only the expected successful health response", () => {
  assert.equal(isHealthyApiResponse(200, { status: "ok" }), true);
  assert.equal(isHealthyApiResponse(200, { status: "starting" }), false);
  assert.equal(isHealthyApiResponse(503, { status: "ok" }), false);
  assert.equal(isHealthyApiResponse(200, null), false);
});

test("shares one cleanup execution and completion across shutdown callers", async () => {
  let cleanupCalls = 0;
  let finishCleanup;
  const cleanupFinished = new Promise((resolve) => {
    finishCleanup = resolve;
  });
  const shutdown = createShutdown(async () => {
    cleanupCalls += 1;
    await cleanupFinished;
  });

  const first = shutdown();
  const second = shutdown();

  assert.strictEqual(first, second);
  await Promise.resolve();
  assert.equal(cleanupCalls, 1);

  finishCleanup();
  await Promise.all([first, second]);
  assert.equal(cleanupCalls, 1);
});

test("normalizes the default and explicitly local API targets", () => {
  assert.deepEqual(resolveApiTarget(), {
    baseUrl: "http://127.0.0.1:8000",
    healthUrl: "http://127.0.0.1:8000/api/health",
    isLocal: true,
  });
  assert.deepEqual(resolveApiTarget("http://localhost:8000/"), {
    baseUrl: "http://localhost:8000",
    healthUrl: "http://localhost:8000/api/health",
    isLocal: true,
  });
});

test("normalizes a custom remote API target without treating it as local", () => {
  assert.deepEqual(resolveApiTarget("https://api.example.com/studybros/"), {
    baseUrl: "https://api.example.com/studybros",
    healthUrl: "https://api.example.com/studybros/api/health",
    isLocal: false,
  });
});

test("starts only an unhealthy local API and never substitutes for a remote API", () => {
  const local = resolveApiTarget();
  const remote = resolveApiTarget("https://api.example.com");

  assert.equal(decideApiStartup(local, true), "reuse");
  assert.equal(decideApiStartup(local, false), "start-local");
  assert.equal(decideApiStartup(remote, true), "reuse");
  assert.equal(decideApiStartup(remote, false), "fail-remote");
});

test("owns POSIX children in detached process groups but not Windows children", () => {
  assert.equal(buildOwnedSpawnOptions("/code", {}, "linux").detached, true);
  assert.equal(buildOwnedSpawnOptions("C:\\code", {}, "win32").detached, false);
  assert.deepEqual(getTerminationPlan(4321, "linux"), {
    kind: "process-group",
    pid: -4321,
  });
  assert.deepEqual(getTerminationPlan(4321, "win32"), {
    kind: "taskkill",
    command: "taskkill",
    args: ["/PID", "4321", "/T", "/F"],
  });
});
