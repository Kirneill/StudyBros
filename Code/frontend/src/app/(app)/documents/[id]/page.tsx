"use client";

import { useCallback, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardHeader, CardTitle, Button, Badge, Spinner, ErrorState, Modal, Toast } from "@/components/ui";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";
import Link from "next/link";

export default function DocumentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const [showDelete, setShowDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const { data: doc, error: docError, loading, refetch: refetchDoc } = useApi(useCallback(() => api.getDocument(id), [id]));
  const { data: chunks, error: chunksError, refetch: refetchChunks } = useApi(useCallback(() => api.getDocumentChunks(id), [id]));

  const handleDelete = useCallback(async () => {
    setDeleting(true);
    try {
      await api.deleteDocument(id);
      setToast({ message: "Document deleted", type: "success" });
      setTimeout(() => router.push("/documents"), 1000);
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

  if (docError) {
    return (
      <ErrorState
        title="Failed to load document"
        description={docError}
        onRetry={refetchDoc}
      />
    );
  }

  if (!doc) {
    return <p className="text-text-muted py-8">Document not found.</p>;
  }

  return (
    <div>
      <Link href="/documents" className="text-sm text-text-muted hover:text-text-primary transition-colors">&larr; Back to Documents</Link>
      <div className="flex items-start justify-between mb-8 mt-4">
        <div>
          <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold">{doc.title || "Untitled"}</h1>
          <div className="flex items-center gap-3 mt-2 text-sm text-text-muted">
            <span>{doc.word_count.toLocaleString()} words</span>
            <span>{doc.chunk_count} chunks</span>
            <span>{new Date(doc.created_at).toLocaleDateString()}</span>
          </div>
        </div>
        <div className="flex gap-2">
          <Link href={`/documents/${id}/generate`}>
            <Button>Generate Study Materials</Button>
          </Link>
          <Button variant="ghost" onClick={() => setShowDelete(true)}>Delete</Button>
        </div>
      </div>

      {/* Chunks */}
      {chunksError ? (
        <Card>
          <CardHeader>
            <CardTitle>Content Chunks</CardTitle>
          </CardHeader>
          <div className="p-4 text-center">
            <p className="text-sm text-error mb-3">Failed to load chunks: {chunksError}</p>
            <Button variant="outline" size="sm" onClick={refetchChunks}>Try Again</Button>
          </div>
        </Card>
      ) : chunks && chunks.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Content Chunks ({chunks.length})</CardTitle>
          </CardHeader>
          <div
            className="space-y-3 max-h-96 overflow-y-auto"
            tabIndex={0}
            aria-label="Document chunks"
          >
            {chunks.map((c) => (
              <div key={c.chunk_index} className="p-3 rounded-lg bg-bg-input border border-border">
                <div className="flex items-center justify-between mb-2">
                  <Badge>Chunk {c.chunk_index + 1}</Badge>
                  <span className="text-xs text-text-muted">{c.char_count} chars</span>
                </div>
                <p className="text-sm text-text-secondary line-clamp-4">{c.content}</p>
              </div>
            ))}
          </div>
        </Card>
      ) : null}

      <Modal open={showDelete} onClose={() => setShowDelete(false)} title="Delete Document">
        <p className="text-text-secondary mb-4">This will permanently delete this document and all associated data.</p>
        <div className="flex gap-3 justify-end">
          <Button variant="ghost" onClick={() => setShowDelete(false)}>Cancel</Button>
          <Button onClick={handleDelete} loading={deleting} variant="destructive">Delete</Button>
        </div>
      </Modal>

      {toast && <Toast message={toast.message} type={toast.type} onDismiss={() => setToast(null)} />}
    </div>
  );
}
