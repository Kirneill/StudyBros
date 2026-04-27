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
