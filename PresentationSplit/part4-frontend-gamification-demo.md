# Part 4 — Frontend, Gamification, Live Demo & Wrap-Up

**Presenter: ___**

**Time budget: ~2.5–3 minutes** (roughly 1.5 min frontend + gamification script, 60–90 s demo, ~20 s wrap-up + close). You go last and you drive the app, so **you own setup**: have both servers running *before* the presentation starts, not during. At this length the demo must be tight — if the room or the network is slow, show the **pre-generated study set** instead of generating live.

## Your Scope (what YOU cover)

- **The frontend** — the Next.js web app, its dark theme, and the pages a student actually moves through (upload → documents → generate → study sets → dashboard → progress).
- **Gamification** — the science-backed motivation layer: rolling streaks, competency-based achievements, and the "You Won" mastery moment. Emphasize it's *honest* gamification, not points-for-time-spent.
- **The live demo** — the real payoff of the whole talk.
- **The wrap-up** — Capstone I accomplishments, the Agile process, and next steps. You close for the whole team.

## NOT Your Scope (belongs to other parts)

- **The learning science behind the gamification** (why streaks are framed the way they are, the 85% rule) → **Part 1** grounded it; you *apply* it visually. Don't re-derive it.
- **How the backend/API serves the pages, ingestion, MCP** → **Part 2**. You show the UI; if something breaks under the hood, Part 2's presenter is your backup narrator.
- **How the AI generates the cards / provider internals** → **Part 3**. In the demo you just pick a provider and click generate; let the schema/provider explanation stay with Part 3.

## Talking Points (full sentences — rehearse these)

1. "Everything you've heard so far comes together in the web app. It's a Next.js front end with a deliberately calm dark theme — charcoal background, a teal accent, ivory text — because a study tool you'll open every day shouldn't fight you visually."
2. "The flow is linear and obvious: you upload your material, it becomes a document in your library, you generate study material from that document, and then you actually study — with a dashboard and a progress view tracking where you are."
3. "The motivation layer is gamification, but we were careful to make it honest. The research is clear that streak counters and points-for-time-spent are engagement theater — they cause anxiety and don't improve learning. So our streaks are a rolling 'five of seven days,' not a brittle consecutive count you lose in one missed day, and we *never* take away visible progress just because you were inactive."
4. "Achievements have to be *earned by demonstrated competence*, not participation — you unlock them by actually reaching a Bloom's level on a topic, not by clicking around. And when you truly master a topic, there's a deliberate 'You Won' moment — a real completion, not an endless treadmill. Motivation is scaffolded to fade over time: habit-building early, then competence, then the goal is that you keep studying because you want the knowledge, not the badge."
5. (Transition into demo) "Let me show you the real thing." — then run the demo below.
6. (After demo, wrap-up) "To put a bow on Capstone I: we shipped a working end-to-end system — ingestion across five-plus file types, AI generation with structured output across four providers, FSRS scheduling and mastery tracking, an MCP server, a REST API, and this web app — built over seven Agile sprints with full scrum documentation. Next steps are production deployment on Vercel, richer strengths-and-weaknesses analytics, and expanding ingestion to things like YouTube links."
7. (Close) "The one-line version: StudyBros takes raw learning material and turns it into an AI-assisted, spaced-repetition study workflow students can actually use day to day. Thank you — we're happy to take questions."

## Script (2–3 minutes, verbatim)

> Deliver the first three paragraphs, run the demo where marked, then come back for the close.

Everything you've heard so far ends up here, in the web app. It's a Next.js front end, and the dark theme was a deliberate choice — charcoal background, teal accent, ivory text — because this is a tool you're supposed to open every day, and something you use daily shouldn't be shouting at you. The pages live under Code/frontend/src/app, and the path through them is meant to be boring in a good way: upload your material, find it in your document library, generate study material from it, then actually study it. Flashcards, quizzes, and practice tests each get their own screen.

