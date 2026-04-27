"""
Markdown exporter - for readable quiz and test printouts.
"""

from pathlib import Path
from datetime import datetime

from study_guide.export.base import BaseExporter, ExportResult


class MarkdownExporter(BaseExporter):
    """Export quizzes and tests to Markdown format."""

    def get_file_extension(self) -> str:
        return ".md"

    @property
    def format_name(self) -> str:
        return "Markdown"

    def export(
        self,
        content: dict | list,
        output_path: Path,
        title: str | None = None,
    ) -> ExportResult:
        """
        Export quiz/test to Markdown format.

        Creates a formatted document with:
        - Title and metadata
        - Questions with options
        - Answer key section

        Args:
            content: Quiz or test content
            output_path: Output file path
            title: Optional title

        Returns:
            ExportResult
        """
        try:
            output_path = Path(output_path)

            # Ensure correct extension
            if output_path.suffix.lower() not in {".md", ".markdown"}:
                output_path = output_path.with_suffix(".md")

            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Determine content type and format accordingly
            if isinstance(content, dict):
                if "cards" in content:
                    markdown = self._format_flashcards(content, title)
                    item_count = len(content["cards"])
                elif "questions" in content:
                    # Check if it's a practice test (has total_points)
                    if "total_points" in content:
                        markdown = self._format_practice_test(content, title)
                    else:
                        markdown = self._format_quiz(content, title)
                    item_count = len(content["questions"])
                elif "key_concepts" in content or "main_points" in content:
                    # Audio summary format
                    markdown = self._format_audio_summary(content, title)
                    item_count = len(content.get("key_concepts", [])) + len(content.get("main_points", []))
                else:
                    markdown = self._format_generic(content, title)
                    item_count = 1
            elif isinstance(content, list):
                markdown = self._format_generic({"items": content}, title)
                item_count = len(content)
            else:
                return ExportResult(
                    success=False,
                    error="Unsupported content format",
                )

            # Write Markdown
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown)

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

    def _format_flashcards(self, content: dict, title: str | None) -> str:
        """Format flashcards as Markdown."""
        lines = []

        # Header
        lines.append(f"# {title or 'Flashcards'}")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append(f"*Total cards: {len(content.get('cards', []))}*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Cards
        for i, card in enumerate(content.get("cards", []), 1):
            question = card.get("question", "")
            answer = card.get("answer", "")
            difficulty = card.get("difficulty", "")
            tags = card.get("tags", [])

            lines.append(f"## Card {i}")
            if difficulty:
                lines.append(f"*Difficulty: {difficulty}*")
            if tags:
                lines.append(f"*Tags: {', '.join(tags)}*")
            lines.append("")
            lines.append(f"**Q:** {question}")
            lines.append("")
            lines.append(f"**A:** {answer}")
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_quiz(self, content: dict, title: str | None) -> str:
        """Format quiz as Markdown."""
        lines = []

        questions = content.get("questions", [])

        # Header
        lines.append(f"# {title or 'Quiz'}")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append(f"*Total questions: {len(questions)}*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Questions section
        lines.append("## Questions")
        lines.append("")

        for i, q in enumerate(questions, 1):
            prompt = q.get("prompt", "")
            options = q.get("options", [])

            lines.append(f"### {i}. {prompt}")
            lines.append("")

            for opt in options:
                label = opt.get("label", "")
                text = opt.get("text", "")
                lines.append(f"- **{label}.** {text}")

            lines.append("")

        # Answer key
        lines.append("---")
        lines.append("")
        lines.append("## Answer Key")
        lines.append("")

        for i, q in enumerate(questions, 1):
            options = q.get("options", [])
            correct_idx = q.get("correct_index", 0)
            explanation = q.get("explanation", "")

            if 0 <= correct_idx < len(options):
                correct_label = options[correct_idx].get("label", "")
                correct_text = options[correct_idx].get("text", "")
            else:
                correct_label = "?"
                correct_text = ""

            lines.append(f"**{i}.** {correct_label} - {correct_text}")
            if explanation:
                lines.append(f"   *{explanation}*")
            lines.append("")

        return "\n".join(lines)

    def _format_practice_test(self, content: dict, title: str | None) -> str:
        """Format practice test as Markdown."""
        lines = []

        questions = content.get("questions", [])
        total_points = content.get("total_points", sum(q.get("points", 1) for q in questions))
        test_title = content.get("title", title) or "Practice Test"

        # Header
        lines.append(f"# {test_title}")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append(f"*Total questions: {len(questions)}*")
        lines.append(f"*Total points: {total_points}*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Instructions
        lines.append("## Instructions")
        lines.append("")
        lines.append("Answer all questions. Point values are indicated for each question.")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Questions section
        lines.append("## Questions")
        lines.append("")

        for i, q in enumerate(questions, 1):
            q_type = q.get("question_type", "")
            prompt = q.get("prompt", "")
            options = q.get("options", [])
            points = q.get("points", 1)

            lines.append(f"### {i}. {prompt}")
            lines.append(f"*({points} point{'s' if points > 1 else ''}) - {q_type.replace('_', ' ').title()}*")
            lines.append("")

            if q_type == "multiple_choice" and options:
                for opt in options:
                    label = opt.get("label", "")
                    text = opt.get("text", "")
                    lines.append(f"- **{label}.** {text}")
                lines.append("")
            elif q_type == "true_false":
                lines.append("- **A.** True")
                lines.append("- **B.** False")
                lines.append("")
            else:  # short_answer
                lines.append("*Answer:* ____________________")
                lines.append("")

        # Answer key
        lines.append("---")
        lines.append("")
        lines.append("## Answer Key")
        lines.append("")

        for i, q in enumerate(questions, 1):
            correct = q.get("correct_answer", "")
            explanation = q.get("explanation", "")
            points = q.get("points", 1)

            lines.append(f"**{i}.** {correct} ({points} pt{'s' if points > 1 else ''})")
            if explanation:
                lines.append(f"   *{explanation}*")
            lines.append("")

        return "\n".join(lines)

    def _format_audio_summary(self, content: dict, title: str | None) -> str:
        """Format audio summary as Markdown."""
        lines = []

        summary_title = content.get("title", title) or "Audio Summary"
        overview = content.get("overview", "")
        key_concepts = content.get("key_concepts", [])
        main_points = content.get("main_points", [])
        conclusion = content.get("conclusion", "")
        read_time = content.get("estimated_read_time_seconds", 0)

        # Header
        lines.append(f"# {summary_title}")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        if read_time:
            minutes = read_time // 60
            seconds = read_time % 60
            lines.append(f"*Estimated read time: {minutes}m {seconds}s*")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Overview
        lines.append("## Overview")
        lines.append("")
        lines.append(overview)
        lines.append("")

        # Key Concepts
        if key_concepts:
            lines.append("---")
            lines.append("")
            lines.append("## Key Concepts")
            lines.append("")

            for i, concept in enumerate(key_concepts, 1):
                concept_name = concept.get("concept", "")
                explanation = concept.get("explanation", "")
                importance = concept.get("importance", "important")

                importance_indicator = {
                    "essential": "⭐",
                    "important": "•",
                    "supplementary": "○",
                }.get(importance, "•")

                lines.append(f"### {importance_indicator} {concept_name}")
                lines.append("")
                lines.append(explanation)
                lines.append("")

        # Main Points
        if main_points:
            lines.append("---")
            lines.append("")
            lines.append("## Main Takeaways")
            lines.append("")

            for point in main_points:
                lines.append(f"- {point}")
            lines.append("")

        # Conclusion
        if conclusion:
            lines.append("---")
            lines.append("")
            lines.append("## Conclusion")
            lines.append("")
            lines.append(f"**{conclusion}**")
            lines.append("")

        return "\n".join(lines)

    def _format_generic(self, content: dict, title: str | None) -> str:
        """Format generic content as Markdown."""
        import json

        lines = []
        lines.append(f"# {title or 'Study Material'}")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(content, indent=2))
        lines.append("```")

        return "\n".join(lines)
