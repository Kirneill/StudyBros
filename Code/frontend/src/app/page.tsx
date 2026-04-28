import Link from "next/link";
import { AnimateIn } from "@/components/AnimateIn";
import { Card } from "@/components/ui";
import { LandingNav } from "@/components/LandingNav";

const comparisonFeatures = [
  "AI-generated materials",
  "Spaced repetition (FSRS)",
  "Mastery detection",
  "Works in any AI assistant",
  "Bloom's taxonomy tagging",
  "Tells you when you're done",
] as const;

const comparisonData: Record<string, boolean[]> = {
  StudyBros: [true, true, true, true, true, true],
  Anki: [false, true, false, false, false, false],
  Quizlet: [false, false, false, false, false, false],
  "Re-reading": [false, false, false, false, false, false],
};

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <LandingNav />

      <main id="main-content">
      {/* ── 1. Hero ── */}
      <section className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
        <div className="max-w-3xl mx-auto text-center">
          <AnimateIn>
            <span className="inline-block mb-6 px-4 py-1.5 rounded-full bg-accent-light text-accent text-sm font-medium">
              Built on learning science, not guesswork
            </span>
          </AnimateIn>
          <AnimateIn delay={0.1}>
            <h1 className="font-[family-name:var(--font-heading)] text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.1] mb-4">
              You forget 70% of what you study within 24 hours.
            </h1>
          </AnimateIn>
          <AnimateIn delay={0.15}>
            <p className="font-[family-name:var(--font-heading)] text-2xl sm:text-3xl font-bold text-accent mb-6">
              Unless you don&apos;t.
            </p>
          </AnimateIn>
          <AnimateIn delay={0.2}>
            <p className="text-text-secondary text-lg sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
              StudyBros uses AI and spaced repetition science to generate study
              materials that adapt to your memory. Upload once. Remember forever.
            </p>
          </AnimateIn>
          <AnimateIn delay={0.25}>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/upload"
                className="inline-flex items-center px-8 py-4 rounded-xl bg-accent text-bg-primary font-semibold text-lg hover:bg-accent-hover transition-colors shadow-[var(--shadow-accent-glow)]"
              >
                Start Studying — Free
              </Link>
              <a
                href="#how-it-works"
                className="inline-flex items-center px-8 py-4 rounded-xl border border-border text-text-secondary font-medium text-lg hover:text-text-primary hover:bg-bg-card transition-colors"
              >
                See how it works
              </a>
            </div>
          </AnimateIn>
        </div>
      </section>

      {/* ── 2. The Forgetting Curve ── */}
      <section className="border-t border-border py-20 sm:py-28 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <AnimateIn>
            <div className="text-center mb-12">
              <h2 className="font-[family-name:var(--font-heading)] text-3xl sm:text-4xl font-bold mb-4">
                The Ebbinghaus Forgetting Curve
              </h2>
              <p className="text-text-secondary text-lg max-w-2xl mx-auto">
                Without active review, you lose most of what you learn within days.
              </p>
            </div>
          </AnimateIn>
          <AnimateIn delay={0.1}>
            <div className="max-w-3xl mx-auto">
              <svg
                viewBox="0 0 600 300"
                className="w-full h-auto"
                role="img"
                aria-label="Forgetting curve chart showing memory retention over 30 days, comparing no review versus spaced repetition"
              >
                {/* Grid lines */}
                {[0, 1, 2, 3, 4].map((i) => (
                  <line
                    key={i}
                    x1="60"
                    y1={40 + i * 55}
                    x2="570"
                    y2={40 + i * 55}
                    stroke="rgba(245,240,235,0.05)"
                    strokeWidth="1"
                  />
                ))}
                {/* Y-axis labels */}
                <text x="50" y="45" textAnchor="end" fill="#6B6B7B" fontSize="12" fontFamily="var(--font-mono)">100%</text>
                <text x="50" y="100" textAnchor="end" fill="#6B6B7B" fontSize="12" fontFamily="var(--font-mono)">75%</text>
                <text x="50" y="155" textAnchor="end" fill="#6B6B7B" fontSize="12" fontFamily="var(--font-mono)">50%</text>
                <text x="50" y="210" textAnchor="end" fill="#6B6B7B" fontSize="12" fontFamily="var(--font-mono)">25%</text>
                <text x="50" y="265" textAnchor="end" fill="#6B6B7B" fontSize="12" fontFamily="var(--font-mono)">0%</text>
                {/* X-axis labels */}
                <text x="60" y="285" textAnchor="middle" fill="#6B6B7B" fontSize="11" fontFamily="var(--font-mono)">Day 1</text>
                <text x="230" y="285" textAnchor="middle" fill="#6B6B7B" fontSize="11" fontFamily="var(--font-mono)">Day 7</text>
                <text x="400" y="285" textAnchor="middle" fill="#6B6B7B" fontSize="11" fontFamily="var(--font-mono)">Day 14</text>
                <text x="570" y="285" textAnchor="middle" fill="#6B6B7B" fontSize="11" fontFamily="var(--font-mono)">Day 30</text>
                {/* Forgetting curve (no review) — rapid exponential decay */}
                <path
                  d="M 60 40 C 120 120, 180 190, 230 210 C 300 235, 400 250, 570 258"
                  fill="none"
                  stroke="#F87171"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />
                {/* Spaced repetition curve — stays high with small dips */}
                <path
                  d="M 60 40 C 80 60, 95 80, 110 75 C 125 60, 140 50, 160 48 C 175 58, 195 70, 220 65 C 240 55, 260 48, 290 46 C 310 52, 340 58, 370 54 C 400 48, 440 46, 480 44 C 520 42, 550 41, 570 40"
                  fill="none"
                  stroke="#00D4AA"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeDasharray="8 4"
                />
                {/* Legend */}
                <line x1="340" y1="16" x2="370" y2="16" stroke="#F87171" strokeWidth="2.5" />
                <text x="376" y="20" fill="#B8B4AF" fontSize="12">No review</text>
                <line x1="460" y1="16" x2="490" y2="16" stroke="#00D4AA" strokeWidth="2.5" strokeDasharray="8 4" />
                <text x="496" y="20" fill="#B8B4AF" fontSize="12">With spaced repetition</text>
              </svg>
              <table className="sr-only">
                <caption>Forgetting curve data</caption>
                <thead>
                  <tr>
                    <th scope="col">Day</th>
                    <th scope="col">Without review</th>
                    <th scope="col">With spaced repetition</th>
                  </tr>
                </thead>
                <tbody>
                  <tr><td>Day 1</td><td>100%</td><td>100%</td></tr>
                  <tr><td>Day 2</td><td>50%</td><td>95%</td></tr>
                  <tr><td>Day 7</td><td>35%</td><td>90%</td></tr>
                  <tr><td>Day 30</td><td>20%</td><td>85%</td></tr>
                </tbody>
              </table>
              <p className="text-text-muted text-sm text-center mt-4">
                Spaced repetition flattens the curve. Each review strengthens the memory trace.
              </p>
            </div>
          </AnimateIn>
        </div>
      </section>

      {/* ── 3. Three Ways to Study ── */}
      <section className="bg-bg-secondary py-20 sm:py-28 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <AnimateIn>
            <div className="text-center mb-12">
              <h2 className="font-[family-name:var(--font-heading)] text-3xl sm:text-4xl font-bold mb-4">
                Use it however you learn
              </h2>
              <p className="text-text-secondary text-lg max-w-2xl mx-auto">
                No new apps to install. No new habits to build.
              </p>
            </div>
          </AnimateIn>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {[
              {
                icon: "\u{1F50C}",
                title: "Any AI Assistant",
                description:
                  "Connect Claude, ChatGPT, or Cursor via MCP. Your AI generates and reviews study materials in your existing workflow.",
              },
              {
                icon: "\u{1F517}",
                title: "Paste a Link",
                description:
                  "Share the StudyBros docs URL with any LLM. It instantly understands how to create study materials for you.",
              },
              {
                icon: "\u{1F310}",
                title: "Web Dashboard",
                description:
                  "Upload files, generate materials, track mastery, and see your progress — all in a gamified dark-theme interface.",
              },
            ].map((item, i) => (
              <AnimateIn key={item.title} delay={i * 0.1}>
                <Card hover className="h-full text-center">
                  <span className="text-4xl mb-4 block" role="img" aria-hidden="true">
                    {item.icon}
                  </span>
                  <h3 className="font-[family-name:var(--font-heading)] text-xl font-semibold mb-2">
                    {item.title}
                  </h3>
                  <p className="text-text-secondary">{item.description}</p>
                </Card>
              </AnimateIn>
            ))}
          </div>
        </div>
      </section>

      {/* ── 4. How It Works ── */}
      <section
        id="how-it-works"
        className="border-t border-border py-20 sm:py-28 px-4 sm:px-6 lg:px-8"
      >
        <div className="max-w-6xl mx-auto">
          <AnimateIn>
            <div className="text-center mb-16">
              <h2 className="font-[family-name:var(--font-heading)] text-3xl sm:text-4xl font-bold mb-4">
                Three steps to mastery
              </h2>
            </div>
          </AnimateIn>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 sm:gap-12">
            {[
              {
                num: "1",
                title: "Upload",
                desc: "Drop your PDFs, slides, or notes. We extract and chunk the content.",
              },
              {
                num: "2",
                title: "Generate",
                desc: "AI creates flashcards, quizzes, and practice tests tailored to your material.",
              },
              {
                num: "3",
                title: "Master",
                desc: "Spaced repetition schedules reviews at optimal intervals. We tell you when you’ve actually learned it.",
              },
            ].map((step, i) => (
              <AnimateIn key={step.num} delay={i * 0.1}>
                <div className="text-center">
                  <span className="font-[family-name:var(--font-mono)] text-5xl sm:text-6xl font-bold text-accent mb-4 block">
                    {step.num}
                  </span>
                  <h3 className="font-[family-name:var(--font-heading)] text-xl font-semibold mb-2">
                    {step.title}
                  </h3>
                  <p className="text-text-secondary">{step.desc}</p>
                </div>
              </AnimateIn>
            ))}
          </div>
        </div>
      </section>

      {/* ── 5. Science Section ── */}
      <section className="bg-bg-secondary py-20 sm:py-28 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <AnimateIn>
            <div className="text-center mb-12">
              <h2 className="font-[family-name:var(--font-heading)] text-3xl sm:text-4xl font-bold mb-4">
                Built on research, not vibes
              </h2>
            </div>
          </AnimateIn>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {[
              {
                title: "FSRS v5",
                text: "Free Spaced Repetition Scheduler — the same algorithm powering Anki’s next generation. Predicts exactly when you’ll forget.",
              },
              {
                title: "Bloom’s Taxonomy",
                text: "Every question is tagged by cognitive level — from recall to analysis. We push you up the ladder, not just sideways.",
              },
              {
                title: "85% Accuracy Rule",
                text: "Learning is maximized when you get ~85% right. Too easy and you’re bored. Too hard and you give up. We keep you in the zone.",
              },
              {
                title: "Mastery Detection",
                text: "We don’t just track streaks. When your retrievability exceeds 90% at 30+ day intervals with 85%+ accuracy — you’re done. Topic complete.",
              },
            ].map((item, i) => (
              <AnimateIn key={item.title} delay={i * 0.08}>
                <Card className="h-full">
                  <h3 className="font-[family-name:var(--font-heading)] text-lg font-semibold mb-2 text-accent">
                    {item.title}
                  </h3>
                  <p className="text-text-secondary">{item.text}</p>
                </Card>
              </AnimateIn>
            ))}
          </div>
        </div>
      </section>

      {/* ── 6. Comparison Table ── */}
      <section className="border-t border-border py-20 sm:py-28 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <AnimateIn>
            <div className="text-center mb-12">
              <h2 className="font-[family-name:var(--font-heading)] text-3xl sm:text-4xl font-bold mb-4">
                How StudyBros compares
              </h2>
            </div>
          </AnimateIn>
          <AnimateIn delay={0.1}>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[600px] border-separate border-spacing-y-0">
                <thead>
                  <tr className="px-4 py-3">
                    <th scope="col" className="text-left text-text-muted text-sm font-medium px-4 py-3">Feature</th>
                    {Object.keys(comparisonData).map((tool) => (
                      <th
                        key={tool}
                        scope="col"
                        className={`text-sm font-semibold text-center px-4 py-3 ${
                          tool === "StudyBros" ? "text-accent" : "text-text-muted"
                        }`}
                      >
                        {tool}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {comparisonFeatures.map((feature, rowIdx) => (
                    <tr
                      key={feature}
                      className={rowIdx % 2 === 0 ? "bg-bg-card" : ""}
                    >
                      <td className="text-text-secondary text-sm px-4 py-3 rounded-l-lg">{feature}</td>
                      {Object.keys(comparisonData).map((tool, colIdx) => (
                        <td key={tool} className={`text-center px-4 py-3${colIdx === Object.keys(comparisonData).length - 1 ? " rounded-r-lg" : ""}`}>
                          {comparisonData[tool][rowIdx] ? (
                            <span className="text-accent font-bold" aria-label="Yes">&#10003;<span className="sr-only"> Yes</span></span>
                          ) : (
                            <span className="text-text-muted" aria-label="No">&mdash;</span>
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </AnimateIn>
        </div>
      </section>

      {/* ── 7. Social Proof ── */}
      <section className="bg-bg-secondary py-20 sm:py-28 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <AnimateIn>
            <div className="text-center mb-12">
              <h2 className="font-[family-name:var(--font-heading)] text-3xl sm:text-4xl font-bold mb-4">
                The science speaks for itself
              </h2>
            </div>
          </AnimateIn>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {[
              {
                quote:
                  "Spaced practice produces a 200% improvement in long-term retention compared to massed practice.",
                cite: "Cepeda et al., 2006",
                citeUrl: "https://doi.org/10.1111/j.1467-9280.2006.01693.x",
              },
              {
                quote:
                  "Students who generated their own study materials scored 22% higher than those who passively reviewed.",
                cite: "Fiorella & Mayer, 2016",
                citeUrl: "https://doi.org/10.1007/s10648-015-9338-z",
              },
              {
                quote:
                  "The optimal error rate for learning is approximately 15.87% — roughly the 85% accuracy rule.",
                cite: "Wilson et al., 2019",
                citeUrl: "https://doi.org/10.1038/s41467-019-12552-4",
              },
            ].map((item, i) => (
              <AnimateIn key={item.cite} delay={i * 0.1}>
                <Card className="h-full flex flex-col justify-between">
                  <blockquote cite={item.citeUrl} className="text-text-secondary italic mb-4 leading-relaxed">
                    &ldquo;{item.quote}&rdquo;
                  </blockquote>
                  <cite className="text-text-muted text-sm not-italic block">
                    &mdash; {item.cite}
                  </cite>
                </Card>
              </AnimateIn>
            ))}
          </div>
        </div>
      </section>

      {/* ── 8. Final CTA ── */}
      <section className="border-t border-border py-20 sm:py-28 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto text-center">
          <AnimateIn>
            <h2 className="font-[family-name:var(--font-heading)] text-3xl sm:text-4xl font-bold mb-4">
              Ready to remember what you study?
            </h2>
          </AnimateIn>
          <AnimateIn delay={0.1}>
            <p className="text-text-secondary text-lg mb-8 max-w-xl mx-auto">
              Upload your first document. No account needed. No credit card. Just learning science.
            </p>
          </AnimateIn>
          <AnimateIn delay={0.15}>
            <Link
              href="/upload"
              className="inline-flex items-center px-10 py-4 rounded-xl bg-accent text-bg-primary font-semibold text-lg hover:bg-accent-hover transition-colors shadow-[var(--shadow-accent-glow)]"
            >
              Upload Your Material
            </Link>
            <p className="text-text-muted text-sm mt-4">
              Supports PDF, PPTX, TXT, MD, and more
            </p>
          </AnimateIn>
        </div>
      </section>
      </main>

      {/* ── 9. Footer ── */}
      <footer className="border-t border-border py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-6 mb-6">
            <span className="font-[family-name:var(--font-heading)] text-xl font-bold">
              <span className="text-accent">Study</span>Bros
            </span>
            <nav className="flex gap-6 text-sm text-text-secondary" aria-label="Footer navigation">
              <Link href="/dashboard" className="hover:text-text-primary transition-colors">
                Dashboard
              </Link>
              <Link href="/upload" className="hover:text-text-primary transition-colors">
                Upload
              </Link>
              <Link href="/progress" className="hover:text-text-primary transition-colors">
                Progress
              </Link>
            </nav>
            <div className="flex items-center gap-2 text-sm text-text-muted">
              <span>Built with learning science</span>
              <span>&middot;</span>
              <a href="https://github.com/Kirneill/StudyBros" className="hover:text-text-primary transition-colors">
                GitHub
              </a>
            </div>
          </div>
          <p className="text-center text-text-muted text-xs">
            Every hour without spaced repetition, you lose a little more of what you learned.
          </p>
        </div>
      </footer>
    </div>
  );
}
