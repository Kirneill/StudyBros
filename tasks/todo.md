# StudyBros — Impeccable Audit Fix Tasks

Last updated: 2026-04-27

---

## Batch 1: Foundation Layer (shared components + layouts)

### 1A. Fix UI Components (Agent A)
- [ ] **Status:** NOT STARTED
- **Files:** `Button.tsx`, `Modal.tsx`, `Toast.tsx`, `Spinner.tsx`, `Skeleton.tsx`, `ProgressBar.tsx`, `Badge.tsx`, `EmptyState.tsx`, NEW `ErrorState.tsx`
- **Fixes:**
  - **C10** Modal: capture `document.activeElement` before `showModal()`, restore focus in `onClose`
  - **C11** Toast: restructure to work with persistent `aria-live` region (content updates, not mount/unmount)
  - **H28** Button: add `aria-hidden="true"` to loading spinner SVG
  - **H29** Skeleton: add `aria-hidden="true"`
  - **H30** Modal: always render close button (not just when `title` provided)
  - **H43** Toast: add dismiss button with `aria-label="Dismiss notification"`
  - **L1** Spinner: remove duplicate "Loading" label; `aria-hidden="true"` on SVG, keep sr-only span
  - **M26** ProgressBar: narrow `color` prop to design token keys or remove
  - **M28** Badge: fix `React.ReactNode` import
  - **NEW** Create `ErrorState` component (icon, title, description, retry button) for C1
- **Acceptance criteria:**
  - [ ] Modal restores focus to previous element on close
  - [ ] Toast has dismiss button; works with persistent aria-live region
  - [ ] All decorative SVGs/spinners have `aria-hidden="true"`
  - [ ] `ErrorState` component created and exported from `@/components/ui`
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### 1B. Fix Gamification Components (Agent B)
- [ ] **Status:** NOT STARTED
- **Files:** All 10 `components/gamification/*.tsx`
- **Fixes:**
  - **C7** KnowledgeHeatMap: add `aria-label` with topic + mastery level to each cell
  - **C8** ForgettingCurve: add `role="progressbar"` with ARIA value attributes; memoize sort (**M29**)
  - **C9** DifficultyMeter: add `role="meter"` with ARIA value attributes
  - **H22** TopicComplete: add `useReducedMotion()` guard; use Card/Button components (**H51**); add accessible text to checkmark (**L4**); add link back to study set (**L2**)
  - **H23** MasteryTree: add `useReducedMotion()` + cap stagger; move pure functions to module scope (**H46**); render div when no onTopicClick (**H24**); import from constants (**H52**)
  - **H25** ConsistencyStreak: add `aria-label` with date + studied status; fix UTC timezone bug (**M25**)
  - **H26** AchievementBadge: add `aria-label` to compact variant
  - **H27** PhaseIndicator: add `aria-label` per dot, `aria-current` on active
  - **M22** CalibrationChart: replace `Record<string, unknown>` with typed interface; add accessible labels (**M27**)
  - **M23** SessionReport: replace `JSON.stringify` fallback with proper text; consider heading level prop (**M24**)
