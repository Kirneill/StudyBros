# StudyBros TODO — Session Tracker

Last updated: 2026-04-27

---

## COMPLETED

### 1. Fix Consistency Endpoint Type Mismatch
**Status:** DONE  
**Problem:** Backend `calculate_consistency_streak()` returned `{days_studied, window_days, percentage, current_week, message, studied_dates}` but frontend `ConsistencyData` type expected `{streak_days, consistency_pct_30d, studied_dates}`. This caused the dashboard and progress pages to crash — `new Set(undefined)` threw a runtime error caught by Next.js error boundary, showing "internal server error."

**Root cause:** No Pydantic response model on the `/consistency` route — the raw domain dict was returned directly, creating an implicit contract that didn't match the frontend type.

**Changes made:**
1. **`Code/api/schemas.py`** (line 125-128) — Added `ConsistencyResponse` Pydantic model:
   ```python
   class ConsistencyResponse(BaseModel):
       streak_days: int
       consistency_pct_30d: float
       studied_dates: list[str]
   ```

2. **`Code/api/routes/gamification.py`** (lines 7-12, 55-63) — Updated route to:
   - Import `ConsistencyResponse`
   - Add `response_model=ConsistencyResponse` to the route decorator
   - Map domain fields to API contract:
     - `streak_days` ← `data["current_week"]["days_studied"]` (rolling 7-day count, per gamification rules)
     - `consistency_pct_30d` ← `data["percentage"] / 100` (convert 0-100 → 0-1, because component does `Math.round(val * 100)`)
     - `studied_dates` ← passed through unchanged

**No changes needed to:**
- `calculate_consistency_streak()` in `study_guide/learning/gamification.py` (domain function, untouched)
- `ConsistencyData` type in `frontend/src/lib/types.ts` (already correct)
- `ConsistencyStreak` component in `frontend/src/components/gamification/ConsistencyStreak.tsx` (already correct)
- Dashboard page or Progress page (they already pass the right prop names)

**Verification (updated 2026-04-27):**
- `pytest -q` now passes after aligning the stale API test with the new contract
- Full backend automated suite passed: `199 passed`
- `Code/tests/test_api.py` now asserts the current `/gamification/consistency` shape:
  `{streak_days, consistency_pct_30d, studied_dates}`
- Added schedule endpoint coverage so the frontend-facing study API has contract tests beyond the original crash path

### 4. Verify Backend/Frontend Contract for ALL Endpoints
**Status:** BACKEND APP SURFACE VERIFIED  
**Scope completed this session:** Audited FastAPI response models/routes against the frontend client/types for the backend-served app surface, then tightened runtime tests to catch contract drift.

**What was checked:**
1. **Frontend contract definitions**
   - `Code/frontend/src/lib/api.ts`
   - `Code/frontend/src/lib/types.ts`
2. **Backend response models and route mappings**
   - `Code/api/schemas.py`
   - `Code/api/routes/study.py`
   - `Code/api/routes/gamification.py`
   - `Code/api/routes/documents.py`
   - `Code/api/routes/study_sets.py`
3. **Runtime test coverage**
   - Updated `Code/tests/test_api.py` to assert exact response keys for:
     - `/api/gamification/phase`
     - `/api/gamification/strengths-weaknesses`
     - `/api/gamification/consistency`
   - Added `/api/study/{study_set_id}/schedule` coverage for empty and populated states

**Result:**
- The known `/consistency` mismatch is fixed end-to-end at the API contract level
- No additional backend/frontend response-shape mismatches were found in the currently wired frontend app surface
- Full backend test suite passes after the test updates
- Live API smoke test passed against a temporary SQLite database using a real `uvicorn` process and HTTP requests:
  - `GET /api/health`
  - `GET /api/documents/`
  - `GET /api/study-sets/`
  - `GET /api/study/{id}/due`
  - `POST /api/study/{id}/review`
  - `GET /api/study/{id}/schedule`
  - `GET /api/gamification/phase`
  - `GET /api/gamification/strengths-weaknesses`
  - `GET /api/gamification/consistency`