The motivation layer is the part I had to think hardest about. The research we read says streak counters and points for time spent are engagement theater — they make people anxious without making them learn. So our streak is a rolling five of the last seven days, not a consecutive count you lose the second you miss a day, and that's calculated in Code/study_guide/learning/gamification.py. Achievements have to be earned by actually demonstrating something — you unlock "Applied Knowledge" by hitting Bloom Level 3 on a topic, not by clicking around — and we never take back progress you already earned just because you went quiet for a week.

When you genuinely master a topic there's a real completion screen, with your stats and your strengths and weaknesses, instead of an endless treadmill. And the gamification itself is designed to fade: there are three phases, and as you get more consistent and more accurate, the interface quiets down. The goal is that eventually you're studying for the material, not the badge.

Let me show you the real thing. **[RUN THE DEMO]**

So, Capstone I. We shipped a working system end to end — ingestion across five-plus file types, AI generation across four providers with validated output, FSRS scheduling and mastery tracking, an MCP server, a REST API, and this web app — with a real test suite behind it, built over seven sprints with the scrum documentation to match. What's next is deploying to Vercel, deeper strengths-and-weaknesses analytics, and pulling in YouTube links as a source.

The one-line version: StudyBros takes raw material and turns it into a study workflow you'd actually keep using. Thank you — we're happy to take questions.

### Side notes for judge questions

- The rolling streak is real, not cosmetic: `calculate_consistency_streak` counts distinct days with a session in a rolling window and returns a "X of last 7 days" message. The `consistency_7` achievement needs 5 of the last 7 days; `consistency_30` needs 20 of the last 30 (Code/study_guide/learning/gamification.py).
- Three SDT phases with concrete thresholds in `detect_phase`: Phase 1 "Habit Formation" is the default; Phase 2 "Growing Competence" requires >= 20 sessions AND 30-day average accuracy above 70%; Phase 3 "Intrinsic Motivation" requires >= 40 sessions plus intrinsic signals (beyond_goal >= 5, voluntary_hard >= 3, ahead_schedule >= 3).
- Eight achievements are defined in `ACHIEVEMENT_DEFS`, and every one is competency-gated: first_session, consistency_7, consistency_30, accuracy_streak (85%+ across 3 consecutive sessions), bloom_apply (Level 3), bloom_analyze (Level 4), topic_mastery, and deep_mastery (95%+ accuracy AND Bloom Level 4+). `_try_award` checks for an existing award first, so nothing is granted twice.
- The "You Won" moment is a real route — Code/frontend/src/app/(app)/study-sets/[id]/complete/page.tsx — backed by `check_topic_completion`, which returns the mastery stats, a Bloom breakdown, up to 3 strengths and 2 weaknesses, and any achievement just earned.
- Metacognition is tracked, not just accuracy: confidence is rated 1–5, and a topic is flagged overconfident when confidence exceeds accuracy by more than 0.15 (underconfident in reverse) in `get_strengths_weaknesses`. Session feedback explicitly calls out the 85% sweet spot when you land under it (`calculate_session_stats`).
- Frontend is Next.js 16 / React 19 / TypeScript 5 / Tailwind 4 / Framer Motion 12 (CLAUDE.md), with 17 page routes under Code/frontend/src/app — including upload, documents, generate, study, quiz, test, achievements, progress, and settings. The gamification API lives in Code/api/routes/gamification.py and the logic is covered by 22 tests in Code/tests/test_gamification.py.

## THE LIVE DEMO (this is your responsibility — own it)

**Setup before you present (from `Presentation.md`):**
- Backend, from `F:\CLAUDE\Capstone1\Code`: `uvicorn api.main:app --reload --host 127.0.0.1 --port 8000`
- Frontend, from `F:\CLAUDE\Capstone1\Code\frontend`: `npm run dev -- --hostname 127.0.0.1 --port 3000`
- Open `http://127.0.0.1:3000`. Have 2-3 small sample files ready (one `.txt`/`.md`, one `.pdf`/`.pptx`). Have a **fast** provider key ready (OpenAI or Claude) — **not** Codex; Codex takes minutes.

