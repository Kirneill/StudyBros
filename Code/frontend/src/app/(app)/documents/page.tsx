"use client";

import { useCallback } from "react";
import Link from "next/link";
import { AnimateIn } from "@/components/AnimateIn";
import { Card, Badge, Spinner, EmptyState } from "@/components/ui";
import { useApi } from "@/lib/hooks";
import * as api from "@/lib/api";

export default function DocumentsPage() {
  const { data: docs, loading } = useApi(useCallback(() => api.listDocuments(), []));

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold">Documents</h1>
        <Link href="/upload">
          <span className="inline-flex items-center px-4 py-2 rounded-lg bg-accent text-bg-primary text-sm font-medium hover:bg-accent-hover transition-colors">
            Upload New
          </span>
        </Link>
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
          {docs.map((doc, i) => (
            <AnimateIn key={doc.id} delay={i * 0.05}>
              <Link href={`/documents/${doc.id}`}>
                <Card hover>
                  <h3 className="font-semibold truncate">{doc.title || "Untitled"}</h3>
                  <div className="flex items-center gap-2 mt-3 text-sm text-text-muted">
                    <Badge>{doc.chunk_count} chunks</Badge>
                    <span>{doc.word_count.toLocaleString()} words</span>
                  </div>
                  <p className="text-xs text-text-muted mt-2">
                    {new Date(doc.created_at).toLocaleDateString()}
                  </p>
                </Card>
              </Link>
            </AnimateIn>
          ))}
        </div>
      )}
    </div>
  );
}
