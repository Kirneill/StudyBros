"""Document CRUD routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import ChunkResponse, DocumentResponse
from study_guide.database.models import Document
from study_guide.database.operations import DatabaseOperations

router = APIRouter()


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
