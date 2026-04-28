"use client";

import { useCallback } from "react";
import { useParams } from "next/navigation";
import { ErrorState, Spinner } from "@/components/ui";
import { TopicComplete } from "@/components/gamification";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";

export default function StudySetCompletePage() {
  const params = useParams();
  const id = Number(params.id);

  /* C1: Wire up error + refetch */
  const { data: studySet, loading, error, refetch } = useApi(
    useCallback(() => api.getStudySet(id), [id]),
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorState
        title="Failed to load study set"
        description={error}
        onRetry={refetch}
      />
    );
  }

  return (
    <TopicComplete
      topic={studySet?.title ?? `Study Set ${id}`}
      stats={{
        totalItems: studySet?.item_count ?? 0,
      }}
    />
  );
}
