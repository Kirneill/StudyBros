"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Button, Card, ErrorState, ProgressBar, Spinner, Badge } from "@/components/ui";
import { DifficultyMeter, SessionReport } from "@/components/gamification";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";
import { FSRS_RATINGS } from "@/lib/constants";
import type { ReviewResponse, StrengthsWeaknesses } from "@/lib/types";
import Link from "next/link";

interface CardData {
  index: number;
  front: string;
  back: string;
  bloomLevel?: number;
}

function getFlashcardItems(content: Record<string, unknown> | unknown[]): unknown[] {
  if (Array.isArray(content)) {
    return content;
  }
  if (Array.isArray(content.cards)) {
    return content.cards;
  }
  return [];
}

function getBloomLevelDistribution(cards: CardData[]): Record<string, number> {
  return cards.reduce<Record<string, number>>((distribution, card) => {
    const level = card.bloomLevel ?? 1;
    const key = String(level);
    distribution[key] = (distribution[key] ?? 0) + 1;
    return distribution;
  }, {});
}

export default function StudyPage() {
  const params = useParams<{ id: string }>();
  const studySetId = Number(params.id);

  const { data: studySet, loading: loadingSet, error: fetchError, refetch } = useApi(
    useCallback(() => api.getStudySet(studySetId), [studySetId])
  );

  const [currentIndex, setCurrentIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [ratings, setRatings] = useState<number[]>([]);
  const [confidenceRatings, setConfidenceRatings] = useState<number[]>([]);
  const [sessionDone, setSessionDone] = useState(false);
  const [lastReview, setLastReview] = useState<ReviewResponse | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [swData, setSwData] = useState<StrengthsWeaknesses | null>(null);
  const [reviewError, setReviewError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const cards: CardData[] = useMemo(() => {
    if (!studySet) return [];
    const content = getFlashcardItems(studySet.content);
    return content.map((item, i) => {
      const obj = item as Record<string, unknown>;
      return {
        index: i,
        front: String(obj.front ?? obj.question ?? `Card ${i + 1}`),
        back: String(obj.back ?? obj.answer ?? obj.explanation ?? ""),
        bloomLevel:
          typeof obj.bloom_level === "number" ? obj.bloom_level : undefined,
      };
    });
  }, [studySet]);

  const currentCard = cards[currentIndex];
  const totalCards = cards.length;
  const goodOrEasy = ratings.filter((r) => r >= 3).length;
  const accuracy = ratings.length > 0 ? goodOrEasy / ratings.length : 0;

  useEffect(() => () => { if (timerRef.current) clearTimeout(timerRef.current); }, []);

  const handleRate = useCallback(
    async (rating: 1 | 2 | 3 | 4, confidence: number) => {
      if (!currentCard || submitting) return;
      setSubmitting(true);
      setReviewError(null);
      try {
        const response = await api.recordReview(studySetId, {
          card_index: currentCard.index,
          rating,
          confidence,
        });
        setLastReview(response);
        const nextRatings = [...ratings, rating];
        const nextConfidenceRatings = [...confidenceRatings, confidence];
        setRatings(nextRatings);
        setConfidenceRatings(nextConfidenceRatings);

        timerRef.current = setTimeout(() => {
          const finalizeReview = async () => {
            setLastReview(null);
            setRevealed(false);

            if (currentIndex + 1 >= totalCards) {
              try {
                await api.completeStudySession(studySetId, {
                  total_items: totalCards,
                  correct_count: nextRatings.filter((value) => value >= 3).length,
                  confidence_sum: nextConfidenceRatings.reduce((sum, value) => sum + value, 0),
                  bloom_level_distribution: getBloomLevelDistribution(cards),
                });
              } catch (sessionError) {
                console.error(
                  "Study session save failed:",
                  sessionError instanceof ApiError ? sessionError.detail : sessionError,
                );
              }

              try {
                const strengths = await api.getStrengthsWeaknesses();
                setSwData(strengths);
              } catch {
                /* non-critical */
              }
              setSessionDone(true);
            } else {
              setCurrentIndex((prev) => prev + 1);
            }

            setSubmitting(false);
          };

          void finalizeReview();
        }, 1200);
      } catch (err) {
        setSubmitting(false);
        const message = err instanceof ApiError ? err.detail : "Failed to save review. Please try again.";
        setReviewError(message);
        console.error("Review failed:", err);
      }
    },
    [cards, confidenceRatings, currentCard, currentIndex, ratings, studySetId, submitting, totalCards]
  );

  if (loadingSet) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size="lg" />
      </div>
    );
  }

  if (fetchError) {
    return (
      <ErrorState
        title="Failed to load study set"
        description={fetchError}
        onRetry={refetch}
      />
    );
  }

  if (cards.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-text-muted text-lg mb-4">
          No cards to study in this set.
        </p>
        <Link href={`/study-sets/${studySetId}`}>
          <Button variant="secondary">Back to Study Set</Button>
        </Link>
      </div>
    );
  }

  if (sessionDone) {
    return (
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-2 text-center">
            Session Complete
          </h1>
          <p className="text-text-secondary text-center mb-8">
            You reviewed {totalCards} card{totalCards !== 1 ? "s" : ""}
          </p>
        </motion.div>

        {swData && (
          <SessionReport
            data={swData}
            accuracy={accuracy}
            totalCards={totalCards}
          />
        )}

        {!swData && (
          <Card className="text-center p-8 mb-6">
            <span
              className="text-5xl block mb-4"
              style={{
                color:
                  accuracy >= 0.85
                    ? "var(--color-success)"
                    : accuracy >= 0.7
                      ? "var(--color-warning)"
                      : "var(--color-error)",
              }}
            >
              {Math.round(accuracy * 100)}%
            </span>
            <p className="text-text-muted">Session accuracy</p>
          </Card>
        )}

        <div className="flex gap-4 justify-center mt-8">
          <Link href={`/study-sets/${studySetId}`}>
            <Button variant="secondary">Back to Study Set</Button>
          </Link>
          <Link href="/progress">
            <Button>View Progress</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Link
          href={`/study-sets/${studySetId}`}
          className="text-text-muted hover:text-text-primary text-sm"
        >
          &larr; Back
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-sm text-text-muted">
            {Math.round(accuracy * 100)}% accuracy
          </span>
          <Badge
            variant={
              accuracy >= 0.85
                ? "success"
                : accuracy >= 0.7
                  ? "warning"
                  : "error"
            }
          >
            {goodOrEasy}/{ratings.length} correct
          </Badge>
        </div>
      </div>

      {/* Progress */}
      <ProgressBar
        value={currentIndex + 1}
        max={totalCards}
        label={`Card ${currentIndex + 1} of ${totalCards}`}
        showValue
      />

      {/* Card */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -50 }}
          transition={{ duration: 0.3 }}
          className="mt-6"
        >
          <Card className="min-h-[280px] flex flex-col">
            {currentCard.bloomLevel !== undefined && (
              <div className="mb-3">
                <Badge variant="bloom">Bloom L{currentCard.bloomLevel}</Badge>
              </div>
            )}

            <div className="flex-1 flex items-center justify-center py-8">
              <p className="text-lg text-center font-medium">
                {currentCard.front}
              </p>
            </div>

            <div aria-live="polite" aria-atomic="true">
              {revealed && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="border-t border-border pt-4 mt-4"
                >
                  <p className="text-text-secondary text-center">
                    {currentCard.back}
                  </p>
                </motion.div>
              )}
            </div>

            {!revealed && (
              <div className="mt-auto pt-4">
                <Button
                  onClick={() => setRevealed(true)}
                  className="w-full"
                  size="lg"
                >
                  Show Answer
                </Button>
              </div>
            )}
          </Card>

          {lastReview && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-3 p-3 rounded-lg bg-accent-light text-accent text-sm text-center"
            >
              Next review:{" "}
              {lastReview.scheduled_days < 1
                ? "in a few hours"
                : `in ${Math.round(lastReview.scheduled_days)} day${Math.round(lastReview.scheduled_days) !== 1 ? "s" : ""}`}
            </motion.div>
          )}

          {revealed && !lastReview && (
            <RatingPanel onRate={handleRate} disabled={submitting} />
          )}

          {reviewError && (
            <div role="alert" className="mt-3 p-3 rounded-lg bg-error/10 text-error text-sm text-center">
              <p>{reviewError}</p>
              <button
                type="button"
                onClick={() => setReviewError(null)}
                className="mt-2 underline text-xs focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
              >
                Dismiss
              </button>
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {ratings.length >= 3 && (
        <div className="mt-8">
          <DifficultyMeter accuracy={accuracy} />
        </div>
      )}
    </div>
  );
}

