"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Button, Card, Badge, ErrorState, Spinner } from "@/components/ui";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";
import type { GenerationProvider } from "@/lib/types";
import Link from "next/link";

interface TestQuestion {
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
  bloomLevel: number | undefined;
}

function isQuestionRecord(
  item: unknown,
): item is Record<string, unknown> & { prompt: string; options?: unknown[] } {
  if (typeof item !== "object" || item === null) return false;
  const obj = item as Record<string, unknown>;
  return typeof obj.prompt === "string";
}

function parseQuestion(item: Record<string, unknown>): TestQuestion {
  const options = Array.isArray(item.options)
    ? item.options.map((opt) =>
        typeof opt === "object" && opt !== null
          ? String((opt as Record<string, unknown>).text ?? "")
          : String(opt),
      )
    : [];
  const correctAnswer = Number(item.correct_index ?? item.correct_answer ?? 0);

  return {
    question: String(item.prompt),
    options,
    correctAnswer: Number.isFinite(correctAnswer) ? correctAnswer : 0,
    explanation: String(item.explanation ?? ""),
    bloomLevel:
      typeof item.bloom_level === "number" ? item.bloom_level : undefined,
  };
}

const BLOOM_LABELS: Record<number, string> = {
  1: "Remember",
  2: "Understand",
  3: "Apply",
  4: "Analyze",
  5: "Evaluate",
  6: "Create",
};