- Lint and typecheck are clean for the backend codebase:
  - `ruff check .` → passes
  - `mypy study_guide api mcp_server` → passes

**Caveat:**
- Remaining warnings are deprecation-level cleanup items (`datetime.utcnow()` and FastAPI `on_event`), not current correctness failures.

### 6. Runtime API Key Prompt for Generation Providers
**Status:** DONE  
**Problem:** The generation flow hard-failed when the server lacked a valid OpenAI key. Users had no way to supply their own Claude, OpenAI, or OpenRouter key in the app and continue generation without editing backend env vars.

**Changes made:**
1. **Backend provider support**
   - `Code/study_guide/config.py`
   - `Code/study_guide/generation/generator.py`
   - `Code/api/routes/generate.py`
   - `Code/api/schemas.py`
   - `Code/mcp_server/server.py`
   - `Code/env.example.txt`
   - `Code/pyproject.toml`
   - Added provider-aware config for `openai`, `anthropic`, and `openrouter`
   - Added per-request `provider`, `api_key`, and optional `model` support on generation requests
   - Added `GET /api/generate/providers` so the frontend can discover which providers have server-side keys configured
   - Added Anthropic and OpenRouter generation paths while keeping the existing OpenAI path

2. **Frontend generate flow**
   - `Code/frontend/src/app/(app)/documents/[id]/generate/page.tsx`
   - `Code/frontend/src/lib/api.ts`
   - `Code/frontend/src/lib/types.ts`
   - Added provider picker for OpenAI, Claude, and OpenRouter
   - If the selected provider has no server key, the app now prompts the user for a key in a modal
   - The entered key is stored only in browser local storage and sent with the generation request
   - Added UI copy explaining whether generation is using a server-configured key or a browser-saved key

3. **Regression coverage**
   - `Code/tests/test_api.py`
   - Added coverage for:
     - `GET /api/generate/providers`
     - generation with a user-supplied provider key
     - rejecting generation when neither the server nor the request provides a key

**Verification (2026-04-27):**
- `pytest -q` -> `202 passed`
- `ruff check .` -> passes
- `mypy study_guide api mcp_server` -> passes
- `npm run lint` -> passes
- `npm run build` -> passes

### 7. Upload Reliability + Multi-File UX
**Status:** DONE  
**Problem:** Local uploads could fail because the frontend posted multipart data to `/api/upload` while the backend only handled `/api/upload/`, causing a redirect in the local proxy path. The upload UI also only allowed one file at a time and advertised `.docx`, which the backend does not actually support.

**Changes made:**
1. **Upload route hardening**
   - `Code/api/routes/upload.py`
   - Added handlers for both `/api/upload` and `/api/upload/` so multipart uploads work without a redirect edge case

2. **Frontend upload flow**
   - `Code/frontend/src/lib/api.ts`
   - `Code/frontend/src/app/(app)/upload/page.tsx`
   - `Code/frontend/next.config.ts`
   - Switched the client upload target to `/api/upload/`
   - Added multi-file selection and drag/drop
   - Files now upload sequentially in one user action
   - Added progress text during upload
   - Single-file success routes to the document page; multi-file success routes to the documents list
   - Updated accepted file extensions to match actual backend support
   - Removed the incorrect `.docx` claim from the upload UI
   - Increased Next.js proxy request buffering limit to `64mb` so local frontend uploads can pass large PDFs through to the backend without truncation

3. **Regression coverage**
   - `Code/tests/test_api.py`
   - Added coverage for uploads to `/api/upload` without the trailing slash

4. **Presentation handoff**
   - `Presentation.md`
   - Added a teammate-facing presentation guide with local setup steps and a demo script

