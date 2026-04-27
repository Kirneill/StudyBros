export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export const MASTERY_COLORS = {
  none: "var(--color-mastery-none)",
  learning: "var(--color-mastery-learning)",
  review: "var(--color-mastery-review)",
  mastered: "var(--color-mastery-mastered)",
  gold: "var(--color-mastery-gold)",
} as const;

export const BLOOM_LEVELS = [
  { level: 1, name: "Remember", color: "var(--color-bloom-remember)" },
  { level: 2, name: "Understand", color: "var(--color-bloom-understand)" },
  { level: 3, name: "Apply", color: "var(--color-bloom-apply)" },
  { level: 4, name: "Analyze", color: "var(--color-bloom-analyze)" },
] as const;

export const FSRS_RATINGS = [
  { value: 1 as const, label: "Again", color: "var(--color-error)", description: "Complete blackout" },
  { value: 2 as const, label: "Hard", color: "var(--color-warning)", description: "Significant difficulty" },
  { value: 3 as const, label: "Good", color: "var(--color-bloom-understand)", description: "Some hesitation" },
  { value: 4 as const, label: "Easy", color: "var(--color-accent)", description: "Perfect recall" },
] as const;

export const STUDY_SET_TYPES = {
  flashcards: { label: "Flashcards", icon: "📇" },
  quiz: { label: "Quiz", icon: "❓" },
  practice_test: { label: "Practice Test", icon: "📝" },
  audio_summary: { label: "Summary", icon: "🔊" },
} as const;

export const PHASE_NAMES: Record<number, string> = {
  1: "Habit Formation",
  2: "Growing Competence",
  3: "Intrinsic Motivation",
};
