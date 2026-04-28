"use client";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const message =
    process.env.NODE_ENV === "production"
      ? "An unexpected error occurred."
      : (error.message || "An unexpected error occurred.");

  return (
    <html lang="en">
      <body className="bg-bg-primary text-text-primary">
        <div className="min-h-screen flex items-center justify-center px-4">
          <div className="text-center max-w-md">
            <span className="text-5xl block mb-4" aria-hidden="true">&#x26A0;&#xFE0F;</span>
            <h1 className="text-2xl font-bold mb-2">
              Something went wrong
            </h1>
            <p className="text-text-secondary mb-6">{message}</p>
            <button
              onClick={reset}
              className="inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors px-4 py-2 text-sm bg-accent text-bg-primary hover:bg-accent-hover"
            >
              Try Again
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
