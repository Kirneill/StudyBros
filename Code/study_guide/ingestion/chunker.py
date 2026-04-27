"""
Text chunking - splits documents into smaller chunks for generation.
"""

import re
from dataclasses import dataclass

from study_guide.config import config


@dataclass
class ChunkResult:
    """Result of chunking operation."""
    chunks: list[str]
    total_chars: int
    chunk_count: int


class TextChunker:
    """
    Splits text into smaller chunks suitable for LLM generation.

    Strategies:
    1. Smart chunking: Split by headings, paragraphs, sentences
    2. Fixed-size fallback: Split by character count with overlap
    """

    def __init__(
        self,
        chunk_size: int = config.CHUNK_SIZE,
        overlap: int = config.CHUNK_OVERLAP,
        min_chunk_size: int = 100,
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size

    def chunk_text(self, text: str, strategy: str = "smart") -> ChunkResult:
        """
        Split text into chunks.

        Args:
            text: The text to chunk
            strategy: "smart" for paragraph/heading-based, "fixed" for fixed-size

        Returns:
            ChunkResult with list of chunks and metadata
        """
        if not text or not text.strip():
            return ChunkResult(chunks=[], total_chars=0, chunk_count=0)

        # Clean the text
        text = self._clean_text(text)

        if strategy == "smart":
            chunks = self._smart_chunk(text)
        else:
            chunks = self._fixed_chunk(text)

        # Filter out empty chunks and chunks below minimum size
        chunks = [c for c in chunks if len(c.strip()) >= self.min_chunk_size]

        return ChunkResult(
            chunks=chunks,
            total_chars=sum(len(c) for c in chunks),
            chunk_count=len(chunks),
        )

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Normalize whitespace
        text = re.sub(r"\r\n", "\n", text)
        text = re.sub(r"\r", "\n", text)
        # Remove excessive blank lines (more than 2)
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    def _smart_chunk(self, text: str) -> list[str]:
        """
        Smart chunking by headings, paragraphs, and sentences.
        Falls back to fixed chunking if needed.
        """
        chunks: list[str] = []

        # First, try to split by major headings (markdown style)
        heading_pattern = r"(?=^#{1,3}\s+.+$)"
        sections = re.split(heading_pattern, text, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]

        if len(sections) > 1:
            # We have headings, process each section
            for section in sections:
                section_chunks = self._chunk_section(section)
                chunks.extend(section_chunks)
        else:
            # No headings found, try paragraph splitting
            chunks = self._chunk_section(text)

        return chunks

    def _chunk_section(self, text: str) -> list[str]:
        """
        Chunk a section of text by paragraphs, then sentences if needed.
        """
        chunks: list[str] = []

        # Split by double newlines (paragraphs)
        paragraphs = re.split(r"\n\n+", text)

        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If adding this paragraph exceeds chunk size
            if len(current_chunk) + len(para) + 2 > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # If single paragraph is too large, split by sentences
                if len(para) > self.chunk_size:
                    sentence_chunks = self._chunk_by_sentences(para)
                    chunks.extend(sentence_chunks)
                    current_chunk = ""
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _chunk_by_sentences(self, text: str) -> list[str]:
        """
        Split text by sentences when paragraphs are too large.
        """
        # Simple sentence splitting (handles common cases)
        sentence_pattern = r"(?<=[.!?])\s+(?=[A-Z])"
        sentences = re.split(sentence_pattern, text)

        chunks: list[str] = []
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_chunk) + len(sentence) + 1 > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # If single sentence is still too long, force-split it
                if len(sentence) > self.chunk_size:
                    chunks.extend(self._fixed_chunk(sentence))
                    current_chunk = ""
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _fixed_chunk(self, text: str) -> list[str]:
        """
        Fixed-size chunking with overlap.
        Used as fallback when smart chunking can't reduce size.
        """
        if len(text) <= self.chunk_size:
            return [text]

        chunks: list[str] = []
        start = 0

        while start < len(text):
            # Get chunk
            end = start + self.chunk_size

            # Try to break at word boundary
            if end < len(text):
                # Look for last space within the chunk
                last_space = text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move forward with overlap
            start = end - self.overlap
            if start <= 0 or end >= len(text):
                start = end

        return chunks
