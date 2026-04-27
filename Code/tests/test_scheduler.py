"""
Tests for the FSRS v5 spaced repetition scheduler.
"""

from datetime import datetime, timedelta

import pytest

from study_guide.database.models import StudySet
from study_guide.learning.models import CardReview, UserProgress
from study_guide.learning.scheduler import (
    FSRS_DEFAULTS,
    calculate_initial_difficulty,
    calculate_initial_stability,
    calculate_next_interval,
    calculate_retrievability,
    check_mastery,
    get_due_cards,
    schedule_card,
)

# ---------------------------------------------------------------------------
# Retrievability
# ---------------------------------------------------------------------------

class TestRetrievability:

    def test_retrievability_at_zero_days(self):
        """Retrievability should be ~1.0 immediately after review."""
        r = calculate_retrievability(0.0, 5.0)
        assert r == pytest.approx(1.0, abs=1e-9)

    def test_retrievability_decreases_over_time(self):
        """Retrievability should decline as elapsed days grow."""
        s = 5.0
        r1 = calculate_retrievability(1.0, s)
        r5 = calculate_retrievability(5.0, s)
        r30 = calculate_retrievability(30.0, s)

        assert r1 > r5 > r30
        assert r1 < 1.0
        assert r30 > 0.0

    def test_retrievability_zero_stability(self):
        """Zero stability should yield 0.0 retrievability."""
        assert calculate_retrievability(1.0, 0.0) == 0.0


# ---------------------------------------------------------------------------
# Initial stability & difficulty
# ---------------------------------------------------------------------------

class TestInitialParameters:

    def test_initial_stability_varies_by_rating(self):
        """Easy should give higher initial stability than Again."""
        w = FSRS_DEFAULTS["w"]
        s_again = calculate_initial_stability(1, w)
        s_hard = calculate_initial_stability(2, w)
        s_good = calculate_initial_stability(3, w)
        s_easy = calculate_initial_stability(4, w)

        assert s_easy > s_good > s_hard > s_again
        assert s_again > 0

    def test_initial_difficulty_varies_by_rating(self):
        """Again should be hardest (highest difficulty), Easy easiest."""
        w = FSRS_DEFAULTS["w"]
        d_again = calculate_initial_difficulty(1, w)
        d_hard = calculate_initial_difficulty(2, w)
        d_good = calculate_initial_difficulty(3, w)
        d_easy = calculate_initial_difficulty(4, w)

        assert d_again > d_good > d_easy
        assert d_again >= d_hard
        # All within valid range
        for d in (d_again, d_hard, d_good, d_easy):
            assert 1.0 <= d <= 10.0


# ---------------------------------------------------------------------------
# schedule_card — new cards
# ---------------------------------------------------------------------------

class TestScheduleNewCard:

    def test_schedule_new_card_good(self):
        """First review rated Good should yield a reasonable interval."""
        result = schedule_card(history=None, rating=3)

        assert result["state"] == "review"
        assert result["retrievability"] == 1.0
        assert result["stability"] > 0
        assert result["scheduled_days"] >= 1
        assert result["next_review"] > datetime.utcnow()

    def test_schedule_new_card_again(self):
        """First review rated Again — short interval, learning state."""
        result = schedule_card(history=None, rating=1)

        assert result["state"] == "learning"
        assert result["scheduled_days"] >= 1
        # Again stability is very low → short interval
        good_result = schedule_card(history=None, rating=3)
        assert result["scheduled_days"] <= good_result["scheduled_days"]

    def test_schedule_new_card_easy(self):
        """First review rated Easy — longest interval."""
        result = schedule_card(history=None, rating=4)

        assert result["state"] == "review"
        assert result["stability"] > 10  # w[3] = 15.47


# ---------------------------------------------------------------------------
# schedule_card — review cards (with history)
# ---------------------------------------------------------------------------

