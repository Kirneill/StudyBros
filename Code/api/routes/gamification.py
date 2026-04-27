"""Gamification routes: phase, achievements, strengths/weaknesses, consistency."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import (
    AchievementResponse,
    ConsistencyResponse,
    PhaseResponse,
    StrengthsWeaknessesResponse,
)
from study_guide.learning.gamification import (
    calculate_consistency_streak,
    check_topic_completion,
    detect_phase,
    get_achievements_earned,
    get_strengths_weaknesses,
)

router = APIRouter()


@router.get("/phase", response_model=PhaseResponse)
def get_phase(db: Session = Depends(get_db)):
    """Get the current gamification phase."""
    result = detect_phase(db)
    db.commit()  # detect_phase flushes state; commit to persist
    return PhaseResponse(
        phase=result["phase"],
        phase_name=result["phase_name"],
        total_sessions=result["total_sessions"],
        avg_accuracy_30d=result["avg_accuracy_30d"],
    )


@router.get("/achievements", response_model=list[AchievementResponse])
def get_achievements(db: Session = Depends(get_db)):
    """Get all earned achievements."""
    return get_achievements_earned(db)


@router.get("/strengths-weaknesses", response_model=StrengthsWeaknessesResponse)
def get_sw(db: Session = Depends(get_db)):
    """Get strengths, weaknesses, recommendations, and calibration data."""
    result = get_strengths_weaknesses(db)
    return StrengthsWeaknessesResponse(
        strengths=result["strengths"],
        weaknesses=result["weaknesses"],
        recommendations=result["recommendations"],
        calibration=result["calibration"],
    )


@router.get("/consistency", response_model=ConsistencyResponse)
def get_consistency(db: Session = Depends(get_db)):
    """Get consistency streak data."""
    data = calculate_consistency_streak(db)
    return ConsistencyResponse(
        streak_days=data["current_week"]["days_studied"],
        consistency_pct_30d=data["percentage"] / 100,
        studied_dates=data["studied_dates"],
    )


@router.post("/complete/{topic}")
def complete_topic(topic: str, db: Session = Depends(get_db)):
    """Check topic completion and potentially award achievements."""
    result = check_topic_completion(db, topic)
    db.commit()
    return result
