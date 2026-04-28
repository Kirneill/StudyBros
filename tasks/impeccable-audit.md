# Impeccable UI Engineering Audit — StudyBros Frontend

**Methodology:** `frontend-ui-engineering` skill + WCAG 2.1 AA accessibility checklist + performance checklist + security checklist  
**Date:** 2026-04-27  
**Scope:** All 16 pages, 2 layouts, 2 error boundaries, 1 not-found, 21 components (42 files total)

---

## Executive Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 21 |
| HIGH | 52 |
| MEDIUM | 32 |
| LOW | 5 |
| **Total** | **110** |

### Top 5 Systemic Issues

1. **`useApi` error state never consumed** — All pages discard API errors, making network failures indistinguishable from empty data (affects all 7 app pages)
2. **No `aria-live` regions for dynamic content** — Card reveals, quiz feedback, score updates, upload progress — all silent to screen readers
3. **No `prefers-reduced-motion` guard** — `AnimateIn` wraps every animated element site-wide; no motion reduction
4. **Color as sole indicator** — Heatmap, forgetting curve, difficulty meter, quiz correct/incorrect, phase dots all rely on color alone
5. **Touch targets undersized** — Mobile nav, confidence buttons, modal close button all below 44×44px WCAG minimum

---

## CRITICAL Findings (21)

### C1. `useApi` error state never consumed (ALL APP PAGES)
- **Files:** dashboard, upload, documents, documents/[id], documents/[id]/generate, achievements, progress, study-sets, study-sets/[id], study-sets/[id]/study, quiz, test
- **Impact:** Every API failure silently degrades to empty/loading state. Users cannot distinguish "no data" from "server unreachable."
- **Fix:** Destructure `error` from all `useApi` calls. Create reusable `<ErrorState>` component with retry button.

### C2. Drag-and-drop zone has no keyboard activation (`upload/page.tsx`)
- **Lines:** 125–153
- **Impact:** Keyboard-only users cannot interact with the prominent drop zone. The "Choose Files" button works as fallback, but the drop zone itself appears interactive (dashed border, state changes) yet is inaccessible. WCAG 2.1.1.
- **Fix:** Add `role="button"`, `tabIndex={0}`, `onKeyDown` (Enter/Space → file picker), `aria-label`.

### C3. No client-side file size validation (`upload/page.tsx`)
- **Lines:** handleFiles function
- **Impact:** UI says "up to 50 MB each" but nothing enforces it. Users wait through full upload before server-side rejection.
- **Fix:** Check `file.size > 50 * 1024 * 1024` before upload; push error to `failedUploads`.

### C4. Card flip/reveal has no screen reader announcement (`study/page.tsx`)
- **Lines:** 275–296
- **Impact:** Core flashcard interaction. Clicking "Show Answer" appends answer text with no `aria-live`, no `aria-expanded`. Screen reader users hear nothing.
- **Fix:** Wrap answer section in `<div aria-live="polite" aria-atomic="true">`.

### C5. Quiz answer feedback not announced (`quiz/page.tsx`)
- **Lines:** 257–282
- **Impact:** After selecting an answer, correct/incorrect state shown via color only. No `aria-live` announcement. Screen reader users get no feedback.
- **Fix:** Add `<div aria-live="assertive" className="sr-only">` with correctness text.

### C6. No keyboard support for card navigation focus (`study/page.tsx`)
- **Impact:** After "Show Answer" hides, focus stays on the now-hidden button. Keyboard users lose focus context. Rating buttons appear but aren't focused.
- **Fix:** `useEffect` to focus first rating button when `revealed` becomes true.

### C7. KnowledgeHeatMap cells are color-only with no text alternatives (`KnowledgeHeatMap.tsx`)
- **Lines:** 19–24
- **Impact:** Each cell is a colored `div` with only a `title` attribute (not keyboard-accessible, unreliably announced). WCAG 1.4.1 and 1.1.1 both fail.
- **Fix:** Add `aria-label={`${t.topic}: ${getMasteryLabel(t.mastery_level)}`}` to each cell.

