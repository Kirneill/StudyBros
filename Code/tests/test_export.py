"""
Tests for export functionality.
"""

import json

from study_guide.export import (
    AnkiExporter,
    JSONExporter,
    MarkdownExporter,
    get_exporter,
)


class TestJSONExporter:
    """Tests for JSONExporter."""

    def test_export_flashcards(self, temp_dir, sample_flashcards):
        """Test exporting flashcards to JSON."""
        exporter = JSONExporter()
        output_path = temp_dir / "flashcards.json"

        result = exporter.export(sample_flashcards, output_path, "Test Flashcards")

        assert result.success
        assert result.filepath.exists()
        assert result.item_count == 2

        # Verify content
        with open(result.filepath) as f:
            data = json.load(f)

        assert data["title"] == "Test Flashcards"
        assert data["item_count"] == 2
        assert "content" in data

    def test_export_quiz(self, temp_dir, sample_quiz):
        """Test exporting quiz to JSON."""
        exporter = JSONExporter()
        output_path = temp_dir / "quiz.json"

        result = exporter.export(sample_quiz, output_path, "Test Quiz")

        assert result.success
        assert result.filepath.exists()
        assert result.item_count == 1

    def test_export_adds_extension(self, temp_dir, sample_flashcards):
        """Test that exporter adds .json extension if missing."""
        exporter = JSONExporter()
        output_path = temp_dir / "flashcards"  # No extension

        result = exporter.export(sample_flashcards, output_path)

        assert result.success
        assert result.filepath.suffix == ".json"

    def test_get_file_extension(self):
        """Test file extension."""
        exporter = JSONExporter()
        assert exporter.get_file_extension() == ".json"


class TestAnkiExporter:
    """Tests for AnkiExporter."""

    def test_export_flashcards(self, temp_dir, sample_flashcards):
        """Test exporting flashcards to Anki CSV."""
        exporter = AnkiExporter()
        output_path = temp_dir / "flashcards.csv"

        result = exporter.export(sample_flashcards, output_path, "Test_Deck")

        assert result.success
        assert result.filepath.exists()
        assert result.item_count == 2

        # Verify content
        content = result.filepath.read_text()
        lines = content.strip().split("\n")

        assert len(lines) == 2
        assert "What is machine learning?" in lines[0]
        assert "Test_Deck" in lines[0]  # Tag should be included

    def test_export_with_tags(self, temp_dir):
        """Test that tags and difficulty are included."""
        cards = {
            "cards": [
                {
                    "question": "Q1?",
                    "answer": "A1",
                    "tags": ["topic1", "topic2"],
                    "difficulty": "hard",
                }
            ]
        }

        exporter = AnkiExporter()
        output_path = temp_dir / "cards.csv"

        result = exporter.export(cards, output_path)

        assert result.success
        content = result.filepath.read_text()

        assert "topic1" in content
        assert "difficulty::hard" in content

    def test_export_non_flashcard_content(self, temp_dir, sample_quiz):
        """Test that non-flashcard content fails gracefully."""
        exporter = AnkiExporter()
        output_path = temp_dir / "quiz.csv"

        result = exporter.export(sample_quiz, output_path)

        assert not result.success
        assert "flashcards" in result.error.lower()


class TestMarkdownExporter:
    """Tests for MarkdownExporter."""

    def test_export_flashcards(self, temp_dir, sample_flashcards):
        """Test exporting flashcards to Markdown."""
        exporter = MarkdownExporter()
        output_path = temp_dir / "flashcards.md"

        result = exporter.export(sample_flashcards, output_path, "Test Flashcards")

        assert result.success
        assert result.filepath.exists()
        assert result.item_count == 2

        content = result.filepath.read_text()
        assert "# Test Flashcards" in content
        assert "Card 1" in content
        assert "What is machine learning?" in content

    def test_export_quiz(self, temp_dir, sample_quiz):
        """Test exporting quiz to Markdown."""
        exporter = MarkdownExporter()
        output_path = temp_dir / "quiz.md"

        result = exporter.export(sample_quiz, output_path, "Test Quiz")

        assert result.success
        assert result.filepath.exists()

        content = result.filepath.read_text()
        assert "# Test Quiz" in content
        assert "Questions" in content
        assert "Answer Key" in content
        assert "Supervised Learning" in content

    def test_export_audio_summary(self, temp_dir, sample_audio_summary):
        """Test exporting audio summary to Markdown."""
        exporter = MarkdownExporter()
        output_path = temp_dir / "summary.md"

        result = exporter.export(sample_audio_summary, output_path, "Test Summary")

        assert result.success
        assert result.filepath.exists()
        # 3 key concepts + 4 main points
        assert result.item_count == 7

        content = result.filepath.read_text(encoding="utf-8")
        assert "Machine Learning Overview" in content
        assert "Overview" in content
        assert "Key Concepts" in content
        assert "Main Takeaways" in content
        assert "Conclusion" in content
        assert "Supervised Learning" in content

    def test_export_creates_parent_dirs(self, temp_dir, sample_flashcards):
        """Test that exporter creates parent directories."""
        exporter = MarkdownExporter()
        output_path = temp_dir / "subdir" / "nested" / "flashcards.md"

        result = exporter.export(sample_flashcards, output_path)

        assert result.success
        assert result.filepath.exists()


class TestGetExporter:
    """Tests for get_exporter factory function."""

    def test_get_json_exporter(self):
        """Test getting JSON exporter."""
        exporter = get_exporter("json")
        assert exporter is not None
        assert isinstance(exporter, JSONExporter)

    def test_get_anki_exporter(self):
        """Test getting Anki exporter."""
        exporter = get_exporter("anki")
        assert exporter is not None
        assert isinstance(exporter, AnkiExporter)

        # Also test alias
        exporter2 = get_exporter("anki_csv")
        assert exporter2 is not None
        assert isinstance(exporter2, AnkiExporter)

    def test_get_markdown_exporter(self):
        """Test getting Markdown exporter."""
        exporter = get_exporter("markdown")
        assert exporter is not None
        assert isinstance(exporter, MarkdownExporter)

        # Also test alias
        exporter2 = get_exporter("md")
        assert exporter2 is not None
        assert isinstance(exporter2, MarkdownExporter)

    def test_get_unknown_exporter(self):
        """Test getting unknown exporter returns None."""
        exporter = get_exporter("unknown")
        assert exporter is None

    def test_case_insensitive(self):
        """Test that format names are case insensitive."""
        assert get_exporter("JSON") is not None
        assert get_exporter("Markdown") is not None
