"""Document CRUD routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import (
    ChunkResponse,
    DocumentBulkDeleteRequest,
    DocumentResponse,
    DocumentUpdateRequest,
)
from study_guide.database.models import Document
from study_guide.database.operations import DatabaseOperations

router = APIRouter()


@router.get("", response_model=list[DocumentResponse])
@router.get("/", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """List all documents."""
    ops = DatabaseOperations(db)
    docs = ops.get_all_documents()
    return [
        DocumentResponse(
            id=d.id,
            title=d.title,
            word_count=d.word_count,
            chunk_count=len(d.chunks),
            created_at=d.created_at,
        )
        for d in docs
    ]


@router.patch("/{document_id}", response_model=DocumentResponse)
def update_document(document_id: int, request: DocumentUpdateRequest, db: Session = Depends(get_db)):
    """Rename a document."""
    ops = DatabaseOperations(db)
    title = request.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Document title cannot be empty")

    doc = ops.update_document_title(document_id, title)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")

    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        word_count=doc.word_count,
        chunk_count=len(doc.chunks),
        created_at=doc.created_at,
    )


@router.post("/bulk-delete")
def bulk_delete_documents(request: DocumentBulkDeleteRequest, db: Session = Depends(get_db)):
    """Delete multiple documents and their associated sources."""
    docs = (
        db.query(Document)
        .filter(Document.id.in_(request.document_ids))
        .all()
    )
    if not docs:
        raise HTTPException(status_code=404, detail="No matching documents found")

    ops = DatabaseOperations(db)
    source_ids = sorted({doc.source_id for doc in docs})
    deleted_count = 0
    for source_id in source_ids:
        if ops.delete_source(source_id):
            deleted_count += 1

    return {
        "detail": f"Deleted {len(docs)} document(s)",
        "deleted_documents": len(docs),
        "deleted_sources": deleted_count,
    }


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a single document by ID."""
    ops = DatabaseOperations(db)
    doc = ops.get_document(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        word_count=doc.word_count,
        chunk_count=len(doc.chunks),
        created_at=doc.created_at,
    )


@router.get("/{document_id}/chunks", response_model=list[ChunkResponse])
def get_document_chunks(document_id: int, db: Session = Depends(get_db)):
    """Get all chunks for a document."""
    ops = DatabaseOperations(db)
    doc = ops.get_document(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    chunks = ops.get_chunks_for_document(document_id)
    return [
        ChunkResponse(
            chunk_index=c.chunk_index,
            content=c.content,
            char_count=c.char_count,
        )
        for c in chunks
    ]


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """Delete a document and all associated data (cascades through source)."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found")
    source_id = doc.source_id
    ops = DatabaseOperations(db)
    ops.delete_source(source_id)
    return {"detail": f"Document {document_id} and associated data deleted"}
