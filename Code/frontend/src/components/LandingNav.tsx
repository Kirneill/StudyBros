import Link from "next/link";

export function LandingNav() {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-bg-primary/80 border-b border-border">
      <nav
        aria-label="Site navigation"
        className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16"
      >
        <Link
          href="/"
          className="font-[family-name:var(--font-heading)] text-xl font-bold"
        >
          <span className="text-accent">Study</span>Bros
        </Link>

        <div className="flex items-center gap-6">
          <Link
            href="/docs"
            className="hidden sm:inline text-sm text-text-secondary hover:text-text-primary transition-colors"
          >
            Docs
          </Link>
          <Link
            href="/docs/ai-setup"
            className="hidden sm:inline text-sm text-text-secondary hover:text-text-primary transition-colors"
          >
            AI Setup
          </Link>
          <Link
            href="/dashboard"
            className="hidden sm:inline text-sm text-text-secondary hover:text-text-primary transition-colors"
          >
            Dashboard
          </Link>
          <Link
            href="/upload"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-accent text-bg-primary text-sm font-semibold hover:bg-accent-hover transition-colors"
          >
            Get Started
          </Link>
        </div>
      </nav>
    </header>
  );
}
