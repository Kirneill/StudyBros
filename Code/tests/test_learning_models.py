"""
Tests for learning science SQLAlchemy models.
"""

from datetime import datetime

from study_guide.learning.models import (
    Achievement,
    CardReview,
    GamificationState,
    StudySession,
    UserProgress,
)


class TestCardReview:
    """Tests for the CardReview model."""

    def test_create_card_review(self, test_db):
        review = CardReview(
            card_id=0,
            study_set_id=1,
            rating=3,
            elapsed_days=0.0,
            scheduled_days=1.0,
            stability=3.12,
            difficulty=5.5,
            retrievability=1.0,
            state="new",
            reviewed_at=datetime.utcnow(),
        )
        test_db.add(review)
        test_db.commit()

        fetched = test_db.query(CardReview).first()
        assert fetched is not None
        assert fetched.card_id == 0
        assert fetched.rating == 3
        assert fetched.stability == 3.12
        assert fetched.state == "new"

    def test_card_review_defaults(self, test_db):
        review = CardReview(
            card_id=1,
            study_set_id=1,
            rating=2,
        )
        test_db.add(review)
        test_db.commit()

        fetched = test_db.query(CardReview).first()
        assert fetched.elapsed_days == 0.0
        assert fetched.scheduled_days == 0.0
        assert fetched.stability == 0.0
        assert fetched.difficulty == 0.0
        assert fetched.state == "new"
        assert fetched.confidence_rating is None

    def test_card_review_with_confidence(self, test_db):
        review = CardReview(
            card_id=2,
            study_set_id=1,
            rating=4,
            confidence_rating=5,
        )
        test_db.add(review)
        test_db.commit()

        fetched = test_db.query(CardReview).first()
        assert fetched.confidence_rating == 5


class TestStudySession:
    """Tests for the StudySession model."""

    def test_create_study_session(self, test_db):
        session_obj = StudySession(
            study_set_id=1,
            session_type="flashcard_review",
            total_items=10,
            correct_count=8,
            accuracy=0.8,
            session_number=1,
        )
        test_db.add(session_obj)
        test_db.commit()

        fetched = test_db.query(StudySession).first()
        assert fetched is not None
        assert fetched.session_type == "flashcard_review"
        assert fetched.total_items == 10
        assert fetched.correct_count == 8
        assert fetched.accuracy == 0.8

    def test_study_session_computed_accuracy(self, test_db):
        """Verify accuracy can be computed from counts."""
        total = 20
        correct = 17
        acc = correct / total

        session_obj = StudySession(
            session_type="quiz",
            total_items=total,
            correct_count=correct,
            accuracy=acc,
            session_number=2,
        )
        test_db.add(session_obj)
        test_db.commit()

        fetched = test_db.query(StudySession).first()
        assert fetched.accuracy == 0.85
        assert fetched.study_set_id is None  # cross-set session

    def test_study_session_defaults(self, test_db):
        session_obj = StudySession(
            session_type="practice_test",
            session_number=1,
        )
        test_db.add(session_obj)
        test_db.commit()

        fetched = test_db.query(StudySession).first()
        assert fetched.total_items == 0
        assert fetched.correct_count == 0
        assert fetched.confidence_sum == 0.0
        assert fetched.accuracy == 0.0
        assert fetched.bloom_level_distribution is None
        assert fetched.ended_at is None


class TestUserProgress:
    """Tests for the UserProgress model."""

    def test_create_user_progress(self, test_db):
        progress = UserProgress(
            topic_tag="machine-learning",
            mastery_level=0.65,
            bloom_highest_level=3,
            total_reviews=42,
        )
        test_db.add(progress)
        test_db.commit()

        fetched = test_db.query(UserProgress).first()
        assert fetched is not None
        assert fetched.topic_tag == "machine-learning"
        assert fetched.mastery_level == 0.65
        assert fetched.bloom_highest_level == 3
        assert fetched.total_reviews == 42

    def test_user_progress_defaults(self, test_db):
        progress = UserProgress(topic_tag="default-topic")
        test_db.add(progress)
        test_db.commit()

        fetched = test_db.query(UserProgress).first()
        assert fetched.mastery_level == 0.0
        assert fetched.bloom_highest_level == 1
        assert fetched.total_reviews == 0
        assert fetched.calibration_score == 0.0
        assert fetched.streak_days == 0
        assert fetched.consistency_pct_30d == 0.0
        assert fetched.document_id is None
        assert fetched.last_reviewed_at is None


class TestAchievement:
    """Tests for the Achievement model."""

    def test_create_achievement(self, test_db):
        achievement = Achievement(
            achievement_type="mastery",
            title="ML Master",
            description="Mastered machine learning basics",
            criteria_json='{"topic": "ml", "level": 0.9}',
            bloom_level_required=3,
            topic_id="ml",
        )
        test_db.add(achievement)
        test_db.commit()

        fetched = test_db.query(Achievement).first()
        assert fetched is not None
        assert fetched.achievement_type == "mastery"
        assert fetched.title == "ML Master"
        assert fetched.bloom_level_required == 3


class TestGamificationState:
    """Tests for the GamificationState model."""

    def test_create_gamification_state(self, test_db):
        state = GamificationState(
            phase=1,
            total_sessions=5,
            avg_accuracy_30d=0.82,
        )
        test_db.add(state)
        test_db.commit()

        fetched = test_db.query(GamificationState).first()
        assert fetched is not None
        assert fetched.phase == 1
        assert fetched.total_sessions == 5
        assert fetched.avg_accuracy_30d == 0.82
        assert fetched.intrinsic_signals is None

    def test_gamification_state_defaults(self, test_db):
        state = GamificationState()
        test_db.add(state)
        test_db.commit()

        fetched = test_db.query(GamificationState).first()
        assert fetched.phase == 1
        assert fetched.total_sessions == 0
        assert fetched.avg_accuracy_30d == 0.0
