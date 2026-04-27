"use client";

import { useCallback, useState } from "react";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";
import { Button, Card, Badge, ProgressBar, Spinner } from "@/components/ui";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import type { QuizQuestion } from "@/lib/types";

function parseQuizQuestions(content: Record<string, unknown> | unknown[]): QuizQuestion[] {
  const items = Array.isArray(content) ? content : [];
  return items
    .filter((item) => {
      const obj = item as Record<string, unknown>;
      return obj.question !== undefined && Array.isArray(obj.options);
    })
    .map((item) => {
      const obj = item as Record<string, unknown>;
      return {
        question: String(obj.question),
        options: (obj.options as string[]).map(String),
        correct_answer: Number(obj.correct_answer ?? 0),
        explanation: String(obj.explanation ?? ""),
        bloom_level:
          typeof obj.bloom_level === "number" ? obj.bloom_level : undefined,
      };
    });
}

function getScoreColor(pct: number): string {
  if (pct >= 0.9) return "var(--color-success)";
  if (pct >= 0.7) return "var(--color-warning)";
  return "var(--color-error)";
}

function getScoreMessage(pct: number): string {
  if (pct >= 0.9) return "Excellent! This material is getting easy for you.";
  if (pct >= 0.7) return "Good work! A few areas to review.";
  return "Let's review the fundamentals. Focus on the questions you missed.";
}

function getOptionStyle(
  index: number,
  answered: boolean,
  selectedAnswer: number | null,
  correctAnswer: number,
): string {
  if (!answered) {
    if (selectedAnswer === index) return "border-accent bg-accent/5";
    return "border-border hover:bg-bg-card-hover";
  }
  if (index === correctAnswer) return "border-success/50 bg-success/10 text-success";
  if (index === selectedAnswer && index !== correctAnswer)
    return "border-error/50 bg-error/10 text-error";
  return "border-border opacity-50";
}

export default function QuizPage() {
  const params = useParams();
  const studySetId = Number(params.id);

  const { data: studySet, loading } = useApi(
    useCallback(() => api.getStudySet(studySetId), [studySetId]),
  );

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [answered, setAnswered] = useState(false);
  const [results, setResults] = useState<boolean[]>([]);
  const [quizDone, setQuizDone] = useState(false);

  const questions = studySet ? parseQuizQuestions(studySet.content) : [];
  const currentQ = questions[currentIndex];
  const totalQuestions = questions.length;
  const correctCount = results.filter(Boolean).length;

  const handleAnswer = (index: number) => {
    if (answered) return;
    setSelectedAnswer(index);
    setAnswered(true);
    setResults((prev) => [...prev, index === currentQ.correct_answer]);
  };

  const handleNext = () => {
    if (currentIndex + 1 >= totalQuestions) {
      setQuizDone(true);
    } else {
      setCurrentIndex((prev) => prev + 1);
      setSelectedAnswer(null);
      setAnswered(false);
    }
  };

  const handleRetry = () => {
    setCurrentIndex(0);
    setSelectedAnswer(null);
    setAnswered(false);
    setResults([]);
    setQuizDone(false);
  };

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
          No quiz questions in this study set.
        </p>
        <Link href={`/study-sets/${studySetId}`}>
          <Button variant="secondary">Back to Study Set</Button>
        </Link>
      </div>
    );
  }

  if (quizDone) {
    const pct = totalQuestions > 0 ? correctCount / totalQuestions : 0;
    const scoreColor = getScoreColor(pct);

    return (
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="text-center mb-8"
        >
          <div
            className="inline-flex items-center justify-center w-32 h-32 rounded-full border-4 mb-4"
            style={{ borderColor: scoreColor }}
          >
            <span
              className="text-4xl font-bold font-mono"
              style={{ color: scoreColor }}
            >
              {Math.round(pct * 100)}%
            </span>
          </div>
          <h1 className="font-[family-name:var(--font-heading)] text-2xl font-bold mb-2">
            Quiz Complete
          </h1>
          <p className="text-text-secondary">
            {correctCount} of {totalQuestions} correct
          </p>
          <p className="text-sm text-text-muted mt-2">{getScoreMessage(pct)}</p>
        </motion.div>

        <div className="space-y-3 mb-8">
          <h2 className="text-sm font-semibold text-text-muted">Review</h2>
          {questions.map((q, i) => (
            <Card key={i} className="p-4">
              <div className="flex items-start gap-3">
                <span
                  className={`text-lg ${results[i] ? "text-success" : "text-error"}`}
                >
                  {results[i] ? "✓" : "✗"}
                </span>
                <div className="flex-1">
                  <p className="text-sm font-medium">{q.question}</p>
                  <p className="text-xs text-text-muted mt-1">
                    Correct: {q.options[q.correct_answer]}
                  </p>
                  {q.explanation && (
                    <p className="text-xs text-text-secondary mt-1">
                      {q.explanation}
                    </p>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>

        <div className="flex gap-4 justify-center">
          <Button variant="secondary" onClick={handleRetry}>
            Try Again
          </Button>
          <Link href={`/study-sets/${studySetId}`}>
            <Button>Back to Study Set</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <Link
          href={`/study-sets/${studySetId}`}
          className="text-text-muted hover:text-text-primary text-sm"
        >
          &larr; Back
        </Link>
        <Badge variant={correctCount > 0 ? "success" : "default"}>
          {correctCount}/{results.length} correct
        </Badge>
      </div>

      <ProgressBar
        value={currentIndex + 1}
        max={totalQuestions}
        label={`Question ${currentIndex + 1} of ${totalQuestions}`}
        showValue
      />

      <motion.div
        key={currentIndex}
        initial={{ opacity: 0, x: 30 }}
        animate={{ opacity: 1, x: 0 }}
        className="mt-6"
      >
        <Card>
          {currentQ.bloom_level !== undefined && (
            <div className="mb-3">
              <Badge variant="bloom">Bloom L{currentQ.bloom_level}</Badge>
            </div>
          )}
          <p className="text-lg font-medium mb-6">{currentQ.question}</p>

          <div className="space-y-2">
            {currentQ.options.map((opt, i) => {
              const style = getOptionStyle(
                i,
                answered,
                selectedAnswer,
                currentQ.correct_answer,
              );
              return (
                <button
                  key={i}
                  onClick={() => handleAnswer(i)}
                  disabled={answered}
                  className={`w-full text-left p-4 rounded-lg border transition-colors ${style}`}
                >
                  <span className="font-medium mr-2">
                    {String.fromCharCode(65 + i)}.
                  </span>
                  {opt}
                </button>
              );
            })}
          </div>

          {answered && currentQ.explanation && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="mt-4 p-3 rounded-lg bg-bg-input border border-border"
            >
              <p className="text-sm text-text-secondary">
                {currentQ.explanation}
              </p>
            </motion.div>
          )}
        </Card>

        {answered && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-4"
          >
            <Button onClick={handleNext} className="w-full" size="lg">
              {currentIndex + 1 >= totalQuestions
                ? "See Results"
                : "Next Question"}
            </Button>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
