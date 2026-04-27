# KSpider Code Review Results

> Full code review of the existing CLI codebase. Issues must be fixed before building MCP/frontend layers.

---

## Verdict: APPROVE WITH SUGGESTIONS

~1900 LOC backend, ~1200 LOC tests. Well-structured Python CLI with clean separation of concerns.

---

## Strengths

- Clean 4-layer architecture: `ingestion/`, `generation/`, `export/`, `database/`
- Modern Python: SQLAlchemy 2.0 Mapped columns, Pydantic v2, Click, type hints throughout
- OpenAI Structured Outputs for guaranteed schema compliance
- Cost guardrails (configurable max chunks/tokens per generation)
- File deduplication via SHA-256 hashing
- Strategy pattern for chunking (smart vs fixed)
- Factory pattern for extractors and exporters
- Comprehensive test fixtures in conftest.py

---

## Critical Issues

### 1. No `.gitignore` — API keys at risk
No `.gitignore` exists anywhere in the repo. If a `.env` file with an OpenAI API key is created, it will be committed.

**Fix:** Create `.gitignore` covering `.env`, `*.db`, `__pycache__/`, `node_modules/`, `.next/`

### 2. `study_guide.db` committed to repo
Binary SQLite file `Code/data/study_guide.db` is tracked in git. Contains local state, causes merge conflicts.

**Fix:** `git rm --cached Code/data/study_guide.db`

---

## Major Issues

### 3. Session management leaks (cli.py)
Every CLI command does `session = get_session()` then `session.close()` at the end. If an exception occurs between, session leaks.

**Files:** `cli.py` lines 103-126, 156-234, 257-284, 288-323, 329-360, 410-456, 469-507, 510-537

**Fix:** Add context manager to `schema.py`:
```python
@contextmanager
def get_session_ctx():
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
```

### 4. `list_chunks` queries DB twice (cli.py:300-305)
Line 302 fetches `ops.get_chunks_for_document(doc_id)[:limit]`, then line 305 calls the same method again just for `len()`.

**Fix:** `all_chunks = ops.get_chunks_for_document(doc_id)` — query once, slice for display.

### 5. `QuizQuestion.correct_index` no upper bound (schemas.py:54)
Has `ge=0` but no validation that `correct_index < len(options)`. LLM could return index 5 for a 4-option question.

**Fix:** Add `@model_validator(mode='after')` checking `correct_index < len(options)`.

### 6. No tests for `StudyMaterialGenerator` (test_generation.py)
Tests only validate Pydantic schemas. Zero tests for the actual OpenAI integration layer.

**Fix:** Add tests with mocked `openai.OpenAI` client.

### 7. `Makefile` references nonexistent `requirements.txt` (line 20)
`make install` runs `pip install -r requirements.txt` but no such file exists.

**Fix:** Change to `pip install .`

### 8. Extension mismatch between scanner and extractors
- `Config.SUPPORTED_EXTENSIONS["document"]` = `.pptx`, `.pdf`, `.txt`, `.md`
- `TextExtractor.supported_extensions()` = `.txt`, `.md`, `.markdown`, `.text`
- `_EXTRACTORS` dict only maps `.txt` and `.md`

`.markdown` and `.text` files are supported by the extractor but not discovered by the scanner.

**Fix:** Add `.markdown` and `.text` to both `config.py` and `extractors/__init__.py`.

---

## Minor Issues

### 9. Unused import: `Inches` in pptx_extractor.py:8
### 10. Unused variable: `total_duration` in video_extractor.py:86
### 11. `get_stats()` fires 12 separate SQL queries (operations.py:241-260)
Could be a single `GROUP BY` query.

### 12. Emoji in markdown export contradicts Windows compatibility
`markdown_export.py:304` uses `"⭐"` but `cli.py:25-32` replaces Unicode with ASCII.

### 13. Export CLI doesn't expose all valid format aliases
`cli.py:461` restricts to `["json", "anki", "markdown"]` but `get_exporter` also accepts `csv`, `md`, `anki_csv`.

### 14. `update_source_status` doesn't clear error messages (operations.py:62-67)
When transitioning from "failed" to "completed", old error_message is preserved.

---

## Academic Quality Assessment

This is strong capstone work demonstrating:
1. End-to-end system design (ingestion → storage → generation → export)
2. Proper software engineering (interfaces, dependency injection, factory patterns)
3. Modern Python tooling (pyproject.toml, ruff, mypy, pytest)
4. Real-world API integration with cost awareness
5. Multiple output formats for practical utility

Gaps for academic scrutiny: (a) no generator-level tests, (b) missing .gitignore, (c) no CLI CliRunner tests.