**Verification (2026-04-27):**
- `pytest -q tests/test_api.py` -> `34 passed`
- `pytest -q` -> `203 passed`
- `npm run lint` -> passes
- `npm run build` -> passes
- Live smoke check through the frontend URL:
  - `POST http://127.0.0.1:3000/api/upload/` with `.txt` -> `200`
  - `POST http://127.0.0.1:3000/api/upload/` with `.md` -> `200`
  - zyBooks PDFs at 16.8 MB and 21.9 MB now upload successfully through the frontend proxy path after the `64mb` proxy limit change

### 8. Model Defaults + Upload Diagnostics
**Status:** DONE  
**Problem:** Generation defaults were still older models, and PDF upload failures could surface as a generic internal server error with poor debugging context.

**Changes made:**
1. **Provider default models**
   - `Code/study_guide/config.py`
   - `Code/env.example.txt`
   - Updated provider defaults to:
     - OpenAI -> `gpt-5.4`
     - Anthropic -> `claude-sonnet-4-6`
     - OpenRouter -> `anthropic/claude-sonnet-4.6`

2. **Upload diagnostics**
   - `Code/api/routes/upload.py`
   - Added stage-aware diagnostics for upload failures (`save`, `scan`, `select extractor`, `hash`, `extract`, `deduplicate`, `persist source`, `persist document`, `chunk`)
   - Added persistent upload logging to `Code/logs/upload_diagnostics.log`
   - Unexpected exceptions now return a file- and stage-specific API error instead of a generic `500`

3. **PDF extraction hardening**
   - `Code/study_guide/ingestion/extractors/pdf_extractor.py`
   - Normalizes metadata titles safely
   - Detects encrypted PDFs explicitly
   - Tracks failed pages during extraction
   - Returns a clean extraction failure when a PDF has no extractable text instead of silently producing an empty document

4. **Regression coverage**
   - `Code/tests/test_api.py`
   - Added invalid PDF upload coverage so malformed PDFs return a diagnostic `422` instead of a generic server error

**Verification (2026-04-27):**
- `pytest -q tests/test_api.py` -> `35 passed`
- `pytest -q` -> `204 passed`
- `ruff check .` -> passes
- `mypy study_guide api mcp_server` -> passes
- `npm run lint` -> passes
- `npm run build` -> passes
- Live checks:
  - `GET /api/generate/providers` returns `gpt-5.4`, `claude-sonnet-4-6`, and `anthropic/claude-sonnet-4.6`
  - invalid PDF upload now returns:
    - `Upload failed during extract for "broken.pdf": Stream has ended unexpectedly`

### 9. Document Management + Personal Key Override UX
**Status:** DONE  
**Problem:** Documents could not be renamed from the app, there was no multi-select management flow, and generation could trap users on a bad server-side provider key with no obvious way to override it with their own browser-saved key.

**Changes made:**
1. **Document management API**
   - `Code/api/routes/documents.py`
   - `Code/api/schemas.py`
   - `Code/study_guide/database/operations.py`
   - Added document rename support
   - Added bulk delete support for multiple selected documents

2. **Documents UI**
   - `Code/frontend/src/app/(app)/documents/page.tsx`
   - `Code/frontend/src/lib/api.ts`
   - `Code/frontend/src/lib/types.ts`
   - Added multi-select checkboxes on the documents grid
   - Added select-all / clear-selection behavior
   - Added bulk delete modal
   - Added rename modal directly from the documents screen

3. **Provider key override UX**
   - `Code/frontend/src/app/(app)/documents/[id]/generate/page.tsx`
   - Added an explicit personal-key action even when the server has a configured key
   - Browser-saved key now clearly overrides the server key
   - Provider auth/billing/credit errors now reopen the key modal so the user can enter a replacement key immediately
   - Fixed provider status messaging so it reflects the actual key in use

