# UI/UX Audit Findings -- StudyBros Frontend

## Summary

**Total findings: 42** (8 Critical, 16 High, 18 Low)

Reviewed all 20 pages, 10 UI components, 10 gamification components, and 4 library files across 5 axes: Accessibility, Performance, Resilience, Design Consistency, and UX Flow.

---

## Critical Issues (must fix)

### C1. Comparison table is not accessible -- uses divs instead of `<table>`

- **File:** `src/app/page.tsx:293-328`
- **Axis:** Accessibility
- **Problem:** The comparison table (StudyBros vs Anki vs Quizlet) is built with `div` grids. Screen readers cannot navigate it as a data table. The checkmark/cross characters have no text alternatives, so a screen reader would read "check mark" or nothing at all -- the meaning (feature supported vs not supported) is lost.
- **Fix:** Use semantic `<table>`, `<thead>`, `<tbody>`, `<th>`, `<td>` elements. Add `scope="col"` on header cells. Use `aria-label="Supported"` / `aria-label="Not supported"` on the check/cross spans, or use `sr-only` text.

### C2. App layout sidebar is `"use client"` -- forces entire child tree to be client-rendered

- **File:** `src/app/(app)/layout.tsx:1`
- **Axis:** Performance
- **Problem:** The app layout is a client component because it uses `usePathname()` and `framer-motion`. This means every page inside the `(app)` group is wrapped by a client boundary. The `motion.div` with `key={pathname}` on line 73 remounts the entire page content on every navigation, destroying any server component benefits and potentially discarding component state.
- **Fix:** Extract the sidebar into its own client component (`Sidebar.tsx`) and the animated content wrapper into another. Keep the layout itself as a server component. This allows pages like documents list, study sets list, etc. to be server components in the future.

### C3. Modal has no focus trap -- keyboard users can tab outside

- **File:** `src/components/ui/Modal.tsx:12-41`
- **Axis:** Accessibility
- **Problem:** The `<dialog>` element is used (good), but there is no focus management: no `autoFocus` on first focusable element, and no focus trap. While `<dialog>` with `showModal()` provides a native focus trap in most browsers, the close button and inner content don't restore focus to the trigger element when the modal closes. Additionally, ESC key handling relies solely on native `<dialog>` behavior with no way to prevent close during async operations (the `onClose` callback fires after the dialog closes, not before).
- **Fix:** Track the trigger element ref. On close, return focus to it. For operations where close should be prevented (saving state), call `event.preventDefault()` on the dialog's `cancel` event when `saving` is true. Test in Safari/Firefox to confirm native focus trap behavior.

### C4. Upload drop zone does not cover the full card -- drag events on inner elements

- **File:** `src/app/(app)/upload/page.tsx:119-154`
- **Axis:** UX Flow
- **Problem:** The drag event handlers (`onDragOver`, `onDragLeave`, `onDrop`) are attached to the inner `div` on line 125, not the outer `Card`. This means dragging a file over the padding area of the Card (p-6) does not trigger the drag state, confusing users who drop files near the edges. Also, `onDragLeave` fires when hovering child elements, causing the drag indicator to flicker.
- **Fix:** Move drag handlers to the `Card` component wrapper. Use a `dragCounter` ref pattern to handle child element drag enter/leave without flickering: increment on `dragenter`, decrement on `dragleave`, set `dragging` when counter > 0.

### C5. `useApi` hook does not expose error state in any page -- API errors silently result in empty UI

- **File:** `src/lib/hooks.ts:34` and every page using `useApi`
- **Axis:** Resilience
- **Problem:** The `useApi` hook returns an `error` property, but almost no page uses it. For example, `DashboardPage` (dashboard/page.tsx:12-16) destructures `data` and `loading` but ignores `error`. If the API returns a 500, the loading spinner disappears and the user sees the empty state ("Welcome to StudyBros") with no indication that something went wrong. This applies to: dashboard, documents list, study sets list, study set detail, progress, achievements, quiz, test, and study pages.
- **Fix:** Create a shared `ErrorState` component (similar to `EmptyState`). In each page, check `error` after `loading` and render it. At minimum: `if (error) return <ErrorState message={error} onRetry={refetch} />;`

