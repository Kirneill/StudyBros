# Quick Start

Get StudyBros running in under 2 minutes.

## 1. Install

```bash
cd /path/to/studybros/Code
pip install -e .
```

## 2. Configure your MCP client

Add this to your MCP client configuration (e.g., `.mcp.json`, `claude_desktop_config.json`, or equivalent):

```json
{
  "mcpServers": {
    "studybros": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/studybros/Code"
    }
  }
}
```

Replace `/path/to/studybros/Code` with the actual path to the `Code` directory.

## 3. Ingest a document

Tell your LLM:

> Ingest /path/to/my/notes.pdf

The server extracts text, chunks it, and stores it in the database. You get back a document ID.

## 4. Generate study materials

> Generate 20 flashcards from document 1

The LLM reads your document content via a prompt, generates flashcards, and stores them as a study set. You get back a study set ID.

## 5. Study with spaced repetition

> Start a flashcard study session for study set 1

The LLM presents cards ordered by FSRS urgency, collects your answers, records reviews, and tells you when each card is due next.

## 6. Track progress

> How am I doing?

The LLM reads your progress data and presents strengths, weaknesses, mastery levels, consistency streaks, and recommendations.

## What just happened

- **Ingest** extracted and chunked your document into the SQLite database
- **Generate** used the document chunks as context for the LLM to produce structured flashcards
- **Study** ran an interactive session with FSRS spaced repetition scheduling each card
- **Progress** analyzed your review history to show mastery and recommend next steps

No API keys are needed for the MCP server itself. The LLM client provides the intelligence; StudyBros provides the data, scheduling, and tracking.
