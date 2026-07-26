# Part 1 — The Problem & The Learning Science

**Presenter: ___**

**Time budget: ~2–2.5 minutes** — the verbatim Script below IS your talk; the Talking Points are your extended Q&A depth. You open the presentation, so you also set the tone and introduce the team in your first 15 seconds.

## Your Scope (what YOU cover)

- **Why the app exists** — the problem StudyBros solves.
- **The learning-science backbone** that makes it different from "an app that spits out flashcards": FSRS spaced repetition, active recall / the testing effect, the 85% difficulty rule, and Bloom's taxonomy for depth of understanding.
- The one-sentence framing that the whole team reuses: *the AI generates the study material, but the real product is the science-backed workflow that happens after generation.*

## NOT Your Scope (belongs to other parts — don't cover these)

- **How FSRS is implemented in code**, the database, ingestion, or the MCP server → **Part 2**.
- **How the AI actually generates cards**, prompts, structured output, model providers → **Part 3**.
- **Gamification** (streaks, achievements, "You Won" moments), the frontend, and the live demo → **Part 4**. You *motivate* why learning takes sustained effort; Part 4 shows the gamification that sustains it. Hand the word "gamification" to them.

## Talking Points (full sentences — rehearse these)

1. "Most students study by rereading their notes and highlighting, and it feels productive — but the research is blunt: rereading produces almost no durable memory. Five minutes after you close the book it looks like it worked; a week later it's mostly gone."
2. "StudyBros is built on the opposite of rereading. It takes whatever you already have — lecture slides, a PDF, a recorded lecture — and turns it into active practice with a schedule, so you're tested at the moment you're about to forget, not before and not after."
3. "The scheduling engine is FSRS, the Free Spaced Repetition Scheduler. It models your memory of each card with a forgetting curve and reschedules the card for the exact day your recall would drop to about ninety percent. In a benchmark of seven hundred million reviews it beat the classic Anki algorithm and needed twenty to thirty percent fewer reviews for the same retention."
4. "Every card requires you to answer *before* it shows you the solution. That's not a UI preference — it's the testing effect and the generation effect. Even guessing wrong before you see the right answer measurably improves memory, because your brain files the correction instead of just recognizing the words."
5. "We deliberately aim for about eighty-five percent accuracy, not a hundred. That number comes from a 2019 Nature paper: the fastest learning happens when roughly fifteen percent of your answers are wrong. Too easy and you're not learning; too hard and you're just failing. So the system nudges difficulty toward that sweet spot."
6. "And we don't treat 'I memorized the definition' as the finish line. We tag every item with a level of Bloom's taxonomy — from Remember, up through Understand and Apply, to Analyze and Create. A topic only counts as *mastered* when you can operate at Apply or higher with high retention and high accuracy — not when you can parrot a flashcard."
7. (Handoff) "So that's *why* the app is shaped the way it is. Everything you'll see next — the pipeline, the AI, the interface — exists to serve that science. [Name] will walk you through how it's actually built."

## Script (2–3 minutes, verbatim)

I want to start with why we built this at all. Every one of us has done the thing where you reread your notes the night before an exam, highlight half the page, feel ready, and then blank on the test. That feeling of readiness is real, but it's mostly recognition — you recognize the words on the page, which is not the same as being able to recall them cold. Five minutes after you close the notes it looks like studying worked; a week later most of it is gone.

StudyBros is built to fight exactly that. You give it what you already have — a PDF of the slides, a lecture recording, your own notes — and it turns that passive material into active practice on a schedule. The scheduling is the part I worked on, and it runs on an algorithm called FSRS, the Free Spaced Repetition Scheduler (see Code/study_guide/learning/scheduler.py). For every card it keeps a small model of your memory and predicts the day your recall will fall to about ninety percent, then shows you the card right at that point — not so early you're wasting time, not so late you've already forgotten. In the published benchmarks FSRS needed twenty to thirty percent fewer reviews than the old Anki formula for the same retention.

There are three ideas I want you to hold onto. First, every card makes you answer before it reveals the solution — that's the testing effect, and even guessing wrong first helps, because your brain files the correction. Second, we aim for about eighty-five percent accuracy on purpose, not a hundred; a 2019 Nature paper showed that's the error rate where people learn fastest. Third, we don't stop at memorizing — every item is tagged with a level of Bloom's taxonomy, and a topic only counts as mastered when you can work at Apply or higher, with high retention and high accuracy, all at the same time (the exact rule is the check_mastery function in scheduler.py).

