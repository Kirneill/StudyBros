"""
Tests for the StudyBros FastAPI REST API.

Overrides the module-level DB singletons in study_guide.database.schema so
every request operates on a fresh in-memory SQLite database.

Uses StaticPool + check_same_thread=False to ensure the in-memory DB is
shared across threads (TestClient runs handlers in a worker thread).
"""

import io
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import study_guide.database.schema as db_schema
from api.main import app
from study_guide.config import config
from study_guide.database.models import Base
from study_guide.database.operations import DatabaseOperations
from study_guide.database.schema import get_session_ctx
from study_guide.generation.generator import GenerationResult, StudyMaterialGenerator
from study_guide.generation.schemas import FlashcardSet

# Import learning models so their tables register on Base.metadata
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
    """Swap the module-level DB singletons to an in-memory SQLite engine.

    Uses StaticPool so all threads share the same in-memory database.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    original_engine = db_schema._engine
    original_session = db_schema._SessionLocal

    db_schema._engine = engine
    db_schema._SessionLocal = session_factory

    yield

    db_schema._engine = original_engine
    db_schema._SessionLocal = original_session


@pytest.fixture()
def client():
    """Create a TestClient bound to the test DB (runs after setup_test_db)."""
    return TestClient(app, raise_server_exceptions=True)


def _seed_document():
    """Create source + document + chunks + flashcard study set.

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
        ops.create_chunks_batch(doc.id, [
            "Python is a programming language.",
            "SQL is used for databases.",
        ])
        study_set = ops.create_study_set(
            set_type="flashcards",
            content={
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
            },
            document_id=doc.id,
            title="Test Flashcards",
            model_used="test",
        )
        return doc.id, study_set.id


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


def test_list_documents_empty(client):
    response = client.get("/api/documents/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_documents_with_data(client):
    doc_id, _ = _seed_document()
    response = client.get("/api/documents/")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) >= 1
    assert any(d["id"] == doc_id for d in docs)


