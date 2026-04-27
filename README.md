# StudyBros

AI-powered study platform -- transforms learning materials into flashcards, quizzes, and practice tests with spaced repetition and mastery tracking.

## Features

- **Multi-format ingestion** -- PDF, PPTX, TXT, MD, video, and audio
- **AI-generated study materials** -- flashcards, quizzes, practice tests, summaries
- **FSRS v5 spaced repetition** -- optimal review scheduling based on a power-law forgetting curve
- **Bloom's taxonomy tracking** -- measures depth of understanding, not just recall
- **85% difficulty targeting** -- keeps study in the optimal learning zone
- **Science-backed gamification** -- SDT 3-phase scaffolding, mastery completion with "You Won" moments
- **MCP server** -- works with any LLM client (Claude, ChatGPT, Cursor, etc.), no API key needed
- **Export** -- JSON, Anki CSV, Markdown

## Quick Start

### MCP Setup (recommended)

Add StudyBros to your MCP client configuration (`.mcp.json`, Claude Desktop config, etc.):

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

The connected LLM does all generation -- no OpenAI API key required.

Once connected, tell your LLM:

1. **Ingest**: "Ingest my lecture slides at /path/to/slides.pdf"
2. **Generate**: "Generate 20 flashcards from document 1"
3. **Study**: "Start a flashcard session for study set 1"
4. **Track**: "How am I doing on organic chemistry?"

### CLI Setup (requires OpenAI API key)

```bash
pip install -e ".[dev]"
cp env.example.txt .env   # Add your OPENAI_API_KEY
python -m study_guide init
python -m study_guide ingest ./materials
python -m study_guide generate flashcards --doc 1 --count 20
```

## Installation

```bash
git clone <repo-url>
cd Code
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

FFmpeg is required for video/audio ingestion:

```bash
# Windows
winget install FFmpeg

# macOS
brew install ffmpeg

# Linux (Debian/Ubuntu)
sudo apt install ffmpeg
```

## MCP Tools Reference

| Tool | Description |
|------|-------------|
| `ingest_file` | Ingest a single file (PDF, PPTX, TXT, MD, video, audio) into the database |
| `ingest_directory` | Ingest all supported files from a directory |
| `store_study_set` | Store a generated study set (flashcards, quiz, practice test, summary) |
| `record_review` | Record a flashcard review with FSRS rating (1-4) and schedule next review |
| `get_due_cards` | Get cards due for review, sorted by FSRS urgency (lowest retrievability first) |
| `check_mastery` | Check if a topic meets mastery criteria (retrievability, accuracy, Bloom level) |
| `get_strengths_weaknesses` | Analyze strengths and weaknesses across all studied topics |
| `export_study_set` | Export a study set to JSON, Anki CSV, or Markdown |
| `delete_document` | Delete a document and all associated chunks and study sets |
| `delete_study_set` | Delete a study set and its review history |

## MCP Resources Reference

| Resource URI | Description |
|--------------|-------------|
| `studybros://status` | Server status, configuration, and database statistics |
| `studybros://documents` | List all ingested documents with metadata |
| `studybros://documents/{doc_id}/chunks` | Text chunks for a specific document |
| `studybros://study-sets` | List all generated study sets |
| `studybros://study-sets/{set_id}` | Full content of a specific study set |
| `studybros://study-sets/{set_id}/schedule` | FSRS review schedule and predicted retention |
| `studybros://progress` | Knowledge heat map: per-topic mastery, Bloom levels, consistency |
| `studybros://progress/strengths-weaknesses` | Detailed strengths, weaknesses, and recommendations |
| `studybros://achievements` | All earned competency achievements |

## MCP Prompts Reference

| Prompt | Description |
|--------|-------------|
| `generate_flashcards` | Generate flashcards from a document (params: document_id, count, difficulty) |
| `generate_quiz` | Generate a multiple-choice quiz from a document |
| `generate_practice_test` | Generate a mixed-format practice test from a document |
| `generate_summary` | Generate an audio-friendly summary of a document |
| `study_flashcards` | Interactive flashcard session with FSRS scheduling |
| `take_quiz` | Interactive quiz session with scoring |
| `explain_concept` | Explain a concept using the Feynman technique |
| `review_progress` | Review overall study progress, achievements, and recommendations |

## CLI Commands

The CLI uses `python -m study_guide` as the entry point.

### Ingest

```bash
# Ingest a directory of learning materials
python -m study_guide ingest ./my_materials
```

Supported formats: `.pptx`, `.pdf`, `.txt`, `.md`, `.mp4`, `.mov`, `.webm`

### List

```bash
python -m study_guide list documents     # All ingested documents
python -m study_guide list chunks --doc 1  # Chunks for a document
python -m study_guide list sets          # All generated study sets
```

