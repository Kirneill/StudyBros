# Prompts Reference

StudyBros exposes 8 MCP prompts. Prompts provide structured instructions and context to the LLM. Some prompts instruct the LLM to call tools as a follow-up action.

---

## generate_flashcards

Generate flashcards from a document's content.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `document_id` | integer | yes | ID of the source document |
| `count` | integer | no (default: 10) | Number of flashcards to generate |
| `difficulty` | string | no (default: "mixed") | Target difficulty: `easy`, `medium`, `hard`, or `mixed` |

**Behavior:** Loads the document's text chunks, constructs a generation prompt with the flashcard JSON schema, and instructs the LLM to generate flashcards and then call `store_study_set` to persist them.

**Expected LLM follow-up:** Call `store_study_set(document_id=<id>, set_type="flashcards", title=<title>, content_json=<generated JSON>)`.

**Example:** "Generate 20 hard flashcards from document 1"

---

## generate_quiz

Generate a multiple-choice quiz from a document.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `document_id` | integer | yes | ID of the source document |
| `count` | integer | no (default: 10) | Number of questions |

**Behavior:** Loads document chunks, provides the quiz JSON schema, and instructs the LLM to generate questions with options, correct answers, and explanations.

**Expected LLM follow-up:** Call `store_study_set(document_id=<id>, set_type="quiz", title=<title>, content_json=<generated JSON>)`.

**Example:** "Create a 15-question quiz from document 2"

---

## generate_practice_test

Generate a practice test with mixed question types (multiple choice, short answer, true/false).

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `document_id` | integer | yes | ID of the source document |
| `count` | integer | no (default: 15) | Number of questions |

**Behavior:** Same as quiz generation but with mixed question types and point values.

**Expected LLM follow-up:** Call `store_study_set(document_id=<id>, set_type="practice_test", title=<title>, content_json=<generated JSON>)`.

**Example:** "Generate a practice test with 20 questions from document 3"

---

## generate_summary

Generate an audio-friendly summary of a document.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `document_id` | integer | yes | ID of the source document |

**Behavior:** Loads document chunks and instructs the LLM to produce a structured summary with overview, key concepts, main points, and conclusion -- designed for reading aloud or TTS playback.

**Expected LLM follow-up:** Call `store_study_set(document_id=<id>, set_type="audio_summary", title=<title>, content_json=<generated JSON>)`.

**Example:** "Summarize document 1 for audio playback"

---

## study_flashcards

Run an interactive flashcard study session with FSRS spaced repetition.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `study_set_id` | integer | yes | ID of the flashcard study set |

**Behavior:** Loads the study set's cards and FSRS due-card data. Instructs the LLM to:

1. Present due cards first (lowest retrievability = most urgent)
2. Show the question and wait for the user's answer
3. Reveal the correct answer and evaluate correctness
4. Ask the user to rate: Again (1) / Hard (2) / Good (3) / Easy (4)
5. Call `record_review` with the rating
6. Report the next review date
7. Summarize the session at the end

**Example:** "Let's study -- start a flashcard session for study set 1"

---

## take_quiz

Run an interactive quiz session with scoring.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `study_set_id` | integer | yes | ID of the quiz study set |

**Behavior:** Loads the quiz questions. Instructs the LLM to:

1. Present one question at a time with options
2. Wait for the user's answer
3. Reveal if correct/incorrect with explanation
4. Track score throughout
5. Show final score and missed questions at the end
6. Suggest topics to review based on missed questions

**Example:** "I want to take the quiz for study set 2"

---

## explain_concept

Explain a concept using the Feynman technique, grounded in document content.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `document_id` | integer | yes | ID of the source document |
| `concept` | string | yes | The concept to explain |

**Behavior:** Loads the document's text as context. Instructs the LLM to explain the concept as if teaching a beginner: simple language, analogies, concrete examples, common misconceptions, and a self-test question.

**Example:** "Explain 'binary search trees' using document 1 as reference"

---

## review_progress

Generate a study progress report with strengths, weaknesses, and recommendations.

**Parameters:** None.

**Behavior:** Loads all progress data (topics, mastery levels, Bloom levels, review counts), strengths/weaknesses analysis, achievements, consistency streaks, and gamification phase. Instructs the LLM to present a report covering:

1. Overall progress overview
2. Current gamification phase
3. Strengths and weaknesses
4. Specific recommendations
5. Consistency streak
6. Earned achievements
7. Confidence calibration notes
8. Suggested next study action

**Example:** "Show me my study progress report"
