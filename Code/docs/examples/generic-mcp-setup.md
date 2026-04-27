# Any MCP Client Setup

StudyBros uses the stdio transport. Any MCP-compatible client can connect by spawning the server process.

## How it works

The MCP client starts a subprocess:

```
python -m mcp_server
```

The working directory must be the `Code` directory (where `mcp_server/` and `study_guide/` live). The server communicates over stdin/stdout using the MCP JSON-RPC protocol.

## Generic JSON config

Most MCP clients accept a configuration like this:

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

**Key fields:**
- `command`: The Python executable. Use `python3` on systems where `python` points to Python 2. Use a full path if the executable is not on PATH.
- `args`: Always `["-m", "mcp_server"]`. This runs the `mcp_server` package as a module.
- `cwd`: Absolute path to the `Code` directory. This is required so Python can find the `mcp_server` and `study_guide` packages.

## Manual testing

You can test the server manually by piping MCP protocol messages:

```bash
cd /path/to/studybros/Code
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0.1"}}}' | python -m mcp_server
```

## Server capabilities

Once connected, the client has access to:

- **10 tools**: ingest_file, ingest_directory, store_study_set, record_review, get_due_cards, check_mastery, get_strengths_weaknesses, export_study_set, delete_document, delete_study_set
- **9 resources**: status, documents, chunks, study sets, schedules, progress, strengths/weaknesses, achievements
- **8 prompts**: generate_flashcards, generate_quiz, generate_practice_test, generate_summary, study_flashcards, take_quiz, explain_concept, review_progress

## Environment

No environment variables are required. The server creates a SQLite database at `data/study_guide.db` relative to `cwd` on first use.

Optional environment variables can be passed via the `env` field:

```json
{
  "mcpServers": {
    "studybros": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/studybros/Code",
      "env": {
        "STUDY_GUIDE_DB_PATH": "/custom/path/study.db"
      }
    }
  }
}
```
