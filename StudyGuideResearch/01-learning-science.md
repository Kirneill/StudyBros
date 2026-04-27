# Evidence-Based Learning Science Research

> Research grounding KSpider's architecture in cognitive science. Every design decision traces to evidence here.

---

## 1. Spaced Repetition

**Evidence: STRONG** — Most replicated finding in cognitive psychology.

### How It Works
Information is better retained when study sessions are distributed over time rather than massed together (Ebbinghaus, 1885). Mechanism: spaced retrieval requires more effortful processing (strengthening traces) and contextual variability across sessions creates multiple retrieval routes.

### Optimal Intervals (Cepeda et al., 2008)
- Optimal inter-study interval is ~10-20% of the desired retention interval
- 1-week test: optimal gap = 1-3 days
- 1-year test: optimal gap = 18-36 days
- No single universal optimal interval exists

### Algorithm Comparison

| Algorithm | Approach | Key Feature | Weakness |
|---|---|---|---|
| **SM-2** (Wozniak, 1987) | Fixed formula: interval x ease factor | Simple, battle-tested in Anki | No memory model. Treats all users identically |
| **SM-5** (Wozniak, 1989) | Adaptive interval matrix | First fast-converging algorithm | Complex, closed-source |
| **FSRS** (Jarrett Ye, 2022-2024) | ML-optimized, 3-component memory model (Retrievability, Stability, Difficulty) | 99.6% superiority over SM-2 in benchmark (728M reviews, 10K users). 20-30% fewer reviews for same retention | Newer, less independently replicated |

### Architecture Implication
- Use FSRS as the scheduling engine
- Track per-card stability, difficulty, and retrievability
- Allow configurable desired retention rate (default 90%)

---

## 2. Active Recall (The Testing Effect)

**Evidence: STRONG** — Rated HIGH utility by Dunlosky et al. (2013).

### Core Finding (Roediger & Karpicke, 2006)
Students who took practice tests recalled significantly more after 1 week than students who restudied. At 5 minutes, restudying looked better — but by 1 week, testing was dramatically superior.

### Types of Recall (Most to Least Effective)
1. **Free recall** — generating answers with no cues (most effortful, most effective)
2. **Cued recall** — partial cues prompt target retrieval (standard flashcard format)
3. **Recognition** — selecting from options/multiple choice (least effective for learning)

### Architecture Implication
- Default to free recall (open-ended answer before reveal)
- Use cued recall for factual items
- Reserve multiple choice for initial exposure or very difficult material
- ALWAYS require an answer attempt before showing the solution

---

## 3. Interleaving

**Evidence: MODERATE-TO-STRONG** — Effect size g = 0.42 (Brunmair & Richter, 2019 meta-analysis).

### Why It Works
Forces learners to discriminate between problem types and strategies. Rohrer et al.: students who interleaved scored 3x better on exams than blocked practice.

### When It Does NOT Work
- When learners use rule-finding strategies (blocking is better: d = 0.64-0.76)
- For completely new concepts (need some baseline familiarity first)
- Low within-category similarity + high between-category similarity

### Metacognitive Illusion
Students consistently rate interleaved practice as harder and believe they learned less — despite performing better on tests.

### Architecture Implication
- After initial blocked introduction, switch to interleaved review
- Mix problem types from different topics in review sessions
- Warn users: "This feels harder because it's working"

---

## 4. Elaborative Interrogation

**Evidence: MODERATE** — Rated moderate utility by Dunlosky et al. (2013).

Prompting "Why is this true?" or "How does this work?" forces activation of prior knowledge schemas and integration with new information. Self-generated elaborations > provided explanations. Domain-specific prompts > generic ones.

### Architecture Implication
- Generate "Why?" and "How?" prompts after presenting information
- Require typed explanations, not click-through
- AI evaluates explanation quality and identifies gaps

---

## 5. Dual Coding Theory (Paivio, 1975)

**Evidence: MODERATE** — Strong for concrete/imageable content.

