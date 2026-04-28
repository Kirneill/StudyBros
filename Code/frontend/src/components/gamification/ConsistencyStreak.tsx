"use client";

import { motion } from "framer-motion";

interface ConsistencyStreakProps {
  streakDays: number;
  consistencyPct: number;
  studiedDates: string[];
}

function formatLocalDate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

export function ConsistencyStreak({
  streakDays,
  consistencyPct,
  studiedDates,
}: ConsistencyStreakProps) {
  const today = new Date();
  const todayStr = formatLocalDate(today);
  const last7 = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(today);
    d.setDate(d.getDate() - (6 - i));
    return formatLocalDate(d);
  });

  const studiedSet = new Set(studiedDates);
  const daysStudied = last7.filter((d) => studiedSet.has(d)).length;

  return (
    <div>
      <div className="flex items-baseline gap-2 mb-3">
        <span className="text-2xl font-bold font-mono text-accent">
          {daysStudied}
        </span>
        <span className="text-text-muted text-sm">of last 7 days</span>
      </div>
      <div className="flex gap-1.5">
        {last7.map((date) => {
          const studied = studiedSet.has(date);
          const isToday = date === todayStr;
          const displayDate = new Date(date + "T12:00:00").toLocaleDateString(
            "en",
            { month: "long", day: "numeric" },
          );
          return (
            <motion.div
              key={date}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-medium ${
                studied
                  ? "bg-accent/20 text-accent border border-accent/30"
                  : "bg-bg-input text-text-muted border border-border"
              } ${isToday ? "ring-1 ring-accent" : ""}`}
              title={date}
              aria-label={`${displayDate}: ${studied ? "studied" : "not studied"}`}
            >
              {new Date(date + "T12:00:00").toLocaleDateString("en", {
                weekday: "narrow",
              })}
            </motion.div>
          );
        })}
      </div>
      <p className="text-xs text-text-muted mt-2">
        30-day consistency: {Math.round(consistencyPct * 100)}%
        {streakDays > 0 && ` · ${streakDays}-day streak`}
      </p>
    </div>
  );
}
