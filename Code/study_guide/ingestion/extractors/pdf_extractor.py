"""
PDF extractor.
"""

from pathlib import Path

from pypdf import PdfReader

from study_guide.ingestion.extractors.base import BaseExtractor, ExtractionResult


class PDFExtractor(BaseExtractor):
    """Extract text from PDF files."""

    def supported_extensions(self) -> set[str]:
        return {".pdf"}

    def extract(self, filepath: Path | str) -> ExtractionResult:
        """
        Extract text from a PDF file.

        Extracts text from all pages, attempting to preserve structure.
        """
        try:
            filepath = self._validate_file(filepath)
            reader = PdfReader(str(filepath))

            all_text: list[str] = []
            page_count = 0
            title = None

            # Try to get title from metadata
            if reader.metadata:
                title = reader.metadata.get("/Title") or reader.metadata.get("title")

            for page_num, page in enumerate(reader.pages, start=1):
                page_count += 1
                page_text = page.extract_text()

                if page_text and page_text.strip():
                    all_text.append(f"\n--- Page {page_num} ---\n")
                    all_text.append(page_text.strip())

            combined_text = "\n".join(all_text)

            # If no title from metadata, try first line
            if not title and combined_text:
                first_line = combined_text.split("\n")[0].strip()
                if first_line and len(first_line) < 200:
                    title = first_line

            return ExtractionResult(
                text=combined_text,
                title=title or filepath.stem,
                metadata={
                    "page_count": page_count,
                    "file_type": "pdf",
                },
                success=True,
            )

        except Exception as e:
            return ExtractionResult(
                text="",
                success=False,
                error=str(e),
            )
