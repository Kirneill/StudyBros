"""
Tests for generation schemas.
"""

import pytest
from pydantic import ValidationError

from study_guide.generation.schemas import (
    Flashcard,
    FlashcardSet,
    QuizOption,
    QuizQuestion,
    Quiz,
    PracticeTestQuestion,
    PracticeTest,
    KeyConcept,
    AudioSummary,
)


class TestFlashcardSchema:
    """Tests for Flashcard schema."""

    def test_valid_flashcard(self):
        """Test creating a valid flashcard."""
        card = Flashcard(
            question="What is Python?",
            answer="A programming language.",
            tags=["python", "programming"],
            difficulty="easy",
        )

        assert card.question == "What is Python?"
        assert card.answer == "A programming language."
        assert "python" in card.tags
        assert card.difficulty == "easy"

    def test_flashcard_default_values(self):
        """Test flashcard default values."""
        card = Flashcard(
            question="Test?",
            answer="Answer.",
        )

        assert card.tags == []
        assert card.difficulty == "medium"

    def test_invalid_difficulty(self):
        """Test that invalid difficulty raises error."""
        with pytest.raises(ValidationError):
            Flashcard(
                question="Test?",
                answer="Answer.",
                difficulty="invalid",
            )


class TestFlashcardSet:
    """Tests for FlashcardSet schema."""

    def test_valid_flashcard_set(self, sample_flashcards):
        """Test creating a valid flashcard set."""
        fs = FlashcardSet(**sample_flashcards)

        assert len(fs.cards) == 2
        assert fs.cards[0].question == "What is machine learning?"


class TestQuizSchema:
    """Tests for Quiz schemas."""

    def test_valid_quiz_option(self):
        """Test creating a valid quiz option."""
        option = QuizOption(label="A", text="First option")

        assert option.label == "A"
        assert option.text == "First option"

    def test_valid_quiz_question(self):
        """Test creating a valid quiz question."""
        question = QuizQuestion(
            prompt="What is 2 + 2?",
            options=[
                QuizOption(label="A", text="3"),
                QuizOption(label="B", text="4"),
                QuizOption(label="C", text="5"),
                QuizOption(label="D", text="6"),
            ],
            correct_index=1,
            explanation="2 + 2 equals 4.",
        )

        assert question.prompt == "What is 2 + 2?"
        assert len(question.options) == 4
        assert question.correct_index == 1

    def test_valid_quiz(self, sample_quiz):
        """Test creating a valid quiz."""
        quiz = Quiz(**sample_quiz)

        assert len(quiz.questions) == 1
        assert quiz.questions[0].correct_index == 1

    def test_invalid_correct_index(self):
        """Test that negative correct_index raises error."""
        with pytest.raises(ValidationError):
            QuizQuestion(
                prompt="Test?",
                options=[
                    QuizOption(label="A", text="Option 1"),
                    QuizOption(label="B", text="Option 2"),
                ],
                correct_index=-1,
                explanation="Test",
            )


class TestPracticeTestSchema:
    """Tests for PracticeTest schemas."""

    def test_valid_practice_test_question(self):
        """Test creating a valid practice test question."""
        question = PracticeTestQuestion(
            question_type="multiple_choice",
            prompt="What is Python?",
            options=[
                QuizOption(label="A", text="A snake"),
                QuizOption(label="B", text="A programming language"),
                QuizOption(label="C", text="A movie"),
                QuizOption(label="D", text="A food"),
            ],
            correct_answer="B",
            explanation="Python is a programming language.",
            points=2,
        )

        assert question.question_type == "multiple_choice"
        assert question.points == 2

    def test_short_answer_question(self):
        """Test creating a short answer question."""
        question = PracticeTestQuestion(
            question_type="short_answer",
            prompt="Name three programming languages.",
            options=None,
            correct_answer="Python, Java, JavaScript",
            explanation="Any three valid languages would be accepted.",
            points=3,
        )

        assert question.question_type == "short_answer"
        assert question.options is None

    def test_valid_practice_test(self):
        """Test creating a valid practice test."""
        test = PracticeTest(
            title="Python Basics Test",
            questions=[
                PracticeTestQuestion(
                    question_type="true_false",
                    prompt="Python is a compiled language.",
                    options=None,
                    correct_answer="False",
                    explanation="Python is an interpreted language.",
                    points=1,
                )
            ],
            total_points=1,
        )

        assert test.title == "Python Basics Test"
        assert len(test.questions) == 1
        assert test.total_points == 1


class TestAudioSummarySchema:
    """Tests for AudioSummary schemas."""

    def test_valid_key_concept(self):
        """Test creating a valid key concept."""
        concept = KeyConcept(
            concept="Machine Learning",
            explanation="A subset of AI that enables systems to learn from data.",
            importance="essential",
        )

        assert concept.concept == "Machine Learning"
        assert concept.importance == "essential"

    def test_key_concept_default_importance(self):
        """Test key concept default importance."""
        concept = KeyConcept(
            concept="Test",
            explanation="Test explanation",
        )

        assert concept.importance == "important"

    def test_invalid_importance(self):
        """Test that invalid importance raises error."""
        with pytest.raises(ValidationError):
            KeyConcept(
                concept="Test",
                explanation="Test explanation",
                importance="invalid",
            )

    def test_valid_audio_summary(self, sample_audio_summary):
        """Test creating a valid audio summary."""
        summary = AudioSummary(**sample_audio_summary)

        assert summary.title == "Machine Learning Overview"
        assert len(summary.key_concepts) == 3
        assert len(summary.main_points) == 4
        assert summary.estimated_read_time_seconds == 120

    def test_audio_summary_minimum_read_time(self):
        """Test that read time has minimum of 30 seconds."""
        with pytest.raises(ValidationError):
            AudioSummary(
                title="Test",
                overview="Overview",
                key_concepts=[],
                main_points=[],
                conclusion="Conclusion",
                estimated_read_time_seconds=10,  # Below minimum
            )
