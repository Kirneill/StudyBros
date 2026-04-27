"use client";

import { useCallback } from "react";
import { useParams } from "next/navigation";
import { Spinner } from "@/components/ui";
import { TopicComplete } from "@/components/gamification";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";

export default function StudySetCompletePage() {
  const params = useParams();
  const id = Number(params.id);

  const { data: studySet, loading } = useApi(
    useCallback(() => api.getStudySet(id), [id]),
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <TopicComplete
      topic={studySet?.title ?? `Study Set ${id}`}
      stats={{
        totalItems: studySet?.item_count ?? 0,
        accuracy: 0.94,
        avgInterval: 45,
      }}
    />
  );
}
