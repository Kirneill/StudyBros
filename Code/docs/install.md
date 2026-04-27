# Installation

## Prerequisites

- **Python 3.11+** (required)
- **FFmpeg** (optional, for video/audio file ingestion)

## Install StudyBros

```bash
git clone https://github.com/your-org/studybros.git
cd studybros/Code
pip install -e ".[dev]"
```

The `.[dev]` extra includes pytest, ruff, and mypy for development. For production use, `pip install -e .` is sufficient.

## Verify installation

```bash
python -c "from mcp_server.server import mcp; print(mcp.name)"
```

Expected output:

```
studybros
```

You can also start the server directly:

```bash
python -m mcp_server
```

This launches the MCP server on stdio transport. It will wait for MCP protocol messages -- you will not see output unless an MCP client connects.

## FFmpeg (optional)

FFmpeg is only needed if you want to ingest video or audio files (`.mp4`, `.mov`, `.mp3`, `.wav`, etc.). Document formats (PDF, PPTX, TXT, MD) work without it.

### Windows

```bash
winget install Gyan.FFmpeg
```

Or download from https://ffmpeg.org/download.html and add to PATH.

### macOS

```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)

```bash
sudo apt install ffmpeg
```

## Environment variables (optional)

All environment variables are optional for MCP server usage. The server uses the connected LLM client for generation -- no API key is needed.

| Variable | Default | Description |
|---|---|---|
| `STUDY_GUIDE_DB_PATH` | `data/study_guide.db` | SQLite database path |
| `STUDY_GUIDE_EXPORT_DIR` | `data/exports` | Directory for exported files |
| `OPENAI_API_KEY` | (none) | Only needed for the standalone CLI, not for MCP |
| `STUDY_GUIDE_GENERATION_MODEL` | `gpt-4o` | Model name for CLI generation |

## Supported file types

| Category | Extensions |
|---|---|
| Documents | `.pdf`, `.pptx`, `.txt`, `.md`, `.markdown`, `.text` |
| Video | `.mp4`, `.mov`, `.webm`, `.avi`, `.mkv` |
| Audio | `.mp3`, `.wav`, `.m4a`, `.aac`, `.ogg` |

Video and audio files require FFmpeg for transcription.

## Database

StudyBros uses SQLite. The database is created automatically on first use at `data/study_guide.db` (relative to the `Code` directory). No setup required.
