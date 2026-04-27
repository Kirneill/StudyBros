"""
Study material generator using OpenAI Structured Outputs.
"""

from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from study_guide.config import config
from study_guide.generation.prompts import (
    SYSTEM_PROMPT,
    get_audio_summary_prompt,
    get_flashcard_prompt,
    get_practice_test_prompt,
    get_quiz_prompt,
)
from study_guide.generation.schemas import AudioSummary, FlashcardSet, PracticeTest, Quiz

T = TypeVar("T", bound=BaseModel)


class GenerationResult:
    """Result of a generation operation."""

    def __init__(
        self,
        content: BaseModel | None,
        success: bool,
        error: str | None = None,
        tokens_used: int = 0,
        model: str | None = None,
    ):
        self.content = content
        self.success = success
        self.error = error
        self.tokens_used = tokens_used
        self.model = model


class StudyMaterialGenerator:
    """Generates study materials using OpenAI's Structured Outputs."""

    def __init__(self):
        self.client: OpenAI | None = None
        self.model = config.GENERATION_MODEL

    def _get_client(self) -> OpenAI:
        """Get or create OpenAI client."""
        if self.client is None:
            if not config.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not set")
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        return self.client

    def _generate_structured(
        self,
        prompt: str,
        schema: Type[T],
    ) -> GenerationResult:
        """
        Generate structured output using OpenAI's response format.

        Args:
            prompt: The user prompt
            schema: Pydantic schema for the response

        Returns:
            GenerationResult with parsed content
        """
        try:
            client = self._get_client()

            response = client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format=schema,
                max_tokens=config.MAX_TOKENS_PER_RESPONSE,
            )

            parsed = response.choices[0].message.parsed
            tokens_used = response.usage.total_tokens if response.usage else 0

            return GenerationResult(
                content=parsed,
                success=True,
                tokens_used=tokens_used,
                model=self.model,
            )

        except Exception as e:
            return GenerationResult(
                content=None,
                success=False,
                error=str(e),
            )

    def generate_flashcards(
        self,
        content: str,
        count: int = 10,
    ) -> GenerationResult:
        """
        Generate flashcards from content.

        Args:
            content: Text content to generate flashcards from
            count: Number of flashcards to generate

        Returns:
            GenerationResult with FlashcardSet
        """
        prompt = get_flashcard_prompt(content, count)
        return self._generate_structured(prompt, FlashcardSet)

    def generate_quiz(
        self,
        content: str,
        count: int = 10,
    ) -> GenerationResult:
        """
        Generate a multiple choice quiz from content.

        Args:
            content: Text content to generate quiz from
            count: Number of questions to generate

        Returns:
            GenerationResult with Quiz
        """
        prompt = get_quiz_prompt(content, count)
        return self._generate_structured(prompt, Quiz)

    def generate_practice_test(
        self,
        content: str,
        count: int = 15,
    ) -> GenerationResult:
        """
        Generate a practice test with mixed question types.

        Args:
            content: Text content to generate test from
            count: Number of questions to generate

        Returns:
            GenerationResult with PracticeTest
        """
        prompt = get_practice_test_prompt(content, count)
        return self._generate_structured(prompt, PracticeTest)

    def generate_audio_summary(
        self,
        content: str,
        concept_count: int = 5,
        point_count: int = 7,
    ) -> GenerationResult:
        """
        Generate an audio-friendly summary suitable for TTS.

        Args:
            content: Text content to summarize
            concept_count: Number of key concepts to extract
            point_count: Number of main points to include

        Returns:
            GenerationResult with AudioSummary
        """
        prompt = get_audio_summary_prompt(content, concept_count, point_count)
        return self._generate_structured(prompt, AudioSummary)

    def generate_from_chunks(
        self,
        chunks: list[str],
        generation_type: str,
        count: int = 10,
    ) -> GenerationResult:
        """
        Generate study materials from multiple chunks.

        Respects the MAX_CHUNKS_PER_GENERATION limit.

        Args:
            chunks: List of text chunks
            generation_type: "flashcards", "quiz", or "practice_test"
            count: Number of items to generate

        Returns:
            GenerationResult
        """
        # Limit chunks to respect cost guardrails
        max_chunks = config.MAX_CHUNKS_PER_GENERATION
        if len(chunks) > max_chunks:
            chunks = chunks[:max_chunks]

        # Combine chunks
        combined_content = "\n\n---\n\n".join(chunks)

        # Generate based on type
        if generation_type == "flashcards":
            return self.generate_flashcards(combined_content, count)
        elif generation_type == "quiz":
            return self.generate_quiz(combined_content, count)
        elif generation_type == "practice_test":
            return self.generate_practice_test(combined_content, count)
        elif generation_type == "audio_summary":
            # For audio summary, count controls number of main points
            return self.generate_audio_summary(combined_content, concept_count=5, point_count=count)
        else:
            return GenerationResult(
                content=None,
                success=False,
                error=f"Unknown generation type: {generation_type}",
            )
