"use client";

import { useCallback } from "react";
import { AnimateIn } from "@/components/AnimateIn";
import { Spinner, EmptyState, ErrorState } from "@/components/ui";
import { AchievementBadge } from "@/components/gamification";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";

export default function AchievementsPage() {
  const { data: achievements, error, loading, refetch } = useApi(useCallback(() => api.getAchievements(), []));

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return <ErrorState title="Failed to load achievements" description={error} onRetry={refetch} />;
  }

  return (
    <div>
      <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-8">Achievements</h1>

      {!achievements || achievements.length === 0 ? (
        <EmptyState
          icon="🏆"
          title="No achievements yet"
          description="Earn achievements by demonstrating real competency — mastering topics, reaching higher Bloom levels, and maintaining consistency."
          actionLabel="Start Studying"
          actionHref="/dashboard"
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {achievements.map((a, i) => (
            <AnimateIn key={`${a.type}-${a.title}`} delay={i * 0.05}>
              <AchievementBadge achievement={a} />
            </AnimateIn>
          ))}
        </div>
      )}
    </div>
  );
}
