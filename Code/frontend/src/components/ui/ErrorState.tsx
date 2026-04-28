"use client";

import { Button } from "./Button";

interface ErrorStateProps {
  title?: string;
  description?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorState({
  title = "Something went wrong",
  description = "An error occurred. Please try again.",
  onRetry,
  className = "",
}: ErrorStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center py-16 text-center ${className}`}>
      <span className="text-4xl mb-4" aria-hidden="true">&#x26A0;&#xFE0F;</span>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-text-secondary max-w-md mb-6">{description}</p>
      {onRetry && (
        <Button onClick={onRetry}>Try Again</Button>
      )}
    </div>
  );
}
