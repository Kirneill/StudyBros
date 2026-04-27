"use client";

import { motion } from "framer-motion";
import Link from "next/link";

interface TopicCompleteProps {
  topic: string;
  stats?: {
    totalItems?: number;
    accuracy?: number;
    avgInterval?: number;
    bloomBreakdown?: Record<string, number>;
  };
}

export function TopicComplete({ topic, stats }: TopicCompleteProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
      {/* Animated checkmark */}
      <motion.div
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 200, damping: 15, delay: 0.2 }}
        className="w-24 h-24 rounded-full bg-mastery-mastered/20 border-2 border-mastery-mastered flex items-center justify-center mb-8"
      >
        <motion.span
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-4xl"
        >
          &#10003;
        </motion.span>
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="text-3xl sm:text-4xl font-bold font-[family-name:var(--font-heading)] mb-4"
      >
        You&apos;ve Mastered{" "}
        <span className="text-accent">{topic}</span>!
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="text-text-secondary max-w-md mb-8"
      >
        This topic is now archived. We&apos;ll bring it back only if your
        retention drops.
      </motion.p>

      {stats && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-10 max-w-lg w-full"
        >
          {stats.totalItems !== undefined && (
            <div className="p-4 rounded-xl bg-bg-card border border-border">
              <span className="text-2xl font-bold font-mono text-text-primary">
                {stats.totalItems}
              </span>
              <p className="text-xs text-text-muted mt-1">Concepts</p>
            </div>
          )}
          {stats.accuracy !== undefined && (
            <div className="p-4 rounded-xl bg-bg-card border border-border">
              <span className="text-2xl font-bold font-mono text-success">
                {Math.round(stats.accuracy * 100)}%
              </span>
              <p className="text-xs text-text-muted mt-1">Accuracy</p>
            </div>
          )}
          {stats.avgInterval !== undefined && (
            <div className="p-4 rounded-xl bg-bg-card border border-border">
              <span className="text-2xl font-bold font-mono text-accent">
                {stats.avgInterval}d
              </span>
              <p className="text-xs text-text-muted mt-1">Avg Interval</p>
            </div>
          )}
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.0 }}
        className="flex gap-4"
      >
        <Link
          href="/progress"
          className="px-6 py-3 rounded-xl bg-accent text-bg-primary font-semibold hover:bg-accent-hover transition-colors"
        >
          View Knowledge Map
        </Link>
        <Link
          href="/dashboard"
          className="px-6 py-3 rounded-xl border border-border text-text-primary font-semibold hover:bg-bg-card transition-colors"
        >
          Next Topic
        </Link>
      </motion.div>
    </div>
  );
}
