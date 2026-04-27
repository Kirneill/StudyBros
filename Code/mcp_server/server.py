"""
StudyBros MCP Server — tools, resources, and prompts for AI-powered study.

Registers 10 tools, 9 resources, and 8 prompts on a FastMCP instance.
All database access uses synchronous SQLAlchemy with SQLite; FastMCP
handles threading so every handler is a plain ``def``.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from fastmcp import FastMCP
from sqlalchemy import and_
from sqlalchemy import func as sa_func

from study_guide.config import config
from study_guide.database.models import Document
from study_guide.database.operations import DatabaseOperations
from study_guide.database.schema import get_session_ctx, init_db
from study_guide.export.base import get_exporter
from study_guide.generation.prompts import (
    SYSTEM_PROMPT,
    get_audio_summary_prompt,
    get_flashcard_prompt,
    get_practice_test_prompt,
    get_quiz_prompt,
)
from study_guide.generation.schemas import (
    AudioSummary,
    FlashcardSet,
    PracticeTest,
    Quiz,
)
from study_guide.ingestion.chunker import TextChunker
from study_guide.ingestion.extractors import get_extractor
from study_guide.ingestion.scanner import FileScanner
from study_guide.learning.gamification import (
    calculate_consistency_streak,
    check_topic_completion,
    detect_phase,
    get_achievements_earned,
)
from study_guide.learning.gamification import (
    get_strengths_weaknesses as _get_strengths_weaknesses,
)
from study_guide.learning.models import CardReview, UserProgress
from study_guide.learning.scheduler import (
    check_mastery as _check_mastery,
)
from study_guide.learning.scheduler import (
    get_due_cards as _get_due_cards,
)
from study_guide.learning.scheduler import (
    schedule_card,
)

mcp = FastMCP(
    "studybros",
    instructions=(
        "StudyBros: AI study guide platform. Ingest documents, generate "
        "flashcards/quizzes, study with FSRS spaced repetition, track mastery progress."
    ),
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SCHEMA_MAP: dict[str, type[FlashcardSet | Quiz | PracticeTest | AudioSummary]] = {
    "flashcards": FlashcardSet,
    "quiz": Quiz,
    "practice_test": PracticeTest,
    "audio_summary": AudioSummary,
}


def _json(obj: object) -> str:
    """Serialize *obj* to a JSON string, handling datetimes."""
    return json.dumps(obj, default=str, ensure_ascii=False)


def _load_chunks_text(session, document_id: int) -> str:
    """Return the concatenated chunk text for a document."""
    ops = DatabaseOperations(session)
    chunks = ops.get_chunks_for_document(document_id)
    if not chunks:
        doc = ops.get_document(document_id)
        if doc:
            return doc.raw_text
        return ""
    return "\n\n".join(c.content for c in chunks)


# ---------------------------------------------------------------------------
# Tools (10)
# ---------------------------------------------------------------------------


@mcp.tool()
def ingest_file(file_path: str) -> str:
    """Ingest a file (PDF, PPTX, TXT, MD, video, audio) into StudyBros.

    Extracts text, chunks it, and stores in the database for study material
    generation.  Returns a summary of what was ingested.
    """
    try:
        init_db()
        filepath = Path(file_path).resolve()
        if not filepath.exists():
            return f"Error: File not found: '{file_path}'"
        if not filepath.is_file():
            return f"Error: Not a file: '{file_path}'"

        scanner = FileScanner()
        scanned = scanner.scan_file(filepath)
        if scanned is None:
            return f"Error: Unsupported file type '{filepath.suffix}'"

        extractor = get_extractor(filepath)
        if extractor is None:
            return f"Error: No extractor available for '{filepath.suffix}'"

        scanned.compute_hash()

        with get_session_ctx() as session:
            ops = DatabaseOperations(session)

            # Deduplicate by hash
            existing = ops.get_source_by_hash(scanned.hash)
            if existing:
                return (
                    f"Skipped '{filepath.name}': already ingested "
                    f"(source ID {existing.id})"
                )

            source = ops.create_source(
                filename=scanned.filename,
                filepath=str(scanned.path),
                file_type=scanned.file_type,
                file_hash=scanned.hash,
                file_size=scanned.size,
            )
            ops.update_source_status(source.id, "processing")

            result = extractor.extract(filepath)
            if not result.success:
                ops.update_source_status(source.id, "failed", result.error)
                return f"Error extracting '{filepath.name}': {result.error}"

            doc = ops.create_document(
                source_id=source.id,
                raw_text=result.text,
                title=result.title or filepath.stem,
            )

            chunker = TextChunker()
            chunk_result = chunker.chunk_text(result.text)
            ops.create_chunks_batch(doc.id, chunk_result.chunks)

            ops.update_source_status(source.id, "completed")

            return (
                f"Ingested '{filepath.name}': {doc.word_count} words, "
                f"{chunk_result.chunk_count} chunks (doc ID {doc.id})"
            )
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def ingest_directory(directory_path: str, skip_existing: bool = True) -> str:
    """Ingest all supported files from a directory.

    Supported: PDF, PPTX, TXT, MD, video/audio files.
    Returns summary of processed/skipped/failed files.
    """
    try:
        init_db()
        scanner = FileScanner()
        files = scanner.scan_directory(directory_path)

        processed, skipped, failed = 0, 0, 0
        details: list[str] = []

        for scanned in files:
            scanned.compute_hash()

            with get_session_ctx() as session:
                ops = DatabaseOperations(session)

                if skip_existing:
                    existing = ops.get_source_by_hash(scanned.hash)
                    if existing:
                        skipped += 1
                        continue

            # Delegate to ingest_file for consistency
            result_msg = ingest_file(str(scanned.path))
            if result_msg.startswith("Error"):
                failed += 1
                details.append(f"  FAIL {scanned.filename}: {result_msg}")
            elif result_msg.startswith("Skipped"):
                skipped += 1
            else:
                processed += 1

        summary = f"Processed: {processed}, Skipped: {skipped}, Failed: {failed}"
        if details:
            summary += "\n" + "\n".join(details)
        return summary
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def store_study_set(
    document_id: int,
    set_type: str,
    title: str,
    content_json: str,
) -> str:
    """Store a generated study set (flashcards, quiz, practice_test, audio_summary).

    The LLM generates the content; this tool stores it.
    content_json must be a JSON string matching the study set schema for the
    given set_type.
    """
    try:
        init_db()
        schema_cls = _SCHEMA_MAP.get(set_type)
        if schema_cls is None:
            valid = ", ".join(_SCHEMA_MAP)
            return f"Error: Invalid set_type '{set_type}'. Must be one of: {valid}"

        # Parse and validate
        try:
            data = json.loads(content_json)
        except json.JSONDecodeError as exc:
            return f"Error: Invalid JSON — {exc}"

        try:
            schema_cls.model_validate(data)
        except Exception as exc:
            return f"Error: Validation failed for {set_type} — {exc}"

        with get_session_ctx() as session:
            ops = DatabaseOperations(session)
            study_set = ops.create_study_set(
                set_type=set_type,
                content=data,
                document_id=document_id,
                title=title,
                model_used="mcp-client",
            )
            return (
                f"Stored {set_type} '{title}' "
                f"(ID: {study_set.id}, {study_set.item_count} items)"
            )
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def record_review(
    study_set_id: int,
    card_index: int,
    rating: int,
    confidence: int = 0,
) -> str:
    """Record a flashcard review for FSRS spaced repetition.

    rating: 1=Again, 2=Hard, 3=Good, 4=Easy
    confidence: 1-5 self-reported confidence (0 to skip)
    Returns the scheduling result with next review date.
    """
    try:
        init_db()
        if rating < 1 or rating > 4:
            return "Error: rating must be 1-4"
        if confidence < 0 or confidence > 5:
            return "Error: confidence must be 0-5"

        now = datetime.utcnow()

        with get_session_ctx() as session:
            # Build history for this card
            history = (
                session.query(CardReview)
                .filter(
                    CardReview.study_set_id == study_set_id,
                    CardReview.card_id == card_index,
                )
                .order_by(CardReview.id)
                .all()
            )

            result = schedule_card(history if history else None, rating, now)

            elapsed = 0.0
            if history:
                elapsed = (now - history[-1].reviewed_at).total_seconds() / 86400.0
                elapsed = max(elapsed, 0.0)

            review = CardReview(
                card_id=card_index,
                study_set_id=study_set_id,
                rating=rating,
                elapsed_days=elapsed,
                scheduled_days=result["scheduled_days"],
                stability=result["stability"],
                difficulty=result["difficulty"],
                retrievability=result["retrievability"],
                state=result["state"],
                reviewed_at=now,
                confidence_rating=confidence if confidence > 0 else None,
            )
            session.add(review)
            session.commit()

            return (
                f"Rated {rating}. Next review: {result['next_review'].date()}. "
                f"Stability: {result['stability']:.1f}, State: {result['state']}"
            )
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def get_due_cards(study_set_id: int) -> str:
    """Get cards due for review in a study set, ordered by FSRS urgency.

    Returns cards sorted by lowest retrievability (most urgent first).
    """
    try:
        init_db()
        with get_session_ctx() as session:
            due = _get_due_cards(session, study_set_id)
            if not due:
                return _json({"due_count": 0, "cards": []})
            return _json({"due_count": len(due), "cards": due})
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def check_mastery(topic: str) -> str:
    """Check if a topic is mastered.

    Mastery requires:
    - All cards: retrievability >90% at >30-day intervals
    - Accuracy >85% over last 3 reviews
    - Demonstrated Bloom Level 3+ (Apply)

    Returns mastery status and detailed breakdown.
    """
    try:
        init_db()
        with get_session_ctx() as session:
            mastery = _check_mastery(session, topic)
            completion = check_topic_completion(session, topic)
            session.commit()
            return _json({
                "mastery": mastery,
                "completion": completion,
            })
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def get_strengths_weaknesses() -> str:
    """Analyze strengths and weaknesses across all studied topics.

    Returns strengths (>80% accuracy + Bloom 3+), weaknesses (<70% or Bloom <2),
    recommendations, and confidence calibration data.
    """
    try:
        init_db()
        with get_session_ctx() as session:
            result = _get_strengths_weaknesses(session)
            return _json(result)
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def export_study_set(study_set_id: int, format: str = "json") -> str:
    """Export a study set to a file.

    Formats: json, anki, markdown.
    Returns the file path of the exported file.
    """
    try:
        init_db()
        exporter = get_exporter(format)
        if exporter is None:
            return f"Error: Unsupported format '{format}'. Use json, anki, or markdown."

        with get_session_ctx() as session:
            ops = DatabaseOperations(session)
            study_set = ops.get_study_set(study_set_id)
            if study_set is None:
                return f"Error: Study set {study_set_id} not found"

            content = json.loads(study_set.content_json)
            config.ensure_directories()
            ext = exporter.get_file_extension()
            raw_title = study_set.title or f"study_set_{study_set_id}"
            safe_title = re.sub(r'[^\w\-]', '_', raw_title)
            output_path = config.EXPORT_DIR / f"{safe_title}{ext}"

            result = exporter.export(content, output_path, title=study_set.title)
            if result.success:
                return f"Exported to: {result.filepath}"
            return f"Error: {result.error}"
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def delete_document(document_id: int) -> str:
    """Delete a document and all its associated chunks and study sets.

    Cascades through Source -> Document -> Chunks, StudySets.
    """
    try:
        init_db()
        with get_session_ctx() as session:
            doc = session.query(Document).filter(Document.id == document_id).first()
            if doc is None:
                return f"Error: Document {document_id} not found"

            source_id = doc.source_id
            ops = DatabaseOperations(session)
            ops.delete_source(source_id)
            return f"Deleted document {document_id} and all associated data"
    except Exception as exc:
        return f"Error: {exc}"


@mcp.tool()
def delete_study_set(study_set_id: int) -> str:
    """Delete a study set and its review history."""
    try:
        init_db()
        with get_session_ctx() as session:
            # Delete associated card reviews first
            session.query(CardReview).filter(
                CardReview.study_set_id == study_set_id
            ).delete()

            ops = DatabaseOperations(session)
            deleted = ops.delete_study_set(study_set_id)
            if deleted:
                return f"Deleted study set {study_set_id}"
            return f"Error: Study set {study_set_id} not found"
    except Exception as exc:
        return f"Error: {exc}"


# ---------------------------------------------------------------------------
# Resources (9)
# ---------------------------------------------------------------------------


@mcp.resource("studybros://status")
def get_status() -> str:
    """StudyBros server status, configuration, and database statistics."""
    try:
        init_db()
        with get_session_ctx() as session:
            ops = DatabaseOperations(session)
            stats = ops.get_stats()
            return _json({
                "version": "0.1.0",
                "db_path": str(config.DB_PATH),
                "generation_provider": config.GENERATION_PROVIDER,
                "generation_model": config.get_generation_model(config.GENERATION_PROVIDER),
                "stats": stats,
            })
    except Exception as exc:
        return _json({"error": str(exc)})


@mcp.resource("studybros://documents")
def list_documents() -> str:
    """List all ingested documents with metadata."""
    try:
        init_db()
        with get_session_ctx() as session:
            ops = DatabaseOperations(session)
            docs = ops.get_all_documents()
            return _json([
                {
                    "id": d.id,
                    "title": d.title,
                    "word_count": d.word_count,
                    "chunk_count": len(d.chunks),
                    "created_at": d.created_at,
                }
                for d in docs
            ])
    except Exception as exc:
        return _json({"error": str(exc)})


@mcp.resource("studybros://documents/{doc_id}/chunks")
def get_document_chunks(doc_id: str) -> str:
    """Get all text chunks for a document.  Used by prompts for generation context."""
    try:
        init_db()
        with get_session_ctx() as session:
            ops = DatabaseOperations(session)
            chunks = ops.get_chunks_for_document(int(doc_id))
            if not chunks:
                return _json({"error": f"No chunks found for document {doc_id}"})
            return _json([
                {
                    "chunk_index": c.chunk_index,
                    "content": c.content,
                    "char_count": c.char_count,
                }
                for c in chunks
            ])
    except Exception as exc:
        return _json({"error": str(exc)})


@mcp.resource("studybros://study-sets")
def list_study_sets() -> str:
    """List all generated study sets."""
    try:
        init_db()
        with get_session_ctx() as session:
            ops = DatabaseOperations(session)
            sets = ops.get_all_study_sets()
            return _json([
                {
                    "id": s.id,
                    "type": s.set_type,
                    "title": s.title,
                    "item_count": s.item_count,
                    "document_id": s.document_id,
                    "created_at": s.created_at,
                }
                for s in sets
            ])
    except Exception as exc:
        return _json({"error": str(exc)})


@mcp.resource("studybros://study-sets/{set_id}")
def get_study_set(set_id: str) -> str:
    """Get a study set with its full content."""
    try:
        init_db()
        with get_session_ctx() as session:
            ops = DatabaseOperations(session)
            study_set = ops.get_study_set(int(set_id))
            if study_set is None:
                return _json({"error": f"Study set {set_id} not found"})
            content = json.loads(study_set.content_json)
            return _json({
                "id": study_set.id,
                "type": study_set.set_type,
                "title": study_set.title,
                "item_count": study_set.item_count,
                "document_id": study_set.document_id,
                "created_at": study_set.created_at,
                "content": content,
            })
    except Exception as exc:
        return _json({"error": str(exc)})


@mcp.resource("studybros://study-sets/{set_id}/schedule")
def get_study_set_schedule(set_id: str) -> str:
    """Get the FSRS review schedule for a study set.

    Shows due cards and predicted retention.
    """
    try:
        init_db()
        with get_session_ctx() as session:
            due = _get_due_cards(session, int(set_id))

            # Also gather all cards with current retrievability
            from study_guide.learning.scheduler import calculate_retrievability

            latest_sub = (
                session.query(
                    CardReview.card_id,
                    sa_func.max(CardReview.id).label("max_id"),
                )
                .filter(CardReview.study_set_id == int(set_id))
                .group_by(CardReview.card_id)
                .subquery()
            )
            latest_reviews = (
                session.query(CardReview)
                .join(
                    latest_sub,
                    and_(
                        CardReview.card_id == latest_sub.c.card_id,
                        CardReview.id == latest_sub.c.max_id,
                    ),
                )
                .all()
            )

            now = datetime.utcnow()
            all_cards = []
            for rev in latest_reviews:
                elapsed = max((now - rev.reviewed_at).total_seconds() / 86400.0, 0.0)
                r = calculate_retrievability(elapsed, rev.stability)
                all_cards.append({
                    "card_id": rev.card_id,
                    "retrievability": round(r, 4),
                    "stability": round(rev.stability, 2),
                    "state": rev.state,
                    "last_review": rev.reviewed_at,
                    "scheduled_days": rev.scheduled_days,
                })

            all_cards.sort(key=lambda c: c["retrievability"])

            return _json({
                "study_set_id": int(set_id),
                "due_count": len(due),
                "due_cards": due,
                "all_cards": all_cards,
            })
    except Exception as exc:
        return _json({"error": str(exc)})


@mcp.resource("studybros://progress")
def get_progress() -> str:
    """Knowledge heat map: per-topic mastery, Bloom levels, consistency, calibration."""
    try:
        init_db()
        with get_session_ctx() as session:
            all_progress = session.query(UserProgress).all()
            streak = calculate_consistency_streak(session)
            phase_info = detect_phase(session)
            session.commit()

            topics = [
                {
                    "topic": p.topic_tag,
                    "mastery_level": round(p.mastery_level, 3),
                    "bloom_highest_level": p.bloom_highest_level,
                    "total_reviews": p.total_reviews,
                    "last_reviewed_at": p.last_reviewed_at,
                    "calibration_score": round(p.calibration_score, 3),
                    "consistency_pct_30d": round(p.consistency_pct_30d, 1),
                }
                for p in all_progress
            ]

            return _json({
                "topics": topics,
                "consistency": streak,
                "phase": phase_info,
            })
    except Exception as exc:
        return _json({"error": str(exc)})


@mcp.resource("studybros://progress/strengths-weaknesses")
def get_progress_sw() -> str:
    """Detailed strengths, weaknesses, and study recommendations."""
    try:
        init_db()
        with get_session_ctx() as session:
            result = _get_strengths_weaknesses(session)
            return _json(result)
    except Exception as exc:
        return _json({"error": str(exc)})


@mcp.resource("studybros://achievements")
def list_achievements() -> str:
    """All earned competency achievements."""
    try:
        init_db()
        with get_session_ctx() as session:
            achievements = get_achievements_earned(session)
            return _json(achievements)
    except Exception as exc:
        return _json({"error": str(exc)})


# ---------------------------------------------------------------------------
# Prompts (8)
# ---------------------------------------------------------------------------

_FLASHCARD_SCHEMA = """\
Output JSON matching this schema:
{
  "cards": [
    {
      "question": "...",
      "answer": "...",
      "tags": ["topic1"],
      "difficulty": "easy" | "medium" | "hard"
    }
  ]
}"""

_QUIZ_SCHEMA = """\
Output JSON matching this schema:
{
  "questions": [
    {
      "prompt": "...",
      "options": [{"label": "A", "text": "..."}, ...],
      "correct_index": 0,
      "explanation": "..."
    }
  ]
}"""

_PRACTICE_TEST_SCHEMA = """\
Output JSON matching this schema:
{
  "title": "...",
  "questions": [
    {
      "question_type": "multiple_choice" | "short_answer" | "true_false",
      "prompt": "...",
      "options": [{"label": "A", "text": "..."}] | null,
      "correct_answer": "...",
      "explanation": "...",
      "points": 1
    }
  ],
  "total_points": <sum of points>
}"""

_AUDIO_SUMMARY_SCHEMA = """\
Output JSON matching this schema:
{
  "title": "...",
  "overview": "2-3 sentence overview",
  "key_concepts": [
    {"concept": "...", "explanation": "...", "importance": "essential"|"important"|"supplementary"}
  ],
  "main_points": ["point as a complete sentence", ...],
  "conclusion": "...",
  "estimated_read_time_seconds": 120
}"""


@mcp.prompt()
def generate_flashcards(
    document_id: int, count: int = 10, difficulty: str = "mixed"
) -> str:
    """Generate flashcards from a document.

    The LLM creates the cards; store them afterward with store_study_set.
    """
    init_db()
    with get_session_ctx() as session:
        content = _load_chunks_text(session, document_id)
        if not content:
            return f"Error: No content found for document {document_id}"

    prompt_text = get_flashcard_prompt(content, count)
    difficulty_note = ""
    if difficulty != "mixed":
        difficulty_note = f"\nTarget difficulty: {difficulty}.\n"

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"{prompt_text}\n"
        f"{difficulty_note}\n"
        f"{_FLASHCARD_SCHEMA}\n\n"
        f"After generating, call the store_study_set tool with:\n"
        f"  document_id={document_id}\n"
        f'  set_type="flashcards"\n'
        f"  title=<a descriptive title>\n"
        f"  content_json=<the JSON you produced>\n"
    )


@mcp.prompt()
def generate_quiz(document_id: int, count: int = 10) -> str:
    """Generate a multiple-choice quiz from a document."""
    init_db()
    with get_session_ctx() as session:
        content = _load_chunks_text(session, document_id)
        if not content:
            return f"Error: No content found for document {document_id}"

    prompt_text = get_quiz_prompt(content, count)

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"{prompt_text}\n\n"
        f"{_QUIZ_SCHEMA}\n\n"
        f"After generating, call the store_study_set tool with:\n"
        f"  document_id={document_id}\n"
        f'  set_type="quiz"\n'
        f"  title=<a descriptive title>\n"
        f"  content_json=<the JSON you produced>\n"
    )


@mcp.prompt()
def generate_practice_test(document_id: int, count: int = 15) -> str:
    """Generate a practice test with mixed question types from a document."""
    init_db()
    with get_session_ctx() as session:
        content = _load_chunks_text(session, document_id)
        if not content:
            return f"Error: No content found for document {document_id}"

    prompt_text = get_practice_test_prompt(content, count)

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"{prompt_text}\n\n"
        f"{_PRACTICE_TEST_SCHEMA}\n\n"
        f"After generating, call the store_study_set tool with:\n"
        f"  document_id={document_id}\n"
        f'  set_type="practice_test"\n'
        f"  title=<a descriptive title>\n"
        f"  content_json=<the JSON you produced>\n"
    )


@mcp.prompt()
def generate_summary(document_id: int) -> str:
    """Generate an audio-friendly summary of a document."""
    init_db()
    with get_session_ctx() as session:
        content = _load_chunks_text(session, document_id)
        if not content:
            return f"Error: No content found for document {document_id}"

    prompt_text = get_audio_summary_prompt(content)

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"{prompt_text}\n\n"
        f"{_AUDIO_SUMMARY_SCHEMA}\n\n"
        f"After generating, call the store_study_set tool with:\n"
        f"  document_id={document_id}\n"
        f'  set_type="audio_summary"\n'
        f"  title=<a descriptive title>\n"
        f"  content_json=<the JSON you produced>\n"
    )


@mcp.prompt()
def study_flashcards(study_set_id: int) -> str:
    """Interactive flashcard study session with FSRS scheduling.

    Instructions for the LLM to present cards, collect answers, and record reviews.
    """
    init_db()
    with get_session_ctx() as session:
        ops = DatabaseOperations(session)
        study_set = ops.get_study_set(study_set_id)
        if study_set is None:
            return f"Error: Study set {study_set_id} not found"

        content = json.loads(study_set.content_json)
        due = _get_due_cards(session, study_set_id)

    cards_json = _json(content.get("cards", []))
    due_json = _json(due)

    return (
        f"You are running an interactive flashcard study session.\n\n"
        f"Study set: {study_set.title} (ID: {study_set_id})\n"
        f"Total cards: {study_set.item_count}\n\n"
        f"Cards:\n{cards_json}\n\n"
        f"Due cards (most urgent first):\n{due_json}\n\n"
        f"Instructions:\n"
        f"1. Present due cards first (lowest retrievability). If none are due, "
        f"present all cards in order.\n"
        f"2. Show the question. Wait for the user to answer.\n"
        f"3. After they answer, show the correct answer and whether they were right.\n"
        f"4. Ask them to rate difficulty: Again(1) / Hard(2) / Good(3) / Easy(4)\n"
        f"5. Call the record_review tool with study_set_id={study_set_id}, "
        f"card_index=<index>, rating=<their rating>\n"
        f"6. Report the next review date from the tool response.\n"
        f"7. Move to the next card.\n"
        f"8. At the end, summarize the session: cards reviewed, accuracy, "
        f"and next recommended study time.\n"
    )


@mcp.prompt()
def take_quiz(study_set_id: int) -> str:
    """Interactive quiz session.  Present questions one at a time, score at the end."""
    init_db()
    with get_session_ctx() as session:
        ops = DatabaseOperations(session)
        study_set = ops.get_study_set(study_set_id)
        if study_set is None:
            return f"Error: Study set {study_set_id} not found"

        content = json.loads(study_set.content_json)

    questions_json = _json(content.get("questions", []))

    return (
        f"You are running an interactive quiz session.\n\n"
        f"Quiz: {study_set.title} (ID: {study_set_id})\n"
        f"Total questions: {len(content.get('questions', []))}\n\n"
        f"Questions:\n{questions_json}\n\n"
        f"Instructions:\n"
        f"1. Present one question at a time with its options.\n"
        f"2. Wait for the user to select an answer.\n"
        f"3. Tell them if they're correct or incorrect.\n"
        f"4. Show the explanation.\n"
        f"5. Track correct/incorrect counts.\n"
        f"6. After all questions, show the final score (e.g., 8/10 = 80%).\n"
        f"7. Highlight which questions they missed and suggest topics to review.\n"
    )


@mcp.prompt()
def explain_concept(document_id: int, concept: str) -> str:
    """Explain a concept using the Feynman technique.

    Load relevant chunks as context.
    """
    init_db()
    with get_session_ctx() as session:
        content = _load_chunks_text(session, document_id)
        if not content:
            return f"Error: No content found for document {document_id}"

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Using the following source material, explain the concept "
        f'"{concept}" as if teaching it to a beginner (Feynman technique).\n\n'
        f"Guidelines:\n"
        f"- Use simple language and analogies\n"
        f"- Break complex ideas into small, digestible pieces\n"
        f"- Give a concrete example\n"
        f"- Highlight common misconceptions\n"
        f"- End with a quick self-test question\n\n"
        f"Source material:\n\n{content}\n"
    )


@mcp.prompt()
def review_progress() -> str:
    """Review overall study progress.

    Shows strengths, weaknesses, recommendations, and achievements.
    """
    init_db()
    with get_session_ctx() as session:
        all_progress = session.query(UserProgress).all()
        sw = _get_strengths_weaknesses(session)
        achievements = get_achievements_earned(session)
        streak = calculate_consistency_streak(session)
        phase_info = detect_phase(session)
        session.commit()

    topics_summary = []
    for p in all_progress:
        topics_summary.append({
            "topic": p.topic_tag,
            "mastery": round(p.mastery_level, 3),
            "bloom_level": p.bloom_highest_level,
            "total_reviews": p.total_reviews,
        })

    data = _json({
        "topics": topics_summary,
        "strengths_weaknesses": sw,
        "achievements": achievements,
        "consistency": streak,
        "phase": phase_info,
    })

    return (
        f"You are presenting a study progress report to the user.\n\n"
        f"Data:\n{data}\n\n"
        f"Instructions:\n"
        f"1. Start with an encouraging but honest overview of their progress.\n"
        f"2. Show their current gamification phase and what it means.\n"
        f"3. List their strengths — topics they're doing well on.\n"
        f"4. List their weaknesses — topics that need work.\n"
        f"5. Present specific recommendations.\n"
        f"6. Show their consistency streak.\n"
        f"7. List achievements they've earned.\n"
        f"8. If calibration data shows over/under confidence, mention it.\n"
        f"9. End with a suggested next study action.\n"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    """Entry point for the MCP server."""
    mcp.run()
