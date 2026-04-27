# KSpider: AI Study Guide
Transform learning materials into structured study assets (flashcards, quizzes, practice tests) with minimal manual work. This README file is organized as follows:

    I.  Features
    II. Prerequisites
    III. Requirements 
    IV. Installation (HOW TO)
    V. Usage (COMMANDS)
    VI. Configuration (SET UP)
    VII. Development
    VIII. Directory Structure
    IX. Phase Roadmap
    X. License

## I. Features
- **Multi-format Ingestion**: Process PPTX, PDF, TXT, MD files and video/audio content
- **AI-Powered Generation**: Create flashcards, quizzes, and practice tests using OpenAI
- **Multiple Export Formats**: JSON, Anki CSV, and Markdown
- **SQLite Storage**: Simple, portable database for all content
- **Cost Guardrails**: Built-in limits to control API usage

## II. Prerequisites
- Python 3.11+
- FFmpeg (for video/audio processing). How install is below
- OpenAI API key. Personal key
## III. Requirements
### Core dependencies
click>=8.1.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
rich>=13.0.0
### Document extraction
python-pptx>=0.6.21
pypdf>=3.0.0

### AI/Generation
openai>=1.0.0

### Audio/Video processing
ffmpeg-python>=0.2.0

### Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
ruff>=0.1.0
mypy>=1.0.0


## IV. Installation
1.  FFmpeg installation

    **Windows:**
    ```bash
    # Using winget
    winget install FFmpeg

    # Or download from https://ffmpeg.org/download.html
    ```

    **macOS:**
    ```bash
    brew install ffmpeg
    ```

    **Linux:**
    ```bash
    sudo apt install ffmpeg  # Debian/Ubuntu
    sudo dnf install ffmpeg  # Fedora
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3. Install dependencies:
    ```bash
    make install
    # or
    pip install -r requirements.txt
    ```

    4. Set up environment variables:
    ```bash
    cp .env.example .env
    # Edit .env and add your OpenAI API key
    ```

5. Initialize the database:
    ```bash
    python -m study_guide init
    ```

## V. Usage

### Ingest Files
Process a directory of learning materials:

```bash
python -m study_guide ingest ./my_materials
```

Supported formats: `.pptx`, `.pdf`, `.txt`, `.md`, `.mp4`, `.mov`, `.webm`

### List Content
```bash
# List all ingested documents
python -m study_guide list documents

# List chunks for a document
python -m study_guide list chunks --doc 1

# List generated study sets
python -m study_guide list sets
```

### Generate Study Materials
```bash
# Generate flashcards from a document
python -m study_guide generate flashcards --doc 1 --count 20

# Generate a quiz
python -m study_guide generate quiz --doc 1 --count 10

# Generate a practice test
python -m study_guide generate test --doc 1 --count 15

# Generate an audio-friendly summary
python -m study_guide generate summary --doc 1 --points 7
```

### Export
```bash
# Export to JSON
python -m study_guide export 1 --format json

# Export flashcards to Anki CSV
python -m study_guide export 1 --format anki

# Export quiz to Markdown
python -m study_guide export 1 --format markdown
```

### Check Status
```bash
python -m study_guide status
```
## VI. Configuration

SETTINGS YOU CAN CHANGE (.env file):

  OPENAI_API_KEY                         ← Required
  STUDY_GUIDE_GENERATION_MODEL=gpt-4o    ← Model to use
  STUDY_GUIDE_MAX_CHUNKS_PER_GENERATION  ← Limit chunks (cost control)
  STUDY_GUIDE_MAX_TOKENS_PER_RESPONSE    ← Limit response size

Environment variables (set in `.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required)!!! | - |
| `STUDY_GUIDE_DB_PATH` | Database file path | `./data/study_guide.db` |
| `STUDY_GUIDE_EXPORT_DIR` | Export directory | `./data/exports` |
| `STUDY_GUIDE_MAX_CHUNKS_PER_GENERATION` | Max chunks per API call | `5` |
| `STUDY_GUIDE_MAX_TOKENS_PER_RESPONSE` | Max tokens per response | `4000` |
| `STUDY_GUIDE_GENERATION_MODEL` | GPT model for generation | `gpt-4o` |

## VII. Development

```bash
# Install dev dependencies
make dev

# Run tests
make test

# Run linter
make lint

# Format code
make format
```
COST NOTES

  - Each generation call uses OpenAI API credits
  - Default limits prevent runaway costs
  - Flashcards: ~$0.02-0.05 per set of 20
  - Quiz: ~$0.02-0.05 per 10 questions
  - Monitor usage at: https://platform.openai.com/usage

## VIII. Directory Structure

```

study_guide/
├── __init__.py
├── __main__.py                 # CLI entry point
├── cli.py                      # Click CLI commands
├── config.py                   # Configuration management
├── database/
│   ├── __init__.py
│   ├── models.py               # SQLAlchemy models
│   ├── schema.py               # DB initialization
│   └── operations.py           # CRUD operations
├── ingestion/
│   ├── __init__.py
│   ├── scanner.py              # File discovery
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── base.py             # Base extractor interface
│   │   ├── pptx_extractor.py   # PowerPoint extraction
│   │   ├── pdf_extractor.py    # PDF extraction
│   │   ├── text_extractor.py   # TXT/MD extraction
│   │   └── video_extractor.py  # Video → audio → transcript
│   └── chunker.py              # Text chunking logic
├── generation/
│   ├── __init__.py
│   ├── schemas.py              # Pydantic schemas for structured outputs
│   ├── prompts.py              # Generation prompts
│   └── generator.py            # OpenAI generation logic
├── export/
│   ├── __init__.py
│   ├── json_export.py          # JSON export
│   ├── anki_export.py          # Anki CSV export
│   └── markdown_export.py      # Markdown export
└── utils/
    ├── __init__.py
    └── audio.py                # FFmpeg audio utilities

tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures
├── test_data/                  # Golden test inputs
│   ├── sample.pptx
│   ├── sample.pdf
│   └── sample.txt
├── test_extraction.py
├── test_chunking.py
├── test_generation.py
└── test_export.py

data/                           # Default data directory
├── study_guide.db              # SQLite database
└── exports/                    # Export output directory

.env.example
.gitignore
Makefile
README.md
pyproject.toml
                 # Database and exports
```

## IX Phase Roadmap
- **Phase 1 (Current)**: CLI-based MVP with file ingestion, generation, and export
- **Phase 2**: Next.js web UI for upload, browse, generate, and export
- **Phase 3**: YouTube links, scheduling, spaced repetition, analytics, multi-user auth

## X. License

MIT
