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
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <span className="text-4xl block mb-4">&#x26A0;&#xFE0F;</span>
      <h2 className="text-xl font-bold mb-2">Something went wrong</h2>
      <p className="text-text-secondary mb-6 max-w-md">
        {error.message || "An unexpected error occurred while loading this page."}
      </p>
      <div className="flex gap-3">
        <Button variant="secondary" onClick={reset}>Try Again</Button>
        <Link href="/dashboard">
          <Button>Go to Dashboard</Button>
        </Link>
      </div>
    </div>
  );
}
