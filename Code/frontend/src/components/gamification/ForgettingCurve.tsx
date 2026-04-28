"use client";

import { useMemo } from "react";
import type { ScheduleCard } from "@/lib/types";

interface ForgettingCurveProps {
  cards: ScheduleCard[];
}

export function ForgettingCurve({ cards }: ForgettingCurveProps) {
  const displayed = useMemo(
    () => [...cards].sort((a, b) => a.retrievability - b.retrievability).slice(0, 20),
    [cards],
  );

  return (
    <div className="space-y-1.5">
      {displayed.map((card) => {
        const pct = Math.round(card.retrievability * 100);
        const color =
          pct >= 90
            ? "var(--color-mastery-mastered)"
            : pct >= 70
              ? "var(--color-mastery-learning)"
              : "var(--color-error)";
        return (
          <div key={card.card_id} className="flex items-center gap-3">
            <span className="text-xs text-text-muted w-12 text-right font-mono">
              #{card.card_id}
            </span>
            <div className="flex-1 h-4 rounded bg-bg-input overflow-hidden">
              <div
                role="progressbar"
                aria-valuenow={pct}
                aria-valuemin={0}
                aria-valuemax={100}
                aria-label={`Card ${card.card_id}: ${pct}% retention`}
                className="h-full rounded transition-all duration-500"
                style={{ width: `${pct}%`, backgroundColor: color }}
              />
            </div>
            <span className="text-xs font-mono w-10" style={{ color }}>
              {pct}%
            </span>
          </div>
        );
      })}
      {cards.length > 20 && (
        <p className="text-xs text-text-muted text-center mt-2">
          Showing 20 of {cards.length} cards
        </p>
      )}
    </div>
  );
}
