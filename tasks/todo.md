# StudyBros — Task List

Last updated: 2026-04-27

---

## Phase A: Landing Page Overhaul

### A1. Build Landing Page
- [ ] **Status:** NOT STARTED
- **File:** `Code/frontend/src/app/page.tsx`
- **Scope:** Replace placeholder hero with full 9-section marketing page based on the behavioral economics research brief (see TODO.md § "Landing Page Overhaul")
- **Sections:** Hero → Forgetting Curve → Three Ways → How It Works → Science → Comparison → Social Proof → Instant Value CTA → Footer CTA
- **Constraints:**
  - Server component (no `"use client"` on the page itself; `AnimateIn` is already client)
  - No new npm dependencies — CSS/SVG for the forgetting curve
  - Use existing design tokens, `AnimateIn`, `Card`, `Button` components
  - Single primary CTA throughout ("Try It Free" → links to `/upload`)
  - Mobile-responsive (single column on mobile, multi-column on desktop)
- **Acceptance criteria:**
  - [ ] Page renders 9 distinct sections with scroll animations
  - [ ] Forgetting curve visualization is visible and animated
  - [ ] Three delivery surfaces (MCP, LLM Skills, Web App) are explained
  - [ ] Comparison table shows StudyBros vs alternatives
  - [ ] Single clear CTA path leads to `/upload`
  - [ ] `npm run build` passes
  - [ ] `npm run lint` passes

### A2. Verify Build
- [ ] **Status:** NOT STARTED
- **Scope:** Run lint + build to confirm no regressions
- **Acceptance criteria:**
  - [ ] `npm run lint` — 0 errors
  - [ ] `npm run build` — successful

### A3. User Review Checkpoint
- [ ] **Status:** NOT STARTED
- **Scope:** Present landing page to user for review. User decides: approve, request changes, or rework.
- **Acceptance criteria:**
  - [ ] User has reviewed the landing page (start dev server or provide screenshots)
  - [ ] User approves or provides specific feedback

---

## Phase B: UI/UX Audit + Fixes

### B1. Audit All Frontend Pages
- [ ] **Status:** NOT STARTED
- **Scope:** Read every page and component. Produce a findings report with severity ratings.
- **Axes:** Accessibility, performance, resilience, design consistency, UX flow
- **Pages:** All 18 routes + layout + error boundaries + gamification components
- **Output:** Findings list in `tasks/audit-findings.md` with severity (critical/high/low)
- **Acceptance criteria:**
  - [ ] Every page read and assessed
  - [ ] Findings documented with file paths and line numbers
  - [ ] Issues prioritized by severity

### B2. Fix Critical + High Issues
- [ ] **Status:** NOT STARTED
- **Scope:** Fix all critical and high-severity findings from B1
- **Constraints:** No new features. Only fix what the audit surfaces.
- **Acceptance criteria:**
  - [ ] All critical issues resolved
  - [ ] All high issues resolved (or justified deferral documented)
  - [ ] `npm run lint` passes
  - [ ] `npm run build` passes

### B3. Verify Build After Fixes
- [ ] **Status:** NOT STARTED
- **Acceptance criteria:**
  - [ ] `npm run lint` — 0 errors
  - [ ] `npm run build` — successful
  - [ ] `pytest -q` — all pass (if any backend touched)

### B4. User Review Checkpoint
- [ ] **Status:** NOT STARTED
- **Scope:** Present audit findings + fixes to user for review
- **Acceptance criteria:**
  - [ ] User reviews the audit report and fixes
  - [ ] User approves or provides feedback

---

## Deferred Items

### D1. Add real LLM Skills URLs to AI Setup page
- [ ] **Status:** BLOCKED (needs backend deployment)
- **File:** `Code/frontend/src/app/docs/ai-setup/page.tsx`
- **Problem:** The "LLM Skills (Paste a Link)" section references `llms.txt` and `llms-full.txt` but has no actual URLs to copy. The files exist in the repo at `Code/docs/` but aren't hosted yet.
- **Fix:** Once the backend is deployed, update the page with real hosted URLs (e.g., `https://your-domain/docs/llms.txt`). Alternatively, link to the raw GitHub files as an interim solution: `https://raw.githubusercontent.com/Kirneill/StudyBros/main/Code/docs/llms.txt`

---

## Phase C: Vercel Deployment

### C1. Backend Hosting Decision
- [ ] **Status:** NOT STARTED
- **Scope:** User decides backend hosting strategy
- **Options:**
  - A: Railway (recommended — free tier, one-click Python deploy)
  - B: Render (free tier, Docker support)
  - C: Frontend-only demo (no backend, app shows empty states)
- **Acceptance criteria:**
  - [ ] User picks an option
  - [ ] If A or B: account created, backend deployed, URL known

### C2. Update API URL Configuration
- [ ] **Status:** NOT STARTED
- **Scope:** Point frontend to production backend
- **Files to change:**
  - `Code/frontend/vercel.json` — update rewrite destination
  - `Code/frontend/next.config.ts` — update fallback API_URL
  - `Code/api/main.py` — add Vercel production domain to CORS
- **Acceptance criteria:**
  - [ ] `vercel.json` rewrites point to production backend URL
  - [ ] CORS allows the Vercel domain
  - [ ] `npm run build` still passes

### C3. Deploy Frontend to Vercel
- [ ] **Status:** NOT STARTED
- **Scope:** Deploy Next.js app to Vercel
- **Steps:**
  1. `cd Code/frontend && npx vercel` (or link to existing project)
  2. Set environment variable `API_URL` in Vercel dashboard
  3. Deploy to production
- **Acceptance criteria:**
  - [ ] Vercel build succeeds
  - [ ] Production URL accessible
  - [ ] Landing page renders correctly

### C4. Production Smoke Test
- [ ] **Status:** NOT STARTED
- **Scope:** Verify golden path works on production
- **Test checklist:**
  - [ ] Landing page loads, all sections render
  - [ ] Navigate to `/dashboard` — loads (empty state OK)
  - [ ] Navigate to `/upload` — drag-drop zone renders
  - [ ] Upload a test file — succeeds (requires backend)
  - [ ] Navigate to `/documents` — shows uploaded doc
  - [ ] Navigate to `/progress` — gamification UI renders
  - [ ] Navigate to `/achievements` — page renders
  - [ ] API proxy: `GET /api/health` returns 200 (requires backend)
  - [ ] Mobile responsive: test at 375px width

### C5. Custom Domain (Optional)
- [ ] **Status:** NOT STARTED
- **Scope:** If user wants a custom domain, configure in Vercel
- **Acceptance criteria:**
  - [ ] Domain resolves to Vercel deployment
  - [ ] HTTPS working
  - [ ] CORS updated for custom domain
