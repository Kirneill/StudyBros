"""
Base extractor interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExtractionResult:
    """Result of text extraction."""
    text: str
    title: str | None = None
    metadata: dict = field(default_factory=dict)
    success: bool = True
    error: str | None = None
    word_count: int = 0

    def __post_init__(self):
        if self.success and self.text:
            self.word_count = len(self.text.split())


class BaseExtractor(ABC):
    """Base class for content extractors."""

    @abstractmethod
    def extract(self, filepath: Path | str) -> ExtractionResult:
        """
        Extract text content from a file.

        Args:
            filepath: Path to the file

        Returns:
            ExtractionResult with extracted text and metadata
        """
        pass

    @abstractmethod
    def supported_extensions(self) -> set[str]:
        """Return set of supported file extensions."""
        pass

    def can_extract(self, filepath: Path | str) -> bool:
        """Check if this extractor can handle the file."""
        filepath = Path(filepath)
        return filepath.suffix.lower() in self.supported_extensions()

    def _validate_file(self, filepath: Path | str) -> Path:
        """Validate that the file exists and is readable."""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        if not filepath.is_file():
            raise ValueError(f"Path is not a file: {filepath}")
        return filepath
