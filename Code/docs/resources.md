# Resources Reference

StudyBros exposes 9 MCP resources. Resources are read-only data endpoints accessed by URI. All return JSON-encoded strings.

---

## studybros://status

Server status, configuration, and database statistics.

**Returns:**
```json
{
  "version": "0.1.0",
  "db_path": "/path/to/data/study_guide.db",
  "generation_model": "gpt-4o",
  "stats": {
    "documents": 5,
    "study_sets": 12,
    "chunks": 87
  }
}
```

---

## studybros://documents

All ingested documents with metadata.

**Returns:**
```json
[
  {
    "id": 1,
    "title": "Chapter 1 - Introduction",
    "word_count": 3420,
    "chunk_count": 8,
    "created_at": "2025-01-15T10:30:00"
  }
]
```

---

## studybros://documents/{doc_id}/chunks

All text chunks for a specific document. Used as context for study material generation.

**URI parameter:** `doc_id` -- integer document ID.

**Returns:**
```json
[
  {
    "chunk_index": 0,
    "content": "The first section of text...",
    "char_count": 1500
  }
]
```

---

## studybros://study-sets

All generated study sets.

**Returns:**
```json
[
  {
    "id": 1,
    "type": "flashcards",
    "title": "Chapter 1 Flashcards",
    "item_count": 20,
    "document_id": 1,
    "created_at": "2025-01-15T11:00:00"
  }
]
```

---

## studybros://study-sets/{set_id}

A specific study set with its full content (all cards/questions).

**URI parameter:** `set_id` -- integer study set ID.

**Returns:**
```json
{
  "id": 1,
  "type": "flashcards",
  "title": "Chapter 1 Flashcards",
  "item_count": 20,
  "document_id": 1,
  "created_at": "2025-01-15T11:00:00",
  "content": {
    "cards": [
      {
        "question": "What is...",
        "answer": "It is...",
        "tags": ["intro"],
        "difficulty": "medium"
      }
    ]
  }
}
```

---

## studybros://study-sets/{set_id}/schedule

FSRS review schedule for a study set. Shows due cards and predicted retention for all reviewed cards.

**URI parameter:** `set_id` -- integer study set ID.

**Returns:**
```json
{
  "study_set_id": 1,
  "due_count": 3,
  "due_cards": [
    {
      "card_id": 5,
      "retrievability": 0.72,
      "state": "review",
      "last_review": "2025-01-14T09:00:00"
    }
  ],
  "all_cards": [
    {
      "card_id": 5,
      "retrievability": 0.72,
      "stability": 4.2,
      "state": "review",
      "last_review": "2025-01-14T09:00:00",
      "scheduled_days": 5.0
    }
  ]
}
```

Cards in `due_cards` have retrievability below the 90% target. `all_cards` includes every reviewed card sorted by retrievability (lowest first).

---

## studybros://progress

Knowledge heat map with per-topic mastery, Bloom levels, consistency, and gamification phase.

**Returns:**
```json
{
  "topics": [
    {
      "topic": "data structures",
      "mastery_level": 0.85,
      "bloom_highest_level": 3,
      "total_reviews": 45,
      "last_reviewed_at": "2025-01-15T10:00:00",
      "calibration_score": 0.92,
      "consistency_pct_30d": 71.4
    }
  ],
  "consistency": {
    "current_streak": 5,
    "longest_streak": 12,
    "days_active_last_30": 20
  },
  "phase": {
    "phase": "competence",
    "description": "Building deep understanding",
    "weeks_active": 8
  }
}
```

**Gamification phases:**
- **Habit** (weeks 1-4): Building study routine
- **Competence** (months 2-3): Deepening understanding
- **Intrinsic** (month 4+): Self-directed mastery

---

## studybros://progress/strengths-weaknesses

Detailed strengths, weaknesses, and study recommendations.

**Returns:**
```json
{
  "strengths": [
    {
      "topic": "algorithms",
      "accuracy": 0.92,
      "bloom_level": 4
    }
  ],
  "weaknesses": [
    {
      "topic": "operating systems",
      "accuracy": 0.61,
      "bloom_level": 1
    }
  ],
  "recommendations": [
    "Focus on operating systems -- accuracy is below 70%",
    "Review data structures cards that are overdue"
  ],
  "calibration": {
    "overconfident_topics": ["networking"],
    "underconfident_topics": []
  }
}
```

---

## studybros://achievements

All earned competency badges. Achievements require demonstrated Bloom level, not just participation.

**Returns:**
```json
[
  {
    "name": "Data Structures Master",
    "topic": "data structures",
    "earned_at": "2025-01-15T10:00:00",
    "criteria": "Bloom level 4+, accuracy > 90%, 30-day retention"
  }
]
```