### C6. Hardcoded stats on completion page -- fake data

- **File:** `src/app/(app)/study-sets/[id]/complete/page.tsx:32-33`
- **Axis:** Correctness
- **Problem:** `accuracy: 0.94` and `avgInterval: 45` are hardcoded on lines 32-33. This means every topic's "You Won" screen shows 94% accuracy and 45-day interval regardless of actual performance. This directly violates the gamification rule "Track REAL competency, not vanity metrics."
- **Fix:** Fetch actual mastery stats from the API. Call `api.checkMastery(topic)` or a dedicated endpoint and pass real values. If the API doesn't expose these stats yet, at minimum display only `totalItems` and omit accuracy/interval rather than showing fake numbers.

### C7. API keys stored in `localStorage` in plaintext

- **File:** `src/app/(app)/documents/[id]/generate/page.tsx:46-58`
- **Axis:** Security
- **Problem:** API keys for OpenAI/Anthropic/OpenRouter are stored in `localStorage` with the prefix `studybros_api_key:`. `localStorage` is accessible to any JavaScript on the page (XSS vector) and is never cleared on session end. The keys persist indefinitely. Any browser extension or XSS vulnerability would exfiltrate them.
- **Fix:** Use `sessionStorage` instead of `localStorage` so keys don't persist across sessions. Better: send the key directly to the server on each request without storing it client-side at all, or use a server-side encryption mechanism. At minimum, document the risk clearly to users and add a "clear all saved keys" option in settings.

### C8. Spinner SVGs have no accessible label

- **File:** `src/components/ui/Spinner.tsx:9-14` and `src/components/ui/Button.tsx:37-39`
- **Axis:** Accessibility
- **Problem:** Both the `Spinner` component and the Button's loading spinner are SVGs with no `role="status"` and no accessible text. Screen readers may announce them as "image" with no further context, or skip them entirely. Users relying on assistive technology get no feedback that content is loading.
- **Fix:** Add `role="status"` and `aria-label="Loading"` to the Spinner SVG. Wrap the SVG in a `<span>` with an `sr-only` "Loading..." label. On Button, add `aria-busy={loading}` when loading is true.

---

## High Issues (should fix)

### H1. No skip-to-content link

- **File:** `src/app/layout.tsx:28-38` and `src/app/(app)/layout.tsx:19-85`
- **Axis:** Accessibility
- **Problem:** No skip navigation link exists. Keyboard users must tab through the entire sidebar (6 items desktop, 5 mobile) on every page navigation before reaching main content.
- **Fix:** Add a visually-hidden skip link as the first child of `<body>`: `<a href="#main-content" class="sr-only focus:not-sr-only ...">Skip to content</a>`. Add `id="main-content"` to the `<main>` element.

### H2. Landing page has no `<main>` landmark

- **File:** `src/app/page.tsx:22-436`
- **Axis:** Accessibility
- **Problem:** The landing page uses `<div>`, `<section>`, and `<footer>` but no `<main>` element. Screen readers use landmarks to navigate, and `<main>` is the primary content landmark.
- **Fix:** Wrap sections 1-8 (hero through final CTA) in a `<main>` element.

### H3. Mobile nav cuts off "Achievements" -- only shows 5 of 6 items

- **File:** `src/app/(app)/layout.tsx:54`
- **Axis:** UX Flow
- **Problem:** `NAV_ITEMS.slice(0, 5)` on line 54 drops the Achievements link from mobile navigation. Mobile users have no way to navigate to the achievements page except by typing the URL or finding a link on the dashboard.
- **Fix:** Either show all 6 items (possibly with a "more" overflow menu if space is tight), or add a link to achievements from the dashboard or progress page with clear mobile visibility.

### H4. `Toast` has `onDismiss` in `useEffect` deps -- causes rapid re-renders

