"""
Ingestion package - File scanning and content extraction.
"""

from study_guide.ingestion.chunker import TextChunker
from study_guide.ingestion.extractors import (
    BaseExtractor,
    PDFExtractor,
    PPTXExtractor,
    TextExtractor,
    VideoExtractor,
    get_extractor,
)
from study_guide.ingestion.scanner import FileScanner

__all__ = [
    "FileScanner",
    "TextChunker",
    "BaseExtractor",
    "PPTXExtractor",
    "PDFExtractor",
    "TextExtractor",
    "VideoExtractor",
    "get_extractor",
]
