"use client";

import { useCallback, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AnimateIn } from "@/components/AnimateIn";
import { Button, Card, Badge, Spinner, EmptyState, ErrorState, Modal, Toast } from "@/components/ui";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";

export default function DocumentsPage() {
  const router = useRouter();
  const { data: docs, error, loading, refetch } = useApi(useCallback(() => api.listDocuments(), []));
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [renameTarget, setRenameTarget] = useState<{ id: number; title: string } | null>(null);
  const [pendingTitle, setPendingTitle] = useState("");
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const documents = useMemo(() => docs ?? [], [docs]);
  const allSelected = documents.length > 0 && selectedIds.length === documents.length;
  const selectedCount = selectedIds.length;

  const selectedDocumentsLabel = useMemo(() => {
    if (selectedCount === 0) {
      return "No documents selected";
    }
    if (selectedCount === 1) {
      return "1 document selected";
    }
    return `${selectedCount} documents selected`;
  }, [selectedCount]);

  const toggleSelected = useCallback((documentId: number) => {
    setSelectedIds((current) =>
      current.includes(documentId)
        ? current.filter((id) => id !== documentId)
        : [...current, documentId],
    );
  }, []);

  const toggleSelectAll = useCallback(() => {
    setSelectedIds((current) => {
      if (documents.length === 0) {
        return current;
      }
      if (current.length === documents.length) {
        return [];
      }
      return documents.map((doc) => doc.id);
    });
  }, [documents]);

  const openRenameModal = useCallback((documentId: number, title: string | null) => {
    setRenameTarget({ id: documentId, title: title ?? "" });
    setPendingTitle(title ?? "");
  }, []);

  const handleRename = useCallback(async () => {
    if (!renameTarget) {
      return;
    }

    const title = pendingTitle.trim();
    if (!title) {
      setToast({ message: "Document title cannot be empty.", type: "error" });
      return;
    }

    setSaving(true);
    try {
      await api.updateDocument(renameTarget.id, { title });
      setToast({ message: "Document renamed.", type: "success" });
      setRenameTarget(null);
      refetch();
    } catch (err) {
      setToast({ message: err instanceof ApiError ? err.detail : "Rename failed", type: "error" });
    } finally {
      setSaving(false);
    }
  }, [pendingTitle, refetch, renameTarget]);

  const handleBulkDelete = useCallback(async () => {
    if (selectedIds.length === 0) {
      setBulkDeleteOpen(false);
      return;
    }

    setSaving(true);
    try {
      const result = await api.bulkDeleteDocuments({ document_ids: selectedIds });
      setToast({ message: result.detail, type: "success" });
      setSelectedIds([]);
      setBulkDeleteOpen(false);
      refetch();
    } catch (err) {
      setToast({ message: err instanceof ApiError ? err.detail : "Bulk delete failed", type: "error" });
    } finally {
      setSaving(false);
    }
  }, [refetch, selectedIds]);

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
        title="Failed to load documents"
        description={error}
        onRetry={refetch}
      />
    );
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold">Documents</h1>
          <p className="text-sm text-text-muted mt-2">{selectedDocumentsLabel}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="outline" onClick={toggleSelectAll} disabled={documents.length === 0}>
            {allSelected ? "Clear Selection" : "Select Multiple"}
          </Button>
          <Button
            variant="ghost"
            onClick={() => setBulkDeleteOpen(true)}
            disabled={selectedIds.length === 0}
            className="text-error hover:text-error hover:bg-error/10"
          >
            Delete Selected
          </Button>
          {selectedIds.length > 0 && (
            <Button
              variant="outline"
              onClick={() => router.push(`/documents/${selectedIds[0]}/generate`)}
              title={selectedIds.length > 1 ? `Generates for "${documents.find((d) => d.id === selectedIds[0])?.title || "first selected"}" only` : undefined}
            >
              {selectedIds.length > 1
                ? `Generate (${documents.find((d) => d.id === selectedIds[0])?.title || "first selected"})`
                : "Generate Study Materials"}
            </Button>
          )}
          <Button onClick={() => router.push("/upload")}>
            Upload New
          </Button>
        </div>
      </div>

      {!docs || docs.length === 0 ? (
        <EmptyState
          icon="&#128196;"
          title="No documents yet"
          description="Upload a PDF, PPTX, or text file to get started."
          actionLabel="Upload Material"
          actionHref="/upload"
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {docs.map((doc, i) => {
            const selected = selectedIds.includes(doc.id);

            return (
              <AnimateIn key={doc.id} delay={i * 0.05}>
                <Card hover className={selected ? "ring-2 ring-accent" : ""}>
                  <div className="flex items-start justify-between gap-3">
                    <label className="inline-flex items-center gap-2 text-sm text-text-muted">
                      <input
                        type="checkbox"
                        checked={selected}
                        onChange={() => toggleSelected(doc.id)}
                        className="accent-accent"
                      />
                      <span className="sr-only">Select {doc.title || "Untitled document"}</span>
                      <span aria-hidden="true">Select</span>
                    </label>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openRenameModal(doc.id, doc.title)}
                    >
                      Rename
                    </Button>
                  </div>
                  <Link href={`/documents/${doc.id}`} className="block mt-3">
                    <h3 className="font-semibold truncate">{doc.title || "Untitled"}</h3>
                    <div className="flex items-center gap-2 mt-3 text-sm text-text-muted">
                      <Badge>{doc.chunk_count} chunks</Badge>
                      <span>{doc.word_count.toLocaleString()} words</span>
                    </div>
                    <p className="text-xs text-text-muted mt-2">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </p>
                  </Link>
                </Card>
              </AnimateIn>
            );
          })}
        </div>
      )}

      <Modal
        open={renameTarget !== null}
        onClose={() => !saving && setRenameTarget(null)}
        title="Rename Document"
        preventClose={saving}
      >
        <form onSubmit={(e) => { e.preventDefault(); handleRename(); }} className="space-y-4">
          <div>
            <label htmlFor="document-title" className="text-sm font-medium mb-2 block">
              Document Title
            </label>
            <input
              id="document-title"
              type="text"
              value={pendingTitle}
              onChange={(e) => setPendingTitle(e.target.value)}
              className="w-full rounded-lg border border-border bg-bg-input px-3 py-2 text-sm text-text-primary"
              placeholder="Enter document title"
            />
          </div>
          <div className="flex justify-end gap-3">
            <Button type="button" variant="ghost" onClick={() => setRenameTarget(null)} disabled={saving}>
              Cancel
            </Button>
            <Button type="submit" loading={saving}>
              Save
            </Button>
          </div>
        </form>
      </Modal>

      <Modal
        open={bulkDeleteOpen}
        onClose={() => !saving && setBulkDeleteOpen(false)}
        title="Delete Selected Documents"
        preventClose={saving}
      >
        <div className="space-y-4">
          <p className="text-text-secondary">
            This will permanently delete {selectedCount} selected document{selectedCount === 1 ? "" : "s"} and all associated study data.
          </p>
          <div className="flex justify-end gap-3">
            <Button variant="ghost" onClick={() => setBulkDeleteOpen(false)} disabled={saving}>
              Cancel
            </Button>
            <Button
              onClick={handleBulkDelete}
              loading={saving}
              variant="destructive"
            >
              Delete Selected
            </Button>
          </div>
        </div>
      </Modal>

      {toast && <Toast message={toast.message} type={toast.type} onDismiss={() => setToast(null)} />}
    </div>
  );
}