function RatingPanel({
  onRate,
  disabled,
}: {
  onRate: (rating: 1 | 2 | 3 | 4, confidence: number) => void;
  disabled: boolean;
}) {
  const [showConfidence, setShowConfidence] = useState(false);
  const [selectedRating, setSelectedRating] = useState<
    1 | 2 | 3 | 4 | null
  >(null);
  const firstRatingRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    firstRatingRef.current?.focus();
  }, []);

  const handleRatingClick = (rating: 1 | 2 | 3 | 4) => {
    setSelectedRating(rating);
    setShowConfidence(true);
  };

  const handleConfidenceClick = (conf: number) => {
    if (selectedRating) {
      onRate(selectedRating, conf);
    }
  };

  return (
    <div className="mt-4 space-y-4">
      <div>
        <p className="text-xs text-text-muted text-center mb-2">
          How well did you know this?
        </p>
        <div className="grid grid-cols-4 gap-2">
          {FSRS_RATINGS.map((r, i) => (
            <button
              key={r.value}
              ref={i === 0 ? firstRatingRef : undefined}
              type="button"
              onClick={() => handleRatingClick(r.value)}
              disabled={disabled || showConfidence}
              aria-pressed={selectedRating === r.value}
              className={`p-3 rounded-lg border text-center transition-colors disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2 ${
                selectedRating === r.value
                  ? "border-accent bg-accent/10"
                  : "border-border hover:bg-bg-card-hover"
              }`}
            >
              <span
                className="block text-sm font-medium"
                style={{ color: r.color }}
              >
                {r.label}
              </span>
              <span className="block text-xs text-text-muted mt-0.5">
                {r.description}
              </span>
            </button>
          ))}
        </div>
      </div>

      {showConfidence && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <p className="text-xs text-text-muted text-center mb-2">
            How confident are you? (1-5)
          </p>
          <div className="flex justify-center gap-2">
            {[1, 2, 3, 4, 5].map((c) => (
              <button
                key={c}
                type="button"
                onClick={() => handleConfidenceClick(c)}
                disabled={disabled}
                className="w-11 h-11 rounded-lg border border-border text-sm font-medium transition-colors hover:bg-bg-card-hover text-text-secondary disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
              >
                {c}
              </button>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
