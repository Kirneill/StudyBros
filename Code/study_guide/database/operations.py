"""
Database CRUD operations.
"""

import json
from typing import Optional, cast

from sqlalchemy.orm import Session

from study_guide.database.models import Chunk, Document, Source, StudySet


class DatabaseOperations:
    """Database operations handler."""

    def __init__(self, session: Session):
        self.session = session

    # --- Source operations ---

    def create_source(
        self,
        filename: str,
        filepath: str,
        file_type: str,
        file_hash: Optional[str] = None,
        file_size: Optional[int] = None,
    ) -> Source:
        """Create a new source record."""
        source = Source(
            filename=filename,
            filepath=filepath,
            file_type=file_type,
            file_hash=file_hash,
            file_size=file_size,
            status="pending",
        )
        self.session.add(source)
        self.session.commit()
        return source

    def get_source(self, source_id: int) -> Optional[Source]:
        """Get a source by ID."""
        return self.session.query(Source).filter(Source.id == source_id).first()

    def get_source_by_hash(self, file_hash: str) -> Optional[Source]:
        """Get a source by file hash (for deduplication)."""
        return self.session.query(Source).filter(Source.file_hash == file_hash).first()

    def get_all_sources(self) -> list[Source]:
        """Get all sources."""
        return self.session.query(Source).order_by(Source.created_at.desc()).all()

    def update_source_status(
        self,
        source_id: int,
        status: str,
        error_message: Optional[str] = None,
    ) -> Optional[Source]:
        """Update the status of a source."""
        source = self.get_source(source_id)
        if source:
            source.status = status
            if error_message:
                source.error_message = error_message
            self.session.commit()
        return source

    def delete_source(self, source_id: int) -> bool:
        """Delete a source and all related data."""
        source = self.get_source(source_id)
        if source:
            self.session.delete(source)
            self.session.commit()
            return True
        return False

    # --- Document operations ---

    def create_document(
        self,
        source_id: int,
        raw_text: str,
        title: Optional[str] = None,
    ) -> Document:
        """Create a new document record."""
        word_count = len(raw_text.split())
        document = Document(
            source_id=source_id,
            title=title,
            raw_text=raw_text,
            word_count=word_count,
        )
        self.session.add(document)
        self.session.commit()
        return document

    def get_document(self, document_id: int) -> Optional[Document]:
        """Get a document by ID."""
        return self.session.query(Document).filter(Document.id == document_id).first()

    def get_all_documents(self) -> list[Document]:
        """Get all documents."""
        return self.session.query(Document).order_by(Document.created_at.desc()).all()

    def get_documents_for_source(self, source_id: int) -> list[Document]:
        """Get all documents for a source."""
        return self.session.query(Document).filter(Document.source_id == source_id).all()

    # --- Chunk operations ---

    def create_chunk(
        self,
        document_id: int,
        chunk_index: int,
        content: str,
    ) -> Chunk:
        """Create a new chunk record."""
        chunk = Chunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            char_count=len(content),
        )
        self.session.add(chunk)
        self.session.commit()
        return chunk

    def create_chunks_batch(
        self,
        document_id: int,
        chunks: list[str],
    ) -> list[Chunk]:
        """Create multiple chunks in a single transaction."""
        chunk_records = []
        for index, content in enumerate(chunks):
            chunk = Chunk(
                document_id=document_id,
                chunk_index=index,
                content=content,
                char_count=len(content),
            )
            self.session.add(chunk)
            chunk_records.append(chunk)
        self.session.commit()
        return chunk_records

    def get_chunks_for_document(self, document_id: int) -> list[Chunk]:
        """Get all chunks for a document, ordered by index."""
        return (
            self.session.query(Chunk)
            .filter(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index)
            .all()
        )

    def get_chunk(self, chunk_id: int) -> Optional[Chunk]:
        """Get a chunk by ID."""
        return self.session.query(Chunk).filter(Chunk.id == chunk_id).first()

    # --- Study Set operations ---

    def create_study_set(
        self,
        set_type: str,
        content: dict | list,
        document_id: Optional[int] = None,
        title: Optional[str] = None,
        model_used: Optional[str] = None,
        tokens_used: Optional[int] = None,
    ) -> StudySet:
        """Create a new study set record."""
        content_json = json.dumps(content)

        # Calculate item count based on set type
        if isinstance(content, dict):
            if "cards" in content:
                item_count = len(content["cards"])
            elif "questions" in content:
                item_count = len(content["questions"])
            elif "key_concepts" in content:
                # Audio summary - count concepts + main points
                item_count = len(content.get("key_concepts", [])) + len(content.get("main_points", []))
            elif "main_points" in content:
                item_count = len(content["main_points"])
            else:
                item_count = 1
        elif isinstance(content, list):
            item_count = len(content)
        else:
            item_count = 1

        study_set = StudySet(
            document_id=document_id,
            set_type=set_type,
            title=title,
            content_json=content_json,
            item_count=item_count,
            model_used=model_used,
            tokens_used=tokens_used,
        )
        self.session.add(study_set)
        self.session.commit()
        return study_set

    def get_study_set(self, set_id: int) -> Optional[StudySet]:
        """Get a study set by ID."""
        return self.session.query(StudySet).filter(StudySet.id == set_id).first()

    def get_all_study_sets(self) -> list[StudySet]:
        """Get all study sets."""
        return self.session.query(StudySet).order_by(StudySet.created_at.desc()).all()

    def get_study_sets_for_document(self, document_id: int) -> list[StudySet]:
        """Get all study sets for a document."""
        return (
            self.session.query(StudySet)
            .filter(StudySet.document_id == document_id)
            .order_by(StudySet.created_at.desc())
            .all()
        )

    def get_study_set_content(self, set_id: int) -> Optional[dict | list]:
        """Get the parsed content of a study set."""
        study_set = self.get_study_set(set_id)
        if study_set:
            return cast(dict | list, json.loads(study_set.content_json))
        return None

    def delete_study_set(self, set_id: int) -> bool:
        """Delete a study set."""
        study_set = self.get_study_set(set_id)
        if study_set:
            self.session.delete(study_set)
            self.session.commit()
            return True
        return False

    # --- Stats operations ---

    def get_stats(self) -> dict:
        """Get database statistics."""
        return {
            "sources": self.session.query(Source).count(),
            "documents": self.session.query(Document).count(),
            "chunks": self.session.query(Chunk).count(),
            "study_sets": self.session.query(StudySet).count(),
            "sources_by_status": {
                "pending": self.session.query(Source).filter(Source.status == "pending").count(),
                "processing": self.session.query(Source).filter(Source.status == "processing").count(),
                "completed": self.session.query(Source).filter(Source.status == "completed").count(),
                "failed": self.session.query(Source).filter(Source.status == "failed").count(),
            },
            "study_sets_by_type": {
                "flashcards": self.session.query(StudySet).filter(StudySet.set_type == "flashcards").count(),
                "quiz": self.session.query(StudySet).filter(StudySet.set_type == "quiz").count(),
                "practice_test": self.session.query(StudySet).filter(StudySet.set_type == "practice_test").count(),
                "audio_summary": self.session.query(StudySet).filter(StudySet.set_type == "audio_summary").count(),
            },
        }