- **File:** `src/components/ui/Toast.tsx:23-29`
- **Axis:** Performance
- **Problem:** `onDismiss` is in the dependency array of `useEffect`. If the parent creates `onDismiss` inline (e.g., `onDismiss={() => setToast(null)}`), a new function reference is created each render, causing the effect to re-run, clear the timer, and restart it. This can make the toast stay visible indefinitely or behave erratically.
- **Fix:** Use `useRef` to capture the latest `onDismiss` callback and exclude it from the dependency array, or use `useCallback` consistently in all parent components. Best practice: wrap `onDismiss` in a ref inside Toast itself.

### H5. Buttons inside Links -- invalid HTML nesting

- **File:** `src/app/(app)/study-sets/[id]/page.tsx:82-84`, `src/app/(app)/documents/[id]/page.tsx:57`, and multiple other files
- **Axis:** Accessibility
- **Problem:** Pattern `<Link href="..."><Button>...</Button></Link>` nests a `<button>` inside an `<a>`. This is invalid HTML (interactive content inside interactive content). Screen readers may announce it confusingly, and behavior varies across browsers.
- **Fix:** Use the `Button` component with `asChild` pattern (render as `<a>`) or use `Link` styled as a button: `<Link href="..." className={buttonStyles}>...</Link>`. Alternatively, create a `LinkButton` component.

### H6. Document detail page has no back navigation

- **File:** `src/app/(app)/documents/[id]/page.tsx:44-93`
- **Axis:** UX Flow
- **Problem:** No breadcrumb or back link to `/documents`. The user must use the sidebar or browser back button to return to the documents list.
- **Fix:** Add a breadcrumb or back link at the top: `<Link href="/documents" class="text-text-muted text-sm">&larr; Back to Documents</Link>`.

### H7. Generate page has no back navigation

- **File:** `src/app/(app)/documents/[id]/generate/page.tsx:178-341`
- **Axis:** UX Flow
- **Problem:** No way to go back to the document detail page. Same issue as H6.
- **Fix:** Add `<Link href="/documents/${docId}">&larr; Back to {doc?.title}</Link>` at the top.

### H8. `!important` overrides on delete buttons

- **File:** `src/app/(app)/documents/page.tsx:240-244`, `src/app/(app)/documents/[id]/page.tsx:87`, `src/app/(app)/study-sets/[id]/page.tsx:213`
- **Axis:** Design Consistency
- **Problem:** Delete confirmation buttons use `className="!bg-error hover:!bg-error/80"` with `!important` to override Button's primary styles. This is a code smell -- the Button component should have a `destructive` variant.
- **Fix:** Add a `destructive` variant to Button: `destructive: "bg-error text-bg-primary hover:bg-error/80"`. Use `<Button variant="destructive">` instead of className overrides.

### H9. `KnowledgeHeatMap` tiles have no accessible text -- tooltip only

- **File:** `src/components/gamification/KnowledgeHeatMap.tsx:19-24`
- **Axis:** Accessibility
- **Problem:** Each tile is a `<div>` with only a `title` attribute for information. `title` is not reliably announced by screen readers and is invisible on touch devices. The color-only encoding (mastery level) fails WCAG 1.4.1 (Use of Color).
- **Fix:** Add `aria-label` to each tile with the topic name and mastery percentage. Add a text label or pattern overlay for color-blind users. Consider making tiles focusable or using a `<table>` structure.

### H10. `ProgressBar` has no ARIA attributes

- **File:** `src/components/ui/ProgressBar.tsx:10-31`
- **Axis:** Accessibility
- **Problem:** The progress bar is built with plain divs. Screen readers see nothing. No `role="progressbar"`, no `aria-valuenow`, no `aria-valuemin/max`.
- **Fix:** Add to the outer bar div: `role="progressbar" aria-valuenow={Math.round(pct)} aria-valuemin={0} aria-valuemax={100} aria-label={label ?? "Progress"}`.

### H11. Pages send 5+ parallel API requests on mount

