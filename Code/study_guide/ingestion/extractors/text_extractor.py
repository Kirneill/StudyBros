"""
Plain text and Markdown extractor.
"""

import re
from pathlib import Path

from study_guide.ingestion.extractors.base import BaseExtractor, ExtractionResult


class TextExtractor(BaseExtractor):
    """Extract text from plain text and Markdown files."""

    def supported_extensions(self) -> set[str]:
        return {".txt", ".md", ".markdown", ".text"}

    def extract(self, filepath: Path | str) -> ExtractionResult:
        """
        Extract text from a text/markdown file.
        """
        try:
            filepath = self._validate_file(filepath)

            # Try different encodings
            text = None
            encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

            for encoding in encodings:
                try:
                    with open(filepath, "r", encoding=encoding) as f:
                        text = f.read()
                    break
                except UnicodeDecodeError:
                    continue

            if text is None:
                return ExtractionResult(
                    text="",
                    success=False,
                    error="Could not decode file with any known encoding",
                )

            # Try to extract title
            title = self._extract_title(text, filepath)

            file_type = "markdown" if filepath.suffix.lower() in {".md", ".markdown"} else "text"

            return ExtractionResult(
                text=text,
                title=title,
                metadata={
                    "file_type": file_type,
                    "line_count": text.count("\n") + 1,
                },
                success=True,
            )

        except Exception as e:
            return ExtractionResult(
                text="",
                success=False,
                error=str(e),
            )

    def _extract_title(self, text: str, filepath: Path) -> str:
        """Try to extract a title from the text."""
        lines = text.strip().split("\n")

        if not lines:
            return filepath.stem

        first_line = lines[0].strip()

        # Check for Markdown heading
        if first_line.startswith("#"):
            # Remove heading markers
            title = re.sub(r"^#+\s*", "", first_line)
            if title:
                return title

        # Check for underline-style heading (next line is === or ---)
        if len(lines) > 1:
            second_line = lines[1].strip()
            if re.match(r"^[=\-]+$", second_line) and first_line:
                return first_line

        # Use first non-empty line if it looks like a title (short enough)
        if first_line and len(first_line) < 100:
            return first_line

        return filepath.stem
