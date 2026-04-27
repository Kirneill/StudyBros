# Tools Reference

StudyBros exposes 10 MCP tools. All tools return a string -- either a success message or a JSON-encoded result. Errors are returned as strings prefixed with `"Error: "`.

---

## ingest_file

Ingest a single file into StudyBros. Extracts text, chunks it, and stores it in the database.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `file_path` | string | yes | Absolute path to the file to ingest |

**Returns:** Summary string with word count, chunk count, and document ID.

**Example:** "Ingest the file at /home/user/notes/chapter1.pdf"

**Supported formats:** PDF, PPTX, TXT, MD, video, audio. Video/audio require FFmpeg.

**Deduplication:** Files are hashed. Re-ingesting the same file is a no-op.

---

## ingest_directory

Ingest all supported files from a directory.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `directory_path` | string | yes | Absolute path to the directory |
| `skip_existing` | boolean | no (default: true) | Skip files already ingested (by hash) |

**Returns:** Summary string with counts of processed, skipped, and failed files.

**Example:** "Ingest all files from /home/user/lectures"

---

## store_study_set

Store a generated study set. The LLM generates the content (via a prompt); this tool persists it.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `document_id` | integer | yes | ID of the source document |
| `set_type` | string | yes | One of: `flashcards`, `quiz`, `practice_test`, `audio_summary` |
| `title` | string | yes | Descriptive title for the study set |
| `content_json` | string | yes | JSON string matching the schema for the given set_type |

**Returns:** Confirmation with study set ID and item count.

**Schemas:**

Flashcards (`set_type="flashcards"`):
```json
{
  "cards": [
    {
      "question": "What is...",
      "answer": "It is...",
      "tags": ["topic1"],
      "difficulty": "easy|medium|hard"
    }
  ]
}
```

Quiz (`set_type="quiz"`):
```json
{
  "questions": [
    {
      "prompt": "Which of the following...",
      "options": [{"label": "A", "text": "..."}, {"label": "B", "text": "..."}],
      "correct_index": 0,
      "explanation": "Because..."
    }
  ]
}
```

Practice test (`set_type="practice_test"`):
```json
{
  "title": "Chapter 5 Test",
  "questions": [
    {
      "question_type": "multiple_choice|short_answer|true_false",
      "prompt": "...",
      "options": [{"label": "A", "text": "..."}],
      "correct_answer": "...",
      "explanation": "...",
      "points": 1
    }
  ],
  "total_points": 15
}
```

Audio summary (`set_type="audio_summary"`):
```json
{
  "title": "...",
  "overview": "2-3 sentence overview",
  "key_concepts": [
    {"concept": "...", "explanation": "...", "importance": "essential|important|supplementary"}
  ],
  "main_points": ["point as a sentence", "..."],
  "conclusion": "...",
  "estimated_read_time_seconds": 120
}
```

---

## record_review

Record a flashcard review for FSRS spaced repetition scheduling.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `study_set_id` | integer | yes | ID of the study set |
| `card_index` | integer | yes | Zero-based index of the card in the set |
| `rating` | integer | yes | 1=Again, 2=Hard, 3=Good, 4=Easy |
| `confidence` | integer | no (default: 0) | Self-reported confidence 1-5 (0 to skip) |

**Returns:** Next review date, stability value, and card state.

**Example:** After a user rates a card as "Good", call `record_review(study_set_id=1, card_index=3, rating=3)`.

---

## get_due_cards

Get cards due for review in a study set, ordered by FSRS urgency.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `study_set_id` | integer | yes | ID of the study set |

**Returns:** JSON string with `due_count` and `cards` array. Cards are sorted by lowest retrievability (most urgent first). Each card includes `card_id`, `retrievability`, `state`, and `last_review`.

**Example:** "Which cards are due for review in study set 1?"

---

## check_mastery

Check if a topic is mastered.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `topic` | string | yes | Topic tag to check |

**Returns:** JSON string with mastery status and detailed breakdown.

**Mastery criteria (all must be met):**
- All cards: current retrievability > 90%
- All cards: most recent scheduled interval > 30 days
- Average accuracy over last 3 reviews per card > 85%
- Bloom's taxonomy level >= 3 (Apply)

**Example:** "Have I mastered the topic 'data structures'?"

---

## get_strengths_weaknesses

Analyze strengths and weaknesses across all studied topics.

**Parameters:** None.

**Returns:** JSON string with:
- `strengths`: topics with > 80% accuracy and Bloom level >= 3
- `weaknesses`: topics with < 70% accuracy or Bloom level < 2
- `recommendations`: specific study actions
- `calibration`: confidence vs. actual accuracy comparison

**Example:** "What are my strengths and weaknesses?"

---

## export_study_set

Export a study set to a file.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `study_set_id` | integer | yes | ID of the study set |
| `format` | string | no (default: "json") | Export format: `json`, `anki`, or `markdown` |

**Returns:** File path of the exported file.

**Example:** "Export study set 1 as an Anki deck"

---

## delete_document

Delete a document and all associated data (chunks, study sets).

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `document_id` | integer | yes | ID of the document to delete |

**Returns:** Confirmation message.

**Example:** "Delete document 3 and all its study materials"

---

## delete_study_set

Delete a study set and its review history.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `study_set_id` | integer | yes | ID of the study set to delete |

**Returns:** Confirmation message.

**Example:** "Delete study set 5"
