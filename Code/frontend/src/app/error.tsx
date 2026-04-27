"use client";

import { Button } from "@/components/ui";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <span className="text-5xl block mb-4">&#x26A0;&#xFE0F;</span>
        <h1 className="font-[family-name:var(--font-heading)] text-2xl font-bold mb-2">
          Something went wrong
        </h1>
        <p className="text-text-secondary mb-6">
          {error.message || "An unexpected error occurred."}
        </p>
        <Button onClick={reset}>Try Again</Button>
      </div>
    </div>
  );
}
