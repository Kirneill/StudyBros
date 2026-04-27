"""
Integration tests for the full Study Guide workflow.

These tests verify the complete pipeline from ingestion to export,
without requiring actual API calls (mocked where needed).
"""


from study_guide.export import get_exporter
from study_guide.ingestion import FileScanner, TextChunker, TextExtractor


class TestIngestionToExportWorkflow:
    """Test the complete workflow from file ingestion to export."""

    def test_text_file_to_chunks(self, temp_dir, sample_text):
        """Test ingesting a text file and chunking it."""
        # Create a test file
        test_file = temp_dir / "test_doc.txt"
        test_file.write_text(sample_text)

        # Scan for file
        scanner = FileScanner()
        files = scanner.scan_directory(temp_dir)

        assert len(files) == 1
        assert files[0].filename == "test_doc.txt"
        assert files[0].file_type == "document"

        # Extract content
        extractor = TextExtractor()
        result = extractor.extract(test_file)

        assert result.success
        assert result.word_count > 0
        assert "Machine Learning" in result.text

        # Chunk the content
        chunker = TextChunker(chunk_size=500, min_chunk_size=50)
        chunk_result = chunker.chunk_text(result.text)

        assert chunk_result.chunk_count > 0
        assert chunk_result.total_chars > 0

    def test_database_workflow(self, db_ops, sample_text, sample_flashcards):
        """Test the database storage workflow."""
        # Create source
        source = db_ops.create_source(
            filename="lecture.txt",
            filepath="/path/to/lecture.txt",
            file_type="document",
            file_hash="test_hash_123",
        )

        assert source.status == "pending"

        # Update status
        db_ops.update_source_status(source.id, "processing")
        assert db_ops.get_source(source.id).status == "processing"

        # Create document
        document = db_ops.create_document(
            source_id=source.id,
            raw_text=sample_text,
            title="Machine Learning Lecture",
        )

        assert document.word_count > 0
        assert document.title == "Machine Learning Lecture"

        # Create chunks
        chunker = TextChunker(chunk_size=500, min_chunk_size=50)
        chunk_result = chunker.chunk_text(sample_text)
        chunks = db_ops.create_chunks_batch(document.id, chunk_result.chunks)

        assert len(chunks) > 0

        # Mark source as completed
        db_ops.update_source_status(source.id, "completed")

        # Create study set
        study_set = db_ops.create_study_set(
            set_type="flashcards",
            content=sample_flashcards,
            document_id=document.id,
            title="ML Flashcards",
            model_used="gpt-4o",
            tokens_used=1500,
        )

        assert study_set.item_count == 2
        assert study_set.set_type == "flashcards"

        # Verify stats
        stats = db_ops.get_stats()
        assert stats["sources"] == 1
        assert stats["documents"] == 1
        assert stats["chunks"] == len(chunks)
        assert stats["study_sets"] == 1
        assert stats["study_sets_by_type"]["flashcards"] == 1

    def test_export_workflow(self, temp_dir, sample_flashcards, sample_quiz, sample_audio_summary):
        """Test exporting study sets in different formats."""
        # Test JSON export
        json_exporter = get_exporter("json")
        json_result = json_exporter.export(
            sample_flashcards,
            temp_dir / "flashcards.json",
            "Test Flashcards",
        )

        assert json_result.success
        assert json_result.filepath.exists()
        assert json_result.item_count == 2

        # Test Anki export
        anki_exporter = get_exporter("anki")
        anki_result = anki_exporter.export(
            sample_flashcards,
            temp_dir / "flashcards.csv",
            "Test Deck",
        )

        assert anki_result.success
        assert anki_result.filepath.exists()
        assert anki_result.item_count == 2

        # Verify Anki CSV format
        csv_content = anki_result.filepath.read_text()
        assert "What is machine learning?" in csv_content
        assert "Test_Deck" in csv_content

        # Test Markdown export for quiz
        md_exporter = get_exporter("markdown")
        md_result = md_exporter.export(
            sample_quiz,
            temp_dir / "quiz.md",
            "Test Quiz",
        )

        assert md_result.success
        assert md_result.filepath.exists()

        md_content = md_result.filepath.read_text()
        assert "# Test Quiz" in md_content
        assert "Answer Key" in md_content

        # Test Markdown export for audio summary
        summary_result = md_exporter.export(
            sample_audio_summary,
            temp_dir / "summary.md",
            "Test Summary",
        )

        assert summary_result.success
        summary_content = summary_result.filepath.read_text(encoding="utf-8")
        assert "Key Concepts" in summary_content
        assert "Main Takeaways" in summary_content


