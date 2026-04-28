"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button, Card, ErrorState, Modal, Spinner, Toast } from "@/components/ui";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";
import Link from "next/link";
import type {
  GenerateRequest,
  GenerationProvider,
  GenerationProviderInfo,
} from "@/lib/types";
import { STUDY_SET_TYPES } from "@/lib/constants";

type GenType = "flashcards" | "quiz" | "practice_test" | "audio_summary";
type ProviderKeyState = Partial<Record<GenerationProvider, string>>;

const GEN_FUNCTIONS: Record<GenType, (req: GenerateRequest) => ReturnType<typeof api.generateFlashcards>> = {
  flashcards: api.generateFlashcards,
  quiz: api.generateQuiz,
  practice_test: api.generatePracticeTest,
  audio_summary: api.generateSummary,
};

const PROVIDER_STORAGE_PREFIX = "studybros_api_key:";
const PROVIDER_LABELS: Record<GenerationProvider, string> = {
  openai: "OpenAI",
  anthropic: "Claude",
  openrouter: "OpenRouter",
};

function isProviderCredentialError(message: string): boolean {
  const normalized = message.toLowerCase();
  return [
    "api key",
    "invalid_api_key",
    "incorrect api key",
    "credit balance",
    "billing",
    "unauthorized",
    "authentication",
  ].some((fragment) => normalized.includes(fragment));
}

function getStoredProviderKeys(): ProviderKeyState {
  if (typeof window === "undefined") {
    return {};
  }

  const storedKeys: ProviderKeyState = {};
  (["openai", "anthropic", "openrouter"] as GenerationProvider[]).forEach((candidate) => {
    const key = window.sessionStorage.getItem(`${PROVIDER_STORAGE_PREFIX}${candidate}`);
    if (key) {
      storedKeys[candidate] = key;
    }
  });
  return storedKeys;
}