- **Acceptance criteria:**
  - [ ] All color-only indicators have text alternatives
  - [ ] All animations respect `prefers-reduced-motion`
  - [ ] No `Record<string, unknown>` or JSON.stringify in user-facing output
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### 1C. Fix Layouts, Error Boundaries, AnimateIn (Agent C)
- [ ] **Status:** NOT STARTED
- **Files:** `app/layout.tsx`, `app/(app)/layout.tsx`, `app/error.tsx`, `app/(app)/error.tsx`, `app/not-found.tsx`, `components/AnimateIn.tsx`
- **Fixes:**
  - **C13** Root layout: add skip-to-content link as first child of body
  - **C14** App layout: add `aria-current="page"` to active nav links (both desktop + mobile)
  - **C15** Rename `app/error.tsx` → `app/global-error.tsx`, add `<html>` + `<body>` wrappers
  - **C16** App error: fix `<Link>` wrapping `<Button>` — use Link with button styling directly
  - **H4** App layout: add `aria-hidden="true"` to emoji icon spans (both navs)
  - **H5** App layout: increase mobile nav touch targets to `min-h-[44px]`
  - **H6** Both error boundaries: add `aria-hidden="true"` to warning emoji
  - **H21** AnimateIn: add `useReducedMotion()` from Framer Motion
  - **H33** Both error boundaries: gate `error.message` behind `NODE_ENV !== 'production'`
  - **H44** App layout: add comment documenting intentional `key={pathname}` trade-off
  - **H49** not-found: replace `font-mono` with `font-[family-name:var(--font-mono)]`
  - **M4** Root layout: export `viewport` config
  - **M5** Root layout: add OG/social metadata (og:type, og:image placeholder, twitter:card)
  - **M6** App layout: add `aria-label="Sidebar"` to `<aside>`
  - **M30** not-found: add "Go Home" link to `/` alongside Dashboard
  - **M31** Root layout: add `suppressHydrationWarning` to `<html>`
- **Acceptance criteria:**
  - [ ] Skip-to-content link present and functional
  - [ ] Active nav items announce current page to screen readers
  - [ ] Error boundaries safe for production (no raw error messages)
  - [ ] AnimateIn respects `prefers-reduced-motion`
  - [ ] All touch targets ≥ 44px
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### 1D. Fix LandingNav — Mobile Menu (Agent D)
- [ ] **Status:** NOT STARTED
- **Files:** `components/LandingNav.tsx`
- **Fixes:**
  - **H1** Add mobile hamburger menu toggle with Docs, AI Setup, Dashboard links
  - **M1** Add active page indicator using `usePathname()`
  - **L5** (optional) Context-aware CTA text
- **Acceptance criteria:**
  - [ ] Mobile users can access all nav links via hamburger menu
  - [ ] Current page highlighted in nav
  - [ ] `LandingNav` converted to `"use client"` for `usePathname`
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### 1E. Batch 1 Verification Gate
- [ ] **Status:** NOT STARTED
- **Scope:** Run lint + build after all Batch 1 agents merge
- **Acceptance criteria:**
  - [ ] `npm run lint` — 0 errors
  - [ ] `npm run build` — successful (all 17 routes)

---

## Batch 2: Marketing Pages

### 2A. Fix Landing Page + Docs Pages (Agent E)
- [ ] **Status:** NOT STARTED
- **Files:** `app/page.tsx`, `app/docs/page.tsx`, `app/docs/ai-setup/page.tsx`
- **Fixes:**
  - **H2** Landing: add visually hidden data table for SVG forgetting curve
  - **H3** Landing: comparison table ✓/✗ — add shape differentiation beyond color
  - **H7** Docs: add `scope="col"` to `<th>` elements in file types table
  - **H45** Landing: replace arbitrary `shadow-[0_0_24px_rgba(...)]` with design token
  - **H48** AI Setup: separate back-link from h1 in AnimateIn block
  - **M2** Landing: add `cite` attribute to blockquotes
  - **M3** AI Setup: fix AnimateIn stagger for back-link + h1
  - **M32** AI Setup: make h3 subsection headings consistent
  - Add `id="main-content"` to all `<main>` elements (required by C13 skip link)
- **Acceptance criteria:**
  - [ ] All `<main>` elements have `id="main-content"`
  - [ ] Comparison table readable without color
  - [ ] SVG chart has hidden data table fallback
  - [ ] No arbitrary Tailwind shadow values
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### 2B. Batch 2 Verification Gate
- [ ] **Status:** NOT STARTED
- **Acceptance criteria:**
  - [ ] `npm run lint` — 0 errors
  - [ ] `npm run build` — successful

---

## Batch 3: App Pages — Documents & Upload Flow