class TestMultiDocumentWorkflow:
    """Test workflows involving multiple documents."""

    def test_multiple_documents_ingestion(self, db_ops, temp_dir):
        """Test ingesting multiple documents."""
        # Create test files
        (temp_dir / "doc1.txt").write_text("Document one content about Python programming.")
        (temp_dir / "doc2.txt").write_text("Document two content about JavaScript development.")
        (temp_dir / "doc3.md").write_text("# Document Three\n\nContent about TypeScript.")

        # Scan directory
        scanner = FileScanner()
        files = scanner.scan_directory(temp_dir)

        assert len(files) == 3

        # Ingest all files
        extractor = TextExtractor()
        chunker = TextChunker()

        for scanned_file in files:
            # Create source
            source = db_ops.create_source(
                filename=scanned_file.filename,
                filepath=str(scanned_file.path),
                file_type=scanned_file.file_type,
                file_hash=scanned_file.compute_hash(),
            )

            # Extract
            result = extractor.extract(scanned_file.path)
            assert result.success

            # Create document
            document = db_ops.create_document(
                source_id=source.id,
                raw_text=result.text,
                title=result.title,
            )

            # Chunk and store
            chunk_result = chunker.chunk_text(result.text)
            if chunk_result.chunks:
                db_ops.create_chunks_batch(document.id, chunk_result.chunks)

            # Update status
            db_ops.update_source_status(source.id, "completed")

        # Verify all documents are ingested
        all_docs = db_ops.get_all_documents()
        assert len(all_docs) == 3

        # Verify sources
        all_sources = db_ops.get_all_sources()
        assert len(all_sources) == 3
        assert all(s.status == "completed" for s in all_sources)


class TestDeduplication:
    """Test file deduplication using hashes."""

    def test_duplicate_file_detection(self, db_ops, temp_dir):
        """Test that duplicate files are detected by hash."""
        # Create two identical files
        content = "This is identical content in both files."
        (temp_dir / "file1.txt").write_text(content)
        (temp_dir / "file2.txt").write_text(content)

        scanner = FileScanner()
        files = scanner.scan_directory(temp_dir)

        # Both files should have the same hash
        hash1 = files[0].compute_hash()
        hash2 = files[1].compute_hash()
        assert hash1 == hash2

        # First file ingested
        source1 = db_ops.create_source(
            filename=files[0].filename,
            filepath=str(files[0].path),
            file_type="document",
            file_hash=hash1,
        )
        db_ops.update_source_status(source1.id, "completed")

        # Second file should be detected as duplicate
        existing = db_ops.get_source_by_hash(hash2)
        assert existing is not None
        assert existing.id == source1.id

    def test_modified_file_detection(self, db_ops, temp_dir):
        """Test that modified files have different hashes."""
        file_path = temp_dir / "changing_file.txt"
        file_path.write_text("Original content")

        scanner = FileScanner()
        file1 = scanner.scan_file(file_path)
        hash1 = file1.compute_hash()

        # Modify the file
        file_path.write_text("Modified content")
        file2 = scanner.scan_file(file_path)
        hash2 = file2.compute_hash()

        # Hashes should be different
        assert hash1 != hash2


class TestErrorHandling:
    """Test error handling in the workflow."""

    def test_missing_file_extraction(self):
        """Test extraction of missing file raises error or returns failure."""
        extractor = TextExtractor()

        # The extractor should either raise FileNotFoundError or return
        # an ExtractionResult with success=False
        try:
            result = extractor.extract("/nonexistent/path/file.txt")
            assert not result.success
        except FileNotFoundError:
            pass  # This is also acceptable behavior

    def test_unsupported_file_type(self, temp_dir):
        """Test that unsupported files are skipped."""
        (temp_dir / "unsupported.xyz").write_text("content")

        scanner = FileScanner()
        files = scanner.scan_directory(temp_dir)

        assert len(files) == 0

    def test_export_invalid_format(self):
        """Test that invalid export format returns None."""
        exporter = get_exporter("invalid_format")
        assert exporter is None

    def test_anki_export_non_flashcards(self, temp_dir, sample_quiz):
        """Test that Anki export fails for non-flashcard content."""
        exporter = get_exporter("anki")
        result = exporter.export(sample_quiz, temp_dir / "quiz.csv")

        assert not result.success
        assert "flashcards" in result.error.lower()
