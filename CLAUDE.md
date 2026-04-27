# CLAUDE.md — StudyBros

## What This Project Is

StudyBros is an AI-powered study guide platform that transforms learning materials (PDFs, PPTX, text, video) into flashcards, quizzes, and practice tests. It uses evidence-based learning science (FSRS spaced repetition, active recall, 85% difficulty targeting, Bloom's taxonomy) and science-backed gamification (SDT, flow state, mastery progression, competency completion).

**Three delivery surfaces:**
1. **MCP Server** — Any LLM client connects via Model Context Protocol. No API key needed.
2. **LLM Skills + Docs** — Users paste a URL; their LLM understands and implements StudyBros.
3. **Web App on Vercel** — Next.js frontend with dark theme, gamification UI, and interactive study modes.

## Tech Stack

### Backend (Python 3.11+)
- **SQLAlchemy 2.0** — ORM with mapped_column style (see `Code/study_guide/database/models.py`)
- **Pydantic v2** — Schemas with `model_validator` (see `Code/study_guide/generation/schemas.py`)
- **Click** — CLI framework (see `Code/study_guide/cli.py`)
- **FastMCP** — MCP server (Phase 1: `Code/mcp_server/`)
- **FastAPI** — REST API (Phase 3: `Code/api/`)
- **FSRS** — Free Spaced Repetition Scheduler (Phase 0: `Code/study_guide/learning/scheduler.py`)

### Frontend (Phase 4+)
- **Next.js 16** + **React 19** + **TypeScript 5**
- **Tailwind CSS 4** (dark theme with `@theme inline`)
- **Framer Motion 12** (animations, page transitions, confetti)
- Location: `Code/frontend/`

### Design Tokens
```
Background: #1A1A2E (charcoal), Cards: #232342
Accent: #00D4AA (teal), Text: #F5F0EB (ivory)
Mastery: gray (#4B5563) → yellow (#F59E0B) → green (#22C55E) → gold (#F59E0B)
Bloom: blue (#60A5FA) → green (#34D399) → yellow (#FBBF24) → red (#F87171)
```

## Project Structure

```
Capstone1/
├── Code/
│   ├── study_guide/           # Python backend
│   │   ├── database/          # SQLAlchemy models, schema, operations
│   │   ├── generation/        # LLM prompts, Pydantic schemas, generator
│   │   ├── ingestion/         # File extractors, chunker, scanner
│   │   ├── export/            # Anki, JSON, Markdown exporters
│   │   ├── learning/          # NEW: FSRS scheduler, gamification, models
│   │   ├── utils/             # Audio utilities
│   │   └── cli.py             # Click CLI (540 lines)
│   ├── mcp_server/            # NEW: MCP server (Phase 1)
│   ├── api/                   # NEW: FastAPI REST (Phase 3)
│   ├── frontend/              # NEW: Next.js app (Phase 4)
│   ├── tests/                 # pytest suite
│   ├── pyproject.toml         # Python config
│   └── Makefile               # Build commands
├── StudyGuideResearch/        # Evidence-based research docs
│   ├── 00-INDEX.md            # READ THIS FIRST
│   ├── 01-learning-science.md # 15 learning methods
│   ├── 02-mcp-architecture.md # MCP SDK patterns
│   ├── 03-code-review.md      # Codebase issues to fix
│   ├── 04-tunedpc-frontend-reference.md  # Design system
│   └── 05-gamification-science.md        # 12 gamification principles
└── CLAUDE.md                  # This file
```

## Build & Test

```bash
# From Code/ directory
pip install -e ".[dev]"        # Install with dev dependencies
pytest -v --tb=short           # Run all tests
ruff check .                   # Lint
mypy study_guide/              # Type check
make test                      # If Makefile is set up

# MCP Server (Phase 1+)
python -m mcp_server           # Start MCP server (stdio)

# Frontend (Phase 4+)
cd frontend && npm install && npm run dev   # Dev server
cd frontend && npm run build                # Production build

# API (Phase 3+)
uvicorn api.main:app --reload  # FastAPI dev server
```

## Key Conventions

### Python
- SQLAlchemy 2.0 style: `Mapped[type]` + `mapped_column()`, NOT old-style `Column()`
- Pydantic v2: `model_validator`, `field_validator`, NOT v1 `validator`
- All DB access through `get_session_ctx()` context manager (Phase 0 adds this)
- Tests in `Code/tests/`, named `test_*.py`, functions `test_*`
- Line length: 100 (ruff config in pyproject.toml)

### TypeScript (Phase 4+)
- Strict mode, no `any` types, no `as unknown` casts
- ESLint with `@typescript-eslint/no-explicit-any: "error"` (see global CLAUDE.md)
- Tailwind 4 with `@theme inline` for design tokens
- Server Components by default; `"use client"` only when needed

### Gamification Rules (MUST follow — see StudyGuideResearch/05-gamification-science.md)
- Track REAL competency, not vanity metrics (no XP for time spent)
- Streaks are "5 of 7 days" rolling, NOT binary consecutive
- Achievements require demonstrated Bloom level, NOT participation
- Three-phase scaffolding: habit (weeks 1-4) → competence (months 2-3) → intrinsic (month 4+)
- Topics have a "You Won" completion moment when mastered
- NEVER take away visible progress for inactivity

### FSRS Rules (MUST follow — see StudyGuideResearch/01-learning-science.md)
- Cards rated 1-4 (Again/Hard/Good/Easy)
- Target ~85% accuracy (Wilson et al., 2019)
- Mastery = retrievability >90% at >30-day intervals + accuracy >85% + Bloom L3+
- Due cards sorted by lowest retrievability first

## Research References

Before implementing any learning, scheduling, or gamification feature, read the relevant research doc:

| Topic | File |
|---|---|
| Spaced repetition, active recall, 85% rule | `StudyGuideResearch/01-learning-science.md` |
| MCP tools, resources, prompts, transport | `StudyGuideResearch/02-mcp-architecture.md` |
| Bugs to fix, code review findings | `StudyGuideResearch/03-code-review.md` |
| Dark theme, TunedPC design system | `StudyGuideResearch/04-tunedpc-frontend-reference.md` |
| SDT, flow, mastery, gamification fading | `StudyGuideResearch/05-gamification-science.md` |

## Skill Routing for Agents

When delegating to subagents, inject the relevant skill from `F:\CLAUDE\.claude\skills\`:

| Task Type | Skill to Inject |
|---|---|
| New feature or module | `spec-driven-development` |
| Multi-file implementation | `incremental-implementation` |
| Writing or fixing tests | `test-driven-development` |
| Code review (every phase gate) | `code-review-and-quality` |
| Frontend UI components | `frontend-ui-engineering` |
| React patterns | `react-2026`, `react-composition-2026`, `react-server-components` |
| Performance work | `performance-optimization` |
| Security hardening | `security-and-hardening` |
| API design | `api-and-interface-design` |
| Planning/breakdown | `planning-and-task-breakdown` |

Agent personas at `F:\CLAUDE\.claude\agents\`:
- `code-reviewer.md` — 5-axis review (correctness, readability, architecture, security, performance)
- `test-engineer.md` — Test strategy, coverage analysis, test writing
- `security-auditor.md` — Vulnerability detection, threat modeling

### Karpathy Guidelines (Plugin: andrej-karpathy-skills)
Available as `/karpathy-guidelines` skill. Core principles: write clean, minimal code. No unnecessary abstractions. Functions should do one thing. Prefer flat over nested. Read before write. These align with this project's conventions.

## Worktree Workflow

All coding subagents use `isolation: "worktree"`:
1. Each subagent gets its own git branch (e.g., `phase-0/fsrs-scheduler`)
2. Parallel agents work on NON-OVERLAPPING files
3. Orchestrator reviews diff after completion
4. `code-reviewer` + `test-writer` validate (Gordon Ramsay pattern)
5. Merge to main only after review passes

## Phase Checklist

Current plan: `~/.claude/plans/vast-hatching-llama.md`

- [ ] Phase 0: Bug fixes + FSRS + gamification data models + tests
- [ ] Phase 1: MCP server (tools, resources, prompts)
- [ ] Phase 2: LLM skills + llms.txt documentation
- [ ] Phase 3: FastAPI backend + gamification endpoints
- [ ] Phase 4: Next.js frontend + gamification UI on Vercel
- [ ] Phase 5: Interactive study UI + "You Won" + strengths/weaknesses
- [ ] Phase 6: Polish + Vercel production deploy

Code review gate after EVERY phase. No exceptions.
