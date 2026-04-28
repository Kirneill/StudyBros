"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { Progress } from "@/lib/types";
import { MASTERY_COLORS } from "@/lib/constants";

interface MasteryTreeProps {
  topics: Progress[];
  onTopicClick?: (topic: string) => void;
}

function getMasteryColor(level: number): string {
  if (level >= 0.9) return MASTERY_COLORS.gold;
  if (level >= 0.7) return MASTERY_COLORS.mastered;
  if (level >= 0.3) return MASTERY_COLORS.learning;
  if (level > 0) return MASTERY_COLORS.review;
  return MASTERY_COLORS.none;
}

function getMasteryLabel(level: number): string {
  if (level >= 0.9) return "Deep Mastery";
  if (level >= 0.7) return "Mastered";
  if (level >= 0.3) return "Learning";
  if (level > 0) return "Started";
  return "Not Started";
}

export function MasteryTree({ topics, onTopicClick }: MasteryTreeProps) {
  const prefersReducedMotion = useReducedMotion();

  if (topics.length === 0) {
    return (
      <div className="text-center py-8 text-text-muted">
        <p>No topics yet. Upload material and start studying!</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {topics.map((topic, i) => {
        const delay = prefersReducedMotion ? 0 : Math.min(i * 0.05, 1.0);
        const initial = prefersReducedMotion
          ? { opacity: 0 }
          : { opacity: 0, scale: 0.9 };
        const animate = prefersReducedMotion
          ? { opacity: 1 }
          : { opacity: 1, scale: 1 };

        const content = (
          <>
            {/* Mastery indicator bar */}
            <div className="absolute top-0 left-0 right-0 h-1 rounded-t-xl overflow-hidden">
              <div
                className="h-full transition-all duration-700"
                style={{
                  width: `${topic.mastery_level * 100}%`,
                  backgroundColor: getMasteryColor(topic.mastery_level),
                }}
              />
            </div>
            <p className="text-sm font-medium text-text-primary truncate mt-1">
              {topic.topic}
            </p>
            <div className="flex items-center gap-2 mt-2">
              <span
                className="text-xs font-medium"
                style={{ color: getMasteryColor(topic.mastery_level) }}
              >
                {getMasteryLabel(topic.mastery_level)}
              </span>
            </div>
            <div className="flex items-center gap-3 mt-2 text-xs text-text-muted">
              <span>{topic.total_reviews} reviews</span>
              <span>Bloom L{topic.bloom_highest_level}</span>
            </div>
          </>
        );

        if (onTopicClick) {
          return (
            <motion.button
              key={topic.topic}
              initial={initial}
              animate={animate}
              transition={{ delay }}
              onClick={() => onTopicClick(topic.topic)}
              className="relative rounded-xl bg-bg-card border border-border p-4 text-left hover:bg-bg-card-hover transition-colors group"
            >
              {content}
            </motion.button>
          );
        }

        return (
          <motion.div
            key={topic.topic}
            initial={initial}
            animate={animate}
            transition={{ delay }}
            className="relative rounded-xl bg-bg-card border border-border p-4 text-left"
          >
            {content}
          </motion.div>
        );
      })}
    </div>
  );
}
