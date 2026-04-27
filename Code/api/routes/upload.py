"""File upload route."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import DocumentResponse
from study_guide.database.operations import DatabaseOperations
from study_guide.ingestion.chunker import TextChunker
from study_guide.ingestion.extractors import get_extractor
from study_guide.ingestion.scanner import FileScanner

router = APIRouter()

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


@router.post("/", response_model=DocumentResponse)
def upload_file(file: UploadFile, db: Session = Depends(get_db)):
    """Upload a file, ingest it, and return the created document."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    suffix = Path(file.filename).suffix.lower()
    if not suffix:
        raise HTTPException(status_code=400, detail="File has no extension")

    # Save to temp file with size guard
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = file.file.read()
            if len(contents) > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="File exceeds 50 MB limit")
            tmp.write(contents)
            tmp_path = Path(tmp.name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {exc}")

    try:
        # Scan
        scanner = FileScanner()
        scanned = scanner.scan_file(tmp_path)
        if scanned is None:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{suffix}'",
            )

        # Extract
        extractor = get_extractor(tmp_path)
        if extractor is None:
            raise HTTPException(
                status_code=400,
                detail=f"No extractor available for '{suffix}'",
            )

        scanned.compute_hash()
        result = extractor.extract(tmp_path)
        if not result.success:
            raise HTTPException(status_code=422, detail=f"Extraction failed: {result.error}")

        # Deduplicate
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
                detail=f"File already ingested (source ID {existing.id}) but document missing",
            )

        # Create source, document, chunks
        source = ops.create_source(
            filename=scanned.filename,
            filepath=str(tmp_path),
            file_type=scanned.file_type,
            file_hash=scanned.hash,
            file_size=scanned.size,
        )
        ops.update_source_status(source.id, "processing")

        doc = ops.create_document(
            source_id=source.id,
            raw_text=result.text,
            title=result.title or Path(file.filename).stem,
        )

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
    finally:
        # Clean up temp file
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
