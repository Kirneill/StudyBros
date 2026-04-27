# Claude Code Setup

Claude Code auto-discovers MCP servers from `.mcp.json` in the project root. StudyBros ships with this file already configured.

## Setup

```bash
cd /path/to/studybros/Code
pip install -e .
```

That's it. The `.mcp.json` in the `Code` directory tells Claude Code how to start the server:

```json
{
  "mcpServers": {
    "studybros": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "."
    }
  }
}
```

Claude Code will start the StudyBros MCP server automatically when you open the project.

## Example conversations

### Ingest lecture notes

> Ingest all my lecture notes from ./lectures

Claude Code calls `ingest_directory` with the path. You get back a summary of how many files were processed.

### Generate flashcards

> Generate flashcards for document 1

Claude Code uses the `generate_flashcards` prompt, reads the document content, generates cards, and calls `store_study_set` to save them.

### Study session

> Let's study -- start a flashcard session for study set 1

Claude Code loads the `study_flashcards` prompt, presents cards ordered by FSRS urgency, and records your ratings via `record_review`.

### Check mastery

> Check my mastery on all topics

Claude Code calls `check_mastery` or reads `studybros://progress` to show your mastery levels, Bloom taxonomy progress, and recommendations.

### Export for Anki

> Export study set 1 as an Anki deck

Claude Code calls `export_study_set(study_set_id=1, format="anki")` and returns the file path.

### Review progress

> Show me my study progress report

Claude Code uses the `review_progress` prompt and presents your strengths, weaknesses, consistency streak, achievements, and next steps.

## Verify the server is running

Ask Claude Code:

> What MCP tools do you have from StudyBros?

It should list all 10 tools. If not, check that `pip install -e .` completed without errors and that your working directory is the `Code` folder.
