# StudyBros — Impeccable Audit Fix Plan

## Current State

**Done:** Phases 0–6, landing page overhaul, docs pages, initial code-reviewer audit (42 findings, 16 fixed).  
**Just Completed:** Impeccable UI engineering audit — 110 findings (21 CRITICAL, 52 HIGH, 32 MEDIUM, 5 LOW).  
**Not done:** Fix all 110 audit findings, then Vercel deployment.

## Dependency Graph

```
                    ┌─────────────────────┐
                    │ lib/hooks.ts        │  useApi (already has error field)
                    │ lib/types.ts        │  Type definitions
                    │ lib/constants.ts    │  Color/rating constants
                    └────────┬────────────┘
                             │ imported by everything
    ┌────────────────────────┼────────────────────────┐
    ▼                        ▼                        ▼
┌──────────┐      ┌──────────────────┐     ┌──────────────────┐
│ UI comps │      │ Gamification     │     │ Layouts / Global │
│ Button   │      │ KnowledgeHeatMap │     │ layout.tsx       │
│ Modal    │      │ ForgettingCurve  │     │ (app)/layout.tsx │
│ Toast    │      │ DifficultyMeter  │     │ error.tsx        │
│ Spinner  │      │ MasteryTree      │     │ not-found.tsx    │
│ Skeleton │      │ ConsistencyStreak│     │ AnimateIn.tsx    │
│ etc.     │      │ etc.             │     │ LandingNav.tsx   │
└─────┬────┘      └────────┬─────────┘     └────────┬─────────┘
      │                    │                         │
      └────────────────────┼─────────────────────────┘
                           ▼ used by
              ┌─────────────────────────┐
              │      Page Components     │
              │  dashboard  upload       │
              │  documents  generate     │
              │  study-sets study quiz   │
              │  test  complete progress │
              │  achievements docs       │
              └─────────────────────────┘
```

**Key insight:** Shared components (UI + gamification) must be fixed FIRST because pages depend on them. Layouts/globals are parallel-safe with components since they don't import each other.

## Strategy: 5 Batches with Checkpoints

### Batch 1 — Foundation Layer (shared components + layouts + new ErrorState)
Create `ErrorState` component. Fix all UI components, gamification components, layouts, error boundaries, not-found, AnimateIn, LandingNav. These are leaf dependencies — no page files touched.

**Parallel subagents (4):**
- Agent A: UI components (Button, Modal, Toast, Spinner, Skeleton, ProgressBar, Badge, EmptyState)
- Agent B: Gamification components (all 10)
- Agent C: Layouts + error boundaries + not-found + AnimateIn
- Agent D: LandingNav (mobile hamburger menu — largest single change in Batch 1)

### Batch 2 — Marketing Pages (no overlap with app pages)
Fix landing page, docs, docs/ai-setup. These are server components that don't share files with app pages.

**Parallel subagent (1):**
- Agent E: All 3 marketing pages

### Batch 3 — App Pages: Documents & Upload Flow
Fix dashboard, upload, documents, documents/[id], documents/[id]/generate, achievements, progress. Wire up `useApi` error + create ErrorState usage.

**Parallel subagents (3):**
- Agent F: dashboard + achievements + progress (read-only pages, similar patterns)
- Agent G: upload (drag-drop keyboard access, file validation, aria-live)
- Agent H: documents + documents/[id] + documents/[id]/generate (forms, modals, API keys)

### Batch 4 — App Pages: Study Flow (most complex)
Fix study-sets list, study-sets/[id], study, quiz, test, complete. These have the most interactive a11y issues (focus management, aria-live, radiogroup semantics).

**Parallel subagents (3):**
- Agent I: study-sets/page.tsx + study-sets/[id]/page.tsx (list + detail)
- Agent J: study/page.tsx (flashcard flow — C4, C6, C21, H16, H17, H34, H35, M17)
- Agent K: quiz/page.tsx + test/page.tsx + complete/page.tsx (quiz/test flow — C5, C17–C20, H18–H20, M19–M21)

### Batch 5 — Verification Gate
Build + lint. Verify all fixes. User review checkpoint.

## File Ownership Map (no conflicts)

| Batch | Agent | Files (exclusive ownership) |
|-------|-------|---------------------------|
| 1 | A | `components/ui/Button.tsx`, `Modal.tsx`, `Toast.tsx`, `Spinner.tsx`, `Skeleton.tsx`, `ProgressBar.tsx`, `Badge.tsx`, `EmptyState.tsx`, NEW `components/ui/ErrorState.tsx` |
| 1 | B | All 10 `components/gamification/*.tsx` |
| 1 | C | `app/layout.tsx`, `app/(app)/layout.tsx`, `app/error.tsx` (→ rename `global-error.tsx`), `app/(app)/error.tsx`, `app/not-found.tsx`, `components/AnimateIn.tsx` |
| 1 | D | `components/LandingNav.tsx` |
| 2 | E | `app/page.tsx`, `app/docs/page.tsx`, `app/docs/ai-setup/page.tsx` |
| 3 | F | `app/(app)/dashboard/page.tsx`, `app/(app)/achievements/page.tsx`, `app/(app)/progress/page.tsx` |
| 3 | G | `app/(app)/upload/page.tsx` |
| 3 | H | `app/(app)/documents/page.tsx`, `app/(app)/documents/[id]/page.tsx`, `app/(app)/documents/[id]/generate/page.tsx` |
| 4 | I | `app/(app)/study-sets/page.tsx`, `app/(app)/study-sets/[id]/page.tsx` |
| 4 | J | `app/(app)/study-sets/[id]/study/page.tsx` |
| 4 | K | `app/(app)/study-sets/[id]/quiz/page.tsx`, `app/(app)/study-sets/[id]/test/page.tsx`, `app/(app)/study-sets/[id]/complete/page.tsx` |

Zero file conflicts between parallel agents within any batch.

## Checkpoint Gates

After each batch:
1. `npm run lint` — 0 errors
2. `npm run build` — successful (all 17 routes)
3. Diff review — verify changes match intended fixes
4. No regressions — existing functionality preserved

After Batch 4: **USER REVIEW CHECKPOINT** — present all fixes for approval before Vercel deployment.
