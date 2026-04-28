"use client";

import { useCallback } from "react";
import { AnimateIn } from "@/components/AnimateIn";
import { Card, CardHeader, CardTitle, Spinner, EmptyState, ErrorState } from "@/components/ui";
import { MasteryTree, ConsistencyStreak, AchievementBadge, PhaseIndicator } from "@/components/gamification";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import Link from "next/link";

export default function DashboardPage() {
  const { data: progress, error: errorProgress, loading: loadingProgress, refetch: refetchProgress } = useApi(useCallback(() => api.getProgress(), []));
  const { data: studySets, error: errorSets, loading: loadingSets, refetch: refetchSets } = useApi(useCallback(() => api.listStudySets(), []));
  const { data: achievements, error: errorAch, loading: loadingAch } = useApi(useCallback(() => api.getAchievements(), []));
  const { data: phase, error: errorPhase, loading: loadingPhase } = useApi(useCallback(() => api.getPhase(), []));
  const { data: consistency } = useApi(useCallback(() => api.getConsistency(), []));

  const loading = loadingProgress || loadingSets;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!loading && (errorProgress || errorSets)) {
    return (
      <ErrorState
        title="Failed to load dashboard"
        description={errorProgress ?? errorSets ?? "An unexpected error occurred."}
        onRetry={() => { refetchProgress(); refetchSets(); }}
      />
    );
  }

  const totalSets = studySets?.length ?? 0;
  const hasContent = totalSets > 0;

  if (!hasContent) {
    return (
      <div>
        <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-8">Dashboard</h1>
        <EmptyState
          icon="📚"
          title="Welcome to StudyBros"
          description="Upload your first study material and we'll help you build real competency, not just review cards."
          actionLabel="Upload Material"
          actionHref="/upload"
        />
      </div>
    );
  }

  return (
    <div>
      <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-8">Dashboard</h1>

      <div className="space-y-8">
        {/* Due cards hero */}
        <AnimateIn>
          <Link href="/study-sets" className="block focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2 rounded-xl">
            <Card hover className="border-accent/20 bg-gradient-to-r from-bg-card to-accent/5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-text-muted text-sm mb-1">Ready to study</p>
                  <p className="text-2xl font-bold font-[family-name:var(--font-heading)]">
                    {totalSets} study set{totalSets !== 1 ? "s" : ""} available
                  </p>
                  <p className="text-text-secondary text-sm mt-1">Pick up where you left off</p>
                </div>
                <div className="text-4xl" aria-hidden="true">📖</div>
              </div>
            </Card>
          </Link>
        </AnimateIn>

        {/* Phase indicator */}
        {!loadingPhase && errorPhase && (
          <p className="text-sm text-red-400">Failed to load learning phase.</p>
        )}
        {!loadingPhase && phase && (
          <AnimateIn delay={0.1}>
            <PhaseIndicator phase={phase} />
          </AnimateIn>
        )}

        {/* Mastery tree */}
        {progress && progress.length > 0 && (
          <AnimateIn delay={0.15}>
            <Card>
              <CardHeader>
                <CardTitle>Knowledge Map</CardTitle>
              </CardHeader>
              <MasteryTree topics={progress} />
            </Card>
          </AnimateIn>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Consistency */}
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

          {/* Recent achievements */}
          {!loadingAch && errorAch && (
            <p className="text-sm text-red-400">Failed to load achievements.</p>
          )}
          {!loadingAch && achievements && achievements.length > 0 && (
            <AnimateIn delay={0.25}>
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Recent Achievements</CardTitle>
                    <Link href="/achievements" className="text-xs text-accent hover:text-accent-hover">
                      View all
                    </Link>
                  </div>
                </CardHeader>
                <div className="space-y-2">
                  {achievements.slice(0, 3).map((a) => (
                    <AchievementBadge key={`${a.type}-${a.title}`} achievement={a} compact />
                  ))}
                </div>
              </Card>
            </AnimateIn>
          )}
        </div>

        {/* Quick links */}
        <AnimateIn delay={0.3}>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { href: "/upload", label: "Upload", icon: "↑" },
              { href: "/documents", label: "Documents", icon: "📄" },
              { href: "/study-sets", label: "Study Sets", icon: "📚" },
              { href: "/progress", label: "Full Progress", icon: "📊" },
            ].map((item) => (
              <Link key={item.href} href={item.href}>
                <Card hover className="text-center py-4">
                  <span className="text-2xl block mb-1">{item.icon}</span>
                  <span className="text-sm text-text-secondary">{item.label}</span>
                </Card>
              </Link>
            ))}
          </div>
        </AnimateIn>
      </div>
    </div>
  );
}
