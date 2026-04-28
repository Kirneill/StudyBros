"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";
import { Card } from "@/components/ui/Card";

interface TopicCompleteProps {
  topic: string;
  backHref?: string;
  stats?: {
    totalItems?: number;
    accuracy?: number;
    avgInterval?: number;
    bloomBreakdown?: Record<string, number>;
  };
}

export function TopicComplete({ topic, backHref, stats }: TopicCompleteProps) {
  const prefersReducedMotion = useReducedMotion();

  const fadeOnly = { initial: { opacity: 0 }, animate: { opacity: 1 } };

  const checkmarkInitial = prefersReducedMotion
    ? { opacity: 0 }
    : { scale: 0, rotate: -180 };
  const checkmarkAnimate = prefersReducedMotion
    ? { opacity: 1 }
    : { scale: 1, rotate: 0 };
  const checkmarkTransition = prefersReducedMotion
    ? { duration: 0.2 }
    : { type: "spring" as const, stiffness: 200, damping: 15, delay: 0.2 };

  const headingInitial = prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: 20 };
  const headingAnimate = prefersReducedMotion ? { opacity: 1 } : { opacity: 1, y: 0 };

  const statsInitial = prefersReducedMotion ? { opacity: 0 } : { opacity: 0, y: 12 };
  const statsAnimate = prefersReducedMotion ? { opacity: 1 } : { opacity: 1, y: 0 };

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
      {/* Animated checkmark */}
      <motion.div
        initial={checkmarkInitial}
        animate={checkmarkAnimate}
        transition={checkmarkTransition}
        className="w-24 h-24 rounded-full bg-mastery-mastered/20 border-2 border-mastery-mastered flex items-center justify-center mb-8"
      >
        <motion.span
          initial={fadeOnly.initial}
          animate={fadeOnly.animate}
          transition={{ delay: prefersReducedMotion ? 0 : 0.5 }}
          className="text-4xl"
        >
          <span aria-hidden="true">&#10003;</span>
          <span className="sr-only">Mastered</span>
        </motion.span>
      </motion.div>

      <motion.h1
        initial={headingInitial}
        animate={headingAnimate}
        transition={{ delay: prefersReducedMotion ? 0 : 0.4 }}
        className="text-3xl sm:text-4xl font-bold font-[family-name:var(--font-heading)] mb-4"
      >
        You&apos;ve Mastered{" "}
        <span className="text-accent">{topic}</span>!
      </motion.h1>

      <motion.p
        initial={fadeOnly.initial}
        animate={fadeOnly.animate}
        transition={{ delay: prefersReducedMotion ? 0 : 0.6 }}
        className="text-text-secondary max-w-md mb-8"
      >
        This topic is now archived. We&apos;ll bring it back only if your
        retention drops.
      </motion.p>

      {stats && (
        <motion.div
          initial={statsInitial}
          animate={statsAnimate}
          transition={{ delay: prefersReducedMotion ? 0 : 0.8 }}
          className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-10 max-w-lg w-full"
        >
          {stats.totalItems !== undefined && (
            <Card className="p-4 text-center">
              <span className="text-2xl font-bold font-mono text-text-primary">
                {stats.totalItems}
              </span>
              <p className="text-xs text-text-muted mt-1">Concepts</p>
            </Card>
          )}
          {stats.accuracy !== undefined && (
            <Card className="p-4 text-center">
              <span className="text-2xl font-bold font-mono text-success">
                {Math.round(stats.accuracy * 100)}%
              </span>
              <p className="text-xs text-text-muted mt-1">Accuracy</p>
            </Card>
          )}
          {stats.avgInterval !== undefined && (
            <Card className="p-4 text-center">
              <span className="text-2xl font-bold font-mono text-accent">
                {stats.avgInterval}d
              </span>
              <p className="text-xs text-text-muted mt-1">Avg Interval</p>
            </Card>
          )}
        </motion.div>
      )}

      <motion.div
        initial={fadeOnly.initial}
        animate={fadeOnly.animate}
        transition={{ delay: prefersReducedMotion ? 0 : 1.0 }}
        className="flex gap-4"
      >
        <Link
          href="/progress"
          className="inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors focus-visible:outline-2 focus-visible:outline-accent bg-accent text-bg-primary hover:bg-accent-hover shadow-[0_0_16px_rgba(0,212,170,0.2)] px-6 py-3 text-base"
        >
          View Knowledge Map
        </Link>
        {backHref && (
          <Link
            href={backHref}
            className="inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors focus-visible:outline-2 focus-visible:outline-accent border border-border text-text-primary hover:bg-bg-card px-6 py-3 text-base"
          >
            Review Cards
          </Link>
        )}
        <Link
          href="/dashboard"
          className="inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors focus-visible:outline-2 focus-visible:outline-accent bg-bg-card text-text-primary hover:bg-bg-card-hover border border-border px-6 py-3 text-base"
        >
          Next Topic
        </Link>
      </motion.div>
    </div>
  );
}