class TestScheduleReviewCard:

    def _make_review(
        self, card_id, set_id, rating, stability, difficulty,
        reviewed_at, scheduled_days=1.0, state="review",
    ):
        """Helper to build a CardReview without DB persistence."""
        return CardReview(
            card_id=card_id,
            study_set_id=set_id,
            rating=rating,
            stability=stability,
            difficulty=difficulty,
            retrievability=1.0,
            elapsed_days=0.0,
            scheduled_days=scheduled_days,
            state=state,
            reviewed_at=reviewed_at,
        )

    def test_schedule_review_card_good(self):
        """Card with prior history, rated Good — interval should increase."""
        past = datetime.utcnow() - timedelta(days=3)
        history = [
            self._make_review(0, 1, 3, 3.12, 5.5, past, scheduled_days=3.0),
        ]
        result = schedule_card(history=history, rating=3)

        assert result["state"] == "review"
        assert result["stability"] > 3.12  # stability should grow
        assert result["scheduled_days"] >= 1

    def test_schedule_lapse(self):
        """Card with history, rated Again — stability drops."""
        past = datetime.utcnow() - timedelta(days=10)
        history = [
            self._make_review(
                0, 1, 3, 10.0, 5.0, past, scheduled_days=10.0
            ),
        ]
        result = schedule_card(history=history, rating=1)

        assert result["state"] == "relearning"
        assert result["stability"] < 10.0  # stability decreased


# ---------------------------------------------------------------------------
# Interval clamping
# ---------------------------------------------------------------------------

class TestIntervalClamping:

    def test_interval_never_below_one(self):
        """Minimum interval is 1 day."""
        interval = calculate_next_interval(0.001, 0.9, 36500)
        assert interval >= 1

    def test_interval_never_exceeds_max(self):
        """Maximum interval is max_interval."""
        interval = calculate_next_interval(999999.0, 0.9, 36500)
        assert interval <= 36500

    def test_interval_custom_max(self):
        """Custom max_interval is respected."""
        interval = calculate_next_interval(999999.0, 0.9, 180)
        assert interval <= 180


# ---------------------------------------------------------------------------
# get_due_cards
# ---------------------------------------------------------------------------

class TestGetDueCards:

    def test_due_cards_sorted_by_retrievability(self, test_db):
        """Due cards should be sorted lowest retrievability first."""
        # Create a study set
        ss = StudySet(
            set_type="flashcards",
            content_json='{"cards":[]}',
            item_count=3,
        )
        test_db.add(ss)
        test_db.commit()

        now = datetime.utcnow()

        # Card 0: reviewed long ago, low stability → lowest R
        r0 = CardReview(
            card_id=0, study_set_id=ss.id, rating=3,
            stability=1.0, difficulty=5.0, retrievability=0.9,
            scheduled_days=1.0, state="review",
            reviewed_at=now - timedelta(days=30),
        )
        # Card 1: reviewed somewhat recently, moderate stability
        r1 = CardReview(
            card_id=1, study_set_id=ss.id, rating=3,
            stability=5.0, difficulty=5.0, retrievability=0.9,
            scheduled_days=5.0, state="review",
            reviewed_at=now - timedelta(days=10),
        )
        # Card 2: reviewed recently, high stability → highest R
        r2 = CardReview(
            card_id=2, study_set_id=ss.id, rating=4,
            stability=20.0, difficulty=3.0, retrievability=0.95,
            scheduled_days=20.0, state="review",
            reviewed_at=now - timedelta(days=5),
        )
        test_db.add_all([r0, r1, r2])
        test_db.commit()

        due = get_due_cards(test_db, ss.id, now=now)

        # All three should be due (their R < 0.9 after elapsed time)
        # At minimum, card 0 with stability=1 and 30 days elapsed is very due
        assert len(due) >= 1
        # First card should have lowest retrievability
        if len(due) > 1:
            assert due[0]["retrievability"] <= due[1]["retrievability"]

    def test_due_cards_excludes_high_retrievability(self, test_db):
        """Cards with retrievability >= desired_retention are not due."""
        ss = StudySet(
            set_type="flashcards",
            content_json='{"cards":[]}',
            item_count=1,
        )
        test_db.add(ss)
        test_db.commit()

        now = datetime.utcnow()
        # Card just reviewed — R should be ~1.0
        r = CardReview(
            card_id=0, study_set_id=ss.id, rating=4,
            stability=100.0, difficulty=3.0, retrievability=1.0,
            scheduled_days=10.0, state="review",
            reviewed_at=now,
        )
        test_db.add(r)
        test_db.commit()

        due = get_due_cards(test_db, ss.id, now=now)
        assert len(due) == 0


