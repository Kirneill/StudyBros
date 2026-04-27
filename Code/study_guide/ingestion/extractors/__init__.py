"""
Content extractors for different file types.
"""

from pathlib import Path

from study_guide.ingestion.extractors.base import BaseExtractor, ExtractionResult
from study_guide.ingestion.extractors.pdf_extractor import PDFExtractor
from study_guide.ingestion.extractors.pptx_extractor import PPTXExtractor
from study_guide.ingestion.extractors.text_extractor import TextExtractor
from study_guide.ingestion.extractors.video_extractor import VideoExtractor

# Mapping of extensions to extractors
_EXTRACTORS: dict[str, type[BaseExtractor]] = {
    ".pptx": PPTXExtractor,
    ".pdf": PDFExtractor,
    ".txt": TextExtractor,
    ".md": TextExtractor,
    ".markdown": TextExtractor,
    ".text": TextExtractor,
    ".mp4": VideoExtractor,
    ".mov": VideoExtractor,
    ".webm": VideoExtractor,
    ".avi": VideoExtractor,
    ".mkv": VideoExtractor,
    ".mp3": VideoExtractor,  # Audio files use same extractor
    ".wav": VideoExtractor,
    ".m4a": VideoExtractor,
    ".aac": VideoExtractor,
    ".ogg": VideoExtractor,
}


def get_extractor(filepath: Path | str) -> BaseExtractor | None:
    """
    Get the appropriate extractor for a file.

    Args:
        filepath: Path to the file

    Returns:
        Extractor instance or None if no extractor available
    """
    filepath = Path(filepath)
    extension = filepath.suffix.lower()

    extractor_class = _EXTRACTORS.get(extension)
    if extractor_class:
        return extractor_class()

    return None


__all__ = [
    "BaseExtractor",
    "ExtractionResult",
    "PPTXExtractor",
    "PDFExtractor",
    "TextExtractor",
    "VideoExtractor",
    "get_extractor",
]
