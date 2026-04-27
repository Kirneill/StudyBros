"""
Learning science module — FSRS scheduling, progress tracking, and gamification.
"""

from study_guide.learning.models import (
    Achievement,
    CardReview,
    GamificationState,
    StudySession,
    UserProgress,
)
from study_guide.learning.scheduler import (
    FSRS_DEFAULTS,
    calculate_initial_difficulty,
    calculate_initial_stability,
    calculate_next_difficulty,
    calculate_next_interval,
    calculate_next_stability,
    calculate_retrievability,
    check_mastery,
    get_due_cards,
    schedule_card,
)
from study_guide.learning.gamification import (
    calculate_consistency_streak,
    calculate_session_stats,
    check_and_award_achievements,
    check_topic_completion,
    detect_phase,
    get_achievements_earned,
    get_strengths_weaknesses,
)

__all__ = [
    "Achievement",
    "CardReview",
    "GamificationState",
    "StudySession",
    "UserProgress",
    "FSRS_DEFAULTS",
    "calculate_initial_difficulty",
    "calculate_initial_stability",
    "calculate_next_difficulty",
    "calculate_next_interval",
    "calculate_next_stability",
    "calculate_retrievability",
    "check_mastery",
    "get_due_cards",
    "schedule_card",
    "calculate_consistency_streak",
    "calculate_session_stats",
    "check_and_award_achievements",
    "check_topic_completion",
    "detect_phase",
    "get_achievements_earned",
    "get_strengths_weaknesses",
]
