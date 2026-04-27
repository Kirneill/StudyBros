---
name: StudyBros
description: Use the StudyBros MCP server for AI-powered study material generation and spaced repetition
---

# StudyBros Skill

## Overview

StudyBros is an MCP server registered in this project's `.mcp.json`. It provides tools, resources, and prompts for:

- Ingesting documents (PDF, PPTX, TXT, MD, video, audio)
- Generating flashcards, quizzes, practice tests, summaries
- FSRS v5 spaced repetition scheduling
- Mastery tracking with Bloom's taxonomy
- Gamification (consistency streaks, achievements, phase detection)

## Workflow: Ingest -> Generate -> Study -> Master

### Step 1: Ingest Materials

- Use `ingest_file` tool for single files
- Use `ingest_directory` tool for batch ingestion
- Check ingested documents via `studybros://documents` resource

### Step 2: Generate Study Materials

- Use `generate_flashcards` prompt (recommended first)
- Use `generate_quiz` prompt for assessment
- Use `generate_practice_test` prompt for comprehensive review
- Use `generate_summary` prompt for overview
- IMPORTANT: After generating, call `store_study_set` tool with the generated JSON

### Step 3: Study with Spaced Repetition

- Use `study_flashcards` prompt for interactive sessions
- Present cards in FSRS priority order (lowest retrievability first)
- After each card: collect rating (1=Again, 2=Hard, 3=Good, 4=Easy)
- Call `record_review` tool with the rating
- Target ~85% accuracy (this is the optimal learning zone)

### Step 4: Track Progress

- Use `review_progress` prompt for a full report
- Check `studybros://progress` resource for knowledge heat map
- Check `studybros://progress/strengths-weaknesses` for detailed analysis
- Use `check_mastery` tool to see if a topic is mastered
- Mastery = retrievability >90% at >30-day intervals, accuracy >85%, Bloom Level 3+

## Tool Quick Reference

| Tool | When to use |
|------|-------------|
| `ingest_file` | User wants to add a document |
| `ingest_directory` | User wants to add multiple documents |
| `store_study_set` | After generating study materials |
| `record_review` | After user rates a flashcard |
| `get_due_cards` | Before starting a study session |
| `check_mastery` | User asks "am I done with this topic?" |
| `get_strengths_weaknesses` | User asks "what should I study?" |
| `export_study_set` | User wants to export to Anki/JSON/Markdown |
| `delete_document` | User wants to remove a document |
| `delete_study_set` | User wants to remove a study set |

## FSRS Rating Guide

When collecting user ratings for flashcard reviews:

- **1 (Again)**: Complete blank, couldn't recall at all
- **2 (Hard)**: Recalled with significant difficulty or errors
- **3 (Good)**: Recalled correctly with some effort
- **4 (Easy)**: Recalled instantly and effortlessly

## Resource Quick Reference

| Resource | Data |
|----------|------|
| `studybros://status` | Server status and DB stats |
| `studybros://documents` | All ingested documents |
| `studybros://study-sets` | All generated study sets |
| `studybros://study-sets/{id}/schedule` | FSRS schedule for a study set |
| `studybros://progress` | Knowledge heat map + gamification phase |
| `studybros://achievements` | Earned competency badges |

## Important Notes

- The MCP server uses stdio transport -- it is auto-started by Claude Code via `.mcp.json`
- No API key needed -- you (the LLM) generate the content directly
- All data is stored in a local SQLite database at `./data/study_guide.db`
- Study set types: `flashcards`, `quiz`, `practice_test`, `audio_summary`
- When generating content, always call `store_study_set` afterward to persist it
- The `generate_*` prompts return system instructions -- follow them to produce correctly formatted JSON
