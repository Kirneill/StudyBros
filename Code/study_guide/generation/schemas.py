"""
Pydantic schemas for structured outputs.

These schemas define the exact structure expected from OpenAI's structured outputs.
"""

from typing import Literal
from pydantic import BaseModel, Field


class Flashcard(BaseModel):
    """A single flashcard with question and answer."""

    question: str = Field(
        description="The question or prompt for the front of the flashcard"
    )
    answer: str = Field(
        description="The answer or response for the back of the flashcard"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Topic tags for categorizing the flashcard",
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium",
        description="Difficulty level of the flashcard",
    )


class FlashcardSet(BaseModel):
    """A set of flashcards generated from content."""

    cards: list[Flashcard] = Field(
        description="List of flashcards generated from the content"
    )


class QuizOption(BaseModel):
    """A single option in a multiple choice question."""

    label: str = Field(description="Option label (A, B, C, D)")
    text: str = Field(description="Option text content")


class QuizQuestion(BaseModel):
    """A multiple choice quiz question."""

    prompt: str = Field(description="The question prompt")
    options: list[QuizOption] = Field(
        description="List of answer options (typically 4)",
        min_length=2,
        max_length=6,
    )
    correct_index: int = Field(
        description="Zero-based index of the correct option",
        ge=0,
    )
    explanation: str = Field(
        description="Explanation of why the correct answer is correct"
    )


class Quiz(BaseModel):
    """A quiz consisting of multiple choice questions."""

    questions: list[QuizQuestion] = Field(
        description="List of quiz questions"
    )


class PracticeTestQuestion(BaseModel):
    """A question in a practice test (various types)."""

    question_type: Literal["multiple_choice", "short_answer", "true_false"] = Field(
        description="Type of question"
    )
    prompt: str = Field(description="The question prompt")
    options: list[QuizOption] | None = Field(
        default=None,
        description="Answer options (for multiple choice and true/false)",
    )
    correct_answer: str = Field(
        description="The correct answer (index for MC, text for short answer, true/false for T/F)"
    )
    explanation: str = Field(
        description="Explanation of the correct answer"
    )
    points: int = Field(
        default=1,
        description="Point value of the question",
        ge=1,
    )


class PracticeTest(BaseModel):
    """A practice test with mixed question types."""

    title: str = Field(description="Title of the practice test")
    questions: list[PracticeTestQuestion] = Field(
        description="List of test questions"
    )
    total_points: int = Field(
        description="Total points possible on the test",
        ge=1,
    )


class KeyConcept(BaseModel):
    """A key concept or topic from the content."""

    concept: str = Field(description="The main concept or topic name")
    explanation: str = Field(description="Clear explanation of the concept")
    importance: Literal["essential", "important", "supplementary"] = Field(
        default="important",
        description="How important this concept is to understand",
    )


class AudioSummary(BaseModel):
    """An audio-friendly summary of the content for TTS playback."""

    title: str = Field(description="Title of the summary")
    overview: str = Field(
        description="A 2-3 sentence high-level overview of the content"
    )
    key_concepts: list[KeyConcept] = Field(
        description="List of key concepts covered in the content"
    )
    main_points: list[str] = Field(
        description="Bullet points of the main takeaways, suitable for reading aloud"
    )
    conclusion: str = Field(
        description="A concluding statement summarizing the most important things to remember"
    )
    estimated_read_time_seconds: int = Field(
        description="Estimated time to read aloud in seconds",
        ge=30,
    )