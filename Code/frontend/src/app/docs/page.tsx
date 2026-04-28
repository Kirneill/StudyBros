import Link from "next/link";
import { AnimateIn } from "@/components/AnimateIn";
import { Card } from "@/components/ui";
import { LandingNav } from "@/components/LandingNav";

export default function DocsPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <LandingNav />

      <main className="flex-1 py-16 sm:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Page header */}
          <AnimateIn>
            <h1 className="font-[family-name:var(--font-heading)] text-4xl sm:text-5xl font-bold mb-4">
              Documentation
            </h1>
            <p className="text-text-secondary text-lg mb-12 max-w-2xl">
              Everything you need to get started with StudyBros — from the web
              app to connecting your own AI assistant.
            </p>
          </AnimateIn>

          {/* ── Getting Started ── */}
          <AnimateIn delay={0.05}>
            <section className="mb-16">
              <h2 className="font-[family-name:var(--font-heading)] text-2xl sm:text-3xl font-bold mb-4">
                Getting Started
              </h2>
              <p className="text-text-secondary mb-8 leading-relaxed">
                StudyBros transforms your study materials into AI-generated
                flashcards, quizzes, and practice tests with spaced repetition.
                There are three ways to use it:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                {[
                  {
                    num: "1",
                    title: "Web App",
                    desc: (
                      <>
                        Upload files at{" "}
                        <Link href="/upload" className="text-accent hover:underline">
                          /upload
                        </Link>
                        , generate materials, study, and track your progress.
                      </>
                    ),
                  },
                  {
                    num: "2",
                    title: "MCP Server",
                    desc: (
                      <>
                        Connect any AI assistant (Claude, ChatGPT, Cursor) via
                        MCP.{" "}
                        <Link
                          href="/docs/ai-setup"
                          className="text-accent hover:underline"
                        >
                          Setup guide &rarr;
                        </Link>
                      </>
                    ),
                  },
                  {
                    num: "3",
                    title: "LLM Skills",
                    desc: "Paste the StudyBros docs URL into any LLM and it will understand how to use the platform.",
                  },
                ].map((item, i) => (
                  <AnimateIn key={item.title} delay={0.05 + i * 0.08}>
                    <Card className="h-full">
                      <span className="font-[family-name:var(--font-mono)] text-3xl font-bold text-accent mb-2 block">
                        {item.num}
                      </span>
                      <h3 className="font-[family-name:var(--font-heading)] text-lg font-semibold mb-2">
                        {item.title}
                      </h3>
                      <p className="text-text-secondary text-sm">{item.desc}</p>
                    </Card>
                  </AnimateIn>
                ))}
              </div>
            </section>
          </AnimateIn>

          {/* ── Using the Web App ── */}
          <AnimateIn delay={0.1}>
            <section className="mb-16">
              <h2 className="font-[family-name:var(--font-heading)] text-2xl sm:text-3xl font-bold mb-6">
                Using the Web App
              </h2>
              <div className="space-y-6">
                {[
                  {
                    step: "Upload",
                    text: "Drag and drop PDF, PPTX, TXT, or MD files. We extract and chunk the content automatically.",
                  },
                  {
                    step: "Generate",
                    text: "Pick an AI provider (OpenAI, Claude, or OpenRouter) and choose your material type — flashcards, quiz, practice test, or summary.",
                  },
                  {
                    step: "Study",
                    text: "Flashcards use FSRS spaced repetition to schedule reviews at optimal intervals. Quizzes give instant scoring. Practice tests simulate real exams.",
                  },
                  {
                    step: "Track",
                    text: "The dashboard shows due cards, a mastery tree, and your consistency streak. The progress page has a knowledge heat map, calibration chart, and achievements.",
                  },
                ].map((item) => (
                  <Card key={item.step}>
                    <div className="flex gap-4">
                      <span className="font-[family-name:var(--font-mono)] text-accent font-bold text-lg shrink-0 w-24">
                        {item.step}
                      </span>
                      <p className="text-text-secondary">{item.text}</p>
                    </div>
                  </Card>
                ))}
              </div>
            </section>
          </AnimateIn>

          {/* ── Supported File Types ── */}
          <AnimateIn delay={0.15}>
            <section className="mb-16">
              <h2 className="font-[family-name:var(--font-heading)] text-2xl sm:text-3xl font-bold mb-6">
                Supported File Types
              </h2>
              <Card>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="pb-3 pr-8 text-sm font-semibold text-text-muted">
                          Category
                        </th>
                        <th className="pb-3 text-sm font-semibold text-text-muted">
                          Formats
                        </th>
                      </tr>
                    </thead>
                    <tbody className="text-sm">
                      <tr className="border-b border-border/50">
                        <td className="py-3 pr-8 text-text-primary font-medium">
                          Documents
                        </td>
                        <td className="py-3 text-text-secondary">
                          <code className="text-accent">PDF</code>,{" "}
                          <code className="text-accent">PPTX</code>,{" "}
                          <code className="text-accent">TXT</code>,{" "}
                          <code className="text-accent">MD</code>
                        </td>
                      </tr>
                      <tr className="border-b border-border/50">
                        <td className="py-3 pr-8 text-text-primary font-medium">
                          Video
                        </td>
                        <td className="py-3 text-text-secondary">
                          <code className="text-accent">MP4</code>,{" "}
                          <code className="text-accent">MOV</code>,{" "}
                          <code className="text-accent">WEBM</code>,{" "}
                          <code className="text-accent">AVI</code>,{" "}
                          <code className="text-accent">MKV</code>
                          <span className="text-text-muted ml-2">
                            (requires FFmpeg)
                          </span>
                        </td>
                      </tr>
                      <tr>
                        <td className="py-3 pr-8 text-text-primary font-medium">
                          Audio
                        </td>
                        <td className="py-3 text-text-secondary">
                          <code className="text-accent">MP3</code>,{" "}
                          <code className="text-accent">WAV</code>,{" "}
                          <code className="text-accent">M4A</code>,{" "}
                          <code className="text-accent">AAC</code>,{" "}
                          <code className="text-accent">OGG</code>
                          <span className="text-text-muted ml-2">
                            (requires FFmpeg)
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </Card>
            </section>
          </AnimateIn>

          {/* ── Science Behind It ── */}
          <AnimateIn delay={0.2}>
            <section className="mb-16">
              <h2 className="font-[family-name:var(--font-heading)] text-2xl sm:text-3xl font-bold mb-6">
                Science Behind It
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {[
                  {
                    title: "FSRS v5",
                    text: "Free Spaced Repetition Scheduler — predicts when you will forget a card and schedules reviews right before that happens. The same algorithm powering Anki's next generation.",
                  },
                  {
                    title: "Bloom's Taxonomy",
                    text: "Every question is tagged by cognitive level (remember, understand, apply, analyze). StudyBros pushes you up the ladder, ensuring deeper understanding over time.",
                  },
                  {
                    title: "85% Rule",
                    text: "Optimal learning happens at approximately 85% accuracy (Wilson et al., 2019). Too easy and you are bored; too hard and you give up. We keep you in the zone.",
                  },
                  {
                    title: "Mastery Detection",
                    text: 'A topic is "complete" when your retrievability exceeds 90% at 30+ day intervals with 85%+ accuracy at Bloom level 3+. No more guessing if you actually know it.',
                  },
                ].map((item, i) => (
                  <AnimateIn key={item.title} delay={0.2 + i * 0.06}>
                    <Card className="h-full">
                      <h3 className="font-[family-name:var(--font-heading)] text-lg font-semibold mb-2 text-accent">
                        {item.title}
                      </h3>
                      <p className="text-text-secondary text-sm leading-relaxed">
                        {item.text}
                      </p>
                    </Card>
                  </AnimateIn>
                ))}
              </div>
            </section>
          </AnimateIn>

          {/* ── Next steps ── */}
          <AnimateIn delay={0.25}>
            <section>
              <Card className="text-center">
                <h2 className="font-[family-name:var(--font-heading)] text-xl font-bold mb-3">
                  Ready to start?
                </h2>
                <p className="text-text-secondary mb-6">
                  Upload your first document or connect your AI assistant.
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                  <Link
                    href="/upload"
                    className="inline-flex items-center px-6 py-3 rounded-lg bg-accent text-bg-primary font-semibold hover:bg-accent-hover transition-colors"
                  >
                    Upload Material
                  </Link>
                  <Link
                    href="/docs/ai-setup"
                    className="inline-flex items-center px-6 py-3 rounded-lg border border-border text-text-secondary font-medium hover:text-text-primary hover:bg-bg-card transition-colors"
                  >
                    AI Setup Guide
                  </Link>
                </div>
              </Card>
            </section>
          </AnimateIn>
        </div>
      </main>
    </div>
  );
}
