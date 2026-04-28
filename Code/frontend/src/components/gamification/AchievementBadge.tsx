"use client";

import { motion } from "framer-motion";
import type { Achievement } from "@/lib/types";
import { BLOOM_LEVELS } from "@/lib/constants";

interface AchievementBadgeProps {
  achievement: Achievement;
  compact?: boolean;
}

export function AchievementBadge({ achievement, compact }: AchievementBadgeProps) {
  const bloom = BLOOM_LEVELS.find((b) => b.level === achievement.bloom_level);

  if (compact) {
    return (
      <div
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-bg-card border border-border"
        aria-label={`${achievement.title}: ${achievement.description}`}
      >
        <span className="text-lg" aria-hidden="true">
          🏆
        </span>
        <span className="text-sm font-medium truncate">
          {achievement.title}
        </span>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl bg-bg-card border border-border p-5"
    >
      <div className="flex items-start gap-3">
        <div className="text-3xl" aria-hidden="true">
          🏆
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-text-primary">
            {achievement.title}
          </h4>
          <p className="text-sm text-text-secondary mt-1">
            {achievement.description}
          </p>
          <div className="flex items-center gap-3 mt-3 text-xs">
            {bloom && (
              <span style={{ color: bloom.color }} className="font-medium">
                {bloom.name} level
              </span>
            )}
            {achievement.topic && (
              <span className="text-text-muted">{achievement.topic}</span>
            )}
            {achievement.earned_at && (
              <span className="text-text-muted">
                {new Date(achievement.earned_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
