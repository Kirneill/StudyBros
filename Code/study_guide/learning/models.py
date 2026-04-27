"""
SQLAlchemy models for learning science tracking — FSRS reviews, sessions,
progress, achievements, and gamification state.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from study_guide.database.models import Base


class CardReview(Base):
    """Individual card review event tracked by the FSRS scheduler."""

    __tablename__ = "card_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    study_set_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("study_sets.id"), nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    elapsed_days: Mapped[float] = mapped_column(Float, default=0.0)
    scheduled_days: Mapped[float] = mapped_column(Float, default=0.0)
    stability: Mapped[float] = mapped_column(Float, default=0.0)
    difficulty: Mapped[float] = mapped_column(Float, default=0.0)
    retrievability: Mapped[float] = mapped_column(Float, default=0.0)
    state: Mapped[str] = mapped_column(String(20), default="new")
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    confidence_rating: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<CardReview(id={self.id}, card={self.card_id}, "
            f"rating={self.rating}, state='{self.state}')>"
        )


class StudySession(Base):
    """A study session spanning one or more card reviews or quiz attempts."""

    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    study_set_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("study_sets.id"), nullable=True, index=True
    )
    session_type: Mapped[str] = mapped_column(String(50), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    confidence_sum: Mapped[float] = mapped_column(Float, default=0.0)
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    bloom_level_distribution: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    session_number: Mapped[int] = mapped_column(Integer, default=1)

    def __repr__(self) -> str:
        return (
            f"<StudySession(id={self.id}, type='{self.session_type}', "
            f"accuracy={self.accuracy:.2f})>"
        )


class UserProgress(Base):
    """Per-topic mastery and engagement tracking."""

    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("documents.id"), nullable=True, index=True
    )
    topic_tag: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )
    mastery_level: Mapped[float] = mapped_column(Float, default=0.0)
    bloom_highest_level: Mapped[int] = mapped_column(Integer, default=1)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    calibration_score: Mapped[float] = mapped_column(Float, default=0.0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    consistency_pct_30d: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<UserProgress(id={self.id}, topic='{self.topic_tag}', "
            f"mastery={self.mastery_level:.2f})>"
        )


class Achievement(Base):
    """Earned achievements tied to demonstrated competency."""

    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    achievement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    criteria_json: Mapped[str] = mapped_column(Text, nullable=False)
    bloom_level_required: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    earned_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    topic_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Achievement(id={self.id}, type='{self.achievement_type}', "
            f"title='{self.title}')>"
        )


class GamificationState(Base):
    """Global gamification state tracking the user's motivational phase."""

    __tablename__ = "gamification_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    phase: Mapped[int] = mapped_column(Integer, default=1)
    phase_entered_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    avg_accuracy_30d: Mapped[float] = mapped_column(Float, default=0.0)
    intrinsic_signals: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )

    def __repr__(self) -> str:
        return (
            f"<GamificationState(id={self.id}, phase={self.phase}, "
            f"sessions={self.total_sessions})>"
        )
