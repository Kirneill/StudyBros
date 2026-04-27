"use client";

import { useCallback, useState } from "react";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import { Button, Card, Badge, Spinner } from "@/components/ui";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
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
  const studySetId = Number(id);

  const { data: studySet, loading } = useApi(
    useCallback(() => api.getStudySet(studySetId), [studySetId]),
  );

  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [submitted, setSubmitted] = useState(false);

  const questions: TestQuestion[] = (() => {
    if (!studySet) return [];
    const content = Array.isArray(studySet.content)
      ? studySet.content
      : Array.isArray(studySet.content.questions)
        ? studySet.content.questions
        : [];
    return content.filter(isQuestionRecord).map(parseQuestion);
  })();

  const totalQuestions = questions.length;
  const allAnswered = Object.keys(answers).length >= totalQuestions;

  const handleSelect = (qIndex: number, optionIndex: number) => {
    if (submitted) return;
    setAnswers((prev) => ({ ...prev, [qIndex]: optionIndex }));
  };

  const handleSubmit = () => {
    setSubmitted(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleRetry = () => {
    setAnswers({});
    setSubmitted(false);
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

  if (questions.length === 0) {
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

      {/* Score banner (after submit) */}
      {submitted && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="mb-6 p-6">
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
                  <p className="font-medium">{q.question}</p>
                </div>
              </div>

              <div className="space-y-2 ml-11">
                {q.options.map((opt, oIdx) => {
                  let optStyle = "border-border";
                  if (submitted) {
                    if (oIdx === q.correctAnswer)
                      optStyle = "border-success/50 bg-success/5";
                    else if (oIdx === userAnswer && oIdx !== q.correctAnswer)
                      optStyle = "border-error/50 bg-error/5";
                  } else if (userAnswer === oIdx) {
                    optStyle = "border-accent bg-accent/5";
                  }

                  return (
                    <button
                      key={oIdx}
                      onClick={() => handleSelect(qIdx, oIdx)}
                      disabled={submitted}
                      className={`w-full text-left p-3 rounded-lg border transition-colors text-sm ${optStyle} ${
                        !submitted ? "hover:bg-bg-card-hover" : ""
                      }`}
                    >
                      <span className="font-medium mr-2">
                        {String.fromCharCode(65 + oIdx)}.
                      </span>
                      {opt}
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
          <Button
            size="lg"
            onClick={handleSubmit}
            disabled={!allAnswered}
            className="w-full max-w-sm"
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