4. **Regression coverage**
   - `Code/tests/test_api.py`
   - Added rename-document coverage
   - Added bulk-delete-documents coverage

**Verification (2026-04-27):**
- `pytest -q tests/test_api.py` -> `37 passed`
- `pytest -q` -> `206 passed`
- `ruff check .` -> passes
- `mypy study_guide api mcp_server` -> passes
- `npm run lint` -> passes
- `npm run build` -> passes

### 10. Study Set Content Rendering Fix
**Status:** DONE  
**Problem:** Generated study sets were stored in structured wrapper objects like `{"cards": [...]}` and `{"questions": [...]}`, but several frontend study-set pages only rendered top-level arrays. This made valid generated content appear empty, including the zyBooks flashcard set showing `10 items` while the detail page rendered `Content (0 items)`.

**Changes made:**
1. **Study set detail normalization**
   - `Code/frontend/src/app/(app)/study-sets/[id]/page.tsx`
   - Added structured-content normalization for `cards`, `questions`, `key_concepts`, and `main_points`
   - Flashcard preview now reads both `front/back` and `question/answer`

2. **Study flashcards normalization**
   - `Code/frontend/src/app/(app)/study-sets/[id]/study/page.tsx`
   - Flashcard study view now reads `content.cards` instead of assuming a top-level array

3. **Quiz/test normalization**
   - `Code/frontend/src/app/(app)/study-sets/[id]/quiz/page.tsx`
   - `Code/frontend/src/app/(app)/study-sets/[id]/test/page.tsx`
   - Updated parsers to handle the backend’s stored `questions` shape and option objects

**Verification (2026-04-27):**
- `npm run lint` -> passes
- `npm run build` -> passes
- Live data check on the generated zyBooks flashcard set confirmed:
  - `set_type = flashcards`
  - `item_count = 10`
  - `content` is a dict with `cards`
  - `len(content.cards) = 10`

### 11. Progress Tracking + Flashcard Session Persistence
**Status:** DONE  
**Problem:** Completing flashcards could still leave `/progress` empty because card reviews were being stored without creating `UserProgress` rows, and completed flashcard sessions were not being persisted as `StudySession` records for phase/consistency analytics.

**Changes made:**
1. **Review-to-progress persistence**
   - `Code/api/routes/study.py`
   - `POST /api/study/{study_set_id}/review` now derives the reviewed card’s topic tags from the stored study-set content and upserts `UserProgress` rows on every review

2. **Backfill for existing review history**
   - `Code/api/routes/study.py`
   - `GET /api/study/progress` now reconstructs `UserProgress` from historical `CardReview` data when old sessions exist but progress rows are missing

3. **Flashcard session persistence**
   - `Code/api/schemas.py`
   - `Code/api/routes/study.py`
   - `Code/frontend/src/lib/types.ts`
   - `Code/frontend/src/lib/api.ts`
   - `Code/frontend/src/app/(app)/study-sets/[id]/study/page.tsx`
   - Added `POST /api/study/{study_set_id}/session`
   - The flashcard study flow now saves a completed session before showing the completion screen, including total items, correct count, confidence sum, and Bloom distribution
   - Session-derived analytics like phase and consistency now have real flashcard-session data instead of only card reviews

4. **Regression coverage**
   - `Code/tests/test_api.py`
   - Added coverage for:
     - review creating progress rows
     - progress backfilling from legacy review history
     - flashcard session completion updating gamification session counts and consistency data

---

## IN PROGRESS

### 2. Landing Page Overhaul — Behavioral Economics + MCP/LLM Messaging
**Status:** RESEARCH COMPLETE, IMPLEMENTATION PENDING  
**Current landing page file:** `Code/frontend/src/app/page.tsx`