### Generate

```bash
python -m study_guide generate flashcards --doc 1 --count 20
python -m study_guide generate quiz --doc 1 --count 10
python -m study_guide generate test --doc 1 --count 15
python -m study_guide generate summary --doc 1 --points 7
```

### Export

```bash
python -m study_guide export 1 --format json
python -m study_guide export 1 --format anki
python -m study_guide export 1 --format markdown
```

### Status

```bash
python -m study_guide status
```

## Configuration

Environment variables (set in `.env`, see `env.example.txt`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required for CLI, not for MCP) | -- |
| `STUDY_GUIDE_DB_PATH` | SQLite database file path | `./data/study_guide.db` |
| `STUDY_GUIDE_EXPORT_DIR` | Export output directory | `./data/exports` |
| `STUDY_GUIDE_GENERATION_MODEL` | OpenAI model for CLI generation | `gpt-4o` |
| `STUDY_GUIDE_TRANSCRIPTION_MODEL` | Model for audio transcription | `whisper-1` |
| `STUDY_GUIDE_MAX_CHUNKS_PER_GENERATION` | Max chunks per API call (cost control) | `5` |
| `STUDY_GUIDE_MAX_TOKENS_PER_RESPONSE` | Max tokens per response | `4000` |
| `STUDY_GUIDE_AUDIO_CHUNK_SIZE_MB` | Audio chunk size for processing | `20` |

## Development

```bash
pip install -e ".[dev]"
pytest -v --tb=short
ruff check .
mypy study_guide/
```

Or using Make:

```bash
make install    # Install dependencies
make test       # Run tests
make lint       # Run linter
make format     # Format code
```

## Project Structure

```
Code/
├── mcp_server/                    # MCP server (FastMCP)
│   ├── __init__.py
│   ├── __main__.py                # Entry point: python -m mcp_server
│   └── server.py                  # 10 tools, 9 resources, 8 prompts
├── study_guide/                   # Core Python library
│   ├── __init__.py
│   ├── __main__.py                # CLI entry point: python -m study_guide
│   ├── cli.py                     # Click CLI commands
│   ├── config.py                  # Configuration management
│   ├── database/
│   │   ├── models.py              # SQLAlchemy 2.0 models
│   │   ├── schema.py              # DB initialization, session context
│   │   └── operations.py          # CRUD operations
│   ├── ingestion/
│   │   ├── scanner.py             # File discovery
│   │   ├── chunker.py             # Text chunking
│   │   └── extractors/
│   │       ├── base.py            # Base extractor interface
│   │       ├── pdf_extractor.py   # PDF extraction
│   │       ├── pptx_extractor.py  # PowerPoint extraction
│   │       ├── text_extractor.py  # TXT/MD extraction
│   │       └── video_extractor.py # Video/audio transcription
│   ├── generation/
│   │   ├── generator.py           # OpenAI generation (CLI)
│   │   ├── prompts.py             # Generation prompt templates
│   │   └── schemas.py             # Pydantic v2 output schemas
│   ├── export/
│   │   ├── base.py                # Base exporter interface
│   │   ├── json_export.py         # JSON export
│   │   ├── anki_export.py         # Anki CSV export
│   │   └── markdown_export.py     # Markdown export
│   ├── learning/
│   │   ├── scheduler.py           # FSRS v5 spaced repetition algorithm
│   │   ├── gamification.py        # SDT phases, achievements, streaks
│   │   └── models.py              # CardReview, UserProgress models
│   └── utils/
│       └── audio.py               # FFmpeg audio utilities
├── tests/
│   ├── conftest.py                # Pytest fixtures
│   ├── test_chunking.py
│   ├── test_database.py
│   ├── test_export.py
│   ├── test_extraction.py
│   ├── test_gamification.py
│   ├── test_generation.py
│   ├── test_integration.py
│   ├── test_learning_models.py
│   ├── test_mcp_server.py
│   └── test_scheduler.py
├── data/                          # SQLite database and exports
├── pyproject.toml
├── Makefile
├── env.example.txt
└── LICENSE
```

## How FSRS Works

FSRS (Free Spaced Repetition Scheduler) v5 models memory with a power-law forgetting curve: `R = (1 + t / (9 * S))^(-1)`, where R is retrievability, t is elapsed days, and S is stability. After each review, the user rates 1 (Again), 2 (Hard), 3 (Good), or 4 (Easy). The algorithm updates two per-card parameters -- stability (how slowly a memory decays) and difficulty (how hard the card is to learn) -- then schedules the next review at the point where retrievability would drop to 90%. A topic is considered mastered when all cards maintain >90% retrievability at >30-day intervals with >85% accuracy and Bloom Level 3+ understanding.

## License

MIT
