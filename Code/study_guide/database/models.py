"""
SQLAlchemy models for the Study Guide database.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Source(Base):
    """Represents an ingested source file."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    filepath: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)  # pptx, pdf, txt, md, video, audio
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # SHA-256 for dedup
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processing, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Source(id={self.id}, filename='{self.filename}', status='{self.status}')>"


class Document(Base):
    """Represents extracted content from a source file."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id"), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    source: Mapped["Source"] = relationship("Source", back_populates="documents")
    chunks: Mapped[list["Chunk"]] = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    study_sets: Mapped[list["StudySet"]] = relationship("StudySet", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title='{self.title}', words={self.word_count})>"


class Chunk(Base):
    """Represents a chunk of text from a document for generation."""

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    char_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<Chunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index}, chars={self.char_count})>"


class StudySet(Base):
    """Represents a generated study set (flashcards, quiz, or practice test)."""

    __tablename__ = "study_sets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("documents.id"), nullable=True)
    set_type: Mapped[str] = mapped_column(String(50), nullable=False)  # flashcards, quiz, practice_test
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON blob of generated content
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    model_used: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    document: Mapped[Optional["Document"]] = relationship("Document", back_populates="study_sets")

    def __repr__(self) -> str:
        return f"<StudySet(id={self.id}, type='{self.set_type}', items={self.item_count})>"
