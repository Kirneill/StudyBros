"""
Tests for database operations.
"""

import pytest

from study_guide.database.operations import DatabaseOperations


class TestSourceOperations:
    """Tests for Source CRUD operations."""

    def test_create_source(self, db_ops):
        """Test creating a source."""
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
            file_hash="abc123",
            file_size=1024,
        )

        assert source.id is not None
        assert source.filename == "test.txt"
        assert source.status == "pending"

    def test_get_source(self, db_ops):
        """Test getting a source by ID."""
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
        )

        retrieved = db_ops.get_source(source.id)
        assert retrieved is not None
        assert retrieved.id == source.id
        assert retrieved.filename == "test.txt"

    def test_get_source_by_hash(self, db_ops):
        """Test getting a source by file hash."""
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
            file_hash="unique_hash_123",
        )

        retrieved = db_ops.get_source_by_hash("unique_hash_123")
        assert retrieved is not None
        assert retrieved.id == source.id

    def test_update_source_status(self, db_ops):
        """Test updating source status."""
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
        )

        updated = db_ops.update_source_status(source.id, "completed")
        assert updated.status == "completed"

        # Test with error message
        updated = db_ops.update_source_status(source.id, "failed", "Test error")
        assert updated.status == "failed"
        assert updated.error_message == "Test error"

    def test_delete_source(self, db_ops):
        """Test deleting a source."""
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
        )

        result = db_ops.delete_source(source.id)
        assert result is True

        retrieved = db_ops.get_source(source.id)
        assert retrieved is None


class TestDocumentOperations:
    """Tests for Document CRUD operations."""

    def test_create_document(self, db_ops):
        """Test creating a document."""
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
        )

        document = db_ops.create_document(
            source_id=source.id,
            raw_text="This is test content with multiple words.",
            title="Test Document",
        )

        assert document.id is not None
        assert document.title == "Test Document"
        assert document.word_count == 7

    def test_get_all_documents(self, db_ops):
        """Test getting all documents."""
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
        )

        db_ops.create_document(source_id=source.id, raw_text="Doc 1", title="First")
        db_ops.create_document(source_id=source.id, raw_text="Doc 2", title="Second")

        documents = db_ops.get_all_documents()
        assert len(documents) == 2


class TestChunkOperations:
    """Tests for Chunk CRUD operations."""

    def test_create_chunk(self, db_ops):
        """Test creating a chunk."""
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
        )
        document = db_ops.create_document(
            source_id=source.id,
            raw_text="Full document text",
        )

        chunk = db_ops.create_chunk(
            document_id=document.id,
            chunk_index=0,
            content="First chunk content",
        )

        assert chunk.id is not None
        assert chunk.chunk_index == 0
        assert chunk.char_count == len("First chunk content")

    def test_create_chunks_batch(self, db_ops):
        """Test creating multiple chunks at once."""
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
        )
        document = db_ops.create_document(
            source_id=source.id,
            raw_text="Full document text",
        )

        chunks = db_ops.create_chunks_batch(
            document_id=document.id,
            chunks=["Chunk 1", "Chunk 2", "Chunk 3"],
        )

        assert len(chunks) == 3
        assert chunks[0].chunk_index == 0
        assert chunks[1].chunk_index == 1
        assert chunks[2].chunk_index == 2

    def test_get_chunks_for_document(self, db_ops):
        """Test getting chunks for a document."""
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
        )
        document = db_ops.create_document(
            source_id=source.id,
            raw_text="Full document text",
        )
        db_ops.create_chunks_batch(
            document_id=document.id,
            chunks=["A", "B", "C"],
        )

        chunks = db_ops.get_chunks_for_document(document.id)
        assert len(chunks) == 3
        # Should be ordered by index
        assert chunks[0].content == "A"
        assert chunks[2].content == "C"


class TestStudySetOperations:
    """Tests for StudySet CRUD operations."""

    def test_create_study_set(self, db_ops, sample_flashcards):
        """Test creating a study set."""
        study_set = db_ops.create_study_set(
            set_type="flashcards",
            content=sample_flashcards,
            title="Test Flashcards",
            model_used="gpt-4",
            tokens_used=500,
        )

        assert study_set.id is not None
        assert study_set.set_type == "flashcards"
        assert study_set.item_count == 2
        assert study_set.model_used == "gpt-4"

    def test_get_study_set_content(self, db_ops, sample_flashcards):
        """Test getting parsed study set content."""
        study_set = db_ops.create_study_set(
            set_type="flashcards",
            content=sample_flashcards,
        )

        content = db_ops.get_study_set_content(study_set.id)
        assert content is not None
        assert "cards" in content
        assert len(content["cards"]) == 2

    def test_get_study_sets_for_document(self, db_ops, sample_flashcards, sample_quiz):
        """Test getting study sets for a document."""
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
        )
        document = db_ops.create_document(
            source_id=source.id,
            raw_text="Content",
        )

        db_ops.create_study_set(
            set_type="flashcards",
            content=sample_flashcards,
            document_id=document.id,
        )
        db_ops.create_study_set(
            set_type="quiz",
            content=sample_quiz,
            document_id=document.id,
        )

        sets = db_ops.get_study_sets_for_document(document.id)
        assert len(sets) == 2


class TestStats:
    """Tests for statistics."""

    def test_get_stats(self, db_ops, sample_flashcards):
        """Test getting database statistics."""
        # Create some data
        source = db_ops.create_source(
            filename="test.txt",
            filepath="/path/to/test.txt",
            file_type="document",
        )
        db_ops.update_source_status(source.id, "completed")

        document = db_ops.create_document(
            source_id=source.id,
            raw_text="Content",
        )
        db_ops.create_chunks_batch(
            document_id=document.id,
            chunks=["Chunk 1", "Chunk 2"],
        )
        db_ops.create_study_set(
            set_type="flashcards",
            content=sample_flashcards,
        )

        stats = db_ops.get_stats()

        assert stats["sources"] == 1
        assert stats["documents"] == 1
        assert stats["chunks"] == 2
        assert stats["study_sets"] == 1
        assert stats["sources_by_status"]["completed"] == 1
        assert stats["study_sets_by_type"]["flashcards"] == 1
