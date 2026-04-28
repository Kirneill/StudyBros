import type {
  Achievement,
  Chunk,
  ConsistencyData,
  Document,
  DueCard,
  GenerateRequest,
  GenerationProvidersResponse,
  BulkDeleteDocumentsRequest,
  MasteryResult,
  Phase,
  Progress,
  ReviewRequest,
  ReviewResponse,
  Schedule,
  StudySessionCompleteRequest,
  StudySessionCompleteResponse,
  StrengthsWeaknesses,
  StudySet,
  StudySetDetail,
  UpdateDocumentRequest,
} from "./types";
import { API_BASE } from "./constants";

class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const headers: HeadersInit = { ...options?.headers };
  if (options?.body) {
    (headers as Record<string, string>)["Content-Type"] = "application/json";
  }
  const method = options?.method ?? "GET";
  const cache = method === "GET" ? "no-store" : options?.cache;
  const res = await fetch(url, { ...options, headers, cache });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? res.statusText);
  }
  return res.json() as Promise<T>;
}

// Health
export const checkHealth = () => request<{ status: string }>("/api/health");

// Documents
export const listDocuments = () => request<Document[]>("/api/documents");
export const getDocument = (id: number) => request<Document>(`/api/documents/${id}`);
export const getDocumentChunks = (id: number) => request<Chunk[]>(`/api/documents/${id}/chunks`);
export const updateDocument = (id: number, req: UpdateDocumentRequest) =>
  request<Document>(`/api/documents/${id}`, {
    method: "PATCH",
    body: JSON.stringify(req),
  });
export const deleteDocument = (id: number) =>
  request<{ detail: string }>(`/api/documents/${id}`, { method: "DELETE" });
export const bulkDeleteDocuments = (req: BulkDeleteDocumentsRequest) =>
  request<{ detail: string; deleted_documents: number; deleted_sources: number }>(
    "/api/documents/bulk-delete",
    {
      method: "POST",
      body: JSON.stringify(req),
    },
  );

// Upload
export async function uploadFile(file: File): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);
  const url = `${API_BASE}/api/upload/`;
  const res = await fetch(url, { method: "POST", body: formData });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? res.statusText);
  }
  return res.json() as Promise<Document>;
}

// Study Sets
export const listStudySets = () => request<StudySet[]>("/api/study-sets");
export const getStudySet = (id: number) => request<StudySetDetail>(`/api/study-sets/${id}`);
export const deleteStudySet = (id: number) =>
  request<{ detail: string }>(`/api/study-sets/${id}`, { method: "DELETE" });

// Export
export function getExportUrl(studySetId: number, format: string): string {
  return `${API_BASE}/api/export/${studySetId}?format=${format}`;
}

// Generate
export const getGenerationProviders = () =>
  request<GenerationProvidersResponse>("/api/generate/providers");
export const generateFlashcards = (req: GenerateRequest) =>
  request<StudySetDetail>("/api/generate/flashcards", {
    method: "POST",
    body: JSON.stringify(req),
  });
export const generateQuiz = (req: GenerateRequest) =>
  request<StudySetDetail>("/api/generate/quiz", {
    method: "POST",
    body: JSON.stringify(req),
  });
export const generatePracticeTest = (req: GenerateRequest) =>
  request<StudySetDetail>("/api/generate/practice-test", {
    method: "POST",
    body: JSON.stringify(req),
  });
export const generateSummary = (req: GenerateRequest) =>
  request<StudySetDetail>("/api/generate/summary", {
    method: "POST",
    body: JSON.stringify(req),
  });

// Study (FSRS)
export const recordReview = (studySetId: number, review: ReviewRequest) =>
  request<ReviewResponse>(`/api/study/${studySetId}/review`, {
    method: "POST",
    body: JSON.stringify(review),
  });
export const getDueCards = (studySetId: number) =>
  request<DueCard[]>(`/api/study/${studySetId}/due`);
export const getSchedule = (studySetId: number) =>
  request<Schedule>(`/api/study/${studySetId}/schedule`);
export const completeStudySession = (
  studySetId: number,
  session: StudySessionCompleteRequest,
) =>
  request<StudySessionCompleteResponse>(`/api/study/${studySetId}/session`, {
    method: "POST",
    body: JSON.stringify(session),
  });
export const checkMastery = (topic: string) =>
  request<MasteryResult>(`/api/study/mastery/${topic}`, { method: "POST" });
export const getProgress = () => request<Progress[]>("/api/study/progress");

// Gamification
export const getPhase = () => request<Phase>("/api/gamification/phase");
export const getAchievements = () => request<Achievement[]>("/api/gamification/achievements");
export const getStrengthsWeaknesses = () =>
  request<StrengthsWeaknesses>("/api/gamification/strengths-weaknesses");
export const getConsistency = () =>
  request<ConsistencyData>("/api/gamification/consistency");
export const completeTopic = (topic: string) =>
  request<Record<string, unknown>>(`/api/gamification/complete/${topic}`, { method: "POST" });

export { ApiError };
