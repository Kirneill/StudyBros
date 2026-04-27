import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <span className="text-6xl font-bold font-mono text-accent block mb-4">404</span>
        <h1 className="font-[family-name:var(--font-heading)] text-2xl font-bold mb-2">
          Page not found
        </h1>
        <p className="text-text-secondary mb-6">
          The page you are looking for does not exist or has been moved.
        </p>
        <Link
          href="/dashboard"
          className="inline-flex items-center px-6 py-3 rounded-xl bg-accent text-bg-primary font-semibold hover:bg-accent-hover transition-colors"
        >
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
