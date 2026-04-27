import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero */}
      <main className="flex-1 flex items-center justify-center px-4">
        <div className="max-w-3xl mx-auto text-center">
          <div className="inline-block mb-6 px-4 py-1.5 rounded-full bg-accent-light text-accent text-sm font-medium">
            Science-backed learning
          </div>
          <h1 className="font-[family-name:var(--font-heading)] text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.1] mb-6">
            Master your material,{" "}
            <span className="text-accent">not just review it</span>
          </h1>
          <p className="text-text-secondary text-lg sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
            Upload your study materials. AI generates flashcards, quizzes, and
            practice tests. FSRS spaced repetition ensures you actually remember.
            Science-backed gamification tells you when you&apos;re done.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center px-8 py-4 rounded-xl bg-accent text-bg-primary font-semibold text-lg hover:bg-accent-hover transition-colors shadow-[0_0_24px_rgba(0,212,170,0.3)]"
            >
              Get Started
            </Link>
            <Link
              href="/upload"
              className="inline-flex items-center px-8 py-4 rounded-xl border border-border text-text-primary font-semibold text-lg hover:bg-bg-card transition-colors"
            >
              Upload Material
            </Link>
          </div>
          {/* Trust bar */}
          <div className="mt-16 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-text-muted text-sm">
            <span>FSRS v5 Spaced Repetition</span>
            <span className="hidden sm:inline">&middot;</span>
            <span>Bloom&apos;s Taxonomy Tagging</span>
            <span className="hidden sm:inline">&middot;</span>
            <span>85% Accuracy Targeting</span>
            <span className="hidden sm:inline">&middot;</span>
            <span>Mastery Completion</span>
          </div>
        </div>
      </main>
    </div>
  );
}
