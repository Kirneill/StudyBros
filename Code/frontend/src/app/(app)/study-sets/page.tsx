"use client";

import { useCallback } from "react";
import Link from "next/link";
import { AnimateIn } from "@/components/AnimateIn";
import { Card, Badge, Spinner, EmptyState } from "@/components/ui";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import { STUDY_SET_TYPES } from "@/lib/constants";

export default function StudySetsPage() {
  const { data: sets, loading } = useApi(useCallback(() => api.listStudySets(), []));

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>;
  }

  return (
    <div>
      <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-8">Study Sets</h1>

      {!sets || sets.length === 0 ? (
        <EmptyState
          icon="&#128218;"
          title="No study sets yet"
          description="Generate flashcards, quizzes, or practice tests from your documents."
          actionLabel="Upload Material"
          actionHref="/upload"
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {sets.map((s, i) => {
            const typeInfo = STUDY_SET_TYPES[s.set_type as keyof typeof STUDY_SET_TYPES];
            return (
              <AnimateIn key={s.id} delay={i * 0.05}>
                <Link href={`/study-sets/${s.id}`}>
                  <Card hover>
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{typeInfo?.icon ?? "&#128203;"}</span>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold truncate">{s.title || "Untitled"}</h3>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="accent">{typeInfo?.label ?? s.set_type}</Badge>
                          <span className="text-sm text-text-muted">{s.item_count} items</span>
                        </div>
                        <p className="text-xs text-text-muted mt-2">
                          {new Date(s.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </Card>
                </Link>
              </AnimateIn>
            );
          })}
        </div>
      )}
    </div>
  );
}
