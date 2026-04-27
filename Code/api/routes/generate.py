"""AI generation routes with provider-aware API key support."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import GenerateRequest, GenerationProvidersResponse, StudySetDetailResponse
from study_guide.config import config
from study_guide.database.operations import DatabaseOperations
from study_guide.generation.generator import StudyMaterialGenerator

router = APIRouter()

PROVIDER_DISPLAY_NAMES = {
    "openai": "OpenAI",
    "anthropic": "Claude",
    "openrouter": "OpenRouter",
}


def _require_provider_key(provider: str, request_key: str | None) -> None:
    """Raise 503 if neither the request nor the server provides a provider key."""
    if request_key:
        return
    if not config.has_provider_api_key(provider):
        provider_label = PROVIDER_DISPLAY_NAMES[provider]
        raise HTTPException(
            status_code=503,
            detail=(
                f"{provider_label} API key not configured on the server. "
                "Provide one in the form or configure it in the server environment."
            ),
        )


@router.get("/providers", response_model=GenerationProvidersResponse)
def get_generation_providers():
    """Return generation providers and whether the server has keys for them."""
    providers = []
    for provider, label in PROVIDER_DISPLAY_NAMES.items():
        providers.append({
            "provider": provider,
            "display_name": label,
            "has_server_key": config.has_provider_api_key(provider),
            "default_model": config.get_generation_model(provider),
        })
    return {"providers": providers}


def _generate_and_store(
    db: Session,
    request: GenerateRequest,
    gen_type: str,
) -> StudySetDetailResponse:
    """Shared logic: load content, generate, store, return."""
    request_key = request.api_key.strip() if request.api_key else None
    _require_provider_key(request.provider, request_key)

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

    generator = StudyMaterialGenerator(
        provider=request.provider,
        api_key=request_key,
        model=request.model,
    )
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
        raise HTTPException(
            status_code=result.status_code,
            detail=f"Generation failed: {result.error}",
        )
    if result.content is None:
        raise HTTPException(status_code=502, detail="Generation failed: empty response content")

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
