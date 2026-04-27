"""Pydantic request/response models for the StudyBros API."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


class DocumentResponse(BaseModel):
    id: int
    title: str | None
    word_count: int
    chunk_count: int
    created_at: datetime
    model_config = {"from_attributes": True}


class ChunkResponse(BaseModel):
    chunk_index: int
    content: str
    char_count: int


# ---------------------------------------------------------------------------
# Study Sets
# ---------------------------------------------------------------------------


class StudySetResponse(BaseModel):
    id: int
    set_type: str
    title: str | None
    item_count: int
    document_id: int | None
    created_at: datetime
    model_config = {"from_attributes": True}


class StudySetDetailResponse(StudySetResponse):
    content: dict | list


# ---------------------------------------------------------------------------
# FSRS / Study
# ---------------------------------------------------------------------------


class ReviewRequest(BaseModel):
    card_index: int
    rating: int = Field(ge=1, le=4, description="1=Again, 2=Hard, 3=Good, 4=Easy")
    confidence: int = Field(default=0, ge=0, le=5, description="0-5 self-reported confidence")


class ReviewResponse(BaseModel):
    stability: float
    difficulty: float
    retrievability: float
    state: str
    scheduled_days: float
    next_review: datetime


class DueCardResponse(BaseModel):
    card_id: int
    retrievability: float
    state: str
    last_review: datetime


class MasteryResponse(BaseModel):
    mastered: bool
    details: dict


class ProgressResponse(BaseModel):
    topic: str
    mastery_level: float
    bloom_highest_level: int
    total_reviews: int


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

GenerationProvider = Literal["openai", "anthropic", "openrouter"]


class GenerateRequest(BaseModel):
    document_id: int
    count: int = Field(default=10, ge=1, le=50)
    difficulty: Literal["easy", "medium", "hard", "mixed"] = "mixed"
    provider: GenerationProvider = "openai"
    api_key: str | None = Field(default=None, min_length=1)
    model: str | None = None


class GenerationProviderResponse(BaseModel):
    provider: GenerationProvider
    display_name: str
    has_server_key: bool
    default_model: str


class GenerationProvidersResponse(BaseModel):
    providers: list[GenerationProviderResponse]


# ---------------------------------------------------------------------------
# Gamification
# ---------------------------------------------------------------------------


class AchievementResponse(BaseModel):
    title: str
    description: str
    type: str
    bloom_level: int | None
    topic: str | None
    earned_at: str | None


class PhaseResponse(BaseModel):
    phase: int
    phase_name: str
    total_sessions: int
    avg_accuracy_30d: float


class StrengthsWeaknessesResponse(BaseModel):
    strengths: list[dict]
    weaknesses: list[dict]
    recommendations: list[dict]
    calibration: dict


class ConsistencyResponse(BaseModel):
    streak_days: int
    consistency_pct_30d: float
    studied_dates: list[str]


class ScheduleCardResponse(BaseModel):
    card_id: int
    retrievability: float
    stability: float
    difficulty: float
    state: str
    last_review: str
    scheduled_days: float


class ScheduleResponse(BaseModel):
    study_set_id: int
    due_count: int
    total_reviewed: int
    cards: list[ScheduleCardResponse]


class StatsResponse(BaseModel):
    sources: int
    documents: int
    chunks: int
    study_sets: int