export default function PracticeTestPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const studySetId = Number(id);

  /* C1: Wire up error + refetch */
  const { data: studySet, loading, error, refetch } = useApi(
    useCallback(() => api.getStudySet(studySetId), [studySetId]),
  );

  /* M20: Restore test state from sessionStorage via lazy initializer */
  const [answers, setAnswers] = useState<Record<number, number>>(() => {
    try {
      const saved = sessionStorage.getItem(`test-${studySetId}`);
      if (saved) {
        const parsed: Record<string, unknown> = JSON.parse(saved);
        if (
          typeof parsed.answers === "object" &&
          parsed.answers !== null &&
          !Array.isArray(parsed.answers)
        ) {
          const restoredAnswers: Record<number, number> = {};
          for (const [key, val] of Object.entries(
            parsed.answers as Record<string, unknown>,
          )) {
            if (typeof val === "number") {
              restoredAnswers[Number(key)] = val;
            }
          }
          if (Object.keys(restoredAnswers).length > 0) return restoredAnswers;
        }
      }
    } catch { /* ignore corrupt data */ }
    return {};
  });
  const [submitted, setSubmitted] = useState(false);
  const [autoGenState, setAutoGenState] = useState<
    "idle" | "checking" | "generating" | "error"
  >("idle");
  const [autoGenError, setAutoGenError] = useState<string | null>(null);

  /* M21: Memoize questions derivation */
  const questions: TestQuestion[] = useMemo(() => {
    if (!studySet) return [];
    const content = Array.isArray(studySet.content)
      ? studySet.content
      : Array.isArray(studySet.content.questions)
        ? studySet.content.questions
        : [];
    return content.filter(isQuestionRecord).map(parseQuestion);
  }, [studySet]);

  const totalQuestions = questions.length;
  const allAnswered = Object.keys(answers).length >= totalQuestions;

  /* M20: Persist test state to sessionStorage on each answer */
  useEffect(() => {
    if (Object.keys(answers).length > 0 && !submitted) {
      sessionStorage.setItem(
        `test-${studySetId}`,
        JSON.stringify({ answers }),
      );
    }
    if (submitted) {
      sessionStorage.removeItem(`test-${studySetId}`);
    }
  }, [answers, studySetId, submitted]);

  /* M19: Mid-test navigation warning */
  useEffect(() => {
    if (Object.keys(answers).length > 0 && !submitted) {
      const handler = (e: BeforeUnloadEvent) => {
        e.preventDefault();
      };
      window.addEventListener("beforeunload", handler);
      return () => window.removeEventListener("beforeunload", handler);
    }
  }, [answers, submitted]);

  useEffect(() => {
    if (!studySet || questions.length > 0) return;
    if (studySet.set_type !== "flashcards" || !studySet.document_id) return;
    if (autoGenState !== "idle") return;

    let cancelled = false;
    const docId = studySet.document_id;

    async function autoGenerate() {
      setAutoGenState("checking");
      setAutoGenError(null);

      try {
        const allSets = await api.listStudySets();
        const existing = allSets.find(
          (s) => s.set_type === "practice_test" && s.document_id === docId,
        );

        if (cancelled) return;

        if (existing) {
          router.replace(`/study-sets/${existing.id}/test`);
          return;
        }

        setAutoGenState("generating");

        const providersRes = await api.getGenerationProviders();
        const serverProvider = providersRes.providers.find(
          (p) => p.has_server_key,
        );

        if (!serverProvider) {
          setAutoGenState("error");
          setAutoGenError(
            "No AI provider with a server key is configured. Ask an admin to set one up.",
          );
          return;
        }

        if (cancelled) return;

        const newTest = await api.generatePracticeTest({
          document_id: docId,
          count: 10,
          difficulty: "mixed",
          provider: serverProvider.provider as GenerationProvider,
        });

        if (cancelled) return;

        router.replace(`/study-sets/${newTest.id}/test`);
      } catch (err) {
        if (cancelled) return;
        setAutoGenState("error");
        setAutoGenError(
          err instanceof ApiError
            ? err.detail
            : "Failed to generate practice test. Please try again.",
        );
      }
    }

    autoGenerate();

    return () => {
      cancelled = true;
    };
  }, [studySet, questions.length, autoGenState, router]);

  const handleSelect = (qIndex: number, optionIndex: number) => {
    if (submitted) return;
    setAnswers((prev) => ({ ...prev, [qIndex]: optionIndex }));
  };

  const handleSubmit = () => {
    if (!allAnswered) return;
    setSubmitted(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleRetry = () => {
    setAnswers({});
    setSubmitted(false);
    sessionStorage.removeItem(`test-${studySetId}`);
  };

  // Scoring
  const correctCount = submitted
    ? questions.filter((q, i) => answers[i] === q.correctAnswer).length
    : 0;
  const pct = totalQuestions > 0 ? correctCount / totalQuestions : 0;

  // Bloom breakdown
  const bloomStats = submitted
    ? questions.reduce<Record<number, { correct: number; total: number }>>(
        (acc, q, i) => {
          const level = q.bloomLevel ?? 0;
          if (!acc[level]) acc[level] = { correct: 0, total: 0 };
          acc[level].total++;
          if (answers[i] === q.correctAnswer) acc[level].correct++;
          return acc;
        },
        {},
      )
    : {};

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size="lg" />
      </div>
    );
  }

  /* C1: Show ErrorState on fetch failure */
  if (error) {
    return (
      <ErrorState
        title="Failed to load test"
        description={error}
        onRetry={refetch}
      />
    );
  }

  if (questions.length === 0) {
    if (autoGenState === "checking") {
      return (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <Spinner size="lg" />
          <p className="text-text-muted text-lg">
            Looking for a practice test...
          </p>
        </div>
      );
    }

    if (autoGenState === "generating") {
      return (
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <Spinner size="lg" />
          <p className="text-text-muted text-lg">
            Generating practice test from your flashcards...
          </p>
          <p className="text-text-muted text-sm">This may take a moment</p>
        </div>
      );
    }

    if (autoGenState === "error") {
      return (
        <div className="text-center py-20">
          <p className="text-error text-lg mb-2">
            {autoGenError ?? "Something went wrong."}
          </p>
          <div className="flex gap-4 justify-center mt-4">
            <Button
              variant="secondary"
              onClick={() => setAutoGenState("idle")}
            >
              Retry
            </Button>
            <Link href={`/study-sets/${studySetId}`}>
              <Button variant="secondary">Back to Study Set</Button>
            </Link>
          </div>
        </div>
      );
    }

    return (
      <div className="text-center py-20">
        <p className="text-text-muted text-lg mb-4">
          No test questions in this study set.
        </p>
        <Link href={`/study-sets/${studySetId}`}>
          <Button variant="secondary">Back to Study Set</Button>
        </Link>
      </div>
    );
  }

  const scoreColor =
    pct >= 0.9
      ? "var(--color-success)"
      : pct >= 0.7
        ? "var(--color-warning)"
        : "var(--color-error)";

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Link
          href={`/study-sets/${studySetId}`}
          className="text-text-muted hover:text-text-primary text-sm"
        >
          &larr; Back
        </Link>
        <h1 className="font-[family-name:var(--font-heading)] text-2xl font-bold">
          Practice Test
        </h1>
        <span className="text-sm text-text-muted">
          {totalQuestions} questions
        </span>
      </div>

      {/* C20: Score banner with aria-live for announcement */}
      {submitted && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="mb-6 p-6" aria-live="polite">
            <div className="flex items-center gap-6">
              <div className="text-center">
                <span
                  className="text-4xl font-bold font-mono"
                  style={{ color: scoreColor }}
                >
                  {Math.round(pct * 100)}%
                </span>
                <p className="text-xs text-text-muted mt-1">
                  {correctCount}/{totalQuestions}
                </p>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium mb-2">
                  Bloom Level Breakdown
                </p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(bloomStats)
                    .sort(([a], [b]) => Number(a) - Number(b))
                    .map(([level, stats]) => {
                      const levelNum = Number(level);
                      const label = BLOOM_LABELS[levelNum] ?? `L${level}`;
                      return (
                        <span
                          key={level}
                          className="text-xs px-2 py-1 rounded bg-bg-input border border-border"
                        >
                          {label}: {stats.correct}/{stats.total}
                        </span>
                      );
                    })}
                </div>
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      {/* Questions */}
      <div className="space-y-6">
        {questions.map((q, qIdx) => {
          const userAnswer = answers[qIdx];
          const isCorrect = submitted && userAnswer === q.correctAnswer;
          const isWrong =
            submitted &&
            userAnswer !== undefined &&
            userAnswer !== q.correctAnswer;

          let borderStyle = "";
          if (submitted) {
            if (isCorrect) borderStyle = "border-success/30";
            else if (isWrong) borderStyle = "border-error/30";
          }

          return (
            <Card key={qIdx} className={borderStyle}>
              <div className="flex items-start gap-3 mb-4">
                <span className="text-sm font-mono text-text-muted w-8 shrink-0">
                  {qIdx + 1}.
                </span>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    {q.bloomLevel !== undefined && (
                      <Badge variant="bloom">
                        Bloom L{q.bloomLevel}
                        {BLOOM_LABELS[q.bloomLevel]
                          ? ` — ${BLOOM_LABELS[q.bloomLevel]}`
                          : ""}
                      </Badge>
                    )}
                    {submitted && (
                      <span
                        className={`text-sm font-medium ${isCorrect ? "text-success" : "text-error"}`}
                      >
                        {isCorrect ? "Correct" : "Incorrect"}
                      </span>
                    )}
                  </div>
                  {/* H19: fieldset + legend for question semantics */}
                  <fieldset className="border-0 p-0 m-0">
                    <legend className="font-medium text-base p-0 mb-0">
                      {q.question}
                    </legend>
                  </fieldset>
                </div>
              </div>

              {/* H19: radiogroup role for option semantics */}
              <div className="space-y-2 ml-11" role="radiogroup" aria-label={`Question ${qIdx + 1}: ${q.question}`}>
                {q.options.map((opt, oIdx) => {
                  let optStyle = "border-border";
                  const isOptionCorrect = oIdx === q.correctAnswer;
                  const isOptionSelected = userAnswer === oIdx;

                  if (submitted) {
                    if (isOptionCorrect)
                      optStyle = "border-success/50 bg-success/5";
                    else if (isOptionSelected && !isOptionCorrect)
                      optStyle = "border-error/50 bg-error/5";
                  } else if (isOptionSelected) {
                    optStyle = "border-accent bg-accent/5";
                  }

                  /* C17: Text/icon indicators beyond color */
                  let indicator = "";
                  if (submitted) {
                    if (isOptionCorrect) indicator = "✓ ";
                    else if (isOptionSelected) indicator = "✗ ";
                  }

                  /* C17: aria-label with answer context */
                  let ariaLabel = opt;
                  if (submitted) {
                    if (isOptionCorrect) ariaLabel = `${opt} — Correct answer`;
                    else if (isOptionSelected) ariaLabel = `${opt} — Your answer, incorrect`;
                  }

                  return (
                    <button
                      key={oIdx}
                      onClick={() => handleSelect(qIdx, oIdx)}
                      /* H19/H20: radio semantics with aria-checked */
                      role="radio"
                      aria-checked={isOptionSelected}
                      aria-label={ariaLabel}
                      className={`w-full text-left p-3 rounded-lg border transition-colors text-sm ${optStyle} ${
                        !submitted ? "hover:bg-bg-card-hover cursor-pointer" : ""
                      }`}
                    >
                      <span className="font-medium mr-2">
                        {String.fromCharCode(65 + oIdx)}.
                      </span>
                      {indicator}{opt}
                    </button>
                  );
                })}
              </div>

              {submitted && q.explanation && (
                <div className="ml-11 mt-3 p-3 rounded-lg bg-bg-input border border-border">
                  <p className="text-xs text-text-secondary">{q.explanation}</p>
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {/* Submit / Actions */}
      <div className="mt-8 mb-12 flex gap-4 justify-center">
        {!submitted ? (
          /* C18: aria-disabled instead of disabled for AT visibility */
          <Button
            size="lg"
            onClick={allAnswered ? handleSubmit : undefined}
            aria-disabled={!allAnswered}
            className={`w-full max-w-sm ${!allAnswered ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            {allAnswered
              ? "Submit Test"
              : `Answer all questions (${Object.keys(answers).length}/${totalQuestions})`}
          </Button>
        ) : (
          <>
            <Button variant="secondary" onClick={handleRetry}>
              Retry Test
            </Button>
            <Link href={`/study-sets/${studySetId}`}>
              <Button>Back to Study Set</Button>
            </Link>
          </>
        )}
      </div>
    </div>
  );
}
