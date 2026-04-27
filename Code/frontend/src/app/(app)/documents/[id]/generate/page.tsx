"use client";

import { useCallback, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button, Spinner, Toast } from "@/components/ui";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";
import type { GenerateRequest } from "@/lib/types";
import { STUDY_SET_TYPES } from "@/lib/constants";

type GenType = "flashcards" | "quiz" | "practice_test" | "audio_summary";

const GEN_FUNCTIONS: Record<GenType, (req: GenerateRequest) => ReturnType<typeof api.generateFlashcards>> = {
  flashcards: api.generateFlashcards,
  quiz: api.generateQuiz,
  practice_test: api.generatePracticeTest,
  audio_summary: api.generateSummary,
};

export default function GeneratePage() {
  const params = useParams();
  const router = useRouter();
  const docId = Number(params.id);

  const { data: doc, loading } = useApi(useCallback(() => api.getDocument(docId), [docId]));

  const [genType, setGenType] = useState<GenType>("flashcards");
  const [count, setCount] = useState(10);
  const [difficulty, setDifficulty] = useState<"easy" | "medium" | "hard" | "mixed">("mixed");
  const [generating, setGenerating] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const handleGenerate = useCallback(async () => {
    setGenerating(true);
    setToast(null);
    try {
      const result = await GEN_FUNCTIONS[genType]({ document_id: docId, count, difficulty });
      setToast({ message: `Generated ${result.item_count} items!`, type: "success" });
      setTimeout(() => router.push(`/study-sets/${result.id}`), 1500);
    } catch (err) {
      const message = err instanceof ApiError ? err.detail : "Generation failed";
      setToast({ message, type: "error" });
    } finally {
      setGenerating(false);
    }
  }, [genType, docId, count, difficulty, router]);

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>;
  }

  return (
    <div>
      <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-2">Generate Study Materials</h1>
      <p className="text-text-secondary mb-8">from {doc?.title || "Untitled"}</p>

      <div className="max-w-xl space-y-6">
        {/* Type selection */}
        <div>
          <label className="text-sm font-medium mb-3 block">Material Type</label>
          <div className="grid grid-cols-2 gap-3">
            {(Object.entries(STUDY_SET_TYPES) as [GenType, { label: string; icon: string }][]).map(([key, val]) => (
              <button
                key={key}
                onClick={() => setGenType(key)}
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
        </div>

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
        <div>
          <label className="text-sm font-medium mb-3 block">Difficulty</label>
          <div className="flex gap-2">
            {(["easy", "medium", "hard", "mixed"] as const).map((d) => (
              <button
                key={d}
                onClick={() => setDifficulty(d)}
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
        </div>

        <Button size="lg" onClick={handleGenerate} loading={generating} disabled={generating} className="w-full">
          {generating ? "Generating with AI..." : "Generate"}
        </Button>

        <p className="text-xs text-text-muted text-center">
          Requires OpenAI API key configured on the server.
        </p>
      </div>

      {toast && <Toast message={toast.message} type={toast.type} onDismiss={() => setToast(null)} />}
    </div>
  );
}
