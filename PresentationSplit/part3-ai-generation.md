# Part 3 — AI Generation

**Presenter: ___**

**Time budget: ~2–2.5 minutes** — the verbatim Script below IS your talk; the Talking Points are your extended Q&A depth. You go third — you own the "magic" step between the pipeline and the interface.

## Your Scope (what YOU cover)

- **How a chunk becomes study material** — the generation step: prompts + a language model + validation.
- **Structured output** — why we force the model into strict schemas (Pydantic v2) instead of accepting free-form text, and how that makes the output reliable.
- **Multi-provider support** — the app is not locked to one AI vendor. It supports **OpenAI, Anthropic (Claude), OpenRouter, and Codex**, and users pick.
- **The newest provider: Codex CLI with no API key** — finished and merged to `main`, and it's your headline. It generates using the developer's local ChatGPT login via the `codex` command line, so no API key is ever sent or stored.

## NOT Your Scope (belongs to other parts)

- **The ingestion pipeline and chunking** that produced the input → **Part 2** (you *receive* chunks; don't re-explain how they were made).
- **The learning science** behind what makes a *good* flashcard (active recall, Bloom's levels) → **Part 1** (you can say the prompts are written to hit Bloom's levels, but don't re-teach Bloom's).
- **The web-app provider picker UI, the API-key modal, and the live demo** → **Part 4**. You explain the *engine*; Part 4 shows the *button*. Coordinate: Part 4 will actually click "generate" in the demo.

## Talking Points (full sentences — rehearse these)

1. "Once the pipeline hands us clean chunks of text, generation is where those chunks become actual study material — flashcards, a multiple-choice quiz, a mixed practice test, or an audio-friendly summary. Each type has its own carefully written prompt that tells the model what good output looks like."
2. "The part we're proud of is that we don't just take whatever the model says. We force it into a strict structure. Every output type has a Pydantic schema — a flashcard *must* have a question, an answer, tags, and a difficulty; a quiz question *must* have exactly four options and one marked correct. The model's response is parsed and validated against that schema, and if it doesn't fit, we catch it instead of shipping a broken card."
3. "That structured-output discipline is what makes the whole downstream system work. Because every flashcard is a validated object with a consistent shape, the scheduler can attach FSRS data to it, the exporter can turn it into an Anki file, and the UI can render it — none of them have to guess at the model's formatting."
4. "The second big design decision is that we're not married to one AI company. The generator supports four providers — OpenAI, Anthropic's Claude, OpenRouter, and Codex — and the exact same prompt-and-validate flow runs regardless of which one you pick. If one vendor is down, expensive, or blocked, you switch providers with one setting."
5. "The newest provider — shipped this sprint — is Codex, and it's genuinely different. Instead of calling an API with a key, it shells out to the `codex` command-line tool and runs generation through the developer's existing ChatGPT login. The prompt is piped in over standard input, so **no API key is ever sent or stored** anywhere in the app."
6. "The honest tradeoff, and I'll say it plainly: the Codex path is slower — a real run takes roughly one to five minutes for a large batch — and having the CLI installed doesn't prove you're logged in, so we detect a logged-out machine and return an actionable error that tells you to run `codex login`. It's the right choice for zero-cost, key-free generation; it's not the right choice for a live demo, which is why the demo uses a fast API provider."
7. (Handoff) "So that's the engine: prompt, generate, validate, across any of four providers. What it feels like to actually use — the interface, the progress, the payoff — [Name] will show you live."

## Script (2–3 minutes, verbatim)

So now we've got clean chunks of text, and my part is turning them into the actual study material — flashcards, a quiz, a practice test, or a summary. Each type has its own prompt that describes what good output looks like (see Code/study_guide/generation/prompts.py), and here's the part I care about most: we don't just trust whatever the model says. Every output type has a strict schema written in Pydantic (see Code/study_guide/generation/schemas.py) — a flashcard has to have a question, an answer, tags, and a difficulty; a quiz question has to have four options with exactly one marked correct. The model's reply is parsed and checked against that schema, and if it doesn't fit, we reject it instead of shipping a broken card. That's what lets the scheduler, the exporter, and the UI all trust the shape of the data.

The second decision was not to marry one AI company. The generator supports four providers — OpenAI, Anthropic's Claude, OpenRouter, and Codex — and the same generate-then-validate flow runs behind all of them (see Code/study_guide/generation/generator.py). In the web app you pick your provider on the Settings page; if the server doesn't already have a key for it, it asks for one.

The newest provider is the one I'll flag, because it's genuinely different: Codex needs no API key at all. Instead of calling an API, we shell out to the local codex command-line tool and run generation through the developer's existing ChatGPT login. The prompt is piped in over standard input — we literally hand `codex exec` a trailing dash so it reads the prompt from stdin — and nothing, no key, is ever sent or stored by us. What comes back is still parsed and validated with the same Pydantic schema as every other provider.

I'll be honest about the tradeoff: Codex is slower, up to about five minutes for a big batch, and if the machine isn't logged in we detect that and tell you to run codex login. It's the right call for zero-cost, key-free generation — it's just not the right call for a live demo.

Speaking of the demo — [Name] is going to show you what all of this actually feels like to use.

### Side notes for judge questions

- Provider dispatch is `GenerationProvider = Literal["openai", "anthropic", "openrouter", "codex"]` in Code/study_guide/generation/generator.py; the default comes from `STUDY_GUIDE_GENERATION_PROVIDER` (config.py, default `"openai"`), and users switch providers on the web Settings page (Code/frontend/src/app/(app)/settings/page.tsx).
- The Codex path (`_generate_with_codex`) runs `codex exec --skip-git-repo-check --ephemeral -s read-only -o <file> [-m model] -`; the prompt is piped via stdin (the trailing `-`), no API key is used — it rides the machine's ChatGPT login — and the result comes back with `tokens_used=0`.
- Codex deliberately does NOT use `--output-schema`: strict constrained decoding needs `additionalProperties: false` on every object, which Pydantic's default JSON schema doesn't emit, so the schema text is embedded in the prompt and the reply is validated with Pydantic (`_parse_structured_text`) — the same text path as Anthropic and OpenRouter.
- The model name is regex-validated (`_CODEX_MODEL_PATTERN`) before any process spawns, so shell metacharacters can't reach the Windows `codex.cmd` / cmd.exe shim. Auth failures surface as HTTP 401 with a "run `codex login`" message; timeouts as 504.
- Codex timeout is `STUDY_GUIDE_CODEX_TIMEOUT` (`config.CODEX_TIMEOUT_SECONDS`, default 300s). Separate cost guardrails cap generation at 5 chunks and 4000 tokens per response (config.py, `MAX_CHUNKS_PER_GENERATION` / `MAX_TOKENS_PER_RESPONSE`).
- The Codex provider has its own dedicated test file, Code/tests/test_generator_codex.py (11 tests), covering the not-installed, not-authenticated, timeout, and bad-model-name paths.

## Slides You Build (maps to `PresentationSlides/slideshowto.txt`)

- **Slide: AI Generation (Design Highlights, part 2 of the deck)** — a simple flow: `Chunk → Prompt → Model → Validated Schema → Study Set`.
- **Slide: Multi-Provider** — four logos/labels (OpenAI, Claude, OpenRouter, Codex) feeding one "Generator." Add a callout on Codex: **"No API key — uses your local ChatGPT login."**

## Source Material To Pull From (real paths)

- `README.md` → the "Codex CLI (no API key)" section is written almost as a script for you; and the Configuration table lists `STUDY_GUIDE_GENERATION_PROVIDER` with values `openai | anthropic | openrouter | codex`, plus `STUDY_GUIDE_CODEX_MODEL` and `STUDY_GUIDE_CODEX_TIMEOUT` (default 300s).
- Actual code (know it, don't open live):
  - `Code/study_guide/generation/generator.py` — the provider dispatch; `GenerationProvider = Literal["openai", "anthropic", "openrouter", "codex"]`, and `_generate_with_codex()` is the stdin/`codex exec` path.
  - `Code/study_guide/generation/schemas.py` — the Pydantic v2 output schemas (Flashcard, Quiz, PracticeTest, AudioSummary).
  - `Code/study_guide/generation/prompts.py` — the per-type generation prompts.

## Demo Responsibility

**Optional / supporting.** The live "generate" click belongs to Part 4, using a fast provider (OpenAI or Claude). If you *want* a moment, you can show the provider dropdown in the UI while you talk about multi-provider — but coordinate with Part 4 so you're not both driving. **Do not attempt a live Codex generation on stage** — it takes minutes. If asked, offer to show a pre-generated Codex result instead.

## Likely Questions & Suggested Answers

- **Q (professor): "How do you stop the AI from hallucinating a wrong answer onto a flashcard?"**
  A: "Two layers. First, structured output — the model is constrained to a schema, so it can't ramble; it has to return a well-formed question/answer/options object or we reject it. Second, the prompts ground the model in the user's own uploaded material rather than open-ended world knowledge, so the answers come from the source, not from the model's imagination. It's not perfect, but the schema validation means a malformed or empty response fails loudly instead of silently becoming a bad card."

- **Q: "Why support four providers instead of just picking the best one?"**
  A: "Three reasons: cost, availability, and access. Different users have keys for different vendors; some have none at all, which is exactly who the Codex and MCP paths are for. And vendor lock-in is a real risk for a student tool — if OpenAI changes pricing or a campus blocks it, our users aren't stranded. Same prompt-and-validate code runs behind all four, so the cost of supporting them is low."

- **Q: "How does the Codex path work without an API key — isn't that a security hole?"**
  A: "The opposite — it's *more* private. It runs the official `codex` command-line tool, which is already authenticated with the developer's ChatGPT account on that machine. We pipe the prompt to it over standard input and read the result back; our app never sees, sends, or stores a key. The credential stays in the CLI's own login, exactly where the user already put it."