### 3A. Fix Dashboard + Achievements + Progress (Agent F)
- [ ] **Status:** NOT STARTED
- **Files:** `dashboard/page.tsx`, `achievements/page.tsx`, `progress/page.tsx`
- **Fixes:**
  - **C1 (partial)** Wire up `useApi` error state + use `<ErrorState>` in all 3 pages
  - **H31** Dashboard: add focus-visible ring to Link wrapping Card
  - **H32** Dashboard: add `aria-hidden="true"` to hero card emoji
  - **H39** Progress: add `?? 0` guard in `avgMastery` reduce
  - **H47** Dashboard: apply focus-visible to Card link
  - **M8** Dashboard: use stable key for achievement list
  - **M9** Dashboard: surface `loadingAch`/`loadingPhase` errors
  - **M13** Progress: add back/breadcrumb navigation
- **Acceptance criteria:**
  - [ ] All 3 pages show error state (not empty state) when API fails
  - [ ] No NaN from null mastery_level
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### 3B. Fix Upload Page (Agent G)
- [ ] **Status:** NOT STARTED
- **Files:** `upload/page.tsx`
- **Fixes:**
  - **C1 (partial)** Wire up `useApi` error state (if any API calls)
  - **C2** Add keyboard activation to drop zone (role, tabIndex, onKeyDown, aria-label)
  - **C3** Add client-side file size validation (50MB cap)
  - **H8** Add `aria-live="polite"` to upload status paragraph
  - **H9** Add `aria-label="Upload files"` to hidden file input
  - **M10** Add accessible announcement for drag-zone state change
- **Acceptance criteria:**
  - [ ] Drop zone activatable via Enter/Space keys
  - [ ] Files > 50MB rejected client-side with user message
  - [ ] Upload progress announced to screen readers
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### 3C. Fix Documents + Generate Pages (Agent H)
- [ ] **Status:** NOT STARTED
- **Files:** `documents/page.tsx`, `documents/[id]/page.tsx`, `documents/[id]/generate/page.tsx`
- **Fixes:**
  - **C1 (partial)** Wire up `useApi` error state in all 3 pages
  - **C12** Generate: switch API keys from `localStorage` to `sessionStorage`
  - **H10** Documents: include document title in checkbox labels
  - **H11** Generate: add `aria-pressed` to toggle buttons
  - **H12** Generate: replace `<label>` headers with `<fieldset>`/`<legend>`
  - **H13** Doc detail: add `tabIndex={0}` + `aria-label` to chunks scrollable region
  - **H36** Documents: pass `preventClose={saving}` to rename Modal
  - **H37** Documents: pass `preventClose={saving}` to bulk delete Modal
  - **H38** Doc detail: show error state when chunks API fails
  - **H40** Generate: show error state when providers fail
  - **H41** Generate: clean up `setTimeout` in `runGenerate`
  - **H42** Documents: disable "Generate" when multiple docs selected or clarify UX
  - **H50** Documents: replace `<span>` buttons with `<Button>` component
  - **M11** Documents: preventClose on bulk delete during operation
  - **M12** Generate: note about duplicate generation behavior
- **Acceptance criteria:**
  - [ ] All API errors surfaced to user with retry
  - [ ] API keys use `sessionStorage` instead of `localStorage`
  - [ ] All toggle buttons have `aria-pressed`
  - [ ] Modals prevent Escape during async operations
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### 3D. Batch 3 Verification Gate
- [ ] **Status:** NOT STARTED
- **Acceptance criteria:**
  - [ ] `npm run lint` — 0 errors
  - [ ] `npm run build` — successful

---

## Batch 4: App Pages — Study Flow