Two channels (verbal + visual) encode independently. When both encode the same information, retrieval routes are additive. Concrete words remembered ~2x better than abstract words. Critical: images must be meaningful and integrated, not decorative.

### Architecture Implication
- Pair flashcards with diagrams for spatial/structural/procedural content
- Avoid decorative images (they distract without helping)
- Allow users to create their own visual associations (generation effect bonus)

---

## 6. The Feynman Technique

**Evidence: MODERATE** (underlying mechanisms have strong evidence)

1. Choose a concept → 2. Explain in plain language → 3. Identify gaps → 4. Fill gaps → 5. Simplify with analogies

Backed by self-explanation effect (Chi et al., 1989: 3x better on tests) and protege effect (Roscoe & Chi, 2007: 10-20% higher scores when teaching others).

### Architecture Implication
- "Explain this concept" mode with AI as confused student
- Progressive difficulty: explain with notes → explain without notes
- AI identifies gaps and misconceptions in explanations

---

## 7. Pomodoro / Time-Boxed Study

**Evidence: MODERATE** — General principle of breaks is strong; specific 25-5 ratio has limited evidence.

- Optimal focus: 25-30 minutes (ultradian rhythms)
- Effective range: 20-45 minutes before significant fatigue
- BMC Medical Education review: Pomodoro correlates with performance (r=0.65), focus (r=0.72), engagement (r=0.68)

### Architecture Implication
- Default 25-minute sessions with break prompts
- User-configurable (25-50 min range)
- Track session length and correlate with performance to personalize
- After 4 sessions, suggest 15-30 minute break

---

## 8. Desirable Difficulties (Bjork, 1994)

**Evidence: STRONG** — Robust theoretical framework.

Training conditions that are difficult during practice yield greater long-term retention. Critical distinction: **performance is not learning.** Performance = what you can do now. Learning = what you can do later.

The four primary desirable difficulties:
1. Spacing over massing
2. Testing over restudying
3. Interleaving over blocking
4. Varying conditions over constant practice

Difficulty is "desirable" only when learner has sufficient prior knowledge and can eventually succeed.

### Architecture Implication
- This is the meta-principle justifying spacing, testing, and interleaving
- Design system to be slightly harder than comfortable
- Show long-term progress to counteract "it's not working" illusion

---

## 9. Bloom's Taxonomy (Revised: Anderson & Krathwohl, 2001)

| Level | Study Format | Example Question |
|---|---|---|
| **Remember** | Basic flashcards, fill-blank | "What is the formula for...?" |
| **Understand** | Explain-in-own-words, summaries | "Explain how X works" |
| **Apply** | Worked examples, practice problems | "Solve using this method" |
| **Analyze** | Comparison questions, case studies | "Compare X and Y approaches" |
| **Evaluate** | Scenario judgments, critiques | "Which solution is better and why?" |
| **Create** | Open-ended design prompts | "Design a system that..." |

### Architecture Implication
- Tag each study item with Bloom's level
- Ensure review sessions span multiple levels (not just Remember)
- AI generates higher-order questions from factual content
- "Mastery" requires Apply or higher, not just Remember

---

## 10. Metacognition

**Evidence: STRONG** — Predicts academic performance controlling for intelligence.

Two components: metacognitive knowledge (knowing what you know) + metacognitive regulation (planning, monitoring learning). Students are notoriously poor at self-assessment (illusion of knowing from re-reading fluency).

### Architecture Implication
- Confidence ratings after each answer (1-5 scale)
- Track calibration: confidence vs. actual accuracy over time
- Knowledge heat maps showing mastery state
- "I don't know" as valid response (penalize guessing less than confident wrong answers)

---

## 11. Concrete Examples & Worked Examples

**Evidence: STRONG for worked examples** (Sweller & Cooper, 1985).

Novices who studied worked examples outperformed those who solved equivalent problems — because problem-solving consumes working memory needed for schema acquisition. BUT the expertise reversal effect (Kalyuga, 2001): as learners gain skill, worked examples become redundant and harmful.