def test_get_document(client):
    doc_id, _ = _seed_document()
    response = client.get(f"/api/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
    assert data["title"] == "Test Doc"


def test_get_document_not_found(client):
    response = client.get("/api/documents/99999")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_rename_document(client):
    doc_id, _ = _seed_document()
    response = client.patch(
        f"/api/documents/{doc_id}",
        json={"title": "Renamed Document"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == doc_id
    assert data["title"] == "Renamed Document"


def test_get_document_chunks(client):
    doc_id, _ = _seed_document()
    response = client.get(f"/api/documents/{doc_id}/chunks")
    assert response.status_code == 200
    chunks = response.json()
    assert len(chunks) == 2
    assert chunks[0]["chunk_index"] == 0
    assert chunks[1]["chunk_index"] == 1


def test_delete_document(client):
    doc_id, _ = _seed_document()
    # Delete
    response = client.delete(f"/api/documents/{doc_id}")
    assert response.status_code == 200
    # Verify gone
    response = client.get(f"/api/documents/{doc_id}")
    assert response.status_code == 404


def test_bulk_delete_documents(client):
    first_doc_id, _ = _seed_document()
    second_doc_id, _ = _seed_document()

    response = client.post(
        "/api/documents/bulk-delete",
        json={"document_ids": [first_doc_id, second_doc_id]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["deleted_documents"] == 2

    first_check = client.get(f"/api/documents/{first_doc_id}")
    second_check = client.get(f"/api/documents/{second_doc_id}")
    assert first_check.status_code == 404
    assert second_check.status_code == 404


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------


def test_upload_text_file(client):
    content = b"This is test content for upload."
    response = client.post(
        "/api/upload/",
        files={"file": ("test_upload.txt", io.BytesIO(content), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] is not None
    assert data["id"] is not None


def test_upload_text_file_without_trailing_slash(client):
    content = b"This is test content for upload without redirect."
    response = client.post(
        "/api/upload",
        files={"file": ("test_upload.txt", io.BytesIO(content), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] is not None
    assert data["id"] is not None


def test_upload_invalid_pdf_returns_diagnostic(client):
    content = b"This is not a valid PDF file."
    response = client.post(
        "/api/upload/",
        files={"file": ("broken.pdf", io.BytesIO(content), "application/pdf")},
    )
    assert response.status_code == 422
    assert 'Upload failed during extract for "broken.pdf"' in response.json()["detail"]


# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------


def test_get_generation_providers(client, monkeypatch):
    monkeypatch.setattr(type(config), "OPENAI_API_KEY", "")
    monkeypatch.setattr(type(config), "ANTHROPIC_API_KEY", "anthropic-test")
    monkeypatch.setattr(type(config), "OPENROUTER_API_KEY", "")

    response = client.get("/api/generate/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    providers = {entry["provider"]: entry for entry in data["providers"]}
    assert providers["openai"]["has_server_key"] is False
    assert providers["anthropic"]["has_server_key"] is True
    assert providers["openrouter"]["has_server_key"] is False


def test_generate_flashcards_with_custom_provider_key(client, monkeypatch):
    doc_id, _ = _seed_document()

    def fake_generate_from_chunks(
        self: StudyMaterialGenerator,
        chunks: list[str],
        generation_type: str,
        count: int = 10,
    ) -> GenerationResult:
        assert self.provider == "anthropic"
        assert self.api_key == "claude-test-key"
        assert generation_type == "flashcards"
        assert count == 5
        return GenerationResult(
            content=FlashcardSet.model_validate({
                "cards": [
                    {
                        "question": "What is Python?",
                        "answer": "A programming language",
                        "tags": ["cs"],
                        "difficulty": "easy",
                    }
                ]
            }),
            success=True,
            tokens_used=123,
            model="claude-test-model",
        )

    monkeypatch.setattr(StudyMaterialGenerator, "generate_from_chunks", fake_generate_from_chunks)

    response = client.post(
        "/api/generate/flashcards",
        json={
            "document_id": doc_id,
            "count": 5,
            "difficulty": "mixed",
            "provider": "anthropic",
            "api_key": "claude-test-key",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["item_count"] == 1
    assert data["set_type"] == "flashcards"


def test_generate_flashcards_requires_provider_key(client, monkeypatch):
    doc_id, _ = _seed_document()
    monkeypatch.setattr(type(config), "OPENAI_API_KEY", "")

    response = client.post(
        "/api/generate/flashcards",
        json={
            "document_id": doc_id,
            "count": 5,
            "difficulty": "mixed",
            "provider": "openai",
        },
    )
    assert response.status_code == 503
    assert "API key not configured" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Study Sets
# ---------------------------------------------------------------------------


def test_list_study_sets_empty(client):
    response = client.get("/api/study-sets/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_study_sets_with_data(client):
    _, study_set_id = _seed_document()
    response = client.get("/api/study-sets/")
    assert response.status_code == 200
    sets = response.json()
    assert len(sets) >= 1
    assert any(s["id"] == study_set_id for s in sets)


def test_get_study_set(client):
    _, study_set_id = _seed_document()
    response = client.get(f"/api/study-sets/{study_set_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == study_set_id
    assert "content" in data
    assert "cards" in data["content"]


def test_get_study_set_not_found(client):
    response = client.get("/api/study-sets/99999")
    assert response.status_code == 404
    assert "detail" in response.json()


def test_delete_study_set(client):
    _, study_set_id = _seed_document()
    response = client.delete(f"/api/study-sets/{study_set_id}")
    assert response.status_code == 200
    # Verify gone
    response = client.get(f"/api/study-sets/{study_set_id}")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Study / FSRS
# ---------------------------------------------------------------------------


def test_record_review(client):
    _, study_set_id = _seed_document()
    response = client.post(
        f"/api/study/{study_set_id}/review",
        json={"card_index": 0, "rating": 3},
    )
    assert response.status_code == 200
    data = response.json()
    assert "stability" in data
    assert "difficulty" in data
    assert "retrievability" in data
    assert "state" in data
    assert "scheduled_days" in data
    assert "next_review" in data


def test_record_review_creates_progress(client):
    _, study_set_id = _seed_document()

    review_response = client.post(
        f"/api/study/{study_set_id}/review",
        json={"card_index": 0, "rating": 3, "confidence": 4},
    )
    assert review_response.status_code == 200

    progress_response = client.get("/api/study/progress")
    assert progress_response.status_code == 200
    data = progress_response.json()
    assert len(data) >= 1
    assert any(entry["topic"] == "cs" for entry in data)
    matching = next(entry for entry in data if entry["topic"] == "cs")
    assert matching["total_reviews"] == 1
    assert matching["mastery_level"] > 0


def test_get_progress_backfills_existing_reviews(client):
    _, study_set_id = _seed_document()

    with get_session_ctx() as session:
        review = CardReview(
            card_id=0,
            study_set_id=study_set_id,
            rating=3,
            elapsed_days=0.0,
            scheduled_days=2.0,
            stability=1.5,
            difficulty=4.5,
            retrievability=0.9,
            state="learning",
            reviewed_at=datetime.utcnow(),
            confidence_rating=4,
        )
        session.add(review)
        session.commit()

    progress_response = client.get("/api/study/progress")
    assert progress_response.status_code == 200
    data = progress_response.json()
    assert any(entry["topic"] == "cs" for entry in data)


def test_record_review_invalid_rating(client):
    _, study_set_id = _seed_document()
    response = client.post(
        f"/api/study/{study_set_id}/review",
        json={"card_index": 0, "rating": 5},
    )
    assert response.status_code == 422


def test_record_review_study_set_not_found(client):
    response = client.post(
        "/api/study/99999/review",
        json={"card_index": 0, "rating": 3},
    )
    assert response.status_code == 404


def test_get_due_cards_empty(client):
    _, study_set_id = _seed_document()
    response = client.get(f"/api/study/{study_set_id}/due")
    assert response.status_code == 200
    assert response.json() == []


def test_get_due_cards_with_old_reviews(client):
    """Insert a CardReview with old reviewed_at and low stability so the card is due."""
    _, study_set_id = _seed_document()

    with get_session_ctx() as session:
        old_date = datetime.utcnow() - timedelta(days=60)
        review = CardReview(
            card_id=0,
            study_set_id=study_set_id,
            rating=3,
            elapsed_days=0.0,
            scheduled_days=1.0,
            stability=0.5,      # low stability => fast decay
            difficulty=5.0,
            retrievability=1.0,
            state="review",
            reviewed_at=old_date,
        )
        session.add(review)
        session.commit()

    response = client.get(f"/api/study/{study_set_id}/due")
    assert response.status_code == 200
    due = response.json()
    assert len(due) >= 1
    assert due[0]["card_id"] == 0


def test_get_schedule_empty(client):
    _, study_set_id = _seed_document()
    response = client.get(f"/api/study/{study_set_id}/schedule")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "study_set_id": study_set_id,
        "due_count": 0,
        "total_reviewed": 0,
        "cards": [],
    }


def test_get_schedule_with_reviews(client):
    _, study_set_id = _seed_document()

    with get_session_ctx() as session:
        old_date = datetime.utcnow() - timedelta(days=7)
        review = CardReview(
            card_id=0,
            study_set_id=study_set_id,
            rating=3,
            elapsed_days=0.0,
            scheduled_days=3.0,
            stability=2.5,
            difficulty=5.0,
            retrievability=1.0,
            state="review",
            reviewed_at=old_date,
        )
        session.add(review)
        session.commit()

    response = client.get(f"/api/study/{study_set_id}/schedule")
    assert response.status_code == 200
    data = response.json()
    assert data["study_set_id"] == study_set_id
    assert data["due_count"] == 1
    assert data["total_reviewed"] == 1
    assert len(data["cards"]) == 1
    assert set(data["cards"][0]) == {
        "card_id",
        "retrievability",
        "stability",
        "difficulty",
        "state",
        "last_review",
        "scheduled_days",
    }


def test_complete_study_session(client):
    _, study_set_id = _seed_document()

    response = client.post(
        f"/api/study/{study_set_id}/session",
        json={
            "total_items": 2,
            "correct_count": 1,
            "confidence_sum": 7,
            "bloom_level_distribution": {"1": 2},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 2
    assert data["correct_count"] == 1
    assert data["accuracy"] == 0.5

    phase_response = client.get("/api/gamification/phase")
    assert phase_response.status_code == 200
    assert phase_response.json()["total_sessions"] == 1

    consistency_response = client.get("/api/gamification/consistency")
    assert consistency_response.status_code == 200
    assert len(consistency_response.json()["studied_dates"]) == 1


def test_check_mastery(client):
    response = client.post("/api/study/mastery/nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert data["mastered"] is False


def test_get_progress_empty(client):
    response = client.get("/api/study/progress")
    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# Gamification
# ---------------------------------------------------------------------------


def test_get_phase(client):
    response = client.get("/api/gamification/phase")
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {
        "phase",
        "phase_name",
        "total_sessions",
        "avg_accuracy_30d",
    }


def test_get_achievements_empty(client):
    response = client.get("/api/gamification/achievements")
    assert response.status_code == 200
    assert response.json() == []


def test_get_strengths_weaknesses(client):
    response = client.get("/api/gamification/strengths-weaknesses")
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {
        "strengths",
        "weaknesses",
        "recommendations",
        "calibration",
    }


def test_get_consistency(client):
    response = client.get("/api/gamification/consistency")
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {
        "streak_days",
        "consistency_pct_30d",
        "studied_dates",
    }
    assert isinstance(data["streak_days"], int)
    assert isinstance(data["consistency_pct_30d"], float)
    assert isinstance(data["studied_dates"], list)


def test_complete_topic(client):
    response = client.post("/api/gamification/complete/nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert "completed" in data


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def test_export_json(client):
    _, study_set_id = _seed_document()
    response = client.get(f"/api/export/{study_set_id}?format=json")
    assert response.status_code == 200


def test_export_not_found(client):
    response = client.get("/api/export/99999?format=json")
    assert response.status_code == 404


def test_export_invalid_format(client):
    _, study_set_id = _seed_document()
    response = client.get(f"/api/export/{study_set_id}?format=bogus")
    assert response.status_code == 400
