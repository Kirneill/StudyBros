# Part 2 — Architecture & Backend

**Presenter: ___**

**Time budget: ~2–2.5 minutes** — the verbatim Script below IS your talk; the Talking Points are your extended Q&A depth. You go second, right after the "why."

## Your Scope (what YOU cover)

- **The system map** — the three delivery surfaces (MCP server, CLI, web app) sharing one Python core.
- **The ingestion pipeline** — how a raw file (PDF, PPTX, text, video/audio) becomes clean, chunked text ready for the AI.
- **The database** — what StudyBros stores and how (SQLAlchemy 2.0 over SQLite: Sources, Documents, Chunks, Study Sets, plus the learning tables).
- **The MCP server** — the "works with any LLM, no API key" surface, and why that's architecturally interesting.

## NOT Your Scope (belongs to other parts)

- **Why FSRS / the learning science** → **Part 1** (you can name-drop FSRS as "the scheduler in the learning layer," but don't re-explain the science).
- **How the AI turns a chunk into flashcards** — prompts, schemas, providers → **Part 3**. You hand off *at* the generation boundary: "the chunks are now ready for the AI, and [Name] will take it from there."
- **The FastAPI REST layer that the web app calls, the frontend, and the live demo** → the API is touched in Part 4's demo. You own the *core library and MCP server*; mention FastAPI exists as the third surface but don't demo it.

## Talking Points (full sentences — rehearse these)

1. "StudyBros isn't one app — it's one Python core with three front doors. There's a command-line tool, there's a web app, and there's an MCP server. They all call the same ingestion, storage, scheduling, and export code, so a fix in the core benefits every surface at once."
2. "Everything starts with ingestion. A file scanner discovers supported files, then a format-specific extractor pulls the text out — we have separate extractors for PDF, for PowerPoint, for plain text and Markdown, and for video and audio. The video path is the interesting one: it strips the audio with FFmpeg and transcribes it with Whisper, so a recorded lecture becomes searchable text."
3. "Raw extracted text is too big and too unstructured to hand an AI directly, so a chunker splits it — preferring natural boundaries like paragraphs and headings, and falling back to fixed-size overlapping chunks when there's no structure. Those chunks are the unit everything downstream operates on."
4. "All of it lands in a SQLite database through SQLAlchemy. The core tables are Sources — the original files — Documents — the extracted content — Chunks — the text segments — and Study Sets — the generated flashcards, quizzes, and tests. On top of those sit the learning tables that record every card review and each user's progress, which is what feeds the scheduling and mastery tracking."
5. "The surface I want to highlight is the MCP server. MCP — Model Context Protocol — lets any LLM client, like Claude Desktop or Cursor, connect to StudyBros as a set of tools. We expose ten tools, nine resources, and eight prompts — things like ingest a file, record a review, get the cards due today, check mastery on a topic."
6. "The clever part: with MCP, *the connected model does the generation* — so the user needs no API key of their own. StudyBros handles the ingestion, the storage, the FSRS scheduling, and the export; the model on the other end handles the language work. It turns any chatbot into a spaced-repetition study coach."
7. (Handoff) "So the pipeline gets us from a messy file to clean, stored chunks. The question is how those chunks become good flashcards and quizzes — and that's the AI generation layer, which [Name] will explain."

## Script (2–3 minutes, verbatim)

What you just heard is the science; my job is how it's actually built. StudyBros is one Python core with three front doors — a command-line tool, a web app, and an MCP server — all calling the same code underneath, so we fix something once and every surface gets it.

Everything begins with ingestion. You hand it a file, a scanner figures out what it is, and then a format-specific extractor pulls the text out — we have separate ones for PDF, PowerPoint, plain text and Markdown, and video and audio (see Code/study_guide/ingestion/extractors). The video path is my favorite: it rips the audio out with FFmpeg and transcribes it with Whisper, so a two-hour lecture recording becomes text we can work with.

That text is usually too big to hand an AI in one piece, so a chunker splits it (see Code/study_guide/ingestion/chunker.py). It tries to cut on natural boundaries first — headings, then paragraphs, then sentences — and only falls back to fixed-size slices with a little overlap when there's no structure to lean on. Those chunks are the unit everything downstream uses.

All of it gets stored in a SQLite database through SQLAlchemy (see Code/study_guide/database/models.py). The core tables are Sources for the original files, Documents for the extracted content, Chunks for the text segments, and Study Sets for the generated material. On top of those sit the learning tables that log every card review and each topic's progress, which is what feeds the scheduling [Name] just described.

The piece I most want to show off is the MCP server (see Code/mcp_server/server.py). MCP lets any language-model client — Claude Desktop, Cursor, whatever you already use — connect to StudyBros as a set of tools; we expose ten tools, nine resources, and eight prompts. The trick is that the connected model does the generation, so the user needs no API key of their own. We handle the files, the storage, the scheduling, and the export; the model on the other end handles the language.

So we can get from a messy file all the way to clean, stored chunks. How those chunks turn into good flashcards and quizzes is the AI layer — [Name], that's your part.

### Side notes for judge questions

- Chunker defaults: `CHUNK_SIZE` 1500 characters, `CHUNK_OVERLAP` 200 characters, `min_chunk_size` 100 characters (config.py lines 67–68; chunker.py). Smart mode splits on markdown headings `#{1,3}` → paragraphs → sentences; the fixed fallback breaks on the last word boundary.
- Audio is chunked to ≤ 20 MB segments (`STUDY_GUIDE_AUDIO_CHUNK_SIZE_MB`, default 20) and downmixed to mono 16 kHz before Whisper transcription (config.py; Documentation/Roadmap.txt).
- The MCP server registers 27 handlers total — 10 tools, 9 resources, 8 prompts — which matches the `@mcp` decorator count in Code/mcp_server/server.py. Tools include `ingest_file`, `record_review`, `get_due_cards`, `check_mastery`, and `export_study_set`.
- Storage is SQLite via SQLAlchemy 2.0 (`Mapped[]` / `mapped_column`): four core tables Source/Document/Chunk/StudySet in Code/study_guide/database/models.py, plus the learning tables CardReview and UserProgress in Code/study_guide/learning/models.py.
- The REST surface is FastAPI, mounted in Code/api/main.py with route modules in Code/api/routes/ (upload, documents, generate, study, study_sets, export, gamification). The MCP server and API are covered by Code/tests/test_mcp_server.py (40 tests) and test_api.py (44 tests).
- Why SQLite: it's zero-config for a single-user local tool, and because all access goes through the SQLAlchemy ORM, moving to Postgres later is a connection-string change, not a rewrite.

## Slides You Build (maps to `PresentationSlides/slideshowto.txt`)

- **Slide: Architecture Overview** — the one that matters most. A layered diagram: three surfaces (CLI / Web / MCP) on top, then Core (Ingestion → Database → Learning → Export). There's a ready-made ASCII version in `Documentation/Roadmap.txt` (lines ~17-47) you can redraw cleanly.
- **Slide: Ingestion Pipeline** — a left-to-right flow: `File → Extractor (PDF/PPTX/Text/Video) → Chunker → Database`.
- **Slide (optional): MCP Server** — the "10 tools / 9 resources / 8 prompts, no API key" callout.

## Source Material To Pull From (real paths)

- `README.md` → "Project Structure" (full module tree), "MCP Tools Reference", "MCP Resources Reference".
- `CLAUDE.md` → "Tech Stack" and "Project Structure".
- `Documentation/Roadmap.txt` → the ASCII architecture diagram and the ingestion milestone list.
- Actual code you can point at if asked (don't open live, just know it exists):
  - Ingestion: `Code/study_guide/ingestion/scanner.py`, `chunker.py`, `extractors/{pdf,pptx,text,video}_extractor.py`
  - Database: `Code/study_guide/database/models.py` (SQLAlchemy 2.0 models), `schema.py`, `operations.py`
  - Learning tables: `Code/study_guide/learning/models.py` (CardReview, UserProgress)
  - MCP server: `Code/mcp_server/server.py`

## Demo Responsibility

**None live, but you are the backup narrator.** If Part 4's live demo breaks during upload, you're the person who can explain *what should be happening* under the hood (scan → extract → chunk → store). Have that 20-second fallback ready.

## Likely Questions & Suggested Answers

- **Q (professor): "Why SQLite instead of a real database like Postgres?"**
  A: "SQLite keeps the app zero-configuration — it runs locally with no server to stand up, which is exactly right for a single-user study tool and for demoing. Because we went through SQLAlchemy as the ORM rather than writing raw SQL, moving to Postgres later is a connection-string change, not a rewrite."

- **Q: "What is MCP and why did you use it instead of just building your own API?"**
  A: "MCP is an open protocol that lets language-model clients call external tools in a standard way. We *did* also build our own REST API for the web app — but MCP gives us something the REST API can't: it plugs StudyBros directly into any existing LLM client with no API key and no code, because the user's own model does the generation. It's the lowest-friction way to reach users who already live in a chat tool."

- **Q: "How do you handle a two-hour lecture video — doesn't that blow up?"**
  A: "The audio is chunked into segments under about twenty megabytes and downmixed to mono sixteen-kilohertz before transcription, which keeps each Whisper call small and cheap. After transcription the text goes through the same chunker as everything else, so the rest of the pipeline doesn't care that it started as video."
