"""
Base exporter interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExportResult:
    """Result of an export operation."""
    success: bool
    filepath: Path | None = None
    error: str | None = None
    item_count: int = 0


class BaseExporter(ABC):
    """Base class for exporters."""

    @abstractmethod
    def export(
        self,
        content: dict | list,
        output_path: Path,
        title: str | None = None,
    ) -> ExportResult:
        """
        Export content to a file.

        Args:
            content: The content to export (parsed JSON from study set)
            output_path: Path for the output file
            title: Optional title for the export

        Returns:
            ExportResult with success status and file path
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Return the file extension for this exporter."""
        pass

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the format name."""
        pass


def get_exporter(format_type: str) -> BaseExporter | None:
    """
    Get an exporter for the specified format.

    Args:
        format_type: Format type ("json", "anki", "markdown")

    Returns:
        Exporter instance or None
    """
    from study_guide.export.anki_export import AnkiExporter
    from study_guide.export.json_export import JSONExporter
    from study_guide.export.markdown_export import MarkdownExporter

    exporters = {
        "json": JSONExporter,
        "anki": AnkiExporter,
        "anki_csv": AnkiExporter,
        "csv": AnkiExporter,
        "markdown": MarkdownExporter,
        "md": MarkdownExporter,
    }

    exporter_class = exporters.get(format_type.lower())
    if exporter_class:
        return exporter_class()
    return None
