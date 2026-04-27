# StudyBros Presentation Guide

This guide is for teammates presenting StudyBros while running it locally.

## What StudyBros Is

StudyBros turns raw learning material into study assets and a spaced-repetition workflow.

Core value:
- Upload class material, notes, slides, or recordings
- Generate flashcards, quizzes, practice tests, or summaries with AI
- Review with scheduling and progress tracking instead of passive rereading

## Local Demo Setup

From `F:\CLAUDE\Capstone1\Code`:

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

From `F:\CLAUDE\Capstone1\Code\frontend`:

```powershell
npm run dev -- --hostname 127.0.0.1 --port 3000
```

Open:
- `http://127.0.0.1:3000`

## What To Prepare Before Presenting

- Have 2-3 small sample files ready:
  - one `.txt` or `.md`
  - one `.pdf` or `.pptx`
  - optionally one short audio or video file
- Have an AI API key ready:
  - OpenAI
  - Claude
  - or OpenRouter

## Recommended Demo Flow

### 1. Open With The Problem

Say:

> Most students reread notes and still forget them. StudyBros turns static material into active recall and spaced repetition.

### 2. Show Upload

Go to:
- `http://127.0.0.1:3000/upload`

Talk track:
- The app accepts multiple files now, not just one at a time
- It supports PDFs, PPTX, text files, audio, and video
- Files are processed into extracted text and chunks for downstream generation

Action:
- Upload 2 or more files at once

### 3. Show The Document Library

Go to:
- `http://127.0.0.1:3000/documents`

Talk track:
- Each uploaded source becomes a document the app can generate study materials from
- This is the content layer that feeds every other workflow

### 4. Generate Study Material

Open any document and go to generate.

Talk track:
- Users can choose flashcards, quiz, practice test, or summary
- Users can choose OpenAI, Claude, or OpenRouter
- If the server does not already have a provider key configured, the UI prompts for one locally

Action:
- Choose a provider
- Enter an API key if prompted
- Generate flashcards

### 5. Show Review And Progress

Go to:
- `/study-sets`
- `/dashboard`
- `/progress`

Talk track:
- The app is not just generation
- It tracks progress, consistency, and what should be reviewed next
- The goal is retention over time, not one-off content generation

## What To Emphasize

- AI is used to create the study assets quickly
- The real product value is the workflow after generation
- Users are not locked into one model provider
- The app works locally and can be demoed without deployment

## If Something Goes Wrong During The Demo

### Upload fails

Check:
- backend is running on `127.0.0.1:8000`
- frontend is running on `127.0.0.1:3000`
- the file type is one of the supported formats

### Generation fails

Check:
- the selected provider key is valid
- the provider key was pasted into the modal if the server does not already have one

### Empty dashboard or progress view

Say:

> These views become more meaningful after review activity, so the key thing to notice here is the pipeline from upload to generated study material to tracked learning.

## Short Version If Time Is Tight

1. Upload 2 files
2. Open a document
3. Generate flashcards with a provider key
4. Open the study set
5. Show dashboard/progress

## One-Line Close

> StudyBros takes raw learning material and turns it into an AI-assisted, spaced-repetition study workflow that students can actually use day to day.
