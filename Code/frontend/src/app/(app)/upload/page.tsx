"use client";

import { useCallback, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, Button, Toast } from "@/components/ui";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const handleFile = useCallback(async (file: File) => {
    setUploading(true);
    setToast(null);
    try {
      const doc = await api.uploadFile(file);
      setToast({ message: `"${doc.title}" uploaded successfully!`, type: "success" });
      setTimeout(() => router.push(`/documents/${doc.id}`), 1500);
    } catch (err) {
      const message = err instanceof ApiError ? err.detail : "Upload failed";
      setToast({ message, type: "error" });
    } finally {
      setUploading(false);
    }
  }, [router]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const onFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  }, [handleFile]);

  return (
    <div>
      <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-8">Upload Material</h1>

      <Card
        className={`border-2 border-dashed transition-colors ${
          dragging ? "border-accent bg-accent/5" : "border-border"
        }`}
      >
        <div
          className="flex flex-col items-center justify-center py-16"
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
        >
          <span className="text-5xl mb-4">{uploading ? "&#9203;" : "&#128194;"}</span>
          <p className="text-lg font-medium mb-2">
            {uploading ? "Uploading..." : "Drop your file here"}
          </p>
          <p className="text-text-secondary text-sm mb-6">
            PDF, PPTX, TXT, DOCX, or video files up to 50 MB
          </p>
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            accept=".pdf,.pptx,.txt,.docx,.mp4,.mkv,.avi"
            onChange={onFileSelect}
          />
          <Button
            onClick={() => inputRef.current?.click()}
            loading={uploading}
            disabled={uploading}
          >
            {uploading ? "Processing..." : "Choose File"}
          </Button>
        </div>
      </Card>

      <div className="mt-6 text-sm text-text-muted">
        <p className="font-medium mb-2">Supported formats:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>PDF documents</li>
          <li>PowerPoint presentations (.pptx)</li>
          <li>Text files (.txt)</li>
          <li>Word documents (.docx)</li>
          <li>Videos (.mp4, .mkv, .avi) — audio transcribed</li>
        </ul>
      </div>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onDismiss={() => setToast(null)}
        />
      )}
    </div>
  );
}
