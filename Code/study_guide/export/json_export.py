"""
JSON exporter - canonical format for study sets.
"""

import json
from pathlib import Path

from study_guide.export.base import BaseExporter, ExportResult


class JSONExporter(BaseExporter):
    """Export study sets to JSON format."""

    def get_file_extension(self) -> str:
        return ".json"

    @property
    def format_name(self) -> str:
        return "JSON"

    def export(
        self,
        content: dict | list,
        output_path: Path,
        title: str | None = None,
    ) -> ExportResult:
        """
        Export content to JSON file.

        Args:
            content: Study set content
            output_path: Output file path
            title: Optional title (added to metadata)

        Returns:
            ExportResult
        """
        try:
            output_path = Path(output_path)

            # Ensure correct extension
            if output_path.suffix.lower() != ".json":
                output_path = output_path.with_suffix(".json")

            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Calculate item count
            if isinstance(content, dict):
                if "cards" in content:
                    item_count = len(content["cards"])
                elif "questions" in content:
                    item_count = len(content["questions"])
                else:
                    item_count = 1
            elif isinstance(content, list):
                item_count = len(content)
            else:
                item_count = 1

            # Create export data with metadata
            export_data = {
                "title": title,
                "item_count": item_count,
                "content": content,
            }

            # Write JSON
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return ExportResult(
                success=True,
                filepath=output_path,
                item_count=item_count,
            )

        except Exception as e:
            return ExportResult(
                success=False,
                error=str(e),
            )
