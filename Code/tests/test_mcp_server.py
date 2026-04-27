"""
Tests for the StudyBros MCP server tools, resources, and prompts.

Overrides the module-level DB singletons in study_guide.database.schema so
every handler operates on a fresh in-memory SQLite database.
"""

import json
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import study_guide.database.schema as db_schema

# --- MCP server functions under test ---
from mcp_server.server import (
    _json,
    _load_chunks_text,
    check_mastery,
    delete_document,
    delete_study_set,
    explain_concept,
    generate_flashcards,
    generate_practice_test,
    generate_quiz,
    generate_summary,
    get_document_chunks,
    get_due_cards,
    get_progress,
    get_progress_sw,
    get_status,
    get_strengths_weaknesses,
    list_achievements,
    list_documents,
    list_study_sets,
    record_review,
    review_progress,
    store_study_set,
    study_flashcards,
    take_quiz,
)
from mcp_server.server import get_study_set as get_study_set_resource
from study_guide.database.models import Base
from study_guide.database.operations import DatabaseOperations
from study_guide.database.schema import get_session_ctx

# Import learning models BEFORE Base.metadata.create_all so their tables
# register on Base.metadata.
from study_guide.learning.models import (  # noqa: F401
    Achievement,
    CardReview,
    GamificationState,
    StudySession,
    UserProgress,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def setup_test_db():
    """Swap the module-level DB singletons to an in-memory SQLite engine."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    original_engine = db_schema._engine
    original_session = db_schema._SessionLocal

    db_schema._engine = engine
    db_schema._SessionLocal = session_factory

    yield

    db_schema._engine = original_engine
    db_schema._SessionLocal = original_session


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seed_document():
    """Seed a source + document + chunks + flashcard study set.

    Returns (doc_id, study_set_id).
    """
    with get_session_ctx() as session:
        ops = DatabaseOperations(session)
        source = ops.create_source(
            filename="test.txt",
            filepath="/tmp/test.txt",
            file_type="txt",
            file_hash="abc123",
            file_size=100,
        )
        doc = ops.create_document(
            source_id=source.id,
            raw_text="Python is a programming language. SQL is used for databases.",
            title="Test Doc",
        )
        ops.create_chunks_batch(
            doc.id,
            [
                "Python is a programming language.",
                "SQL is used for databases.",
            ],
        )

        flashcard_content = {
            "cards": [
                {
                    "question": "What is Python?",
                    "answer": "A programming language",
                    "tags": ["cs"],
                    "difficulty": "easy",
                },
                {
                    "question": "What is SQL?",
                    "answer": "Structured Query Language",
                    "tags": ["db"],
                    "difficulty": "medium",
                },
            ]
        }
        study_set = ops.create_study_set(
            set_type="flashcards",
            content=flashcard_content,
            document_id=doc.id,
            title="Test Flashcards",
            model_used="test",
        )
        return doc.id, study_set.id


# Valid content payloads --------------------------------------------------

VALID_FLASHCARD_JSON = json.dumps({
    "cards": [
        {
            "question": "What is Python?",
            "answer": "A programming language",
            "tags": ["cs"],
            "difficulty": "easy",
        },
        {
            "question": "What is SQL?",
            "answer": "Structured Query Language",
            "tags": ["db"],
            "difficulty": "medium",
        },
    ]
})

VALID_QUIZ_JSON = json.dumps({
    "questions": [
        {
            "prompt": "What is 2+2?",
            "options": [
                {"label": "A", "text": "3"},
                {"label": "B", "text": "4"},
            ],
            "correct_index": 1,
            "explanation": "Basic math",
        }
    ]
})


# ===========================================================================
# Tool tests
# ===========================================================================


class TestStoreStudySet:

    def test_store_study_set_valid_flashcards(self):
        doc_id, _ = _seed_document()
        result = store_study_set(
            document_id=doc_id,
            set_type="flashcards",
            title="My Flashcards",
            content_json=VALID_FLASHCARD_JSON,
        )
        assert "Stored" in result
        assert "flashcards" in result

    def test_store_study_set_invalid_type(self):
        doc_id, _ = _seed_document()
        result = store_study_set(
            document_id=doc_id,
            set_type="bogus",
            title="Bad Type",
            content_json=VALID_FLASHCARD_JSON,
        )
        assert "Error" in result
        assert "Invalid set_type" in result

    def test_store_study_set_invalid_json(self):
        doc_id, _ = _seed_document()
        result = store_study_set(
            document_id=doc_id,
            set_type="flashcards",
            title="Bad JSON",
            content_json="not json",
        )
        assert "Invalid JSON" in result

    def test_store_study_set_validation_failure(self):
        doc_id, _ = _seed_document()
        # Valid JSON but missing required 'cards' field for flashcards
        bad_schema = json.dumps({"wrong_key": []})
        result = store_study_set(
            document_id=doc_id,
            set_type="flashcards",
            title="Bad Schema",
            content_json=bad_schema,
        )
        assert "Validation failed" in result


class TestRecordReview:

    def test_record_review_creates_card_review(self):
        _, study_set_id = _seed_document()
        result = record_review(
            study_set_id=study_set_id,
            card_index=0,
            rating=3,
        )
        assert "Rated" in result
        assert "Next review" in result

    def test_record_review_invalid_rating(self):
        _, study_set_id = _seed_document()
        result = record_review(
            study_set_id=study_set_id,
            card_index=0,
            rating=5,
        )
        assert "rating must be 1-4" in result

    def test_record_review_invalid_rating_zero(self):
        _, study_set_id = _seed_document()
        result = record_review(
            study_set_id=study_set_id,
            card_index=0,
            rating=0,
        )
        assert "rating must be 1-4" in result

    def test_record_review_builds_history(self):
        """Second review for the same card should use history (no error)."""
        _, study_set_id = _seed_document()
        first = record_review(
            study_set_id=study_set_id,
            card_index=0,
            rating=3,
        )
        assert "Rated" in first

        second = record_review(
            study_set_id=study_set_id,
            card_index=0,
            rating=4,
        )
        assert "Rated" in second
        assert "Next review" in second


class TestGetDueCards:

    def test_get_due_cards_empty(self):
        """No reviews exist, so due_count should be 0."""
        _, study_set_id = _seed_document()
        result = get_due_cards(study_set_id=study_set_id)
        data = json.loads(result)
        assert data["due_count"] == 0
        assert data["cards"] == []

    def test_get_due_cards_with_reviews(self):
        """Cards reviewed long ago should show as due."""
        _, study_set_id = _seed_document()
        # Create a review that happened 100 days ago with low stability
        with get_session_ctx() as session:
            old_review = CardReview(
                card_id=0,
                study_set_id=study_set_id,
                rating=3,
                elapsed_days=0.0,
                scheduled_days=1.0,
                stability=0.5,
                difficulty=5.0,
                retrievability=1.0,
                state="review",
                reviewed_at=datetime.utcnow() - timedelta(days=100),
            )
            session.add(old_review)
            session.commit()

        result = get_due_cards(study_set_id=study_set_id)
        data = json.loads(result)
        assert data["due_count"] >= 1
        assert data["cards"][0]["card_id"] == 0


class TestDeleteStudySet:

    def test_delete_study_set_exists(self):
        _, study_set_id = _seed_document()
        result = delete_study_set(study_set_id=study_set_id)
        assert f"Deleted study set {study_set_id}" in result

    def test_delete_study_set_not_found(self):
        result = delete_study_set(study_set_id=99999)
        assert "Error" in result
        assert "not found" in result


class TestDeleteDocument:

    def test_delete_document_exists(self):
        doc_id, _ = _seed_document()
        result = delete_document(document_id=doc_id)
        assert f"Deleted document {doc_id}" in result

    def test_delete_document_not_found(self):
        result = delete_document(document_id=99999)
        assert "Error" in result
        assert "not found" in result


class TestCheckMastery:

    def test_check_mastery_no_progress(self):
        """Topic with no UserProgress returns mastered=False."""
        result = check_mastery(topic="nonexistent")
        data = json.loads(result)
        assert data["mastery"]["mastered"] is False


class TestGetStrengthsWeaknesses:

    def test_get_strengths_weaknesses_empty(self):
        """With no data, should return valid JSON without error."""
        result = get_strengths_weaknesses()
        assert not result.startswith("Error")
        data = json.loads(result)
        assert isinstance(data, dict)


# ===========================================================================
# Resource tests
# ===========================================================================


class TestResources:

    def test_resource_status(self):
        result = get_status()
        data = json.loads(result)
        assert "version" in data
        assert data["version"] == "0.1.0"
        assert "stats" in data

    def test_resource_list_documents(self):
        _seed_document()
        result = list_documents()
        data = json.loads(result)
        assert len(data) >= 1
        assert data[0]["title"] == "Test Doc"

    def test_resource_get_document_chunks(self):
        doc_id, _ = _seed_document()
        result = get_document_chunks(doc_id=str(doc_id))
        data = json.loads(result)
        assert len(data) == 2
        assert data[0]["content"] == "Python is a programming language."
        assert data[1]["content"] == "SQL is used for databases."

    def test_resource_list_study_sets(self):
        _seed_document()
        result = list_study_sets()
        data = json.loads(result)
        assert len(data) >= 1
        assert data[0]["type"] == "flashcards"

    def test_resource_get_study_set(self):
        _, study_set_id = _seed_document()
        result = get_study_set_resource(set_id=str(study_set_id))
        data = json.loads(result)
        assert data["id"] == study_set_id
        assert data["type"] == "flashcards"
        assert "content" in data

    def test_resource_get_study_set_not_found(self):
        result = get_study_set_resource(set_id="99999")
        data = json.loads(result)
        assert "error" in data

    def test_resource_get_progress(self):
        result = get_progress()
        data = json.loads(result)
        assert "topics" in data
        assert "consistency" in data
        assert "phase" in data

    def test_resource_get_progress_sw(self):
        result = get_progress_sw()
        assert not result.startswith("Error")
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_resource_list_achievements(self):
        result = list_achievements()
        assert not result.startswith("Error")
        data = json.loads(result)
        assert isinstance(data, list)


# ===========================================================================
# Prompt tests
# ===========================================================================


class TestPrompts:

    def test_prompt_generate_flashcards(self):
        doc_id, _ = _seed_document()
        result = generate_flashcards(document_id=doc_id)
        assert "store_study_set" in result
        assert "flashcards" in result
        # Should contain the document content
        assert "Python" in result
        # Should contain the schema instructions
        assert "cards" in result

    def test_prompt_generate_flashcards_no_document(self):
        result = generate_flashcards(document_id=99999)
        assert "Error" in result

    def test_prompt_generate_quiz(self):
        doc_id, _ = _seed_document()
        result = generate_quiz(document_id=doc_id)
        assert "store_study_set" in result
        assert "quiz" in result
        assert "questions" in result

    def test_prompt_generate_practice_test(self):
        doc_id, _ = _seed_document()
        result = generate_practice_test(document_id=doc_id)
        assert "store_study_set" in result
        assert "practice_test" in result

    def test_prompt_generate_summary(self):
        doc_id, _ = _seed_document()
        result = generate_summary(document_id=doc_id)
        assert "store_study_set" in result
        assert "audio_summary" in result

    def test_prompt_study_flashcards(self):
        _, study_set_id = _seed_document()
        result = study_flashcards(study_set_id=study_set_id)
        assert "flashcard study session" in result
        assert "record_review" in result
        # Should contain card data
        assert "What is Python?" in result

    def test_prompt_study_flashcards_not_found(self):
        result = study_flashcards(study_set_id=99999)
        assert "Error" in result

    def test_prompt_take_quiz(self):
        """take_quiz requires a quiz study set, so create one."""
        doc_id, _ = _seed_document()
        # Store a quiz study set
        store_study_set(
            document_id=doc_id,
            set_type="quiz",
            title="Test Quiz",
            content_json=VALID_QUIZ_JSON,
        )
        # The quiz study set is the second one created (after flashcards)
        with get_session_ctx() as session:
            ops = DatabaseOperations(session)
            sets = ops.get_all_study_sets()
            quiz_set = [s for s in sets if s.set_type == "quiz"][0]

        result = take_quiz(study_set_id=quiz_set.id)
        assert "quiz session" in result
        assert "What is 2+2?" in result

    def test_prompt_explain_concept(self):
        doc_id, _ = _seed_document()
        result = explain_concept(document_id=doc_id, concept="Python")
        assert "Feynman" in result
        assert "Python" in result

    def test_prompt_review_progress(self):
        result = review_progress()
        assert "progress report" in result
        assert "achievements" in result


# ===========================================================================
# Helper tests
# ===========================================================================


class TestHelpers:

    def test_json_helper_handles_datetime(self):
        now = datetime.utcnow()
        result = _json({"ts": now, "value": 42})
        data = json.loads(result)
        assert data["value"] == 42
        # datetime was serialized to a string
        assert isinstance(data["ts"], str)

    def test_json_helper_handles_plain_dict(self):
        result = _json({"key": "value"})
        assert json.loads(result) == {"key": "value"}

    def test_load_chunks_text_returns_content(self):
        doc_id, _ = _seed_document()
        with get_session_ctx() as session:
            text = _load_chunks_text(session, doc_id)
        assert "Python is a programming language." in text
        assert "SQL is used for databases." in text

    def test_load_chunks_text_falls_back_to_raw_text(self):
        """When no chunks exist, _load_chunks_text returns raw_text."""
        with get_session_ctx() as session:
            ops = DatabaseOperations(session)
            source = ops.create_source(
                filename="bare.txt",
                filepath="/tmp/bare.txt",
                file_type="txt",
                file_hash="nochunks",
                file_size=50,
            )
            doc = ops.create_document(
                source_id=source.id,
                raw_text="Raw text fallback content.",
                title="No Chunks Doc",
            )
            # No chunks created
            text = _load_chunks_text(session, doc.id)
        assert text == "Raw text fallback content."

    def test_load_chunks_text_returns_empty_for_missing_doc(self):
        with get_session_ctx() as session:
            text = _load_chunks_text(session, 99999)
        assert text == ""
