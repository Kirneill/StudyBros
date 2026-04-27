"""
Prompts for study material generation.
"""

SYSTEM_PROMPT = """You are an expert educator and study material creator. Your task is to create high-quality study materials from the provided content.

Guidelines:
1. Only use information from the provided content - do not add external facts
2. Create clear, concise, and educational materials
3. Focus on key concepts, definitions, and important details
4. Vary difficulty levels appropriately
5. Ensure all content is accurate and directly derived from the source material
6. Make questions and answers specific enough to be useful for learning"""


FLASHCARD_PROMPT = """Create flashcards from the following content.

Requirements:
- Generate exactly {count} flashcards
- Each flashcard should have a clear question and comprehensive answer
- Cover the most important concepts, definitions, and key facts
- Assign appropriate difficulty levels (easy, medium, hard)
- Add relevant topic tags for each card
- Questions should be specific and answerable from the content
- Answers should be complete but concise

Content to create flashcards from:

{content}"""


QUIZ_PROMPT = """Create a multiple choice quiz from the following content.

Requirements:
- Generate exactly {count} questions
- Each question should have 4 answer options (A, B, C, D)
- Only one option should be correct
- Distractors (wrong answers) should be plausible but clearly incorrect
- Include an explanation for why the correct answer is correct
- Cover different topics and difficulty levels from the content
- Questions should test understanding, not just recall

Content to create quiz from:

{content}"""


PRACTICE_TEST_PROMPT = """Create a comprehensive practice test from the following content.

Requirements:
- Generate exactly {count} questions total
- Include a mix of question types:
  * Multiple choice (about 50%) - 4 options each
  * True/False (about 25%)
  * Short answer (about 25%) - provide the expected answer
- Assign point values (1-3 points based on difficulty)
- Include explanations for all answers
- Cover key concepts comprehensively
- Progress from easier to harder questions
- Calculate the total points correctly

Content to create practice test from:

{content}"""


AUDIO_SUMMARY_PROMPT = """Create an audio-friendly summary of the following content.

The summary should be suitable for text-to-speech playback - clear, concise, and easy to understand when heard aloud.

Requirements:
- Write a brief 2-3 sentence overview that captures the essence of the content
- Identify {concept_count} key concepts with clear explanations
- Create {point_count} main takeaway points as complete sentences (not fragments)
- Write a memorable conclusion summarizing what's most important
- Use natural language that sounds good when spoken
- Avoid abbreviations, symbols, or complex formatting
- Estimate the read-aloud time in seconds (about 150 words per minute)

Content to summarize:

{content}"""


def get_flashcard_prompt(content: str, count: int = 10) -> str:
    """Generate the flashcard generation prompt."""
    return FLASHCARD_PROMPT.format(content=content, count=count)


def get_quiz_prompt(content: str, count: int = 10) -> str:
    """Generate the quiz generation prompt."""
    return QUIZ_PROMPT.format(content=content, count=count)


def get_practice_test_prompt(content: str, count: int = 15) -> str:
    """Generate the practice test generation prompt."""
    return PRACTICE_TEST_PROMPT.format(content=content, count=count)


def get_audio_summary_prompt(
    content: str, concept_count: int = 5, point_count: int = 7
) -> str:
    """Generate the audio summary generation prompt."""
    return AUDIO_SUMMARY_PROMPT.format(
        content=content, concept_count=concept_count, point_count=point_count
    )
