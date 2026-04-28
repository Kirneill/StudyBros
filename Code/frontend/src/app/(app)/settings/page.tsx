"use client";

import { useCallback, useEffect, useState } from "react";
import { Button, Card, CardHeader, CardTitle, Toast } from "@/components/ui";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import type { GenerationProvider, GenerationProviderInfo } from "@/lib/types";
import {
  getPreferredProvider,
  setPreferredProvider,
  getStoredApiKey,
  setStoredApiKey,
  clearStoredApiKey,
} from "@/lib/provider-prefs";

const PROVIDERS: { id: GenerationProvider; label: string; description: string }[] = [
  { id: "openai", label: "OpenAI", description: "GPT models" },
  { id: "anthropic", label: "Anthropic", description: "Claude models" },
  { id: "openrouter", label: "OpenRouter", description: "Multiple providers via one key" },
];

export default function SettingsPage() {
  const { data: providerData, loading } = useApi(
    useCallback(() => api.getGenerationProviders(), []),
  );

  const [selectedProvider, setSelectedProvider] = useState<GenerationProvider>("openai");
  const [apiKey, setApiKey] = useState("");
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  useEffect(() => {
    const saved = getPreferredProvider();
    if (saved) {
      setSelectedProvider(saved);
      const key = getStoredApiKey(saved);
      if (key) setApiKey(key);
    }
  }, []);

  const handleProviderChange = (provider: GenerationProvider) => {
    setSelectedProvider(provider);
    const key = getStoredApiKey(provider);
    setApiKey(key ?? "");
  };

  const handleSave = () => {
    setPreferredProvider(selectedProvider);
    setStoredApiKey(selectedProvider, apiKey);
    setToast({ message: "Settings saved", type: "success" });
  };

  const handleClearKey = () => {
    clearStoredApiKey(selectedProvider);
    setApiKey("");
    setToast({ message: "API key cleared", type: "success" });
  };

  const getServerStatus = (providerId: GenerationProvider): boolean => {
    if (!providerData) return false;
    const info = providerData.providers.find((p: GenerationProviderInfo) => p.provider === providerId);
    return info?.has_server_key ?? false;
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-8">Settings</h1>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>AI Provider</CardTitle>
        </CardHeader>
        <div className="px-6 pb-6">
          <p className="text-sm text-text-muted mb-4">
            Choose your preferred AI provider for generating quizzes, tests, and flashcards.
          </p>
          <div className="space-y-2">
            {PROVIDERS.map((p) => {
              const hasServerKey = getServerStatus(p.id);
              const isSelected = selectedProvider === p.id;
              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => handleProviderChange(p.id)}
                  className={`w-full flex items-center justify-between p-4 rounded-lg border text-left transition-colors ${
                    isSelected
                      ? "border-accent bg-accent/5"
                      : "border-border hover:bg-bg-card-hover"
                  }`}
                >
                  <div>
                    <span className="font-medium text-sm">{p.label}</span>
                    <span className="text-xs text-text-muted ml-2">{p.description}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {hasServerKey && (
                      <span className="text-[10px] text-success bg-success/10 px-2 py-0.5 rounded-full">
                        Server key
                      </span>
                    )}
                    {isSelected && (
                      <span className="w-3 h-3 rounded-full bg-accent" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </Card>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>API Key</CardTitle>
        </CardHeader>
        <div className="px-6 pb-6">
          <p className="text-sm text-text-muted mb-4">
            {getServerStatus(selectedProvider)
              ? `The server has a key for ${PROVIDERS.find((p) => p.id === selectedProvider)?.label}. You can override it with your own.`
              : `Enter your ${PROVIDERS.find((p) => p.id === selectedProvider)?.label} API key to enable generation.`}
          </p>
          <div className="flex gap-2">
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={`Enter ${selectedProvider} API key...`}
              className="flex-1 px-3 py-2 rounded-lg bg-bg-input border border-border text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent"
            />
            {apiKey && (
              <Button variant="ghost" size="sm" onClick={handleClearKey}>
                Clear
              </Button>
            )}
          </div>
        </div>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave} disabled={loading}>
          Save Settings
        </Button>
      </div>

      {toast && <Toast message={toast.message} type={toast.type} onDismiss={() => setToast(null)} />}
    </div>
  );
}
