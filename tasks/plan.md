# StudyBros — Ship-to-Vercel Plan

## Current State

**Done:** Phases 0–6 complete. MCP server (stdio, 10 tools, 9 resources, 8 prompts), FastAPI backend (all routes, gamification, FSRS), Next.js frontend (20 pages, gamification UI, study modes), 11 bug fixes. Backend test suite: 206 passed. Frontend: lint + build clean.

**Not done:** Landing page is a placeholder. No UI/UX audit. Not deployed to Vercel. Backend has no production host.

## What Remains — 3 Phases

```
Phase A: Landing Page Overhaul
  → USER REVIEW CHECKPOINT
Phase B: UI/UX Audit + Fixes
  → USER REVIEW CHECKPOINT
Phase C: Vercel Deployment
  → LIVE VERIFICATION
```

---

## Phase A: Landing Page Overhaul

### Dependency Graph

```
A1 (Landing page build) → A2 (Lint + build verify) → A3 (User review)
```

### Why This First

The landing page is the first thing users (and capstone reviewers) see. The current page is a generic hero with no feature breakdown, no explanation of the three delivery surfaces, and no persuasive copy. The behavioral economics research brief (in TODO.md) is complete — this is pure implementation.

### Scope

Single file: `Code/frontend/src/app/page.tsx` (server component, outside `(app)` layout — no sidebar).

Uses existing design system: Tailwind 4 tokens, `AnimateIn` component, `Card`/`Button` from `ui/`. May need a few CSS-only additions in `globals.css` for the forgetting curve animation.

### Sections (from research brief)

| # | Section | Content |
|---|---------|---------|
| 1 | Hero | Loss aversion headline + single primary CTA |
| 2 | Problem | Forgetting curve visualization (CSS/SVG animated) |
| 3 | Three Ways to Study | MCP Server, LLM Skills, Web App cards |
| 4 | How It Works | Upload → Generate → Master (3-step flow) |
| 5 | Science Section | FSRS, Bloom's, 85% rule — with plain-language explanations |
| 6 | Comparison Table | StudyBros vs Anki vs Quizlet vs traditional study |
| 7 | Social Proof | Research authority quotes (not fake testimonials) |
| 8 | Instant Value CTA | Upload link embedded in page |
| 9 | Footer CTA | Final loss-aversion push |

### What NOT To Do

- No new npm dependencies (no chart libraries — use CSS/SVG)
- No client-side interactivity beyond AnimateIn scroll animations
- No backend changes
- No new component files — everything inline in `page.tsx` (it's a marketing page, not reusable UI)

---

## Phase B: UI/UX Audit + Fixes

### Dependency Graph

```
B1 (Audit all pages) → B2 (Fix critical issues) → B3 (Lint + build verify) → B4 (User review)
```

### Why After Landing Page

The audit should cover the landing page too — build it first, audit everything together.

### Scope

Audit all 20 frontend pages across these axes:

| Axis | What to Check |
|------|--------------|
| **Accessibility** | Focus management, aria labels, color contrast, keyboard nav, screen reader text |
| **Performance** | Unnecessary client components, bundle-impacting patterns, lazy loading |
| **Resilience** | Empty states, loading states, error boundaries, API failure handling |
| **Design Consistency** | Token usage, spacing, typography, component reuse, responsive behavior |
| **UX Flow** | Navigation dead ends, confusing states, missing affordances |

### Pages to Audit

1. Landing page (`page.tsx`)
2. Dashboard (`dashboard/page.tsx`)
3. Upload (`upload/page.tsx`)
4. Documents list (`documents/page.tsx`)
5. Document detail (`documents/[id]/page.tsx`)
6. Generate (`documents/[id]/generate/page.tsx`)
7. Study sets list (`study-sets/page.tsx`)
8. Study set detail (`study-sets/[id]/page.tsx`)
9. Flashcard study (`study-sets/[id]/study/page.tsx`)
10. Quiz (`study-sets/[id]/quiz/page.tsx`)
11. Practice test (`study-sets/[id]/test/page.tsx`)
12. Completion (`study-sets/[id]/complete/page.tsx`)
13. Progress (`progress/page.tsx`)
14. Achievements (`achievements/page.tsx`)
15. Error boundary (`error.tsx`, `(app)/error.tsx`)
16. Not found (`not-found.tsx`)
17. Loading (`(app)/loading.tsx`)
18. App layout + sidebar (`(app)/layout.tsx`)

### Fix Strategy

- **Critical** (a11y violations, broken flows, wrong data): Fix immediately
- **High** (missing empty states, inconsistent tokens, responsive breaks): Fix in this phase
- **Low** (polish, animation tweaks, copy improvements): Note but skip unless trivial

---

## Phase C: Vercel Deployment

### Dependency Graph

```
C1 (Backend deploy decision) → C2 (Update API URL config)
C2 → C3 (Vercel project setup + deploy)
C3 → C4 (Smoke test production)
C4 → C5 (DNS/domain if applicable)
```

### Architecture Decision: Backend Hosting

Vercel runs serverless Node.js — it cannot host the Python FastAPI backend. Options:

| Option | Pros | Cons |
|--------|------|------|
| **A: Railway** | One-click Python deploy, free tier, auto-sleep | Cold starts on free tier |
| **B: Render** | Free tier, Docker support, auto-deploy from git | Cold starts on free tier, 15-min spin-down |
| **C: Vercel serverless (rewrite API as Next.js routes)** | Single deploy, no separate host | Massive rewrite, SQLite won't persist on serverless |
| **D: Skip backend deploy (frontend-only demo)** | Zero backend cost, fastest path | App shows empty states, no generation, no study flow |

**Recommendation:** Option A or B (Railway or Render) for backend. The app needs a persistent SQLite file and long-running generation requests — serverless doesn't fit. This is a capstone demo, so free tier with cold starts is acceptable.

**User must decide:** Which backend host? Or frontend-only demo?

### Frontend Deploy Steps

1. Update `vercel.json` rewrites to point to the production backend URL
2. Set `API_URL` environment variable in Vercel project settings
3. `vercel deploy` from `Code/frontend/`
4. Verify: landing page loads, API proxy works, golden path functions

### What Needs to Change

- `Code/frontend/vercel.json` — Update rewrite destination from `localhost:8000` to production backend URL
- Vercel project env var: `API_URL=https://<backend-host>/`
- Backend CORS: Add Vercel production domain to allowed origins in `Code/api/main.py`

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Backend cold starts during demo | High (free tier) | Medium | Pre-warm before presenting; add loading states |
| SQLite concurrency under load | Low (single user) | Low | Acceptable for capstone |
| Vercel build fails (Next.js 16 edge cases) | Low | Medium | Build locally first, fix before deploying |
| Landing page too long/overwhelming | Medium | Low | User review checkpoint catches this |
| API URL misconfigured in production | Medium | High | Smoke test every endpoint after deploy |

---

## Estimated Effort

| Phase | Tasks | Est. Time |
|-------|-------|-----------|
| A: Landing Page | 3 tasks | 1–2 hours |
| B: UI/UX Audit + Fixes | 4 tasks | 1–2 hours |
| C: Vercel Deployment | 5 tasks | 1–2 hours |
| **Total** | **12 tasks** | **3–6 hours** |