export default function GeneratePage() {
  const params = useParams();
  const router = useRouter();
  const docId = Number(params.id);

  const { data: doc, error: docError, loading, refetch: refetchDoc } = useApi(useCallback(() => api.getDocument(docId), [docId]));
  const { data: providerData, error: providersError, loading: loadingProviders, refetch: refetchProviders } = useApi(
    useCallback(() => api.getGenerationProviders(), []),
  );

  const [provider, setProvider] = useState<GenerationProvider>("openai");
  const [genType, setGenType] = useState<GenType>("flashcards");
  const [count, setCount] = useState(10);
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard" | "mixed">("mixed");
  const [generating, setGenerating] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const [providerKeys, setProviderKeys] = useState<ProviderKeyState>(getStoredProviderKeys);
  const [keyModalOpen, setKeyModalOpen] = useState(false);
  const [pendingKey, setPendingKey] = useState("");
  const [keyModalMessage, setKeyModalMessage] = useState<string | null>(null);
  const navTimerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => () => {
    if (navTimerRef.current) clearTimeout(navTimerRef.current);
  }, []);

  const availableProviders = useMemo(
    () => providerData?.providers ?? [],
    [providerData],
  );
  const effectiveProvider = useMemo<GenerationProvider>(() => {
    if (availableProviders.some((entry) => entry.provider === provider)) {
      return provider;
    }
    const serverBacked = availableProviders.find((entry) => entry.has_server_key);
    return serverBacked?.provider ?? availableProviders[0]?.provider ?? provider;
  }, [availableProviders, provider]);

  const selectedProvider = useMemo<GenerationProviderInfo | undefined>(
    () => availableProviders.find((entry) => entry.provider === effectiveProvider),
    [availableProviders, effectiveProvider],
  );

  const activeClientKey = providerKeys[effectiveProvider]?.trim();

  const persistProviderKey = useCallback((target: GenerationProvider, key: string) => {
    const normalized = key.trim();
    setProviderKeys((current) => {
      const next = { ...current };
      if (normalized) {
        next[target] = normalized;
        window.sessionStorage.setItem(`${PROVIDER_STORAGE_PREFIX}${target}`, normalized);
      } else {
        delete next[target];
        window.sessionStorage.removeItem(`${PROVIDER_STORAGE_PREFIX}${target}`);
      }
      return next;
    });
  }, []);

  const openKeyModal = useCallback((message?: string) => {
    setPendingKey(providerKeys[effectiveProvider] ?? "");
    setKeyModalMessage(
      message ?? `Enter a ${PROVIDER_LABELS[effectiveProvider]} API key. A saved browser key overrides the server key for this provider.`,
    );
    setKeyModalOpen(true);
  }, [effectiveProvider, providerKeys]);

  const runGenerate = useCallback(async (apiKeyOverride?: string) => {
    setGenerating(true);
    setToast(null);
    try {
      const result = await GEN_FUNCTIONS[genType]({
        document_id: docId,
        count,
        difficulty,
        provider: effectiveProvider,
        api_key: apiKeyOverride ?? activeClientKey ?? undefined,
      });
      setToast({ message: `Generated ${result.item_count} items!`, type: "success" });
      navTimerRef.current = setTimeout(() => {
        router.push(`/study-sets/${result.id}`);
        router.refresh();
      }, 1500);
    } catch (err) {
      const message = err instanceof ApiError ? err.detail : "Generation failed";
      setToast({ message, type: "error" });
      if (isProviderCredentialError(message)) {
        openKeyModal(
          `The current ${PROVIDER_LABELS[effectiveProvider]} key failed. Enter your own key to override it for this browser and try again.`,
        );
      }
    } finally {
      setGenerating(false);
    }
  }, [activeClientKey, count, difficulty, docId, effectiveProvider, genType, openKeyModal, router]);

  const handleGenerate = useCallback(async () => {
    if (!selectedProvider?.has_server_key && !activeClientKey) {
      openKeyModal(
        `The server does not have a ${PROVIDER_LABELS[effectiveProvider]} key configured. Enter your key to continue.`,
      );
      return;
    }
    await runGenerate();
  }, [activeClientKey, effectiveProvider, openKeyModal, runGenerate, selectedProvider]);

  const handleSaveKeyAndGenerate = useCallback(async () => {
    const normalized = pendingKey.trim();
    if (!normalized) {
      setToast({ message: `Enter a ${PROVIDER_LABELS[effectiveProvider]} API key first.`, type: "error" });
      return;
    }
    persistProviderKey(effectiveProvider, normalized);
    setKeyModalOpen(false);
    await runGenerate(normalized);
  }, [effectiveProvider, pendingKey, persistProviderKey, runGenerate]);

  if (loading || loadingProviders) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>;
  }

  if (docError) {
    return (
      <ErrorState
        title="Failed to load document"
        description={docError}
        onRetry={refetchDoc}
      />
    );
  }

  if (providersError) {
    return (
      <ErrorState
        title="Failed to load AI providers"
        description={providersError}
        onRetry={refetchProviders}
      />
    );
  }

  return (
    <div>
      <Link href={`/documents/${docId}`} className="text-sm text-text-muted hover:text-text-primary transition-colors">&larr; Back to {doc?.title || "Document"}</Link>
      <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-2 mt-4">Generate Study Materials</h1>
      <p className="text-text-secondary mb-8">from {doc?.title || "Untitled"}</p>

      <div className="max-w-xl space-y-6">
        {/* Provider selection */}
        <fieldset className="border-0 p-0 m-0">
          <legend className="text-sm font-medium mb-3 block">AI Provider</legend>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {availableProviders.map((entry) => (
              <button
                key={entry.provider}
                onClick={() => setProvider(entry.provider)}
                aria-pressed={effectiveProvider === entry.provider}
                className={`p-4 rounded-xl border text-left transition-colors ${
                  effectiveProvider === entry.provider
                    ? "border-accent bg-accent/5 text-accent"
                    : "border-border bg-bg-card hover:bg-bg-card-hover text-text-secondary"
                }`}
              >
                <span className="text-sm font-semibold block mb-1">{entry.display_name}</span>
                <span className="text-xs text-text-muted block">{entry.default_model}</span>
              </button>
            ))}
          </div>
          {selectedProvider && (
            <Card className="mt-3 p-4">
              <p className="text-sm text-text-secondary">
                {activeClientKey
                  ? `Using a ${selectedProvider.display_name} key saved in this browser. This overrides the server key for generation.`
                  : selectedProvider.has_server_key
                    ? `Using the server-configured ${selectedProvider.display_name} key.`
                    : `No ${selectedProvider.display_name} key is configured on the server. You will be prompted to enter one.`}
              </p>
              <div className="mt-3 flex flex-wrap gap-3 text-xs">
                <button
                  onClick={() => openKeyModal()}
                  className="text-accent hover:text-accent-hover"
                >
                  {activeClientKey ? "Edit personal key" : "Use your own key"}
                </button>
                {activeClientKey && (
                  <button
                    onClick={() => persistProviderKey(effectiveProvider, "")}
                    className="text-text-muted hover:text-text-primary"
                  >
                    {selectedProvider.has_server_key ? "Use server key instead" : "Clear saved key"}
                  </button>
                )}
              </div>
            </Card>
          )}
        </fieldset>

        {/* Type selection */}
        <fieldset className="border-0 p-0 m-0">
          <legend className="text-sm font-medium mb-3 block">Material Type</legend>
          <div className="grid grid-cols-2 gap-3">
            {(Object.entries(STUDY_SET_TYPES) as [GenType, { label: string; icon: string }][]).map(([key, val]) => (
              <button
                key={key}
                onClick={() => setGenType(key)}
                aria-pressed={genType === key}
                className={`p-4 rounded-xl border text-left transition-colors ${
                  genType === key
                    ? "border-accent bg-accent/5 text-accent"
                    : "border-border bg-bg-card hover:bg-bg-card-hover text-text-secondary"
                }`}
              >
                <span className="text-2xl block mb-1">{val.icon}</span>
                <span className="text-sm font-medium">{val.label}</span>
              </button>
            ))}
          </div>
        </fieldset>

        {/* Count */}
        <div>
          <label htmlFor="count" className="text-sm font-medium mb-2 block">
            Number of items: <span className="font-mono text-accent">{count}</span>
          </label>
          <input
            id="count"
            type="range"
            min={1}
            max={50}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
            className="w-full accent-accent"
          />
          <div className="flex justify-between text-xs text-text-muted mt-1">
            <span>1</span>
            <span>50</span>
          </div>
        </div>

        {/* Difficulty */}
        <fieldset className="border-0 p-0 m-0">
          <legend className="text-sm font-medium mb-3 block">Difficulty</legend>
          <div className="flex gap-2">
            {(["easy", "medium", "hard", "mixed"] as const).map((d) => (
              <button
                key={d}
                onClick={() => setDifficulty(d)}
                aria-pressed={difficulty === d}
                className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                  difficulty === d
                    ? "bg-accent text-bg-primary"
                    : "bg-bg-card border border-border text-text-secondary hover:bg-bg-card-hover"
                }`}
              >
                {d}
              </button>
            ))}
          </div>
        </fieldset>

        <Button size="lg" onClick={handleGenerate} loading={generating} disabled={generating} className="w-full">
          {generating ? "Generating with AI..." : "Generate"}
        </Button>

        <p className="text-xs text-text-muted text-center">
          Generating the same type and count again will create a new study set (not overwrite).
          If the server does not have a key for the selected provider, you can enter your own and
          it will be stored locally in this browser.
        </p>
      </div>

      <Modal
        open={keyModalOpen}
        onClose={() => setKeyModalOpen(false)}
        title={`Add ${PROVIDER_LABELS[effectiveProvider]} API Key`}
      >
        <div className="space-y-4">
          <p className="text-sm text-text-secondary">
            {keyModalMessage}
          </p>
          <p className="text-xs text-text-muted">
            Your key is stored only in this browser on this device.
          </p>
          <div>
            <label htmlFor="provider-api-key" className="text-sm font-medium mb-2 block">
              {PROVIDER_LABELS[effectiveProvider]} API Key
            </label>
            <input
              id="provider-api-key"
              type="password"
              value={pendingKey}
              onChange={(e) => setPendingKey(e.target.value)}
              className="w-full rounded-lg border border-border bg-bg-input px-3 py-2 text-sm text-text-primary"
              placeholder={`Paste your ${PROVIDER_LABELS[effectiveProvider]} API key`}
            />
          </div>
          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={() => setKeyModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveKeyAndGenerate} loading={generating}>
              Save & Generate
            </Button>
          </div>
        </div>
      </Modal>

      {toast && <Toast message={toast.message} type={toast.type} onDismiss={() => setToast(null)} />}
    </div>
  );
}