**Demo flow (60–90 seconds — this fits the 7–10 min total; rehearse it with a timer):**
1. Go to `/upload`, upload one small file — say in passing it also takes PDF, PPTX, audio, and video.
2. Go to `/documents` — the upload is now a document you can generate from. Click **generate** on it (fast provider, key already entered before the talk).
3. While it generates, flip to the **pre-generated study set** at `/study-sets` and flip one flashcard.
4. Show `/dashboard` or `/progress` (pick ONE) — "this is the tracking layer" — and get out.

If you have spare time at the end, come back to the live generation result. The full five-step walkthrough in `Presentation.md` is for practice runs, not the stage.

**Safety nets (rehearse these):**
- Generation is not instant. **Pre-generate one study set before the presentation** so you can cut to a finished result if the live call is slow or fails.
- If upload fails: confirm backend is on `127.0.0.1:8000` and frontend on `:3000` and the file type is supported (Part 2's presenter can narrate the pipeline while you recover).
- If generation fails: the provider key is wrong or wasn't pasted into the modal — switch to your pre-generated set and keep talking.
- If the dashboard/progress look empty: say the line from the guide — "these views get richer after review activity; the thing to notice is the pipeline from upload to generated material to tracked learning."

## Slides You Build (maps to `PresentationSlides/slideshowto.txt`)

- **Slide: Design Highlights (UI)** — a screenshot of the dark-theme app + the gamification callouts (rolling streak, earned achievement, "You Won").
- **Slide: Capstone I Accomplishments** — bullet list of what shipped (this is an explicitly requested outline slide).
- **Slide: Next Steps** — Vercel deploy, analytics, YouTube ingestion (also an explicitly requested outline slide).
- Keep the app itself as the star — slides are backup in case the demo dies.

## Source Material To Pull From (real paths)

- `Presentation.md` → your entire demo script, the exact server commands, the recommended flow, the "if something goes wrong" fixes, and the one-line close all live here. **Read this file end to end before presenting.**
- `CLAUDE.md` → "Design Tokens" (the exact colors) and the "Gamification Rules" (rolling streaks, earned achievements, "You Won", never remove progress).
- `StudyGuideResearch/05-gamification-science.md` → the science-vs-engagement-theater backbone if the professor pushes on gamification.
- Real routes exist as `/upload`, `/documents`, `/study-sets`, `/dashboard`, `/progress`; the API routes behind them are in `Code/api/routes/` (`upload.py`, `generate.py`, `gamification.py`, etc.). Frontend is `Code/frontend/` (Next.js, `src/app`).

## Likely Questions & Suggested Answers

- **Q (professor): "Streaks and badges are cheap engagement tricks — how is this different?"**
  A: "We agree, and we designed against exactly that. The research calls point-for-time-spent and brittle streaks 'engagement theater' — they create anxiety without improving learning. So our streaks are a forgiving rolling five-of-seven, achievements require a demonstrated Bloom's level rather than participation, and mastering a topic ends with a real 'You Won' completion instead of an endless grind. And we never claw back visible progress for inactivity. The motivation is meant to fade as intrinsic interest takes over."

- **Q: "Is this actually deployed, or only running on your laptop?"**
  A: "Right now it runs locally, which is what you're seeing — and that's intentional for Capstone I, because it lets anyone run the whole stack with no cloud account. The architecture is already deployment-ready — the frontend targets Vercel and the backend is a standard FastAPI app — so production deployment is our first next step, not a rebuild."

- **Q: "What did each of you actually build, and how did you manage the work?"**
  A: "We ran seven Agile sprints — the daily scrums, sprint planning, reviews, and retrospectives are all archived in the project. Work split roughly along the layers you saw today: the learning-science and scheduling core, the ingestion-and-data backend, the AI generation layer, and the web front end plus gamification. The MCP server and REST API were shared integration work." (Fill in real names/ownership before presenting.)
