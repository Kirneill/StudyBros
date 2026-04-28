"use client";

import { useCallback } from "react";
import { AnimateIn } from "@/components/AnimateIn";
import { Card, CardHeader, CardTitle, Spinner, EmptyState, ErrorState } from "@/components/ui";
import {
  KnowledgeHeatMap,
  MasteryTree,
  ConsistencyStreak,
  CalibrationChart,
  DifficultyMeter,
  PhaseIndicator,
  SessionReport,
} from "@/components/gamification";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import Link from "next/link";

export default function ProgressPage() {
  const { data: progress, error: errorProgress, loading: loadingProgress, refetch: refetchProgress } = useApi(useCallback(() => api.getProgress(), []));
  const { data: phase, error: errorPhase, loading: loadingPhase, refetch: refetchPhase } = useApi(useCallback(() => api.getPhase(), []));
  const { data: consistency, error: errorConsistency } = useApi(useCallback(() => api.getConsistency(), []));
  const { data: sw, error: errorSw } = useApi(useCallback(() => api.getStrengthsWeaknesses(), []));

  if (loadingProgress || loadingPhase) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size="lg" />
      </div>
    );
  }

  if (errorProgress || errorPhase) {
    return (
      <ErrorState
        title="Failed to load progress"
        description={errorProgress ?? errorPhase ?? "An unexpected error occurred."}
        onRetry={() => { refetchProgress(); refetchPhase(); }}
      />
    );
  }

  if (!progress || progress.length === 0) {
    return (
      <div>
        <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-8">Progress</h1>
        <EmptyState
          icon="📊"
          title="No progress data yet"
          description="Start studying to see your mastery progress, strengths, and areas for improvement."
          actionLabel="Go to Dashboard"
          actionHref="/dashboard"
        />
      </div>
    );
  }

  // Calculate overall accuracy from mastery levels
  const avgMastery = progress.reduce((sum, p) => sum + (p.mastery_level ?? 0), 0) / progress.length;

  return (
    <div>
      <Link href="/dashboard" className="text-sm text-text-muted hover:text-text-primary transition-colors mb-6 inline-block">
        ← Dashboard
      </Link>
      <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-8">Progress</h1>

      <div className="space-y-8">
        {/* Phase */}
        {phase && (
          <AnimateIn>
            <PhaseIndicator phase={phase} />
          </AnimateIn>
        )}

        {/* Knowledge heat map */}
        <AnimateIn delay={0.05}>
          <Card>
            <CardHeader>
              <CardTitle>Knowledge Heat Map</CardTitle>
            </CardHeader>
            <KnowledgeHeatMap topics={progress} />
          </Card>
        </AnimateIn>

        {/* Mastery tree */}
        <AnimateIn delay={0.1}>
          <Card>
            <CardHeader>
              <CardTitle>Topic Mastery</CardTitle>
            </CardHeader>
            <MasteryTree topics={progress} />
          </Card>
        </AnimateIn>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Difficulty meter */}
          <AnimateIn delay={0.15}>
            <Card>
              <CardHeader>
                <CardTitle>Difficulty Zone</CardTitle>
              </CardHeader>
              <DifficultyMeter accuracy={avgMastery} />
            </Card>
          </AnimateIn>

          {/* Consistency */}
          {errorConsistency && (
            <p className="text-sm text-red-400">Failed to load consistency data.</p>
          )}
          {consistency && (
            <AnimateIn delay={0.2}>
              <Card>
                <CardHeader>
                  <CardTitle>Study Consistency</CardTitle>
                </CardHeader>
                <ConsistencyStreak
                  streakDays={consistency.streak_days}
                  consistencyPct={consistency.consistency_pct_30d}
                  studiedDates={consistency.studied_dates}
                />
              </Card>
            </AnimateIn>
          )}
        </div>

        {/* Calibration / Strengths & weaknesses */}
        {errorSw && (
          <p className="text-sm text-red-400">Failed to load strengths and weaknesses.</p>
        )}
        {sw && (
          <AnimateIn delay={0.25}>
            <Card>
              <CardHeader>
                <CardTitle>Confidence Calibration</CardTitle>
              </CardHeader>
              <CalibrationChart calibration={sw.calibration} />
            </Card>
          </AnimateIn>
        )}

        {/* Strengths & weaknesses */}
        {sw && (
          <AnimateIn delay={0.3}>
            <Card>
              <CardHeader>
                <CardTitle>Strengths & Weaknesses</CardTitle>
              </CardHeader>
              <SessionReport data={sw} />
            </Card>
          </AnimateIn>
        )}
      </div>
    </div>
  );
}