### 4A. Fix Study-Sets List + Detail (Agent I)
- [ ] **Status:** NOT STARTED
- **Files:** `study-sets/page.tsx`, `study-sets/[id]/page.tsx`
- **Fixes:**
  - **C1 (partial)** Wire up `useApi` error state
  - **H14** Add `aria-hidden="true"` to decorative emojis
  - **H15** Add focus-visible ring to card Link elements
  - **M14** Add accessible loading announcement
  - **M15** Add `focus-visible:outline-offset` to export links
  - **M16** Surface study-set detail API error
- **Acceptance criteria:**
  - [ ] Error states shown for API failures
  - [ ] All emojis aria-hidden
  - [ ] Card links have visible focus rings
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### 4B. Fix Flashcard Study Page (Agent J)
- [ ] **Status:** NOT STARTED
- **Files:** `study-sets/[id]/study/page.tsx`
- **Fixes:**
  - **C1 (partial)** Wire up `useApi` error state
  - **C4** Wrap answer section in `aria-live="polite"` region
  - **C6** Focus management: move focus to first rating button on reveal
  - **C21** Add `aria-pressed` to rating buttons
  - **H16** Add `type="button"` and focus-visible ring to rating buttons
  - **H17** Change confidence buttons from `w-10 h-10` to `w-11 h-11`
  - **H34** Surface `handleRate` error via toast
  - **H35** Fix `setTimeout` leak in `handleRate` with ref-based cleanup
  - **M17** Memoize `cards` array with `useMemo`
  - **M18** Improve ProgressBar aria-label for card count context
- **Acceptance criteria:**
  - [ ] Card reveal announced to screen readers
  - [ ] Focus moves to rating panel after reveal
  - [ ] Rating selection announced via `aria-pressed`
  - [ ] All touch targets ≥ 44px
  - [ ] No timer leaks on unmount
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### 4C. Fix Quiz + Test + Complete Pages (Agent K)
- [ ] **Status:** NOT STARTED
- **Files:** `quiz/page.tsx`, `test/page.tsx`, `complete/page.tsx`
- **Fixes:**
  - **C1 (partial)** Wire up `useApi` error state
  - **C5** Quiz: add `aria-live="assertive"` for answer feedback
  - **C17** Quiz + Test: add text/icon indicators alongside color for correct/incorrect
  - **C18** Test: replace `disabled` with `aria-disabled` + onClick guard
  - **C19** Quiz: focus management on question transitions
  - **C20** Test: add `aria-live` to score banner
  - **H18** Quiz: add text alternatives to ✓/✗ result symbols
  - **H19** Test: add `fieldset`/`legend` or radiogroup semantics to options
  - **H20** Test: add `aria-pressed` to option buttons pre-submit
  - **M19** Quiz: add beforeunload confirmation when mid-quiz
  - **M20** Quiz + Test: persist answers to `sessionStorage`
  - **M21** Test: memoize questions array
- **Acceptance criteria:**
  - [ ] Quiz feedback announced to screen readers
  - [ ] Correct/incorrect distinguishable without color
  - [ ] Focus moves to new question on advance
  - [ ] Test score announced when submitted
  - [ ] Mid-session state persists across refresh
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### 4D. Batch 4 Verification Gate
- [ ] **Status:** NOT STARTED
- **Acceptance criteria:**
  - [ ] `npm run lint` — 0 errors
  - [ ] `npm run build` — successful
  - [ ] All 110 findings addressed

---

## Batch 5: User Review Checkpoint

### 5A. User Review
- [ ] **Status:** NOT STARTED
- **Scope:** Present all fixes to user for review
- **Acceptance criteria:**
  - [ ] Summary of all changes provided
  - [ ] Dev server running for manual testing
  - [ ] User approves or provides feedback

### 5B. Vercel Deployment (Phase C from original plan)
- [ ] **Status:** NOT STARTED
- **Scope:** Deploy frontend to Vercel (backend deferred)
- **Acceptance criteria:**
  - [ ] Vercel build succeeds
  - [ ] Production URL accessible
  - [ ] Landing page + all routes render correctly