### Architecture Implication
- Worked examples for novices → fade to independent problems as expertise grows
- Detect expertise level and reduce scaffolding automatically
- Progressive: worked example → partial completion → independent problem

---

## 12. Sleep and Consolidation

**Evidence: STRONG**

During slow-wave sleep, memories transfer from hippocampus to neocortex. Meta-analysis: sleep deprivation before learning (g = 0.621) is 2.2x more damaging than after learning (g = 0.277). The forgetting curve shows a 24-hour "bump" — retention increases from 9h to 24h, consistent with sleep consolidation.

### Architecture Implication
- Suggest evening study for important material
- Discourage all-nighters (warn about consolidation impact)
- Track study timing and correlate with next-day performance

---

## 13. The Forgetting Curve (Ebbinghaus, 1885; replicated Murre & Dros, 2015)

| Interval | Retention (Savings %) |
|---|---|
| 20 minutes | ~42% |
| 1 hour | ~34% |
| 9 hours | ~27% |
| 1 day | ~32% (sleep bump) |
| 2 days | ~24% |
| 6 days | ~17% |
| 31 days | ~9% |

Each review resets the curve at a higher baseline and slows the rate of forgetting. After 4-5 well-spaced reviews, retention persists for months to years.

### Architecture Implication
- Visualize forgetting curve per card/topic
- Show predicted memory strength
- Show how each review flattens the curve

---

## 14. Generation Effect (Slamecka & Graf, 1978)

**Evidence: STRONG** — Robust across multiple paradigms.

Information generated by the learner is remembered better than information passively read. Even generating an INCORRECT answer before seeing the correct one improves learning (the "pretesting effect" / "productive failure"). Mechanism: generation activates knowledge structures and creates prediction error signals.

### Architecture Implication
- **Single most important design decision:** Always require answer attempt before reveal
- Even for new material, ask users to predict/guess first
- Fill-in-the-blank > passive reading, even when wrong
- Track wrong answers for elaborative hooks in later reviews

---

## 15. The 85% Rule (Wilson et al., 2019, Nature Communications)

**Evidence: MODERATE** — Mathematical derivation for gradient descent; theoretical for humans.

Optimal error rate for learning is ~15.87% (accuracy ~85%). Training at this difficulty produces exponential improvements in learning rate. Aligns with Vygotsky's zone of proximal development.

### Architecture Implication
- Target ~85% success rate across review sessions
- >90% consistently → increase difficulty (harder cards, higher Bloom's levels)
- <75% consistently → decrease difficulty (more scaffolding, hints)
- Dynamic difficulty adjustment is the key feedback loop

---

## Learning App Analysis: Science vs. Engagement Theater

### Science-Backed
- FSRS/SM-2 spaced repetition (Anki, RemNote)
- Active recall requiring answer generation
- Adaptive difficulty targeting ~85%
- Honest calibration feedback

### Engagement Theater (avoid)
- Streak counters (motivating but no learning benefit; causes anxiety)
- XP/points for time spent rather than material mastered
- Leaderboards (extrinsic motivation undermines intrinsic)
- "Set completed!" celebrations after passive reading
- Animations on correct answers (rewards feeling, not learning)

---

## Key Sources

- Dunlosky, J., et al. (2013). Psychological Science in the Public Interest, 14(1).
- Roediger, H. L., & Karpicke, J. D. (2006). Psychological Science, 17(3), 249-255.
- Cepeda, N. J., et al. (2008). Psychological Science, 19(11), 1095-1102.
- Bjork, R. A. (1994). Memory and metamemory considerations.
- Wilson, R. C., et al. (2019). Nature Communications, 10, 4646.
- Slamecka, N. J., & Graf, P. (1978). J. Exp. Psych: Human Learning & Memory, 4(6).
- Murre, J. M. J., & Dros, J. (2015). PLOS ONE, 10(7).
- Brunmair, M., & Richter, T. (2019). Psychological Bulletin, 145(11).
- Paivio, A. (1975, 1986). Dual Coding Theory.
- FSRS Benchmark: https://expertium.github.io/Benchmark.html
