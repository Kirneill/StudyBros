"""
Generation package - AI-powered study material generation.
"""

from study_guide.generation.generator import StudyMaterialGenerator
from study_guide.generation.schemas import (
    AudioSummary,
    Flashcard,
    FlashcardSet,
    KeyConcept,
    PracticeTest,
    PracticeTestQuestion,
    Quiz,
    QuizOption,
    QuizQuestion,
)

__all__ = [
    "Flashcard",
    "FlashcardSet",
    "QuizOption",
    "QuizQuestion",
    "Quiz",
    "PracticeTestQuestion",
    "PracticeTest",
    "KeyConcept",
    "AudioSummary",
    "StudyMaterialGenerator",
]