- **File:** `src/app/(app)/dashboard/page.tsx:12-16`, `src/app/(app)/progress/page.tsx:19-23`
- **Axis:** Performance
- **Problem:** Dashboard fires 5 API calls simultaneously on mount. Progress page fires 4. Each uses a separate `useApi` hook with no batching or deduplication. If the backend is slow or rate-limited, this creates a waterfall of loading states where some sections appear before others.
- **Fix:** Consider a single `/api/dashboard` endpoint that returns all needed data in one response. Or at minimum, use React Query / SWR with request deduplication and caching so navigating back to the dashboard doesn't re-fetch everything.

### H12. Content type casting with `as Record<string, unknown>` is fragile

- **File:** `src/app/(app)/study-sets/[id]/page.tsx:151`, `src/app/(app)/study-sets/[id]/study/page.tsx:63`, `src/app/(app)/study-sets/[id]/quiz/page.tsx:27`
- **Axis:** Correctness
- **Problem:** Study set `content` is typed as `Record<string, unknown> | unknown[]` and parsed with `as Record<string, unknown>` casts and manual field checks. This is error-prone -- if the API shape changes, the UI silently renders wrong data or empty strings.
- **Fix:** Define discriminated union types for each content shape (FlashcardContent, QuizContent, TestContent). Create type guards (e.g., `isFlashcardContent(content)`) that validate shape at runtime. Use Zod for runtime validation if content is truly dynamic.

### H13. `ConsistencyStreak` date parsing may fail across timezones

- **File:** `src/components/gamification/ConsistencyStreak.tsx:17-21`
- **Axis:** Correctness
- **Problem:** `new Date().toISOString().split("T")[0]` returns UTC date, but `new Date(today).setDate(...)` operates in local time. For users in UTC- timezones, the "today" date in UTC could be tomorrow locally, causing the streak display to show wrong days as "today."
- **Fix:** Use a consistent timezone approach. Either normalize all dates to UTC, or use `toLocaleDateString('en-CA')` (which returns YYYY-MM-DD in local time) for comparison with `studiedDates`.

### H14. Study page `cards` array is recalculated on every render

- **File:** `src/app/(app)/study-sets/[id]/study/page.tsx:58-71`
- **Axis:** Performance
- **Problem:** The `cards` array is computed via an IIFE that runs on every render. It parses the entire study set content array each time. This causes unnecessary work on every state change (rating, revealing, etc.).
- **Fix:** Wrap in `useMemo` with `[studySet]` dependency.

### H15. No file size validation on client before upload

- **File:** `src/app/(app)/upload/page.tsx:36-98`
- **Axis:** Resilience
- **Problem:** The UI text says "up to 50 MB each" (line 135) but there's no client-side validation. A user could select a 500MB video, wait for a long upload, then get a server error. Wasted time and bandwidth.
- **Fix:** Check `file.size` before calling `api.uploadFile`. Show an immediate error toast for files exceeding the limit.

### H16. Rename input has no keyboard submit handling

- **File:** `src/app/(app)/documents/page.tsx:206-211`
- **Axis:** UX Flow
- **Problem:** The rename modal input has no `onKeyDown` handler for Enter key. Users must click the Save button -- pressing Enter does nothing.
- **Fix:** Add `onKeyDown={(e) => { if (e.key === "Enter") handleRename(); }}` to the input, or wrap the modal content in a `<form>` with `onSubmit`.

---

## Low Issues (nice to have)

### L1. `font-[family-name:var(--font-heading)]` repeated everywhere

- **Files:** Every page and component that uses heading font
- **Axis:** Design Consistency
- **Problem:** The verbose Tailwind class `font-[family-name:var(--font-heading)]` appears ~30+ times across the codebase. This is fragile and verbose.
- **Fix:** Define a utility class in `globals.css`: `.font-heading { font-family: var(--font-heading); }` and use `font-heading` everywhere. Or configure the font in Tailwind's theme.

### L2. Footer GitHub link goes to `#`

- **File:** `src/app/page.tsx:425`
- **Axis:** UX Flow
- **Problem:** `<a href="#">GitHub</a>` is a dead link. Clicking it scrolls to top.
- **Fix:** Either link to the actual repository or remove the link.

