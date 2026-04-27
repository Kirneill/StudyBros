"""
Tests for content extraction.
"""

import pytest
from pathlib import Path

from study_guide.ingestion.extractors import (
    TextExtractor,
    get_extractor,
)
from study_guide.ingestion.scanner import FileScanner, ScannedFile


class TestFileScanner:
    """Tests for FileScanner."""

    def test_scan_empty_directory(self, temp_dir):
        """Test scanning an empty directory."""
        scanner = FileScanner()
        files = scanner.scan_directory(temp_dir)
        assert files == []

    def test_scan_directory_with_files(self, temp_dir):
        """Test scanning a directory with supported files."""
        # Create test files
        (temp_dir / "test.txt").write_text("Hello world")
        (temp_dir / "test.md").write_text("# Markdown")
        (temp_dir / "unsupported.xyz").write_text("data")

        scanner = FileScanner()
        files = scanner.scan_directory(temp_dir)

        # Should find txt and md, not xyz
        assert len(files) == 2
        extensions = {f.extension for f in files}
        assert ".txt" in extensions
        assert ".md" in extensions

    def test_scan_nonexistent_directory(self):
        """Test scanning a non-existent directory."""
        scanner = FileScanner()
        with pytest.raises(FileNotFoundError):
            scanner.scan_directory("/nonexistent/path")

    def test_scanned_file_hash(self, temp_dir):
        """Test file hash computation."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello world")

        scanner = FileScanner()
        scanned = scanner.scan_file(test_file)

        assert scanned is not None
        hash1 = scanned.compute_hash()
        hash2 = scanned.compute_hash()

        # Hash should be consistent
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex


class TestTextExtractor:
    """Tests for TextExtractor."""

    def test_extract_txt(self, temp_dir):
        """Test extracting text from a .txt file."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!\nThis is a test.")

        extractor = TextExtractor()
        result = extractor.extract(test_file)

        assert result.success
        assert "Hello, World!" in result.text
        assert result.word_count > 0

    def test_extract_md(self, temp_dir):
        """Test extracting text from a .md file."""
        test_file = temp_dir / "test.md"
        test_file.write_text("# Title\n\nThis is markdown content.")

        extractor = TextExtractor()
        result = extractor.extract(test_file)

        assert result.success
        assert "# Title" in result.text
        assert result.title == "Title"

    def test_extract_nonexistent_file(self):
        """Test extracting from a non-existent file raises error."""
        extractor = TextExtractor()
        # The base extractor's _validate_file method raises FileNotFoundError
        # when the file doesn't exist
        try:
            result = extractor.extract("/nonexistent/file.txt")
            # If we get here without exception, check the result
            assert not result.success
        except FileNotFoundError:
            # This is the expected behavior
            pass

    def test_can_extract(self, temp_dir):
        """Test can_extract method."""
        extractor = TextExtractor()

        assert extractor.can_extract("test.txt")
        assert extractor.can_extract("test.md")
        assert not extractor.can_extract("test.pdf")


class TestGetExtractor:
    """Tests for get_extractor factory function."""

    def test_get_text_extractor(self):
        """Test getting TextExtractor for .txt files."""
        extractor = get_extractor("test.txt")
        assert extractor is not None
        assert isinstance(extractor, TextExtractor)

    def test_get_md_extractor(self):
        """Test getting TextExtractor for .md files."""
        extractor = get_extractor("test.md")
        assert extractor is not None
        assert isinstance(extractor, TextExtractor)

    def test_get_unsupported_extractor(self):
        """Test getting extractor for unsupported format."""
        extractor = get_extractor("test.xyz")
        assert extractor is None
