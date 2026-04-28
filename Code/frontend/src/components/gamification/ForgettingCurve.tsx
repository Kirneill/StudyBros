"use client";

import { useMemo, useState } from "react";
import type { ScheduleCard } from "@/lib/types";

interface ForgettingCurveProps {
  cards: ScheduleCard[];
  cardLabels?: Map<number, string>;
}

const MAX_DOTS = 15;

function formatScheduledDays(days: number): string {
  if (days <= 0) return "Due now";
  if (days === 1) return "Tomorrow";
  if (days <= 6) return `In ${days} days`;
  if (days <= 13) return "In ~1 week";
  const weeks = Math.round(days / 7);
  return `In ~${weeks} weeks`;
}

interface Bucket {
  scheduledDays: number;
  label: string;
  cards: ScheduleCard[];
}

export function ForgettingCurve({ cards, cardLabels }: ForgettingCurveProps) {
  const [expanded, setExpanded] = useState<number | null>(null);

  const buckets = useMemo(() => {
    const grouped = new Map<number, ScheduleCard[]>();
    for (const card of cards) {
      const key = Math.max(0, card.scheduled_days);
      const list = grouped.get(key);
      if (list) {
        list.push(card);
      } else {
        grouped.set(key, [card]);
      }
    }

    const result: Bucket[] = [];
    for (const [days, group] of grouped) {
      result.push({
        scheduledDays: days,
        label: formatScheduledDays(days),
        cards: group,
      });
    }

    result.sort((a, b) => a.scheduledDays - b.scheduledDays);
    return result;
  }, [cards]);

  const summary = useMemo(() => {
    if (cards.length === 0) return "No cards scheduled yet.";
    const dueNow = buckets.find((b) => b.scheduledDays === 0);
    if (dueNow) {
      return `${dueNow.cards.length} card${dueNow.cards.length === 1 ? "" : "s"} due for review.`;
    }
    const next = buckets[0];
    if (!next) return "All caught up!";
    const dayLabel =
      next.scheduledDays === 1
        ? "1 day"
        : `${next.scheduledDays} days`;
    return `All caught up! Next review in ${dayLabel}.`;
  }, [cards.length, buckets]);

  if (cards.length === 0) {
    return (
      <p className="text-sm text-text-muted">{summary}</p>
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-sm text-text-secondary">{summary}</p>
      <div className="space-y-1">
        {buckets.map((bucket) => {
          const isDue = bucket.scheduledDays === 0;
          const dotCount = Math.min(bucket.cards.length, MAX_DOTS);
          const overflow = bucket.cards.length - dotCount;
          const isExpanded = expanded === bucket.scheduledDays;

          return (
            <div key={bucket.scheduledDays}>
              <button
                type="button"
                onClick={() =>
                  setExpanded(isExpanded ? null : bucket.scheduledDays)
                }
                aria-expanded={isExpanded}
                className={`flex items-center gap-3 px-2 py-1.5 rounded-md w-full text-left transition-colors hover:bg-bg-card-hover ${
                  isDue ? "bg-error/10 hover:bg-error/15" : ""
                }`}
              >
                <span
                  className={`text-[10px] shrink-0 transition-transform ${
                    isExpanded ? "rotate-90" : ""
                  } ${isDue ? "text-error" : "text-text-muted"}`}
                >
                  ▶
                </span>
                <span
                  className={`text-xs w-24 shrink-0 ${
                    isDue
                      ? "text-error font-semibold"
                      : "text-text-muted"
                  }`}
                >
                  {bucket.label}
                </span>
                <div
                  className="flex items-center gap-0.5 flex-wrap"
                  role="img"
                  aria-label={`${bucket.cards.length} card${bucket.cards.length === 1 ? "" : "s"} ${bucket.label.toLowerCase()}`}
                >
                  {Array.from({ length: dotCount }, (_, i) => {
                    const card = bucket.cards[i];
                    const dotColor = isDue
                      ? "bg-error"
                      : card.state === "learning" || card.state === "relearning"
                        ? "bg-warning"
                        : "bg-accent";
                    return (
                      <span
                        key={card.card_id}
                        className={`w-2 h-2 rounded-full ${dotColor}`}
                      />
                    );
                  })}
                  {overflow > 0 && (
                    <span className="text-[10px] text-text-muted ml-0.5">
                      +{overflow}
                    </span>
                  )}
                </div>
                <span
                  className={`text-xs ml-auto shrink-0 tabular-nums ${
                    isDue ? "text-error" : "text-text-muted"
                  }`}
                >
                  {bucket.cards.length} card{bucket.cards.length === 1 ? "" : "s"}
                </span>
              </button>

              {isExpanded && (
                <ul className="ml-8 mt-1 mb-2 space-y-0.5">
                  {bucket.cards.map((card) => {
                    const label = cardLabels?.get(card.card_id);
                    return (
                      <li
                        key={card.card_id}
                        className="flex items-center gap-2 text-xs text-text-secondary py-0.5 px-2"
                      >
                        <span className="text-text-muted tabular-nums shrink-0">
                          #{card.card_id + 1}
                        </span>
                        {label ? (
                          <span className="truncate">{label}</span>
                        ) : (
                          <span className="text-text-muted italic">
                            Card {card.card_id + 1}
                          </span>
                        )}
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