### L3. Landing page emojis may render differently across OS

- **File:** `src/app/page.tsx:158-174`
- **Axis:** Design Consistency
- **Problem:** Icons for "Any AI Assistant" (plug), "Paste a Link" (link), "Web Dashboard" (globe) use emoji. These render differently on Windows, Mac, Android. Consider using consistent SVG icons.
- **Fix:** Replace emoji with SVG icons from a consistent icon set (Lucide, Heroicons, etc.) for the feature cards.

### L4. `AnimateIn` component forces `"use client"` on landing page

- **File:** `src/components/AnimateIn.tsx:1`, used in `src/app/page.tsx`
- **Axis:** Performance
- **Problem:** `AnimateIn` is a client component (uses `framer-motion`). The landing page imports it, making the entire landing page a client component tree. For SEO-critical content (hero, science section), this means the initial HTML may not include the animated content in the server-rendered output (framer-motion `initial` styles set `opacity: 0`).
- **Fix:** For the landing page, consider a CSS-only fade-in animation for the initial sections (using `@keyframes` + `animation-delay`) so the content is visible in SSR HTML. Reserve `AnimateIn` for app pages.

### L5. No responsive handling for comparison table

- **File:** `src/app/page.tsx:292-330`
- **Axis:** Design Consistency
- **Problem:** The comparison table has `min-w-[600px]` and `overflow-x-auto`, but on mobile it requires horizontal scrolling with no visual indicator that it's scrollable.
- **Fix:** Add a subtle fade/shadow on the right edge to hint at scrollability, or restructure the table for mobile (stacked cards instead of table).

### L6. `SkeletonCard` component is defined but never used

- **File:** `src/components/ui/Skeleton.tsx:9-17`
- **Axis:** Design Consistency
- **Problem:** `SkeletonCard` is exported but no page uses it. All loading states use `<Spinner>` instead. Skeleton screens provide better perceived performance.
- **Fix:** Replace full-page spinner loading states with skeleton layouts on data-heavy pages (dashboard, documents list, study sets list, progress).

### L7. Mobile bottom nav overlaps content

- **File:** `src/app/(app)/layout.tsx:52-69` and `72`
- **Axis:** Design Consistency
- **Problem:** Main content has `pb-20 md:pb-0` to account for the bottom nav, but on pages with action buttons at the bottom (practice test submit button, study flashcard rating panel), the bottom nav may overlap interactive elements.
- **Fix:** Test on actual mobile viewport. Consider increasing `pb-20` to `pb-24` or `pb-28`, or use `safe-area-inset-bottom` for devices with gesture bars.

### L8. No loading state for generation -- just a disabled button

- **File:** `src/app/(app)/documents/[id]/generate/page.tsx:293`
- **Axis:** UX Flow
- **Problem:** During AI generation (which can take 10-30+ seconds), the only feedback is a disabled button saying "Generating with AI..." and a spinner inside it. No progress indication, no estimate, no animation.
- **Fix:** Add a more prominent generating state: a card with a pulsing animation, estimated time, or step indicators ("Analyzing document... Generating questions..."). Consider a progress bar even if it's estimated.

### L9. `nav` items use emoji icons inconsistently

- **File:** `src/app/(app)/layout.tsx:7-14`
- **Axis:** Design Consistency
- **Problem:** Navigation items mix Unicode characters (the circle and arrow on lines 8-9) with emoji (lines 10-14). These render at different sizes and styles.
- **Fix:** Use a consistent icon set (SVG icons from Lucide or Heroicons) for all nav items.

### L10. No `<meta name="viewport">` tag

- **File:** `src/app/layout.tsx:28-38`
- **Axis:** Design Consistency
- **Problem:** No viewport meta tag is explicitly set. Next.js may add a default one, but it's good practice to be explicit, especially for the responsive breakpoints used throughout.
- **Fix:** Next.js 13+ generates viewport by default. Verify by checking the rendered HTML. If missing, add `export const viewport = { width: 'device-width', initialScale: 1 }` to layout.

### L11. Practice test scroll-to-top on submit may be jarring