So that's the why: the science decides the shape of everything else. Next, [Name] is going to show you how we actually built the system that delivers it.

### Side notes for judge questions

- FSRS v5 with 19 tuned weights (w0–w18) from the paper; `desired_retention` is hardcoded to 0.9 and `maximum_interval` to 36500 days (Code/study_guide/learning/scheduler.py, `FSRS_DEFAULTS`).
- Retrievability is `R = (1 + elapsed_days / (9 · S))^-1`; the next interval is `round(9 · S · (1/0.9 − 1))` days, clamped to at least 1 (scheduler.py, `calculate_retrievability` / `calculate_next_interval`).
- Mastery requires ALL four at once: every card's retrievability > 0.90, every card's scheduled interval > 30 days, average accuracy over each card's last 3 reviews > 0.85, and `bloom_highest_level >= 3` (Apply) (scheduler.py, `check_mastery`).
- Ratings are 1–4 (Again/Hard/Good/Easy); a review counts as "correct" when the rating is >= 2; an out-of-range rating raises a ValueError (scheduler.py, `schedule_card`).
- Due cards are only surfaced when current retrievability drops below 0.9 and are sorted lowest-retrievability-first, so the most-urgent card comes up first (scheduler.py, `get_due_cards`).
- The research behind all of this is cited in StudyGuideResearch/01-learning-science.md — Roediger & Karpicke (2006) for the testing effect, Wilson et al. (2019, Nature Communications) for the 85% rule.

## Slides You Build (maps to the outline in `PresentationSlides/slideshowto.txt`)

- **Slide: Problem & Motivation** — one stark contrast (reread-and-forget vs. active recall). One image or curve, few words.
- **Slide: The Science (Design Highlights, part 1 of the deck)** — four labeled callouts: *FSRS scheduling*, *Active recall*, *85% rule*, *Bloom's mastery*. Keep it to four; Part 3 covers a separate "Design Highlights" slide about the AI.

## Source Material To Pull From

- `StudyGuideResearch/01-learning-science.md` — this is your primary source. Sections 1 (Spaced Repetition), 2 (Active Recall), 9 (Bloom's Taxonomy), 14 (Generation Effect), and 15 (The 85% Rule) are exactly your five talking points. Cite the researcher names if the professor likes rigor: Roediger & Karpicke (2006) for the testing effect, Wilson et al. (2019) for the 85% rule.
- `README.md` → "How FSRS Works" section has the exact retrievability formula `R = (1 + t / (9 * S))^(-1)` and the mastery definition if you want one precise technical line.
- `Presentation.md` → the "Open With The Problem" script is the seed for talking point 1.

## Demo Responsibility

**None — you present concepts only.** Do not open the app. Your job is to make the audience *want* the workflow that Part 4 will demo. Keep momentum; don't stall on a live tool.

## Likely Questions & Suggested Answers

- **Q (professor): "Isn't this just Anki with an AI wrapper?"**
  A: "The scheduling shares DNA with Anki, but two things differ. First, we use FSRS, which is a newer memory-model algorithm that beat Anki's SM-2 in a 728-million-review benchmark. Second, Anki makes *you* write every card by hand — the friction that stops most students. We remove that: you drop in your existing material and the cards are generated for you, then scheduled with the better algorithm."

- **Q: "How do you know a student has actually mastered a topic instead of just memorizing?"**
  A: "We separate performance from learning. Mastery in our system requires three things at once: retrievability above ninety percent at intervals longer than thirty days, accuracy above eighty-five percent, and questions answered at Bloom's level three or higher — Apply and above, not just Remember. Memorizing a definition can't satisfy the Bloom's requirement."

- **Q: "Where does the 85% number come from — did you make it up?"**
  A: "No — Wilson and colleagues, Nature Communications, 2019. They showed mathematically that for a learning system the optimal error rate is about fifteen-point-nine percent, i.e. roughly eighty-five percent accuracy. It lines up with Vygotsky's zone of proximal development. We target it explicitly as the difficulty feedback loop."
