# StudyBros Research Index

> All research documents grounding the StudyBros AI Study Guide architecture. Read this file first.

## Documents

| # | File | What It Covers |
|---|---|---|
| 01 | [learning-science.md](01-learning-science.md) | 15 evidence-based learning methods (spaced repetition, active recall, interleaving, generation effect, 85% rule, etc.) with implementation recommendations |
| 02 | [mcp-architecture.md](02-mcp-architecture.md) | MCP Python SDK, FastMCP, tool/resource/prompt definitions, transport modes, registration, distribution, llms.txt convention |
| 03 | [code-review.md](03-code-review.md) | Full code review of existing CLI: 2 critical issues, 6 major, 6 minor. Fix list for Phase 0 |
| 04 | [tunedpc-frontend-reference.md](04-tunedpc-frontend-reference.md) | TunedPC.com design system: colors, typography, layout, components, animations. Reference for frontend |
| 05 | [gamification-science.md](05-gamification-science.md) | 12 evidence-based gamification principles (SDT, flow, mastery progression, habit loops, overjustification, competency completion). Science vs. engagement theater |

## How These Connect

The **learning science research** (01) defines WHAT KSpider should do — FSRS scheduling, active recall, interleaving, 85% difficulty targeting, metacognitive calibration. Every feature traces to evidence.

The **MCP architecture** (02) defines HOW users interact with it — as an MCP server that any LLM client can connect to. The LLM does the generation; KSpider handles ingestion, storage, scheduling, and export.

The **code review** (03) identifies what must be fixed in the existing backend before building on top of it.

The **frontend reference** (04) provides the visual design language for the web UI (Phase 2 after MCP).
