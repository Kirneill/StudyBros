"""
Tests for the gamification engine.
"""

import json
from datetime import datetime, timedelta

import pytest

from study_guide.database.models import Document, Source, StudySet
from study_guide.learning.gamification import (
    calculate_consistency_streak,
    calculate_session_stats,
    check_and_award_achievements,
    check_topic_completion,
    detect_phase,
    get_achievements_earned,
    get_strengths_weaknesses,
)
from study_guide.learning.models import (
    Achievement,
    CardReview,
    GamificationState,
    StudySession,
    UserProgress,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sessions(db, count, accuracy=0.80, days_spread=1):
    """Create `count` study sessions spread across days."""
    now = datetime.utcnow()
    for i in range(count):
        s = StudySession(
            session_type="flashcard_review",
            total_items=10,
            correct_count=int(10 * accuracy),
            accuracy=accuracy,
            session_number=i + 1,
            started_at=now - timedelta(days=i * days_spread),
        )
        db.add(s)
    db.commit()


def _make_topic_with_reviews(
    db, topic_tag, bloom_level, stability, scheduled_days,
    ratings, days_ago=0,
):
    """Create source, doc, study set, progress, and card reviews."""
    source = Source(
        filename="t.txt", filepath="/t.txt", file_type="txt",
    )
    db.add(source)
    db.commit()

    doc = Document(
        source_id=source.id, raw_text="content", word_count=1,
    )
    db.add(doc)
    db.commit()

    ss = StudySet(
        document_id=doc.id,
        set_type="flashcards",
        content_json='{"cards":[]}',
        item_count=1,
    )
    db.add(ss)
    db.commit()

    progress = UserProgress(
        document_id=doc.id,
        topic_tag=topic_tag,
        bloom_highest_level=bloom_level,
        mastery_level=0.9,
        total_reviews=len(ratings),
    )
    db.add(progress)
    db.commit()

    now = datetime.utcnow()
    for i, rating in enumerate(ratings):
        review = CardReview(
            card_id=0,
            study_set_id=ss.id,
            rating=rating,
            stability=stability,
            difficulty=5.0,
            retrievability=0.95,
            elapsed_days=1.0,
            scheduled_days=scheduled_days,
            state="review",
            reviewed_at=now - timedelta(days=days_ago + len(ratings) - i),
        )
        db.add(review)
    db.commit()

    return progress, ss


# ---------------------------------------------------------------------------
# Phase detection
# ---------------------------------------------------------------------------

class TestDetectPhase:

    def test_detect_phase_habit_formation(self, test_db):
        """New user with <20 sessions should be phase 1."""
        _make_sessions(test_db, 5)
        result = detect_phase(test_db)

        assert result["phase"] == 1
        assert result["phase_name"] == "Habit Formation"
        assert result["total_sessions"] == 5

    def test_detect_phase_growing_competence(self, test_db):
        """User with 20+ sessions and good accuracy is phase 2."""
        _make_sessions(test_db, 25, accuracy=0.85)
        result = detect_phase(test_db)

        assert result["phase"] == 2
        assert result["phase_name"] == "Growing Competence"
        assert result["total_sessions"] == 25

    def test_detect_phase_intrinsic(self, test_db):
        """User with 40+ sessions and strong intrinsic signals is phase 3."""
        _make_sessions(test_db, 45, accuracy=0.90)

        # Seed intrinsic signals in existing state
        state = GamificationState(
            phase=2,
            total_sessions=45,
            avg_accuracy_30d=0.90,
            intrinsic_signals=json.dumps({
                "beyond_goal": 6,
                "voluntary_hard": 4,
                "ahead_schedule": 5,
            }),
        )
        test_db.add(state)
        test_db.commit()

        result = detect_phase(test_db)

        assert result["phase"] == 3
        assert result["phase_name"] == "Intrinsic Motivation"
        assert result["intrinsic_signals"]["beyond_goal"] >= 5

    def test_detect_phase_creates_state_record(self, test_db):
        """detect_phase should create a GamificationState if none exists."""
        _make_sessions(test_db, 3)
        detect_phase(test_db)

        state = test_db.query(GamificationState).first()
        assert state is not None
        assert state.phase == 1
        assert state.total_sessions == 3

    def test_detect_phase_updates_existing_state(self, test_db):
        """detect_phase should update an existing GamificationState."""
        state = GamificationState(phase=1, total_sessions=0)
        test_db.add(state)
        test_db.commit()

        _make_sessions(test_db, 25, accuracy=0.85)
        result = detect_phase(test_db)

        updated = test_db.query(GamificationState).first()
        assert updated.phase == result["phase"]
        assert updated.total_sessions == 25

    def test_detect_phase_strong_intrinsic_mid_sessions(self, test_db):
        """User with 25 sessions + strong intrinsic should be Phase 2."""
        _make_sessions(test_db, 25, accuracy=0.85)

        # Seed strong intrinsic signals
        state = GamificationState(
            phase=1,
            total_sessions=25,
            avg_accuracy_30d=0.85,
            intrinsic_signals=json.dumps({
                "beyond_goal": 6,
                "voluntary_hard": 4,
                "ahead_schedule": 5,
            }),
        )
        test_db.add(state)
        test_db.commit()

        result = detect_phase(test_db)

        # Should be Phase 2 (not Phase 1) because sessions >= 20
        # and accuracy > 70%, even though intrinsic signals are
        # strong (not enough sessions for Phase 3)
        assert result["phase"] == 2
        assert result["phase_name"] == "Growing Competence"


# ---------------------------------------------------------------------------
# Topic completion
# ---------------------------------------------------------------------------

class TestTopicCompletion:

    def test_topic_completion_not_mastered(self, test_db):
        """Incomplete topic returns completed=False."""
        _make_topic_with_reviews(
            test_db, "test-topic",
            bloom_level=2,
            stability=5.0,
            scheduled_days=10.0,
            ratings=[2, 2, 3],
        )

        result = check_topic_completion(test_db, "test-topic")
        assert result["completed"] is False
        assert result["topic"] == "test-topic"
        assert len(result["weaknesses"]) > 0

    def test_topic_completion_mastered(self, test_db):
        """Mastered topic returns celebration data."""
        _make_topic_with_reviews(
            test_db, "mastered-topic",
            bloom_level=4,
            stability=100.0,
            scheduled_days=60.0,
            ratings=[3, 4, 3],
            days_ago=0,
        )

        result = check_topic_completion(test_db, "mastered-topic")
        assert result["completed"] is True
        assert result["topic"] == "mastered-topic"
        assert len(result["strengths"]) > 0
        assert "bloom_breakdown" in result["stats"]

    def test_topic_completion_nonexistent(self, test_db):
        """Nonexistent topic returns empty result."""
        result = check_topic_completion(test_db, "nonexistent")
        assert result["completed"] is False
        assert result["stats"]["total_concepts"] == 0


# ---------------------------------------------------------------------------
# Strengths and weaknesses
# ---------------------------------------------------------------------------

class TestStrengthsWeaknesses:

    def test_strengths_weaknesses(self, test_db):
        """User with mixed topics gets correct categorization."""
        # Strong topic
        prog_strong = UserProgress(
            topic_tag="strong-topic",
            bloom_highest_level=4,
            mastery_level=0.9,
            total_reviews=20,
        )
        # Weak topic
        prog_weak = UserProgress(
            topic_tag="weak-topic",
            bloom_highest_level=1,
            mastery_level=0.2,
            total_reviews=5,
        )
        test_db.add_all([prog_strong, prog_weak])
        test_db.commit()

        # Add sessions with good accuracy (so the strong topic qualifies)
        _make_sessions(test_db, 5, accuracy=0.90)

        result = get_strengths_weaknesses(test_db)

        # The function should return structured data
        assert "strengths" in result
        assert "weaknesses" in result
        assert "recommendations" in result
        assert "calibration" in result

    def test_strengths_weaknesses_empty(self, test_db):
        """Empty DB returns empty lists."""
        result = get_strengths_weaknesses(test_db)
        assert result["strengths"] == []
        assert result["weaknesses"] == []
        assert result["recommendations"] == []


# ---------------------------------------------------------------------------
# Consistency streak
# ---------------------------------------------------------------------------

class TestConsistencyStreak:

    def test_consistency_streak(self, test_db):
        """Sessions across different days produce correct X-of-Y count."""
        now = datetime.utcnow()
        # Create sessions on 5 different days in the last 7
        for i in range(5):
            s = StudySession(
                session_type="review",
                total_items=5,
                correct_count=4,
                accuracy=0.80,
                session_number=i + 1,
                started_at=now - timedelta(days=i),
            )
            test_db.add(s)
        test_db.commit()

        result = calculate_consistency_streak(test_db, days=7)
        assert result["days_studied"] == 5
        assert result["window_days"] == 7
        assert result["percentage"] == pytest.approx(71.4, abs=0.1)
        assert result["current_week"]["days_studied"] == 5
        assert "5 of last 7 days" in result["message"]

    def test_consistency_streak_no_sessions(self, test_db):
        """No sessions means 0 days studied."""
        result = calculate_consistency_streak(test_db, days=30)
        assert result["days_studied"] == 0
        assert result["percentage"] == 0.0

    def test_consistency_streak_same_day_multiple(self, test_db):
        """Multiple sessions on the same day count as 1 day."""
        now = datetime.utcnow()
        for _ in range(3):
            s = StudySession(
                session_type="review",
                total_items=5,
                correct_count=4,
                accuracy=0.80,
                session_number=1,
                started_at=now,
            )
            test_db.add(s)
        test_db.commit()

        result = calculate_consistency_streak(test_db, days=7)
        assert result["days_studied"] == 1


# ---------------------------------------------------------------------------
# Achievements
# ---------------------------------------------------------------------------

class TestCheckAndAwardAchievements:

    def test_check_and_award_first_session(self, test_db):
        """First session awards 'first_session' achievement."""
        _make_sessions(test_db, 1)

        # Need a UserProgress for the topic_tag check
        prog = UserProgress(
            topic_tag="test-topic",
            bloom_highest_level=1,
            total_reviews=1,
        )
        test_db.add(prog)
        test_db.commit()

        newly = check_and_award_achievements(test_db, "test-topic")

        types = [a["type"] for a in newly]
        assert "first_session" in types

    def test_check_and_award_no_duplicates(self, test_db):
        """Already-earned achievement is not re-awarded."""
        _make_sessions(test_db, 1)
        prog = UserProgress(
            topic_tag="test-topic",
            bloom_highest_level=1,
            total_reviews=1,
        )
        test_db.add(prog)
        test_db.commit()

        first_run = check_and_award_achievements(test_db, "test-topic")
        first_types = [a["type"] for a in first_run]
        assert "first_session" in first_types

        # Run again — should NOT re-award
        second_run = check_and_award_achievements(test_db, "test-topic")
        second_types = [a["type"] for a in second_run]
        assert "first_session" not in second_types

    def test_check_and_award_bloom_apply(self, test_db):
        """Bloom Level 3+ awards bloom_apply achievement."""
        _make_sessions(test_db, 1)
        prog = UserProgress(
            topic_tag="bloom-topic",
            bloom_highest_level=3,
            total_reviews=10,
        )
        test_db.add(prog)
        test_db.commit()

        newly = check_and_award_achievements(test_db, "bloom-topic")
        types = [a["type"] for a in newly]
        assert "bloom_apply" in types

    def test_check_and_award_accuracy_streak(self, test_db):
        """3 consecutive sessions at 85%+ awards accuracy_streak."""
        now = datetime.utcnow()
        for i in range(3):
            s = StudySession(
                session_type="review",
                total_items=20,
                correct_count=18,
                accuracy=0.90,
                session_number=i + 1,
                started_at=now - timedelta(hours=i),
            )
            test_db.add(s)
        prog = UserProgress(
            topic_tag="acc-topic",
            bloom_highest_level=1,
            total_reviews=5,
        )
        test_db.add(prog)
        test_db.commit()

        newly = check_and_award_achievements(test_db, "acc-topic")
        types = [a["type"] for a in newly]
        assert "accuracy_streak" in types


class TestAchievementsEarned:

    def test_achievements_earned_sorted(self, test_db):
        """Achievements returned most recent first."""
        now = datetime.utcnow()
        a1 = Achievement(
            achievement_type="first_session",
            title="First Steps",
            description="First session",
            criteria_json="{}",
            earned_at=now - timedelta(days=5),
        )
        a2 = Achievement(
            achievement_type="bloom_apply",
            title="Applied Knowledge",
            description="Bloom L3",
            criteria_json="{}",
            bloom_level_required=3,
            earned_at=now - timedelta(days=1),
        )
        a3 = Achievement(
            achievement_type="accuracy_streak",
            title="Sharp Mind",
            description="3 sessions 85%+",
            criteria_json="{}",
            earned_at=now,
        )
        test_db.add_all([a1, a2, a3])
        test_db.commit()

        result = get_achievements_earned(test_db)

        assert len(result) == 3
        assert result[0]["type"] == "accuracy_streak"
        assert result[1]["type"] == "bloom_apply"
        assert result[2]["type"] == "first_session"

    def test_achievements_earned_empty(self, test_db):
        """No achievements returns empty list."""
        result = get_achievements_earned(test_db)
        assert result == []


# ---------------------------------------------------------------------------
# Session stats
# ---------------------------------------------------------------------------

class TestSessionStats:

    def test_calculate_session_stats(self, test_db):
        """Session stats are correctly calculated."""
        now = datetime.utcnow()
        ss = StudySession(
            session_type="flashcard_review",
            total_items=10,
            correct_count=8,
            accuracy=0.80,
            confidence_sum=35.0,
            session_number=1,
            started_at=now - timedelta(minutes=15),
            ended_at=now,
        )
        test_db.add(ss)
        test_db.commit()

        result = calculate_session_stats(test_db, ss.id)
        assert result["accuracy"] == 80.0
        assert result["total_items"] == 10
        assert result["correct_count"] == 8
        assert result["time_spent_minutes"] == pytest.approx(15.0, abs=0.1)

    def test_calculate_session_stats_nonexistent(self, test_db):
        """Nonexistent session returns zeroed stats."""
        result = calculate_session_stats(test_db, 999)
        assert result["accuracy"] == 0.0
        assert result["total_items"] == 0