**Problems with current page:**
- Generic hero copy ("Master your material, not just review it")
- No mention of MCP server, LLM Skills, or the three delivery surfaces
- No feature breakdown, screenshots, comparison, or social proof
- Two competing CTAs of equal weight ("Get Started" + "Upload Material")
- Trust bar uses jargon (FSRS v5, Bloom's) without context

**Research completed — content brief ready:**
Anki's landing page (ankiweb.net) analyzed. Behavioral economics principles mapped to 9 sections:

| Section | Principle | Purpose |
|---|---|---|
| 1. Hero | Loss Aversion + Anchoring | "You forget 70% in 24 hours" — forgetting curve framing |
| 2. Problem (Forgetting Curve) | Loss Aversion | Interactive/animated forgetting curve visualization |
| 3. Three Ways to Study | Status Quo Bias | MCP Server, LLM Skills, Web App — "zero new habits" |
| 4. How It Works | Commitment/Consistency | Upload → Generate → Master — 3-step micro-commitments |
| 5. Science Section | Anchoring + Authority | FSRS v5, Bloom's, 85% rule, Mastery with research citations |
| 6. Comparison Table | Anchoring | StudyBros vs Traditional vs Anki vs Quizlet |
| 7. Social Proof | Social Proof + Authority | Testimonials or research authority quotes |
| 8. Instant Value CTA | Endowment Effect | Embed upload/paste on landing page — create ownership before signup |
| 9. Footer CTA | Loss Aversion | "Every hour without SR, you lose 70%" |

**Headline options for hero:**
- "You forget 70% of what you study within 24 hours. Unless you don't."
- "Stop re-learning what you already studied."
- "Your brain forgets. StudyBros remembers for you."

**CTA strategy:** Single primary CTA ("Try It Free — No Account Needed"), progressive commitment escalation through the page.

**Next step:** Run impeccable skills (audit, frontend-design) to implement the new landing page based on this brief.

---

## NOT STARTED

### 3. Full UI/UX Review (Impeccable Audit)
**Status:** PENDING (after landing page implementation)  
**Scope:** Run `impeccable:audit` across the full frontend — dashboard, progress, study pages, achievements, upload flow. Check a11y, performance, resilience, and design consistency.

### 5. Test the Fix End-to-End
**Status:** COMPLETE  
**Verification completed this session:**  
- `pytest -q` passed for the full backend suite after contract-test updates
- Live `uvicorn` smoke test passed against the main app endpoints
- Real browser validation passed for `/dashboard` and `/progress` against live frontend + backend with seeded study data:
  - Both pages returned HTTP 200
  - Expected page markers rendered (`Knowledge Map`, `Knowledge Heat Map`)
  - No browser console errors or warnings were captured
  - No failed network requests were captured

**Steps:**
1. Start backend: `cd Code && uvicorn api.main:app --reload`
2. Start frontend: `cd Code/frontend && npm run dev`
3. Navigate to `/dashboard` — consistency section should render without error
4. Navigate to `/progress` — consistency section should render without error
5. Verify the 7-day calendar shows correct studied dates
6. Verify the 30-day percentage displays correctly

---

## CONTEXT FOR NEXT SESSION

- **Project:** StudyBros — AI-powered study platform (Capstone1)
- **Tech stack:** FastAPI (Python) + Next.js 16 / React 19 / TypeScript 5 / Tailwind 4
- **Project root:** `F:\CLAUDE\Capstone1\`
- **Code root:** `F:\CLAUDE\Capstone1\Code\`
- **Frontend:** `F:\CLAUDE\Capstone1\Code\frontend\`
- **Project CLAUDE.md:** `F:\CLAUDE\Capstone1\CLAUDE.md` — has full architecture, conventions, phase checklist
- **Research docs:** `F:\CLAUDE\Capstone1\StudyGuideResearch/` — read `00-INDEX.md` first
- **Three delivery surfaces:** MCP Server, LLM Skills + docs, Web App on Vercel
- **Design tokens:** Dark theme — bg #1A1A2E, cards #232342, accent teal #00D4AA, text ivory #F5F0EB
