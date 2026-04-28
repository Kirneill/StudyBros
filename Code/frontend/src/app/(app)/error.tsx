"use client";

import { Button } from "@/components/ui";
import Link from "next/link";

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const message =
    process.env.NODE_ENV === "production"
      ? "An unexpected error occurred while loading this page."
      : (error.message || "An unexpected error occurred while loading this page.");

  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <span className="text-4xl block mb-4" aria-hidden="true">&#x26A0;&#xFE0F;</span>
      <h2 className="text-xl font-bold mb-2">Something went wrong</h2>
      <p className="text-text-secondary mb-6 max-w-md">{message}</p>
      <div className="flex gap-3">
        <Button variant="secondary" onClick={reset}>Try Again</Button>
        <Link
          href="/dashboard"
          className="inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors px-4 py-2 text-sm bg-accent text-bg-primary hover:bg-accent-hover"
        >
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