### C8. ForgettingCurve bars have no accessible role or label (`ForgettingCurve.tsx`)
- **Lines:** 22–33
- **Impact:** Color-coded retention bars with no `role="progressbar"`, no `aria-label`. Screen readers read nothing.
- **Fix:** Add `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, `aria-label`.

### C9. DifficultyMeter has no accessible role (`DifficultyMeter.tsx`)
- **Lines:** 31–38
- **Impact:** Visual positioning widget with no ARIA semantics. Screen readers hear nothing.
- **Fix:** Add `role="meter"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`, `aria-label`.

### C10. Modal focus not restored on close (`Modal.tsx`)
- **Lines:** 13–43
- **Impact:** When dialog closes, focus lands unpredictably in the DOM. Screen reader users lose context.
- **Fix:** Capture `document.activeElement` before `showModal()`, restore in `onClose`.

### C11. Toast `role="alert"` unreliable on conditional mount (`Toast.tsx`)
- **Lines:** 36–44
- **Impact:** `role="alert"` on a conditionally-mounted element is unreliable in Safari/VoiceOver. Messages missed.
- **Fix:** Persistent `<div aria-live="assertive">` in layout; Toast writes content into it rather than mounting/unmounting.

### C12. API key storage in `localStorage` with no expiry (`generate/page.tsx`)
- **Lines:** 47–59, 107–113
- **Impact:** Keys persist indefinitely, enumerable via predictable prefix `studybros_api_key:`. Any XSS exposes all keys.
- **Fix:** Use `sessionStorage` or add expiry/encryption.

### C13. Skip-to-content link missing (ALL PAGES)
- **Impact:** Keyboard users must Tab through entire nav on every page. WCAG 2.4.1 (Bypass Blocks, Level A).
- **Fix:** Add `<a href="#main-content" className="sr-only focus:not-sr-only ...">Skip to content</a>` as first child. Add `id="main-content"` to all `<main>` elements.

### C14. Active nav items have no `aria-current="page"` (`(app)/layout.tsx`)
- **Lines:** 29–45, 57–67
- **Impact:** Screen reader users cannot identify current page in sidebar or mobile nav. WCAG 2.4.3.
- **Fix:** Add `aria-current={active ? "page" : undefined}` to both Link elements.

### C15. `app/error.tsx` should be `global-error.tsx` (`error.tsx`)
- **Impact:** Root error boundary doesn't catch layout-level errors. Missing `<html>` and `<body>` wrappers required for global error handler.
- **Fix:** Rename to `global-error.tsx`, add document wrappers.

### C16. `<Link>` wraps `<Button>` — invalid HTML nesting (`(app)/error.tsx`)
- **Lines:** 22–25
- **Impact:** `<a>` cannot contain `<button>`. Unpredictable keyboard/screen reader behavior. WCAG 4.1.1.
- **Fix:** Use `<Link>` with button styling directly, or `<Button onClick={() => router.push(href)}>`.

### C17. Quiz/test option buttons use color as sole correct/incorrect indicator
- **Files:** `quiz/page.tsx`, `test/page.tsx`
- **Impact:** Green/red borders are the only feedback for correct/incorrect answers. WCAG 1.4.1.
- **Fix:** Add `aria-label` with correctness text, or add ✓/✗ icons alongside color.

### C18. Test submit button disabled removes it from AT focus (`test/page.tsx`)
- **Lines:** 292–301
- **Impact:** HTML `disabled` removes the button from screen reader interaction in some AT. Users don't know it exists.
- **Fix:** Use `aria-disabled="true"` + `onClick` guard instead of HTML `disabled`.

### C19. No focus management between quiz questions (`quiz/page.tsx`)
- **Impact:** `key={currentIndex}` remounts the question div. Focus is not moved to new question. Keyboard users lose position.
- **Fix:** `useEffect` with ref to focus first option on `currentIndex` change.

### C20. Test score not announced after submit (`test/page.tsx`)
- **Lines:** ~87
- **Impact:** Score banner appears with `window.scrollTo`, but no `aria-live` announces it. Screen reader users hear nothing.
- **Fix:** Add `aria-live="polite"` or `role="status"` to score banner container.

### C21. Rating buttons have no `aria-pressed` state (`study/page.tsx`)
- **Lines:** 358–379
- **Impact:** Selected rating not announced. Screen readers show plain buttons with no selection state.
- **Fix:** Add `aria-pressed={selectedRating === r.value}` to each button.

---

## HIGH Findings (52)

### Accessibility (32)

| # | Finding | File(s) | Fix |
|---|---------|---------|-----|
| H1 | Mobile nav links hidden with no hamburger replacement | `LandingNav.tsx` | Add mobile menu toggle |
| H2 | SVG forgetting curve chart has no data table fallback | `page.tsx` (landing) | Add visually hidden data table |
| H3 | Comparison table ✓/✗ rely on color for sighted users | `page.tsx` (landing) | Use distinct shapes, not just color |
| H4 | Emoji icons in sidebar nav lack `aria-hidden="true"` | `(app)/layout.tsx` | Add `aria-hidden="true"` to emoji spans |
| H5 | Mobile bottom nav touch targets undersized (~32px tall) | `(app)/layout.tsx` | Increase to `min-h-[44px]` or `py-3` |
| H6 | Warning emoji in error boundaries not `aria-hidden` | `error.tsx`, `(app)/error.tsx` | Add `aria-hidden="true"` |
| H7 | Docs table missing `scope="col"` on `<th>` | `docs/page.tsx` | Add `scope="col"` |
| H8 | Upload status paragraph has no `aria-live` | `upload/page.tsx` | Add `aria-live="polite"` |
| H9 | Hidden file input has no accessible label | `upload/page.tsx` | Add `aria-label="Upload files"` |
| H10 | Document checkbox labels all say "Select" — ambiguous | `documents/page.tsx` | Include document title in label |
| H11 | Generate page toggle buttons lack `aria-pressed` | `generate/page.tsx` | Add `aria-pressed` to provider/type/difficulty buttons |
| H12 | Generate page `<label>` not associated with inputs | `generate/page.tsx` | Use `<fieldset>`/`<legend>` instead |
| H13 | Chunks scrollable region not keyboard-focusable | `documents/[id]/page.tsx` | Add `tabIndex={0}` + `aria-label` |
| H14 | Study-set list card emojis lack `aria-hidden` | `study-sets/page.tsx`, `[id]/page.tsx` | Add `aria-hidden="true"` |
| H15 | Card links have no `focus-visible` ring | `study-sets/page.tsx` | Add focus-visible outline to Link elements |
| H16 | FSRS rating buttons lack `type="button"` and focus ring | `study/page.tsx` | Add type + focus-visible styles |
| H17 | Confidence rating buttons are 40×40px (below 44px minimum) | `study/page.tsx` | Change `w-10 h-10` to `w-11 h-11` |
| H18 | Quiz results ✓/✗ symbols lack explicit text alternatives | `quiz/page.tsx` | Add `aria-label="Correct"/"Incorrect"` |
| H19 | Test question options have no `role="radiogroup"` semantics | `test/page.tsx` | Add `fieldset`/`legend` or ARIA radio roles |
| H20 | Test option buttons lack `aria-pressed` pre-submit | `test/page.tsx` | Add `aria-pressed={userAnswer === oIdx}` |
| H21 | `AnimateIn` has no `prefers-reduced-motion` guard | `AnimateIn.tsx` | Add `useReducedMotion()` from Framer Motion |
| H22 | `TopicComplete` has no motion reduction for celebration animation | `TopicComplete.tsx` | `useReducedMotion()` — skip rotate/scale spring |
| H23 | `MasteryTree` has no motion reduction; stagger delay uncapped | `MasteryTree.tsx` | `useReducedMotion()` + cap stagger delay |
| H24 | `MasteryTree` renders buttons even when `onTopicClick` undefined | `MasteryTree.tsx` | Render `<div>` when no click handler |
| H25 | `ConsistencyStreak` day cells color-only with no accessible state | `ConsistencyStreak.tsx` | Add `aria-label` with date + studied status |
| H26 | `AchievementBadge` compact variant has no accessible description | `AchievementBadge.tsx` | Add `aria-label` with achievement description |
| H27 | `PhaseIndicator` dots communicate state via color only | `PhaseIndicator.tsx` | Add `aria-label` per dot, `aria-current` on active |
| H28 | `Button` loading spinner SVG not `aria-hidden` | `Button.tsx` | Add `aria-hidden="true"` to SVG |
| H29 | `Skeleton` has no `aria-hidden` | `Skeleton.tsx` | Add `aria-hidden="true"` |
| H30 | `Modal` close button only rendered when `title` provided | `Modal.tsx` | Always render close button |
| H31 | Dashboard `<Link>` wrapping `<Card hover>` — no focus ring on card | `dashboard/page.tsx` | Move focus-visible ring to Link |
| H32 | Dashboard emoji on hero card not `aria-hidden` | `dashboard/page.tsx` | Add `aria-hidden="true"` |

### Resilience (12)

| # | Finding | File(s) | Fix |
|---|---------|---------|-----|
| H33 | Raw `error.message` shown to users in production | `error.tsx`, `(app)/error.tsx` | Gate behind `NODE_ENV !== 'production'` |
| H34 | Review failure during `handleRate` silently drops card | `study/page.tsx` | Surface error via toast, add retry |
| H35 | `setTimeout` in `handleRate` leaks on unmount | `study/page.tsx` | Use ref-based cleanup |
| H36 | Modal Escape-key state desync when `saving` (rename modal) | `documents/page.tsx` | Pass `preventClose={saving}` |
| H37 | Modal Escape-key state desync (bulk delete modal) | `documents/page.tsx` | Pass `preventClose={saving}` |
| H38 | Chunks section shows nothing when API fails | `documents/[id]/page.tsx` | Destructure `error`, show inline error |
| H39 | `avgMastery` becomes NaN if any `mastery_level` is null | `progress/page.tsx` | Add `?? 0` guard in reduce |
| H40 | Generate page provider fetch failure silently shows key prompt | `generate/page.tsx` | Show error state when providers fail |
| H41 | `setTimeout` in `runGenerate` leaks on unmount | `generate/page.tsx` | Clean up via useEffect/ref |
| H42 | "Generate Study Materials" only uses first selected document | `documents/page.tsx` | Disable for multi-select or clarify behavior |
| H43 | Toast has no dismiss button for keyboard users | `Toast.tsx` | Add close button with `aria-label` |
| H44 | `key={pathname}` on motion.div destroys page state on navigation | `(app)/layout.tsx` | Document as intentional or provide alternative |

### Performance (4)

| # | Finding | File(s) | Fix |
|---|---------|---------|-----|
| H45 | Arbitrary shadow value `shadow-[0_0_24px_rgba(...)]` repeated | `page.tsx` (landing) | Use design token |
| H46 | `MasteryTree` pure functions recreated on every render | `MasteryTree.tsx` | Move to module scope |
| H47 | Dashboard `<Card hover>` keyboard focus not styled | `dashboard/page.tsx` | Apply focus-visible to Link |
| H48 | Back-nav link animated with h1 in same AnimateIn block | `docs/ai-setup/page.tsx` | Separate into own AnimateIn |

### Design Consistency (4)

| # | Finding | File(s) | Fix |
|---|---------|---------|-----|
| H49 | `not-found.tsx` uses `font-mono` instead of design token | `not-found.tsx` | Use `font-[family-name:var(--font-mono)]` |
| H50 | `documents/page.tsx` uses `<span>` to simulate Button styles | `documents/page.tsx` | Use `<Button>` component |
| H51 | `TopicComplete` duplicates Card/Button class strings | `TopicComplete.tsx` | Use actual components |
| H52 | `MasteryTree` duplicates color mapping instead of importing constants | `MasteryTree.tsx` | Import from `@/lib/constants` |

---

## MEDIUM Findings (32)

| # | Finding | File(s) |
|---|---------|---------|
| M1 | No active page indicator in `LandingNav` | `LandingNav.tsx` |
| M2 | `blockquote` missing `cite` attribute | `page.tsx` (landing) |
| M3 | `AnimateIn` wrapping disrupts stagger for back-link + h1 | `docs/ai-setup/page.tsx` |
| M4 | No `<meta name="viewport">` explicitly exported | `layout.tsx` |
| M5 | No OG/social metadata | `layout.tsx` |
| M6 | `<aside>` has no `aria-label` | `(app)/layout.tsx` |
| M7 | Sidebar version text in unlabeled `<div>` | `(app)/layout.tsx` |
| M8 | Achievement list uses array index as key | `dashboard/page.tsx` |
| M9 | `loadingAch`/`loadingPhase` errors not surfaced | `dashboard/page.tsx` |
| M10 | Drag-zone state change has no accessible announcement | `upload/page.tsx` |
| M11 | Bulk delete modal missing `preventClose` during delete | `documents/page.tsx` |
| M12 | No explanation for duplicate generation behavior | `generate/page.tsx` |
| M13 | Progress page has no back/breadcrumb navigation | `progress/page.tsx` |
| M14 | Loading state on study-sets list has no accessible announcement | `study-sets/page.tsx` |
| M15 | Export links missing `focus-visible:outline-offset` | `study-sets/[id]/page.tsx` |
| M16 | Study-set detail API error silently swallowed | `study-sets/[id]/page.tsx` |
| M17 | `cards` array recomputed on every render (no useMemo) | `study/page.tsx` |
| M18 | ProgressBar percentage vs card count ambiguity | `study/page.tsx` |
| M19 | No confirmation when navigating back mid-quiz | `quiz/page.tsx` |
| M20 | No state persistence across page refresh (quiz/test) | `quiz/page.tsx`, `test/page.tsx` |
| M21 | Test questions array not memoized | `test/page.tsx` |
| M22 | `CalibrationChart` uses `Record<string, unknown>` | `CalibrationChart.tsx` |
| M23 | `SessionReport` renders `JSON.stringify` fallback to users | `SessionReport.tsx` |
| M24 | `SessionReport` heading levels may conflict with parent | `SessionReport.tsx` |
| M25 | `ConsistencyStreak` UTC timezone bug for late-night users | `ConsistencyStreak.tsx` |
| M26 | `ProgressBar` color prop accepts arbitrary string | `ProgressBar.tsx` |
| M27 | `CalibrationChart` numeric stats lack accessible labels | `CalibrationChart.tsx` |
| M28 | `Badge.tsx` uses `React.ReactNode` without import | `Badge.tsx` |
| M29 | `ForgettingCurve` sort runs on every render (no useMemo) | `ForgettingCurve.tsx` |
| M30 | `not-found.tsx` only links to dashboard (confusing for unauthenticated users) | `not-found.tsx` |
| M31 | `suppressHydrationWarning` missing on forced dark `<html>` | `layout.tsx` |
| M32 | `h3` subsection headings inconsistent in AI Setup page | `docs/ai-setup/page.tsx` |

---

## LOW Findings (5)

| # | Finding | File(s) |
|---|---------|---------|
| L1 | `Spinner.tsx` duplicates "Loading" label (aria-label + sr-only) | `Spinner.tsx` |
| L2 | `TopicComplete` no link back to completed study set | `TopicComplete.tsx` |
| L3 | `AchievementBadge` hardcoded trophy emoji for all types | `AchievementBadge.tsx` |
| L4 | `TopicComplete` checkmark lacks accessible text pairing | `TopicComplete.tsx` |
| L5 | "Get Started" CTA in nav incongruent with AI Setup page context | `LandingNav.tsx` |

---

## Prioritized Fix Plan

### Tier 1: Fix Before Public Launch (CRITICAL + HIGH blocking)

**Batch 1 — Systemic (affects entire app)**
1. Wire up `useApi` error state in all pages + create `<ErrorState>` component (C1)
2. Add skip-to-content link in root layout (C13)
3. Add `aria-current="page"` to active nav items (C14)
4. Add `useReducedMotion()` to `AnimateIn` (H21)
5. Persistent `aria-live` region in layout for Toast (C11)

**Batch 2 — Study Flow (core user journey)**
6. Add `aria-live` to flashcard reveal (C4), quiz feedback (C5), test score (C20)
7. Focus management: study reveal → rating buttons (C6), quiz next question (C19)
8. `aria-pressed` on rating buttons (C21), quiz/test option buttons (H20)
9. Color-only fixes: quiz/test correct/incorrect (C17), heatmap (C7), forgetting curve (C8), difficulty meter (C9), comparison table (H3)
10. Touch targets: mobile nav (H5), confidence buttons (H17), modal close (H30)

**Batch 3 — Upload & Documents**
11. Keyboard-accessible drop zone (C2)
12. File size validation (C3)
13. Upload status `aria-live` (H8)
14. Document checkbox labels (H10)
15. Modal `preventClose` during async (H36, H37)

**Batch 4 — Component fixes**
16. Modal focus restore on close (C10)
17. `aria-hidden` on all decorative emojis (H4, H6, H14, H32)
18. Error boundary: rename to `global-error.tsx` (C15), fix Link/Button nesting (C16)
19. Button spinner `aria-hidden` (H28), Skeleton `aria-hidden` (H29)
20. `sessionStorage` for API keys instead of `localStorage` (C12)

### Tier 2: Fix Soon (remaining HIGH)

21. Mobile hamburger menu for LandingNav (H1)
22. Test `fieldset`/`legend` semantics (H19)
23. Resilience: `handleRate` error surfacing + timeout cleanup (H34, H35)
24. Generate page: `aria-pressed` + `fieldset`/`legend` (H11, H12)
25. `TopicComplete` / `MasteryTree` motion reduction (H22, H23)
26. Design consistency: font-mono token (H49), span→Button (H50), constant imports (H52)

### Tier 3: Address Later (MEDIUM + LOW)

All medium and low findings can be addressed in a subsequent cleanup pass. None are blocking for launch, but M25 (timezone bug) and M22 (type safety) should be prioritized within this tier.