- **File:** `src/app/(app)/study-sets/[id]/test/page.tsx:87`
- **Axis:** UX Flow
- **Problem:** `window.scrollTo({ top: 0, behavior: "smooth" })` on submit scrolls to the top. If the user just answered the last question at the bottom, they see the results but lose their place in the question list for review.
- **Fix:** Consider scrolling to the score banner specifically (using a ref and `scrollIntoView`) rather than the page top.

### L12. Quiz page answer options use `key={i}` (index-based keys)

- **File:** `src/app/(app)/study-sets/[id]/quiz/page.tsx:234`
- **Axis:** Correctness
- **Problem:** Options use index-based keys (`key={i}`). Since options don't reorder, this is not a bug, but if shuffling is added later, it will cause incorrect UI updates.
- **Fix:** Use option text or a stable ID as key if available.

### L13. `EmptyState` icon has no `aria-hidden`

- **File:** `src/components/ui/EmptyState.tsx:16`
- **Axis:** Accessibility
- **Problem:** The emoji icon is rendered as text. Screen readers will attempt to announce it (e.g., "books" for the books emoji).
- **Fix:** Add `aria-hidden="true"` to the icon span: `<span className="text-4xl mb-4" aria-hidden="true">{icon}</span>`.

### L14. No `role="alert"` or live region on error messages

- **File:** Multiple pages with inline error text
- **Axis:** Accessibility
- **Problem:** When API errors occur and error text is rendered conditionally, screen readers don't automatically announce the change. The `Toast` component has `role="alert"` (good), but pages that show inline errors (e.g., document not found text on line 41 of `documents/[id]/page.tsx`) don't.
- **Fix:** Use `role="alert"` on inline error messages or wrap them in an `aria-live="polite"` region.

### L15. Dashboard quick links cards don't have accessible names

- **File:** `src/app/(app)/dashboard/page.tsx:129-143`
- **Axis:** Accessibility
- **Problem:** The quick link cards have emoji icons and text, but the Link element's accessible name comes from all child text content including the emoji. Screen readers would announce something like "up arrow Upload" or "books Study Sets."
- **Fix:** Add `aria-label` on the Link element with just the label text, and `aria-hidden="true"` on the icon span.

### L16. Upload page hidden file input has no accessible label

- **File:** `src/app/(app)/upload/page.tsx:138-145`
- **Axis:** Accessibility
- **Problem:** The hidden `<input type="file">` has no `id` or associated `<label>`. While it's triggered programmatically via the button, some screen readers might still find and announce it as "file input" with no label.
- **Fix:** Add `id="file-upload"` and `aria-label="Choose files to upload"` to the input.

### L17. `CalibrationChart` receives `Record<string, unknown>` -- too loose

- **File:** `src/components/gamification/CalibrationChart.tsx:1-2` and `src/lib/types.ts:129`
- **Axis:** Correctness
- **Problem:** `calibration` is typed as `Record<string, unknown>`, then values are extracted with `Number(calibration.avg_confidence ?? 0)`. If the API changes field names, this silently returns 0 with no type error.
- **Fix:** Define a proper `CalibrationData` interface with `avg_confidence: number`, `avg_accuracy: number`, `calibration_score: number` and use it instead.

### L18. Study page has nested async logic inside `setTimeout`

- **File:** `src/app/(app)/study-sets/[id]/study/page.tsx:94-129`
- **Axis:** Correctness
- **Problem:** `handleRate` starts a `setTimeout` that runs an async function (`finalizeReview`) inside it. This async function is not error-handled at the `setTimeout` level. If `completeStudySession` or `getStrengthsWeaknesses` throws, the `submitting` state may not reset correctly since `setSubmitting(false)` is inside the async function, and the outer `catch` block (line 133) won't catch errors from the `setTimeout` callback.
- **Fix:** Move the delay logic to a state-based approach (e.g., a "showing review feedback" state with `useEffect` to transition after a delay), or at minimum wrap the entire `finalizeReview` body in try/catch with a `finally` that always calls `setSubmitting(false)`.
