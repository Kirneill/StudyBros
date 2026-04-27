"""File upload route."""

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import DocumentResponse
from study_guide.config import config
from study_guide.database.operations import DatabaseOperations
from study_guide.ingestion.chunker import TextChunker
from study_guide.ingestion.extractors import get_extractor
from study_guide.ingestion.scanner import FileScanner

router = APIRouter()

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB

upload_logger = logging.getLogger("studybros.upload")
if not upload_logger.handlers:
    config.ensure_directories()
    handler = logging.FileHandler(config.LOG_DIR / "upload_diagnostics.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    upload_logger.addHandler(handler)
upload_logger.setLevel(logging.INFO)
upload_logger.propagate = True


def _diagnostic_detail(stage: str, filename: str, message: str) -> str:
    """Build a client-visible diagnostic message."""
    return f'Upload failed during {stage} for "{filename}": {message}'


@router.post("", response_model=DocumentResponse)
@router.post("/", response_model=DocumentResponse)
def upload_file(file: UploadFile, db: Session = Depends(get_db)):
    """Upload a file, ingest it, and return the created document."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    suffix = Path(file.filename).suffix.lower()
    if not suffix:
        raise HTTPException(status_code=400, detail="File has no extension")

    stage = "save"
    tmp_path: Path | None = None
    source_id: int | None = None

    # Save to temp file with size guard
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = file.file.read()
            if len(contents) > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="File exceeds 50 MB limit")
            tmp.write(contents)
            tmp_path = Path(tmp.name)
    except HTTPException:
        raise
    except Exception as exc:
        upload_logger.exception('stage=%s filename="%s" suffix="%s"', stage, file.filename, suffix)
        raise HTTPException(
            status_code=500,
            detail=_diagnostic_detail(stage, file.filename, str(exc)),
        ) from exc

    try:
        stage = "scan"
        scanner = FileScanner()
        scanned = scanner.scan_file(tmp_path)
        if scanned is None:
            raise HTTPException(
                status_code=400,
                detail=_diagnostic_detail(stage, file.filename, f"Unsupported file type '{suffix}'"),
            )

        stage = "select extractor"
        extractor = get_extractor(tmp_path)
        if extractor is None:
            raise HTTPException(
                status_code=400,
                detail=_diagnostic_detail(
                    stage,
                    file.filename,
                    f"No extractor available for '{suffix}'",
                ),
            )

        stage = "hash"
        scanned.compute_hash()

        stage = "extract"
        result = extractor.extract(tmp_path)
        if not result.success:
            error_message = result.error or "Unknown extraction failure"
            upload_logger.warning(
                'stage=%s filename="%s" suffix="%s" error="%s"',
                stage,
                file.filename,
                suffix,
                error_message,
            )
            raise HTTPException(
                status_code=422,
                detail=_diagnostic_detail(stage, file.filename, error_message),
            )

        # Deduplicate
        stage = "deduplicate"
        ops = DatabaseOperations(db)
        existing = ops.get_source_by_hash(scanned.hash)
        if existing:
            # Return the existing document instead of creating a duplicate
            docs = ops.get_documents_for_source(existing.id)
            if docs:
                doc = docs[0]
                return DocumentResponse(
                    id=doc.id,
                    title=doc.title,
                    word_count=doc.word_count,
                    chunk_count=len(doc.chunks),
                    created_at=doc.created_at,
                )
            raise HTTPException(
                status_code=409,
                detail=_diagnostic_detail(
                    stage,
                    file.filename,
                    f"File already ingested (source ID {existing.id}) but document missing",
                ),
            )

        # Create source, document, chunks
        stage = "persist source"
        source = ops.create_source(
            filename=scanned.filename,
            filepath=str(tmp_path),
            file_type=scanned.file_type,
            file_hash=scanned.hash,
            file_size=scanned.size,
        )
        source_id = source.id
        ops.update_source_status(source.id, "processing")

        stage = "persist document"
        doc = ops.create_document(
            source_id=source.id,
            raw_text=result.text,
            title=result.title or Path(file.filename).stem,
        )

        stage = "chunk"
        chunker = TextChunker()
        chunk_result = chunker.chunk_text(result.text)
        ops.create_chunks_batch(doc.id, chunk_result.chunks)

        ops.update_source_status(source.id, "completed")

        return DocumentResponse(
            id=doc.id,
            title=doc.title,
            word_count=doc.word_count,
            chunk_count=chunk_result.chunk_count,
            created_at=doc.created_at,
        )
    except HTTPException as exc:
        if source_id is not None:
            ops = DatabaseOperations(db)
            ops.update_source_status(source_id, "failed", exc.detail)
        raise
    except Exception as exc:
        upload_logger.exception(
            'stage=%s filename="%s" suffix="%s" source_id=%s',
            stage,
            file.filename,
            suffix,
            source_id,
        )
        if source_id is not None:
            ops = DatabaseOperations(db)
            ops.update_source_status(
                source_id,
                "failed",
                _diagnostic_detail(stage, file.filename, str(exc)),
            )
        raise HTTPException(
            status_code=500,
            detail=_diagnostic_detail(stage, file.filename, str(exc)),
        ) from exc
    finally:
        # Clean up temp file
        try:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
