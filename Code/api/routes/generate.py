"""AI generation routes (requires OPENAI_API_KEY)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import GenerateRequest, StudySetDetailResponse
from study_guide.config import config
from study_guide.database.operations import DatabaseOperations
from study_guide.generation.generator import StudyMaterialGenerator

router = APIRouter()


def _require_openai_key():
    """Raise 503 if OpenAI API key is not configured."""
    if not config.OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Set OPENAI_API_KEY environment variable.",
        )


def _generate_and_store(
    db: Session,
    request: GenerateRequest,
    gen_type: str,
) -> StudySetDetailResponse:
    """Shared logic: load content, generate, store, return."""
    _require_openai_key()

    ops = DatabaseOperations(db)
    doc = ops.get_document(request.document_id)
    if doc is None:
        raise HTTPException(
            status_code=404,
            detail=f"Document {request.document_id} not found",
        )

    chunks = ops.get_chunks_for_document(request.document_id)
    chunk_texts = [c.content for c in chunks]

    if not chunk_texts:
        if not doc.raw_text or not doc.raw_text.strip():
            raise HTTPException(
                status_code=422,
                detail=f"Document {request.document_id} has no extractable content",
            )

    generator = StudyMaterialGenerator()
    if chunk_texts:
        result = generator.generate_from_chunks(chunk_texts, gen_type, count=request.count)
    else:
        if gen_type == "flashcards":
            result = generator.generate_flashcards(doc.raw_text, count=request.count)
        elif gen_type == "quiz":
            result = generator.generate_quiz(doc.raw_text, count=request.count)
        elif gen_type == "practice_test":
            result = generator.generate_practice_test(doc.raw_text, count=request.count)
        elif gen_type == "audio_summary":
            result = generator.generate_audio_summary(doc.raw_text, point_count=request.count)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown generation type: {gen_type}")

    if not result.success:
        raise HTTPException(status_code=502, detail=f"Generation failed: {result.error}")

    # Store the result
    content_data = result.content.model_dump()
    study_set = ops.create_study_set(
        set_type=gen_type,
        content=content_data,
        document_id=request.document_id,
        title=f"{gen_type.replace('_', ' ').title()} - {doc.title or 'Untitled'}",
        model_used=result.model,
        tokens_used=result.tokens_used,
    )

    return StudySetDetailResponse(
        id=study_set.id,
        set_type=study_set.set_type,
        title=study_set.title,
        item_count=study_set.item_count,
        document_id=study_set.document_id,
        created_at=study_set.created_at,
        content=content_data,
    )


@router.post("/flashcards", response_model=StudySetDetailResponse)
def generate_flashcards(request: GenerateRequest, db: Session = Depends(get_db)):
    """Generate flashcards from a document."""
    return _generate_and_store(db, request, "flashcards")


@router.post("/quiz", response_model=StudySetDetailResponse)
def generate_quiz(request: GenerateRequest, db: Session = Depends(get_db)):
    """Generate a multiple-choice quiz from a document."""
    return _generate_and_store(db, request, "quiz")


@router.post("/practice-test", response_model=StudySetDetailResponse)
def generate_practice_test(request: GenerateRequest, db: Session = Depends(get_db)):
    """Generate a practice test from a document."""
    return _generate_and_store(db, request, "practice_test")


@router.post("/summary", response_model=StudySetDetailResponse)
def generate_summary(request: GenerateRequest, db: Session = Depends(get_db)):
    """Generate an audio-friendly summary from a document."""
    return _generate_and_store(db, request, "audio_summary")
