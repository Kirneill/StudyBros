"""
Anki CSV exporter - for importing flashcards into Anki.
"""

import csv
from pathlib import Path

from study_guide.export.base import BaseExporter, ExportResult


class AnkiExporter(BaseExporter):
    """Export flashcards to Anki-compatible CSV format."""

    def get_file_extension(self) -> str:
        return ".csv"

    @property
    def format_name(self) -> str:
        return "Anki CSV"

    def export(
        self,
        content: dict | list,
        output_path: Path,
        title: str | None = None,
    ) -> ExportResult:
        """
        Export flashcards to Anki CSV format.

        Anki CSV format:
        - Tab-separated or semicolon-separated
        - Column 1: Front (question)
        - Column 2: Back (answer)
        - Column 3: Tags (space-separated)

        Args:
            content: Flashcard set content (should have "cards" key)
            output_path: Output file path
            title: Optional title (used as tag prefix)

        Returns:
            ExportResult
        """
        try:
            output_path = Path(output_path)

            # Ensure correct extension
            if output_path.suffix.lower() != ".csv":
                output_path = output_path.with_suffix(".csv")

            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Extract cards from content
            if isinstance(content, dict) and "cards" in content:
                cards = content["cards"]
            elif isinstance(content, list):
                cards = content
            else:
                return ExportResult(
                    success=False,
                    error="Content does not contain flashcards",
                )

            if not cards:
                return ExportResult(
                    success=False,
                    error="No flashcards to export",
                )

            # Write CSV using semicolon as separator (works well with Anki)
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_ALL)

                for card in cards:
                    front = card.get("question", "")
                    back = card.get("answer", "")

                    # Build tags
                    tags = card.get("tags", [])
                    difficulty = card.get("difficulty", "")
                    if difficulty:
                        tags.append(f"difficulty::{difficulty}")
                    if title:
                        tags.insert(0, title.replace(" ", "_"))

                    tags_str = " ".join(tags)

                    writer.writerow([front, back, tags_str])

            return ExportResult(
                success=True,
                filepath=output_path,
                item_count=len(cards),
            )

        except Exception as e:
            return ExportResult(
                success=False,
                error=str(e),
            )
