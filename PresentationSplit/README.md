# StudyBros — Presentation Work Split

This folder splits the StudyBros capstone presentation into **four equal parts, one per team member**. Each person owns one part file, rehearses it, and builds the matching slides. Nobody has to understand the whole system deeply — you own your slice and know where the seams are.

## The Split

| Part | Owner | Topic | Time |
|---|---|---|---|
| [Part 1](part1-problem-and-learning-science.md) | `___` | Problem + learning science (why the app exists, FSRS, active recall, 85% rule, Bloom's) | ~2–2.5 min |
| [Part 2](part2-architecture-and-backend.md) | `___` | Architecture + backend (ingestion pipeline, database, MCP server) | ~2–2.5 min |
| [Part 3](part3-ai-generation.md) | `___` | AI generation (prompts, structured output, multi-provider incl. new Codex no-key path) | ~2–2.5 min |
| [Part 4](part4-frontend-gamification-demo.md) | `___` | Frontend + gamification + live demo + Capstone I wrap-up | ~2.5–3 min (incl. demo) |

## Length

**7–10 minutes total, 2–3 minutes of speaking each**, with Q&A after (shared — whoever owns the relevant part fields the question). The **verbatim Script section in each part file IS your talk** — rehearse it as written and it lands at ~2–2.5 minutes. The longer "Talking Points" lists are the extended version: use them as your Q&A depth, not as extra stage time. If the four of you run long in rehearsal, cut from Part 4's demo (show the pre-generated study set instead of generating live) before cutting anyone's script.

The order is deliberate — it walks the audience from *why* → *how it's built* → *how the AI works* → *what it looks like and what's next*. Run the parts **1 → 2 → 3 → 4** with no reordering; each part hands off to the next (the last line of every part file is the handoff sentence).

## How To Claim A Part

1. Open the part file you want.
2. Put your name on the `Presenter: ___` line at the top.
3. Tell the group in chat so two people don't claim the same one.
4. Balance is by **speaking time, not file length** — Part 1 has more prose because learning-science talking points need full sentences, but every part's script is ~2–2.5 minutes out loud. Don't pad or rush to match file size.

## Slides — Important

`PresentationSlides/` currently contains **only `slideshowto.txt`, an instructions stub** — there are no finished slides yet. That stub says the deck must be a `.pptx` and suggests this outline: *Problem & motivation → Architecture overview → Design highlights → Capstone I accomplishments → Next steps*. Each part file below maps its content to that outline and tells you which slides you are responsible for building. **Someone still has to assemble the actual `.pptx`** — agree on who owns the file and each person drops in their 2-4 slides.

## Shared Facts Everyone Should Know (in case of a cross-part question)

- The product is **StudyBros** (older internal docs and `Documentation/KSpiderDocumentation.pdf` call it "KSpider" — same project, renamed).
- It has **three delivery surfaces**: (1) an MCP server any LLM client can use with no API key, (2) a CLI, and (3) a Next.js web app. The live demo uses the web app.
- Backend is **Python 3.11+** (SQLAlchemy 2.0, Pydantic v2, Click, FastMCP, FastAPI); frontend is **Next.js 16 / React 19 / TypeScript / Tailwind 4**.
- It was built over **7 Agile sprints** (Sprint archives with daily scrums, planning, reviews, and retros are in `Documentation/SprintArchives/`).
