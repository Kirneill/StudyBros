"use client";

import { motion } from "framer-motion";
import type { Progress } from "@/lib/types";

interface MasteryTreeProps {
  topics: Progress[];
  onTopicClick?: (topic: string) => void;
}

export function MasteryTree({ topics, onTopicClick }: MasteryTreeProps) {
  function getMasteryColor(level: number): string {
    if (level >= 0.9) return "var(--color-mastery-gold)";
    if (level >= 0.7) return "var(--color-mastery-mastered)";
    if (level >= 0.3) return "var(--color-mastery-learning)";
    if (level > 0) return "var(--color-mastery-review)";
    return "var(--color-mastery-none)";
  }

  function getMasteryLabel(level: number): string {
    if (level >= 0.9) return "Deep Mastery";
    if (level >= 0.7) return "Mastered";
    if (level >= 0.3) return "Learning";
    if (level > 0) return "Started";
    return "Not Started";
  }

  if (topics.length === 0) {
    return (
      <div className="text-center py-8 text-text-muted">
        <p>No topics yet. Upload material and start studying!</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {topics.map((topic, i) => (
        <motion.button
          key={topic.topic}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.05 }}
          onClick={() => onTopicClick?.(topic.topic)}
          className="relative rounded-xl bg-bg-card border border-border p-4 text-left hover:bg-bg-card-hover transition-colors group"
        >
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
        </motion.button>
      ))}
    </div>
  );
}
