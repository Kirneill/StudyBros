# MCP Server Architecture Research

> How to build KSpider as an MCP server so any LLM client can use it without an API key.

---

## What is MCP (Model Context Protocol)

MCP is a protocol that lets LLM applications (Claude Code, Claude Desktop, Cursor, VS Code Copilot) connect to external tools and data sources. Instead of the tool calling an LLM API, the LLM client calls the tool — the connected LLM does the generation natively.

---

## MCP Python SDK

**Package:** `mcp` on PyPI (v1.27.0 as of April 2026). MIT license. Requires Python >= 3.10.

### Installation
```bash
pip install "mcp[cli]"
```

### High-Level API: FastMCP (built into the SDK)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("kspider-study-guide")

@mcp.tool()
def ingest_file(file_path: str) -> str:
    """Ingest a file and extract text for study material generation."""
    # implementation
    return "Ingested: 5000 tokens across 10 chunks"

@mcp.resource("study://documents/{doc_id}/chunks")
def get_document_chunks(doc_id: str) -> str:
    """Get all text chunks for a document."""
    return json.dumps(chunks)

@mcp.prompt()
def generate_flashcards(topic: str, num_cards: int = 10) -> str:
    """Generate flashcards from study material."""
    chunks = load_chunks(topic)
    return f"Generate {num_cards} flashcards from:\n\n{chunks}"

if __name__ == "__main__":
    mcp.run()  # stdio transport by default
```

### Key Concepts

**Tools** — Model-controlled functions. LLM decides when to call them. Can have side effects.
```python
@mcp.tool()
def chunk_text(text: str, max_tokens: int = 500) -> list[str]:
    """Split text into chunks."""
```

**Resources** — Application-controlled, read-only data. User/app selects them explicitly.
```python
@mcp.resource("study://topics/{id}/chunks")
def get_chunks(id: str) -> str:
    """Get chunks for a topic."""
```

**Prompts** — User-controlled reusable templates. Appear as slash commands in clients.
```python
@mcp.prompt()
def generate_quiz(topic: str, count: int = 10) -> str:
    """Generate a quiz from study material."""
```

### Tool Descriptions Are Critical
The docstring is what the LLM reads to decide whether to call the tool. Write them like API docs.

---

## Transport Modes

| Transport | Use Case | Details |
|---|---|---|
| **stdio** | Local tools, IDE integrations, single-user | Process runs as child. stdin/stdout JSON-RPC. Microsecond latency. |
| **Streamable HTTP** | Remote, multi-user, production | Single HTTP endpoint. OAuth 2.1 built-in. Stateless mode available. |
| **SSE** | Legacy only | Being removed mid-2026. Avoid. |

**Rule:** stdio for local, Streamable HTTP for remote. Never print to stdout in stdio mode (corrupts JSON-RPC).

---

## Registration

### Claude Code
```bash
# Local Python server
claude mcp add kspider -- uv run /path/to/server.py

# With env vars
claude mcp add --env OPENAI_API_KEY=secret kspider -- uv run server.py

# HTTP transport
claude mcp add --transport http kspider http://localhost:8000/mcp

# Scopes
claude mcp add --scope user kspider -- ...     # all projects
claude mcp add --scope project kspider -- ...   # shared via .mcp.json
claude mcp add --scope local kspider -- ...     # just you + this project
```

### Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "kspider": {
      "command": "uv",
      "args": ["--directory", "/path/to/kspider", "run", "kspider-mcp"],
      "env": {}
    }
  }
}
```

### Project-level `.mcp.json` (checked into repo)
```json
{
  "mcpServers": {
    "kspider": {
      "command": "uv",
      "args": ["run", "python", "src/server.py"],
      "env": { "DB_PATH": "${DB_PATH:-./data/study_guide.db}" }
    }
  }
}
```

---

## Advanced Patterns

### Lifespan Management (database connections)
```python
from contextlib import asynccontextmanager
from dataclasses import dataclass

@dataclass
class AppContext:
    db: Database

@asynccontextmanager
async def app_lifespan(server: FastMCP):
    db = await Database.connect()
    try:
        yield AppContext(db=db)
    finally:
        await db.disconnect()

mcp = FastMCP("kspider", lifespan=app_lifespan)

@mcp.tool()
def query(ctx: Context[ServerSession, AppContext]) -> str:
    db = ctx.request_context.lifespan_context.db
    return db.query()
```

### Progress Reporting
```python
@mcp.tool()
async def ingest_file(path: str, ctx: Context) -> str:
    await ctx.report_progress(progress=0.5, total=1.0, message="Extracting text")
    # ...
    await ctx.report_progress(progress=1.0, total=1.0, message="Done")
    return "Complete"
```

### Mounting into ASGI (FastAPI coexistence)
```python
from starlette.applications import Starlette
from starlette.routing import Mount

mcp = FastMCP("kspider", json_response=True)
app = Starlette(routes=[Mount("/mcp", app=mcp.streamable_http_app())])
```

---

## Distribution

### PyPI (recommended for Python servers)
```toml
[project]
name = "kspider-mcp"
version = "0.1.0"
dependencies = ["mcp[cli]>=1.2.0"]

[project.scripts]
kspider-mcp = "kspider_mcp.server:main"
```

Users install: `pip install kspider-mcp && claude mcp add kspider -- kspider-mcp`

### uvx (no install needed)
```bash
claude mcp add kspider -- uvx kspider-mcp
```

---

## llms.txt Convention

Standard for making websites LLM-readable. A markdown file at `/llms.txt`:

```markdown
# KSpider Study Guide

> AI-powered study guide generator. MCP server for any LLM client.

## Getting Started
- [Installation](https://kspider.dev/docs/install.md): How to install and configure
- [MCP Setup](https://kspider.dev/docs/mcp-setup.md): Register with Claude Code/Desktop

## API Reference
- [Tools](https://kspider.dev/docs/tools.md): All MCP tools
- [Resources](https://kspider.dev/docs/resources.md): Available resources
- [Prompts](https://kspider.dev/docs/prompts.md): Reusable prompt templates
```

Companion files:
- `llms-ctx.txt` — expanded version without Optional section
- `llms-ctx-full.txt` — all URLs resolved inline (full context dump)

Adopted by thousands of sites via Mintlify, GitBook, ReadTheDocs.
