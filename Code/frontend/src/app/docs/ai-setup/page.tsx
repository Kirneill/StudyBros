import Link from "next/link";
import { AnimateIn } from "@/components/AnimateIn";
import { Card } from "@/components/ui";
import { LandingNav } from "@/components/LandingNav";

function CodeBlock({ children }: { children: string }) {
  return (
    <pre className="bg-bg-input rounded-lg p-4 font-[family-name:var(--font-mono)] text-sm overflow-x-auto">
      <code>{children}</code>
    </pre>
  );
}

export default function AISetupPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <LandingNav />

      <main id="main-content" className="flex-1 py-16 sm:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          {/* Page header */}
          <AnimateIn delay={0}>
            <Link
              href="/docs"
              className="text-sm text-text-muted hover:text-text-primary transition-colors mb-6 inline-block"
            >
              &larr; Back to Docs
            </Link>
          </AnimateIn>
          <AnimateIn>
            <h1 className="font-[family-name:var(--font-heading)] text-4xl sm:text-5xl font-bold mb-4">
              AI Setup
            </h1>
            <p className="text-text-secondary text-lg mb-12 max-w-2xl">
              Connect StudyBros to any AI assistant via MCP, or paste a link
              into any LLM.
            </p>
          </AnimateIn>

          {/* ── MCP Server Setup ── */}
          <AnimateIn delay={0.05}>
            <section className="mb-16">
              <h2 className="font-[family-name:var(--font-heading)] text-2xl sm:text-3xl font-bold mb-4">
                MCP Server Setup
              </h2>
              <p className="text-text-secondary mb-8 leading-relaxed">
                StudyBros has a built-in MCP (Model Context Protocol) server
                that any AI assistant can connect to. Once connected, your AI
                can ingest files, generate study materials, run review sessions,
                and check your mastery — all through natural conversation.
              </p>

              {/* Claude Code */}
              <div className="mb-8">
                <h3 className="font-[family-name:var(--font-heading)] text-xl font-semibold mb-3">
                  Claude Code
                </h3>
                <p className="text-text-secondary mb-4 text-sm">
                  The simplest setup. Claude Code auto-discovers the server from{" "}
                  <code className="text-accent bg-bg-input px-1.5 py-0.5 rounded text-xs">
                    .mcp.json
                  </code>{" "}
                  in the project root.
                </p>
                <CodeBlock>{`cd /path/to/studybros/Code\npip install -e .`}</CodeBlock>
                <p className="text-text-muted text-sm mt-2">
                  That&apos;s it. Claude Code reads{" "}
                  <code className="text-accent">.mcp.json</code> automatically.
                </p>
              </div>

              {/* Claude Desktop */}
              <div className="mb-8">
                <h3 className="font-[family-name:var(--font-heading)] text-xl font-semibold mb-3">
                  Claude Desktop
                </h3>
                <p className="text-text-secondary mb-4 text-sm">
                  Edit the Claude Desktop config file:
                </p>
                <Card className="mb-4">
                  <div className="space-y-2 text-sm">
                    <div className="flex gap-2">
                      <span className="text-text-muted shrink-0">macOS:</span>
                      <code className="text-accent font-[family-name:var(--font-mono)] text-xs break-all">
                        ~/Library/Application Support/Claude/claude_desktop_config.json
                      </code>
                    </div>
                    <div className="flex gap-2">
                      <span className="text-text-muted shrink-0">
                        Windows:
                      </span>
                      <code className="text-accent font-[family-name:var(--font-mono)] text-xs break-all">
                        %APPDATA%\Claude\claude_desktop_config.json
                      </code>
                    </div>
                  </div>
                </Card>
                <CodeBlock>
                  {`{
  "mcpServers": {
    "studybros": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/studybros/Code"
    }
  }
}`}
                </CodeBlock>
              </div>

              {/* Any MCP Client */}
              <div className="mb-4">
                <h3 className="font-[family-name:var(--font-heading)] text-xl font-semibold mb-3">
                  Any MCP Client
                </h3>
                <p className="text-text-secondary mb-4 text-sm">
                  Use the same JSON config shown above. Point{" "}
                  <code className="text-accent bg-bg-input px-1.5 py-0.5 rounded text-xs">
                    cwd
                  </code>{" "}
                  to the{" "}
                  <code className="text-accent bg-bg-input px-1.5 py-0.5 rounded text-xs">
                    Code
                  </code>{" "}
                  directory and your client will connect over stdio.
                </p>
              </div>
            </section>
          </AnimateIn>

          {/* ── What You Can Do ── */}
          <AnimateIn delay={0.1}>
            <section className="mb-16">
              <h2 className="font-[family-name:var(--font-heading)] text-2xl sm:text-3xl font-bold mb-6">
                What You Can Do
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                {[
                  {
                    count: "10",
                    label: "Tools",
                    desc: "Ingest files, generate study sets, record reviews, get due cards, check mastery, export to Anki/JSON/Markdown.",
                  },
                  {
                    count: "9",
                    label: "Resources",
                    desc: "Browse documents, study sets, schedules, progress, and achievements programmatically.",
                  },
                  {
                    count: "8",
                    label: "Prompts",
                    desc: "Generate flashcards and quizzes, run study sessions, explain concepts, and review your progress.",
                  },
                ].map((item, i) => (
                  <AnimateIn key={item.label} delay={0.1 + i * 0.06}>
                    <Card className="h-full text-center">
                      <span className="font-[family-name:var(--font-mono)] text-4xl font-bold text-accent block mb-1">
                        {item.count}
                      </span>
                      <h3 className="font-[family-name:var(--font-heading)] text-lg font-semibold mb-2">
                        {item.label}
                      </h3>
                      <p className="text-text-secondary text-sm">
                        {item.desc}
                      </p>
                    </Card>
                  </AnimateIn>
                ))}
              </div>
            </section>
          </AnimateIn>

          {/* ── Example Conversations ── */}
          <AnimateIn delay={0.15}>
            <section className="mb-16">
              <h2 className="font-[family-name:var(--font-heading)] text-2xl sm:text-3xl font-bold mb-6">
                Example Conversations
              </h2>
              <p className="text-text-secondary mb-6">
                Once connected, try these prompts with your AI assistant:
              </p>
              <div className="space-y-3">
                {[
                  "Ingest all my lecture notes from ./lectures",
                  "Generate 20 flashcards for document 1",
                  "Start a flashcard study session for study set 1",
                  "Check my mastery on all topics",
                  "Export study set 1 as an Anki deck",
                ].map((prompt) => (
                  <Card key={prompt} className="!py-3 !px-4">
                    <code className="font-[family-name:var(--font-mono)] text-sm text-accent">
                      &ldquo;{prompt}&rdquo;
                    </code>
                  </Card>
                ))}
              </div>
            </section>
          </AnimateIn>

          {/* ── LLM Skills ── */}
          <AnimateIn delay={0.2}>
            <section className="mb-16">
              <h2 className="font-[family-name:var(--font-heading)] text-2xl sm:text-3xl font-bold mb-4">
                LLM Skills (Paste a Link)
              </h2>
              <p className="text-text-secondary mb-6 leading-relaxed">
                No MCP setup needed? No problem. You can share the StudyBros
                documentation URL with any LLM — ChatGPT, Claude, Gemini,
                Llama, or any other — and it will understand how to use the
                platform.
              </p>
              <Card>
                <p className="text-text-secondary text-sm mb-4">
                  Copy one of these URLs and paste it into your LLM:
                </p>
                <div className="space-y-2">
                  <div className="bg-bg-input rounded-lg px-4 py-2.5 font-[family-name:var(--font-mono)] text-sm">
                    <span className="text-text-muted">Quick summary: </span>
                    <a
                      href="https://raw.githubusercontent.com/Kirneill/StudyBros/main/Code/docs/llms.txt"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-accent hover:text-accent-hover underline underline-offset-4 break-all"
                    >
                      https://raw.githubusercontent.com/Kirneill/StudyBros/main/Code/docs/llms.txt
                    </a>
                  </div>
                  <div className="bg-bg-input rounded-lg px-4 py-2.5 font-[family-name:var(--font-mono)] text-sm">
                    <span className="text-text-muted">Full reference: </span>
                    <a
                      href="https://raw.githubusercontent.com/Kirneill/StudyBros/main/Code/docs/llms-full.txt"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-accent hover:text-accent-hover underline underline-offset-4 break-all"
                    >
                      https://raw.githubusercontent.com/Kirneill/StudyBros/main/Code/docs/llms-full.txt
                    </a>
                  </div>
                </div>
                <p className="text-text-muted text-xs mt-4">
                  The LLM reads the docs and can generate study materials,
                  explain concepts, and help you study — all from a single
                  link.
                </p>
              </Card>
            </section>
          </AnimateIn>

          {/* ── CTA ── */}
          <AnimateIn delay={0.25}>
            <section>
              <Card className="text-center">
                <h2 className="font-[family-name:var(--font-heading)] text-xl font-bold mb-3">
                  Ready to connect?
                </h2>
                <p className="text-text-secondary mb-6">
                  Set up MCP or start using the web app right away.
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                  <Link
                    href="/upload"
                    className="inline-flex items-center px-6 py-3 rounded-lg bg-accent text-bg-primary font-semibold hover:bg-accent-hover transition-colors"
                  >
                    Upload Material
                  </Link>
                  <Link
                    href="/docs"
                    className="inline-flex items-center px-6 py-3 rounded-lg border border-border text-text-secondary font-medium hover:text-text-primary hover:bg-bg-card transition-colors"
                  >
                    Back to Docs
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
