"use client";

import { useCallback, useState } from "react";
import { useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Button, Card, ProgressBar, Spinner, Badge } from "@/components/ui";
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

export default function StudyPage() {
  const params = useParams<{ id: string }>();
  const studySetId = Number(params.id);

  const { data: studySet, loading: loadingSet } = useApi(
    useCallback(() => api.getStudySet(studySetId), [studySetId])
  );

  const [currentIndex, setCurrentIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [ratings, setRatings] = useState<number[]>([]);
  const [sessionDone, setSessionDone] = useState(false);
  const [lastReview, setLastReview] = useState<ReviewResponse | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [swData, setSwData] = useState<StrengthsWeaknesses | null>(null);

  const cards: CardData[] = (() => {
    if (!studySet) return [];
    const content = Array.isArray(studySet.content) ? studySet.content : [];
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
  })();

  const currentCard = cards[currentIndex];
  const totalCards = cards.length;
  const goodOrEasy = ratings.filter((r) => r >= 3).length;
  const accuracy = ratings.length > 0 ? goodOrEasy / ratings.length : 0;

  const handleRate = useCallback(
    async (rating: 1 | 2 | 3 | 4, confidence: number) => {
      if (!currentCard || submitting) return;
      setSubmitting(true);
      try {
        const response = await api.recordReview(studySetId, {
          card_index: currentCard.index,
          rating,
          confidence,
        });
        setLastReview(response);
        setRatings((prev) => [...prev, rating]);

        setTimeout(() => {
          setLastReview(null);
          setRevealed(false);
          if (currentIndex + 1 >= totalCards) {
            api
              .getStrengthsWeaknesses()
              .then(setSwData)
              .catch(() => {
                /* non-critical */
              });
            setSessionDone(true);
          } else {
            setCurrentIndex((prev) => prev + 1);
          }
          setSubmitting(false);
        }, 1200);
      } catch (err) {
        setSubmitting(false);
        console.error(
          "Review failed:",
          err instanceof ApiError ? err.detail : err
        );
      }
    },
    [currentCard, currentIndex, totalCards, studySetId, submitting]
  );

  if (loadingSet) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size="lg" />
      </div>
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
          {FSRS_RATINGS.map((r) => (
            <button
              key={r.value}
              onClick={() => handleRatingClick(r.value)}
              disabled={disabled || showConfidence}
              className={`p-3 rounded-lg border text-center transition-colors disabled:opacity-50 ${
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
                onClick={() => handleConfidenceClick(c)}
                disabled={disabled}
                className="w-10 h-10 rounded-lg border border-border text-sm font-medium transition-colors hover:bg-bg-card-hover text-text-secondary disabled:opacity-50"
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
