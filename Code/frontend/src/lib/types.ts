// Documents
export interface Document {
  id: number;
  title: string | null;
  word_count: number;
  chunk_count: number;
  created_at: string;
}

export interface Chunk {
  chunk_index: number;
  content: string;
  char_count: number;
}

export interface UpdateDocumentRequest {
  title: string;
}

export interface BulkDeleteDocumentsRequest {
  document_ids: number[];
}

// Study Sets
export interface StudySet {
  id: number;
  set_type: string;
  title: string | null;
  item_count: number;
  document_id: number | null;
  created_at: string;
}

export interface StudySetDetail extends StudySet {
  content: Record<string, unknown> | unknown[];
}

// FSRS / Study
export interface ReviewRequest {
  card_index: number;
  rating: 1 | 2 | 3 | 4;
  confidence: number;
}

export interface ReviewResponse {
  stability: number;
  difficulty: number;
  retrievability: number;
  state: string;
  scheduled_days: number;
  next_review: string;
}

export interface DueCard {
  card_id: number;
  retrievability: number;
  state: string;
  last_review: string;
}

export interface MasteryResult {
  mastered: boolean;
  details: Record<string, unknown>;
}

export interface Progress {
  topic: string;
  mastery_level: number;
  bloom_highest_level: number;
  total_reviews: number;
}

export interface StudySessionCompleteRequest {
  total_items: number;
  correct_count: number;
  confidence_sum: number;
  bloom_level_distribution: Record<string, number>;
}

export interface StudySessionCompleteResponse {
  session_id: number;
  total_items: number;
  correct_count: number;
  accuracy: number;
}

// Generation
export type GenerationProvider = "openai" | "anthropic" | "openrouter";

export interface GenerateRequest {
  document_id: number;
  count: number;
  difficulty: "easy" | "medium" | "hard" | "mixed";
  provider: GenerationProvider;
  api_key?: string;
  model?: string;
}

export interface GenerationProviderInfo {
  provider: GenerationProvider;
  display_name: string;
  has_server_key: boolean;
  default_model: string;
}

export interface GenerationProvidersResponse {
  providers: GenerationProviderInfo[];
}

// Gamification
export interface Achievement {
  title: string;
  description: string;
  type: string;
  bloom_level: number | null;
  topic: string | null;
  earned_at: string | null;
}

export interface Phase {
  phase: number;
  phase_name: string;
  total_sessions: number;
  avg_accuracy_30d: number;
}

export interface StrengthsWeaknesses {
  strengths: Record<string, unknown>[];
  weaknesses: Record<string, unknown>[];
  recommendations: Record<string, unknown>[];
  calibration: Record<string, unknown>;
}

export interface ScheduleCard {
  card_id: number;
  retrievability: number;
  stability: number;
  difficulty: number;
  state: string;
  last_review: string;
  scheduled_days: number;
}

export interface Schedule {
  study_set_id: number;
  due_count: number;
  total_reviewed: number;
  cards: ScheduleCard[];
}

export interface Stats {
  sources: number;
  documents: number;
  chunks: number;
  study_sets: number;
}

// Flashcard content types
export interface Flashcard {
  front: string;
  back: string;
  bloom_level?: number;
  topic?: string;
}

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
  bloom_level?: number;
}

// Consistency
export interface ConsistencyData {
  streak_days: number;
  consistency_pct_30d: number;
  studied_dates: string[];
}
