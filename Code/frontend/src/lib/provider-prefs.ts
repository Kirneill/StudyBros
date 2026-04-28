import type { GenerationProvider } from "./types";

const PREF_PROVIDER_KEY = "studybros_preferred_provider";
const API_KEY_PREFIX = "studybros_api_key:";

export function getPreferredProvider(): GenerationProvider | null {
  if (typeof window === "undefined") return null;
  const stored = sessionStorage.getItem(PREF_PROVIDER_KEY);
  if (stored === "openai" || stored === "anthropic" || stored === "openrouter") return stored;
  return null;
}

export function setPreferredProvider(provider: GenerationProvider): void {
  sessionStorage.setItem(PREF_PROVIDER_KEY, provider);
}

export function getStoredApiKey(provider: GenerationProvider): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(`${API_KEY_PREFIX}${provider}`) || null;
}

export function setStoredApiKey(provider: GenerationProvider, key: string): void {
  if (key.trim()) {
    sessionStorage.setItem(`${API_KEY_PREFIX}${provider}`, key.trim());
  } else {
    sessionStorage.removeItem(`${API_KEY_PREFIX}${provider}`);
  }
}

export function clearStoredApiKey(provider: GenerationProvider): void {
  sessionStorage.removeItem(`${API_KEY_PREFIX}${provider}`);
}
