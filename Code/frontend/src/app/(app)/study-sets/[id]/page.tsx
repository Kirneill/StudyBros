"use client";

import { useCallback, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle, Button, Badge, Spinner, Modal, Toast, ErrorState } from "@/components/ui";
import { ForgettingCurve } from "@/components/gamification";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";
import { STUDY_SET_TYPES } from "@/lib/constants";
import Link from "next/link";

function getStudySetItems(content: Record<string, unknown> | unknown[]): unknown[] {
  if (Array.isArray(content)) {
    return content;
  }
  if (Array.isArray(content.cards)) {
    return content.cards;
  }
  if (Array.isArray(content.questions)) {
    return content.questions;
  }
  if (Array.isArray(content.key_concepts)) {
    return content.key_concepts;
  }
  if (Array.isArray(content.main_points)) {
    return content.main_points;
  }
  return [];
}

export default function StudySetDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);

  const { data: studySet, loading, error, refetch } = useApi(useCallback(() => api.getStudySet(id), [id]));
  const { data: schedule } = useApi(useCallback(() => api.getSchedule(id), [id]));

  const [showDelete, setShowDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const handleDelete = useCallback(async () => {
    setDeleting(true);
    try {
      await api.deleteStudySet(id);
      setToast({ message: "Study set deleted", type: "success" });
      setTimeout(() => router.push("/study-sets"), 1000);
    } catch (err) {
      setToast({ message: err instanceof ApiError ? err.detail : "Delete failed", type: "error" });
    } finally {
      setDeleting(false);
      setShowDelete(false);
    }
  }, [id, router]);

  if (loading) {
    return <div className="flex items-center justify-center py-20"><Spinner size="lg" /></div>;
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

  if (!studySet) {
    return <p className="text-text-muted py-8">Study set not found.</p>;
  }

  const typeInfo = STUDY_SET_TYPES[studySet.set_type as keyof typeof STUDY_SET_TYPES];
  const items = getStudySetItems(studySet.content);

  return (
    <div>
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold">{studySet.title || "Untitled"}</h1>
          <div className="flex items-center gap-3 mt-2">
            <Badge variant="accent">{typeInfo?.label ?? studySet.set_type}</Badge>
            <span className="text-sm text-text-muted">{studySet.item_count} items</span>
            <span className="text-sm text-text-muted">{new Date(studySet.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <a href={api.getExportUrl(id, "json")} download className="inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2 bg-bg-card border border-border text-text-primary hover:bg-bg-card-hover px-3 py-1.5 text-sm">
            Export JSON
          </a>
          <a href={api.getExportUrl(id, "markdown")} download className="inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2 bg-bg-card border border-border text-text-primary hover:bg-bg-card-hover px-3 py-1.5 text-sm">
            Export MD
          </a>
          <Button variant="ghost" size="sm" onClick={() => setShowDelete(true)}>Delete</Button>
        </div>
      </div>

      {/* Study actions */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
        <Link href={`/study-sets/${id}/study`}>
          <Card hover className="text-center py-5 border-accent/20 hover:border-accent/40">
            <span className="text-2xl block mb-2" aria-hidden="true">📖</span>
            <span className="font-medium text-sm">Study Flashcards</span>
            {schedule && schedule.due_count > 0 && (
              <p className="text-xs text-warning mt-1">{schedule.due_count} cards due</p>
            )}
          </Card>
        </Link>
        <Link href={`/study-sets/${id}/quiz`}>
          <Card hover className="text-center py-5">
            <span className="text-2xl block mb-2" aria-hidden="true">❓</span>
            <span className="font-medium text-sm">Take Quiz</span>
            <p className="text-xs text-text-muted mt-1">One at a time</p>
          </Card>
        </Link>
        <Link href={`/study-sets/${id}/test`}>
          <Card hover className="text-center py-5">
            <span className="text-2xl block mb-2" aria-hidden="true">📝</span>
            <span className="font-medium text-sm">Practice Test</span>
            <p className="text-xs text-text-muted mt-1">All questions</p>
          </Card>
        </Link>
      </div>

      {/* FSRS Schedule */}
      {schedule && schedule.cards.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Retention Schedule</CardTitle>
              <Badge variant={schedule.due_count > 0 ? "warning" : "success"}>
                {schedule.due_count} due
              </Badge>
            </div>
          </CardHeader>
          <ForgettingCurve cards={schedule.cards} />
        </Card>
      )}

      {/* Content preview */}
      <Card>
        <CardHeader>
          <CardTitle>Content ({items.length} items)</CardTitle>
        </CardHeader>
        <div className="space-y-3 max-h-[60vh] overflow-y-auto">
          {items.map((item, i) => {
            if (typeof item === "string") {
              return (
                <div key={i} className="p-4 rounded-lg bg-bg-input border border-border">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge>#{i + 1}</Badge>
                  </div>
                  <p className="text-sm text-text-secondary">{item}</p>
                </div>
              );
            }

            const obj = item as Record<string, unknown>;
            return (
              <div key={i} className="p-4 rounded-lg bg-bg-input border border-border">
                <div className="flex items-center gap-2 mb-2">
                  <Badge>#{i + 1}</Badge>
                  {obj.bloom_level !== undefined && (
                    <Badge variant="bloom">Bloom L{String(obj.bloom_level)}</Badge>
                  )}
                </div>
                {/* Flashcard */}
                {(obj.front !== undefined || obj.question !== undefined) && (
                  <div>
                    <p className="text-sm font-medium">{String(obj.front ?? obj.question)}</p>
                    <p className="text-sm text-text-secondary mt-2">{String(obj.back ?? obj.answer ?? "")}</p>
                  </div>
                )}
                {/* Quiz question */}
                {obj.prompt !== undefined && (
                  <div>
                    <p className="text-sm font-medium">{String(obj.prompt)}</p>
                    {Array.isArray(obj.options) && obj.options.every((opt) => typeof opt === "object") && (
                      <ul className="mt-2 space-y-1">
                        {(obj.options as Record<string, unknown>[]).map((opt, j) => (
                          <li key={j} className={`text-sm px-2 py-1 rounded ${
                            j === Number(obj.correct_index) ? "text-success bg-success/5" : "text-text-secondary"
                          }`}>
                            {String.fromCharCode(65 + j)}. {String(opt.text ?? "")}
                          </li>
                        ))}
                      </ul>
                    )}
                    {Array.isArray(obj.options) && obj.options.every((opt) => typeof opt === "string") && (
                      <ul className="mt-2 space-y-1">
                        {(obj.options as string[]).map((opt, j) => (
                          <li key={j} className={`text-sm px-2 py-1 rounded ${
                            j === Number(obj.correct_answer) ? "text-success bg-success/5" : "text-text-secondary"
                          }`}>
                            {String.fromCharCode(65 + j)}. {opt}
                          </li>
                        ))}
                      </ul>
                    )}
                    {typeof obj.explanation === "string" && (
                      <p className="text-xs text-text-muted mt-2">{obj.explanation}</p>
                    )}
                  </div>
                )}
              </div>
            );
          })}
          {items.length === 0 && (
            <p className="text-text-muted text-sm py-4 text-center">
              Content is stored in a structured format.
            </p>
          )}
        </div>
      </Card>

      <Modal open={showDelete} onClose={() => setShowDelete(false)} title="Delete Study Set">
        <p className="text-text-secondary mb-4">This will permanently delete this study set.</p>
        <div className="flex gap-3 justify-end">
          <Button variant="ghost" onClick={() => setShowDelete(false)}>Cancel</Button>
          <Button onClick={handleDelete} loading={deleting} variant="destructive">Delete</Button>
        </div>
      </Modal>

      {toast && <Toast message={toast.message} type={toast.type} onDismiss={() => setToast(null)} />}
    </div>
  );
}
