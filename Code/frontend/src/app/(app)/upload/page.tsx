"use client";

import { useCallback, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, Button, Toast } from "@/components/ui";
import * as api from "@/lib/api";
import { ApiError } from "@/lib/api";

const ACCEPTED_FILE_TYPES = [
  ".pdf",
  ".pptx",
  ".txt",
  ".md",
  ".markdown",
  ".text",
  ".mp4",
  ".mov",
  ".webm",
  ".avi",
  ".mkv",
  ".mp3",
  ".wav",
  ".m4a",
  ".aac",
  ".ogg",
].join(",");

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50 MB

export default function UploadPage() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const handleFiles = useCallback(async (incomingFiles: FileList | File[]) => {
    const files = Array.from(incomingFiles);
    if (files.length === 0) {
      return;
    }

    setUploading(true);
    setUploadStatus(null);
    setToast(null);

    const uploadedDocs: Awaited<ReturnType<typeof api.uploadFile>>[] = [];
    const failedUploads: string[] = [];

    try {
      for (const [index, file] of files.entries()) {
        if (file.size > MAX_FILE_SIZE) {
          failedUploads.push(`${file.name} exceeds 50 MB limit (${(file.size / 1024 / 1024).toFixed(1)} MB)`);
          continue;
        }
        setUploadStatus(`Uploading ${index + 1} of ${files.length}: ${file.name}`);
        try {
          const doc = await api.uploadFile(file);
          uploadedDocs.push(doc);
        } catch (err) {
          const message = err instanceof ApiError ? err.detail : "Upload failed";
          failedUploads.push(`${file.name}: ${message}`);
        }
      }

      if (failedUploads.length === 0) {
        const successMessage = uploadedDocs.length === 1
          ? `"${uploadedDocs[0].title}" uploaded successfully!`
          : `${uploadedDocs.length} files uploaded successfully!`;
        setToast({ message: successMessage, type: "success" });
        setTimeout(() => {
          if (uploadedDocs.length === 1) {
            router.push(`/documents/${uploadedDocs[0].id}`);
            return;
          }
          router.push("/documents");
        }, 1500);
        return;
      }

      if (uploadedDocs.length > 0) {
        setToast({
          message: `${uploadedDocs.length} file(s) uploaded, ${failedUploads.length} failed. First error: ${failedUploads[0]}`,
          type: "error",
        });
        setTimeout(() => router.push("/documents"), 2000);
        return;
      }

      setToast({
        message: failedUploads[0] ?? "Upload failed",
        type: "error",
      });
    } catch (err) {
      const message = err instanceof ApiError ? err.detail : "Upload failed";
      setToast({ message, type: "error" });
    } finally {
      setUploading(false);
      setUploadStatus(null);
      if (inputRef.current) {
        inputRef.current.value = "";
      }
    }
  }, [router]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files.length > 0) {
      void handleFiles(e.dataTransfer.files);
    }
  }, [handleFiles]);

  const onFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      void handleFiles(e.target.files);
    }
  }, [handleFiles]);

  return (
    <div>
      <h1 className="font-[family-name:var(--font-heading)] text-3xl font-bold mb-8">Upload Material</h1>

      <Card
        className={`border-2 border-dashed transition-colors ${
          dragging ? "border-accent bg-accent/5" : "border-border"
        }`}
      >
        <div
          role="button"
          tabIndex={0}
          aria-label="Drop files here or press Enter to choose files"
          className="flex flex-col items-center justify-center py-16 focus-visible:outline-2 focus-visible:outline-accent focus-visible:outline-offset-2"
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              inputRef.current?.click();
            }
          }}
        >
          <span className="sr-only" aria-live="polite">
            {dragging ? "Drop files to upload" : ""}
          </span>
          <span className="text-5xl mb-4">{uploading ? "&#9203;" : "&#128194;"}</span>
          <p className="text-lg font-medium mb-2">
            {uploading ? "Uploading..." : "Drop your files here"}
          </p>
          <p className="text-text-secondary text-sm mb-6">
            PDF, PPTX, text, audio, or video files up to 50 MB each
          </p>
          {uploadStatus && <p className="text-sm text-text-muted mb-4" aria-live="polite" aria-atomic="true">{uploadStatus}</p>}
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            accept={ACCEPTED_FILE_TYPES}
            multiple
            onChange={onFileSelect}
            aria-label="Upload files"
          />
          <Button
            onClick={() => inputRef.current?.click()}
            loading={uploading}
            disabled={uploading}
          >
            {uploading ? "Processing..." : "Choose Files"}
          </Button>
        </div>
      </Card>

      <div className="mt-6 text-sm text-text-muted">
        <p className="font-medium mb-2">Supported formats:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>PDF documents</li>
          <li>PowerPoint presentations (.pptx)</li>
          <li>Text files (.txt, .md, .markdown, .text)</li>
          <li>Audio files (.mp3, .wav, .m4a, .aac, .ogg)</li>
          <li>Videos (.mp4, .mov, .webm, .mkv, .avi) — audio transcribed</li>
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
