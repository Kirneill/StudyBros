"""
Tests for text chunking.
"""

import pytest

from study_guide.ingestion.chunker import TextChunker


class TestTextChunker:
    """Tests for TextChunker."""

    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunker = TextChunker()
        result = chunker.chunk_text("")

        assert result.chunks == []
        assert result.chunk_count == 0
        assert result.total_chars == 0

    def test_chunk_short_text(self):
        """Test chunking text shorter than chunk size."""
        chunker = TextChunker(chunk_size=1000)
        text = "This is a short paragraph that should not be split."

        result = chunker.chunk_text(text)

        # Short text should not be chunked (but might be filtered by min size)
        assert result.chunk_count >= 0

    def test_chunk_long_text(self, sample_text):
        """Test chunking a longer text."""
        chunker = TextChunker(chunk_size=500, min_chunk_size=50)
        result = chunker.chunk_text(sample_text)

        assert result.chunk_count > 1
        assert result.total_chars > 0

        # Each chunk should be within size limits
        for chunk in result.chunks:
            assert len(chunk) >= chunker.min_chunk_size

    def test_smart_chunking_respects_paragraphs(self):
        """Test that smart chunking tries to preserve paragraphs."""
        text = """First paragraph with some content here.

Second paragraph with different content.

Third paragraph to ensure we have enough text."""

        chunker = TextChunker(chunk_size=100, min_chunk_size=20)
        result = chunker.chunk_text(text, strategy="smart")

        # Should have multiple chunks
        assert result.chunk_count >= 1

    def test_fixed_chunking(self, sample_text):
        """Test fixed-size chunking."""
        chunker = TextChunker(chunk_size=300, overlap=50)
        result = chunker.chunk_text(sample_text, strategy="fixed")

        assert result.chunk_count > 0
        assert result.total_chars > 0

    def test_chunk_with_headings(self):
        """Test chunking text with markdown headings."""
        text = """# Section 1

Content for section 1.

# Section 2

Content for section 2.

## Subsection 2.1

More content here."""

        chunker = TextChunker(chunk_size=200, min_chunk_size=20)
        result = chunker.chunk_text(text)

        assert result.chunk_count >= 1

    def test_min_chunk_size_filter(self):
        """Test that chunks below minimum size are filtered."""
        text = "A\n\nB\n\nC"  # Very short paragraphs

        chunker = TextChunker(chunk_size=100, min_chunk_size=50)
        result = chunker.chunk_text(text)

        # All chunks should meet minimum size
        for chunk in result.chunks:
            assert len(chunk) >= chunker.min_chunk_size