# ---------------------------------------------------------------------------
# check_mastery
# ---------------------------------------------------------------------------

class TestCheckMastery:

    def _setup_mastery_scenario(
        self, test_db, bloom_level, stability, scheduled_days,
        ratings, days_ago=0,
    ):
        """Helper: create progress, study set, and reviews for a topic."""
        from study_guide.database.models import Document, Source

        source = Source(
            filename="t.txt", filepath="/t.txt", file_type="txt",
        )
        test_db.add(source)
        test_db.commit()

        doc = Document(
            source_id=source.id, raw_text="content", word_count=1,
        )
        test_db.add(doc)
        test_db.commit()

        ss = StudySet(
            document_id=doc.id,
            set_type="flashcards",
            content_json='{"cards":[]}',
            item_count=1,
        )
        test_db.add(ss)
        test_db.commit()

        progress = UserProgress(
            document_id=doc.id,
            topic_tag="test-topic",
            bloom_highest_level=bloom_level,
            mastery_level=0.9,
            total_reviews=len(ratings),
        )
        test_db.add(progress)
        test_db.commit()

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
            test_db.add(review)
        test_db.commit()

        return progress

    def test_mastery_check_not_mastered(self, test_db):
        """Low bloom level prevents mastery."""
        self._setup_mastery_scenario(
            test_db,
            bloom_level=2,  # below 3
            stability=50.0,
            scheduled_days=60.0,
            ratings=[3, 3, 4],
        )
        result = check_mastery(test_db, "test-topic")
        assert result["mastered"] is False
        assert result["details"]["bloom_ok"] is False

    def test_mastery_check_not_mastered_low_interval(self, test_db):
        """Short intervals prevent mastery even with high bloom."""
        self._setup_mastery_scenario(
            test_db,
            bloom_level=4,
            stability=50.0,
            scheduled_days=10.0,  # below 30
            ratings=[3, 3, 4],
        )
        result = check_mastery(test_db, "test-topic")
        assert result["mastered"] is False
        assert result["details"]["all_long_interval"] is False

    def test_mastery_check_not_mastered_low_accuracy(self, test_db):
        """Low accuracy on recent reviews prevents mastery."""
        self._setup_mastery_scenario(
            test_db,
            bloom_level=4,
            stability=50.0,
            scheduled_days=60.0,
            ratings=[1, 1, 1],  # all Again → 0% accuracy
        )
        result = check_mastery(test_db, "test-topic")
        assert result["mastered"] is False
        assert result["details"]["avg_accuracy_ok"] is False

    def test_mastery_check_mastered(self, test_db):
        """Topic meeting all criteria is mastered."""
        self._setup_mastery_scenario(
            test_db,
            bloom_level=4,
            stability=100.0,
            scheduled_days=60.0,
            ratings=[3, 4, 3],  # all successful → 100% accuracy
            days_ago=0,  # recent reviews → high retrievability
        )
        result = check_mastery(test_db, "test-topic")
        assert result["mastered"] is True
        assert result["details"]["bloom_ok"] is True
        assert result["details"]["all_retrievable"] is True
        assert result["details"]["all_long_interval"] is True
        assert result["details"]["avg_accuracy_ok"] is True

    def test_mastery_check_no_progress(self, test_db):
        """Topic with no progress record is not mastered."""
        result = check_mastery(test_db, "nonexistent-topic")
        assert result["mastered"] is False
