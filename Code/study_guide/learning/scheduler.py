"""
FSRS v5 spaced repetition scheduler.

Implements the Free Spaced Repetition Scheduler algorithm for computing
optimal review intervals based on a power-law forgetting curve.

Reference: https://github.com/open-spaced-repetition/fsrs4anki
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta

from sqlalchemy import and_
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from study_guide.learning.models import CardReview, UserProgress

# FSRS v5 default weights from the paper
FSRS_DEFAULTS: dict = {
    "w": [
        0.4072, 1.1829, 3.1262, 15.4722,  # w0-w3: initial stability
        7.2102, 0.5316,                      # w4-w5: initial difficulty
        1.0651, 0.0589,                      # w6-w7: difficulty update
        1.5330, 0.1647, 1.0621,              # w8-w10: success stability
        1.8364, 0.0613, 0.3399, 2.7316,      # w11-w14: fail stability
        0.1542, 2.8555, 0.0536, 0.3931,      # w15-w18: (reserved)
    ],
    "desired_retention": 0.9,
    "maximum_interval": 36500,
}


def calculate_retrievability(elapsed_days: float, stability: float) -> float:
    """Power forgetting curve: R = (1 + elapsed_days / (9 * s))^(-1).

    Returns 1.0 when elapsed_days is 0, decaying toward 0 over time.
    """
    if stability <= 0:
        return 0.0
    return (1.0 + elapsed_days / (9.0 * stability)) ** -1


def calculate_initial_stability(rating: int, w: list[float]) -> float:
    """Initial stability for a new card based on the first rating.

    Uses w[0]-w[3], indexed by rating-1.
    """
    return max(w[rating - 1], 0.01)


def calculate_initial_difficulty(rating: int, w: list[float]) -> float:
    """Initial difficulty for a new card.

    Formula: w[4] - exp(w[5] * (rating - 1)) + 1, clamped to [1, 10].
    """
    d = w[4] - math.exp(w[5] * (rating - 1)) + 1
    return min(max(d, 1.0), 10.0)


def calculate_next_difficulty(
    d: float, rating: int, w: list[float]
) -> float:
    """Update difficulty after a review using mean-reversion formula.

    d' = w[7] * d_initial(3, w) + (1 - w[7]) * (d - w[6] * (rating - 3))
    Clamped to [1, 10].
    """
    d_initial_3 = calculate_initial_difficulty(3, w)
    new_d = w[7] * d_initial_3 + (1 - w[7]) * (d - w[6] * (rating - 3))
    return min(max(new_d, 1.0), 10.0)


def calculate_next_stability(
    d: float, s: float, r: float, rating: int, w: list[float]
) -> float:
    """Calculate new stability after a review.

    For successful reviews (rating >= 2):
        s' = s * (exp(w[8]) * (11 - d) * s^(-w[9])
             * (exp(w[10] * (1 - r)) - 1) + 1)

    For failed reviews (rating == 1):
        s' = w[11] * d^(-w[12]) * ((s + 1)^w[13] - 1) * exp(w[14] * (1 - r))
    """
    if rating == 1:
        # Lapse / failure
        new_s = (
            w[11]
            * d ** (-w[12])
            * ((s + 1) ** w[13] - 1)
            * math.exp(w[14] * (1 - r))
        )
    else:
        # Successful recall
        new_s = s * (
            math.exp(w[8])
            * (11 - d)
            * s ** (-w[9])
            * (math.exp(w[10] * (1 - r)) - 1)
            + 1
        )
    return max(new_s, 0.01)


def calculate_next_interval(
    stability: float, desired_retention: float, max_interval: int
) -> int:
    """Compute the next review interval in days.

    interval = round(9 * s * (1/desired_retention - 1))
    Clamped to [1, max_interval].
    """
    interval = round(9.0 * stability * (1.0 / desired_retention - 1.0))
    return min(max(interval, 1), max_interval)


def _determine_state(
    history: list[CardReview] | None, rating: int
) -> str:
    """Determine the card state after this review."""
    if not history:
        if rating == 1:
            return "learning"
        return "review"

    prev_state = history[-1].state
    if rating == 1:
        if prev_state in ("review", "relearning"):
            return "relearning"
        return "learning"
    return "review"


def schedule_card(
    history: list[CardReview] | None,
    rating: int,
    now: datetime | None = None,
) -> dict:
    """Main scheduling entry point.

    Takes the card's review history and a new rating (1-4), returns
    the updated FSRS parameters and the next review date.

    Returns:
        {
            "stability": float,
            "difficulty": float,
            "retrievability": float,
            "state": str,
            "scheduled_days": float,
            "next_review": datetime,
        }
    """
    if rating < 1 or rating > 4:
        raise ValueError(f"rating must be 1-4, got {rating}")

    if now is None:
        now = datetime.utcnow()

    w = FSRS_DEFAULTS["w"]
    desired_retention = FSRS_DEFAULTS["desired_retention"]
    max_interval = FSRS_DEFAULTS["maximum_interval"]

    if not history:
        # Brand-new card — first review
        s = calculate_initial_stability(rating, w)
        d = calculate_initial_difficulty(rating, w)
        r = 1.0  # Just seen, retrievability is perfect
    else:
        last = history[-1]
        elapsed = (now - last.reviewed_at).total_seconds() / 86400.0
        elapsed = max(elapsed, 0.0)

        s_prev = last.stability
        d_prev = last.difficulty

        r = calculate_retrievability(elapsed, s_prev)
        d = calculate_next_difficulty(d_prev, rating, w)
        s = calculate_next_stability(d_prev, s_prev, r, rating, w)

    state = _determine_state(history, rating)
    interval = calculate_next_interval(s, desired_retention, max_interval)
    next_review = now + timedelta(days=interval)

    return {
        "stability": s,
        "difficulty": d,
        "retrievability": r,
        "state": state,
        "scheduled_days": float(interval),
        "next_review": next_review,
    }


def get_due_cards(
    session: Session,
    study_set_id: int,
    now: datetime | None = None,
) -> list[dict]:
    """Query due cards for a study set, sorted by lowest retrievability.

    For each card_id in the given study_set_id, finds the most recent
    CardReview and computes current retrievability. Returns cards where
    retrievability < desired_retention, most urgent first.
    """
    if now is None:
        now = datetime.utcnow()

    desired_retention = FSRS_DEFAULTS["desired_retention"]

    # Subquery: latest review id per (card_id, study_set_id)
    latest_sub = (
        session.query(
            CardReview.card_id,
            CardReview.study_set_id,
            sa_func.max(CardReview.id).label("max_id"),
        )
        .filter(CardReview.study_set_id == study_set_id)
        .group_by(CardReview.card_id, CardReview.study_set_id)
        .subquery()
    )

    latest_reviews = (
        session.query(CardReview)
        .join(
            latest_sub,
            and_(
                CardReview.card_id == latest_sub.c.card_id,
                CardReview.study_set_id
                == latest_sub.c.study_set_id,
                CardReview.id == latest_sub.c.max_id,
            ),
        )
        .all()
    )

    due: list[dict] = []
    for review in latest_reviews:
        elapsed = (now - review.reviewed_at).total_seconds() / 86400.0
        elapsed = max(elapsed, 0.0)
        r = calculate_retrievability(elapsed, review.stability)

        if r < desired_retention:
            due.append({
                "card_id": review.card_id,
                "retrievability": r,
                "state": review.state,
                "last_review": review.reviewed_at,
            })

    due.sort(key=lambda c: c["retrievability"])
    return due


def check_mastery(session: Session, topic_tag: str) -> dict:
    """Check whether a topic meets mastery criteria.

    Criteria (all must be met):
        1. All cards: current retrievability > 0.90
        2. All cards: most recent scheduled interval > 30 days
        3. Average accuracy over last 3 reviews per card > 0.85
        4. UserProgress.bloom_highest_level >= 3 (Apply)

    Returns:
        {"mastered": bool, "details": {... stats ...}}
    """
    now = datetime.utcnow()

    # Look up user progress for this topic
    progress = (
        session.query(UserProgress)
        .filter(UserProgress.topic_tag == topic_tag)
        .first()
    )

    bloom_ok = progress is not None and progress.bloom_highest_level >= 3

    # Get all study_set_ids linked to reviews for this topic.
    # We use a convention: reviews are tied to study_sets, and the topic
    # is tracked on UserProgress which may link to a document_id.
    # For check_mastery we examine all card reviews across all study sets
    # that share the same document_id as the progress record.
    if progress is None or progress.document_id is None:
        return {
            "mastered": False,
            "details": {
                "bloom_ok": False,
                "bloom_level": 0,
                "all_retrievable": False,
                "all_long_interval": False,
                "avg_accuracy_ok": False,
                "reason": "no progress record or document",
            },
        }

    from study_guide.database.models import StudySet

    study_set_ids = [
        sid
        for (sid,) in session.query(StudySet.id)
        .filter(StudySet.document_id == progress.document_id)
        .all()
    ]

    if not study_set_ids:
        return {
            "mastered": False,
            "details": {
                "bloom_ok": bloom_ok,
                "bloom_level": progress.bloom_highest_level,
                "all_retrievable": False,
                "all_long_interval": False,
                "avg_accuracy_ok": False,
                "reason": "no study sets found",
            },
        }

    # Get latest review per card across all relevant study sets
    latest_sub = (
        session.query(
            CardReview.card_id,
            CardReview.study_set_id,
            sa_func.max(CardReview.id).label("max_id"),
        )
        .filter(CardReview.study_set_id.in_(study_set_ids))
        .group_by(CardReview.card_id, CardReview.study_set_id)
        .subquery()
    )

    latest_reviews = (
        session.query(CardReview)
        .join(
            latest_sub,
            and_(
                CardReview.card_id == latest_sub.c.card_id,
                CardReview.study_set_id == latest_sub.c.study_set_id,
                CardReview.id == latest_sub.c.max_id,
            ),
        )
        .all()
    )

    if not latest_reviews:
        return {
            "mastered": False,
            "details": {
                "bloom_ok": bloom_ok,
                "bloom_level": progress.bloom_highest_level,
                "all_retrievable": False,
                "all_long_interval": False,
                "avg_accuracy_ok": False,
                "reason": "no reviews found",
            },
        }

    # Criterion 1: all cards retrievability > 0.90
    all_retrievable = True
    min_retrievability = 1.0
    for review in latest_reviews:
        elapsed = (now - review.reviewed_at).total_seconds() / 86400.0
        r = calculate_retrievability(max(elapsed, 0.0), review.stability)
        min_retrievability = min(min_retrievability, r)
        if r <= 0.90:
            all_retrievable = False

    # Criterion 2: all cards interval > 30 days
    all_long_interval = all(
        review.scheduled_days > 30 for review in latest_reviews
    )

    # Criterion 3: average accuracy over last 3 reviews per card > 0.85
    # "Accuracy" for a single review: rating >= 2 counts as correct
    card_keys = {
        (r.card_id, r.study_set_id) for r in latest_reviews
    }
    correct_total = 0
    review_total = 0

    for card_id, set_id in card_keys:
        last_3 = (
            session.query(CardReview)
            .filter(
                CardReview.card_id == card_id,
                CardReview.study_set_id == set_id,
            )
            .order_by(CardReview.id.desc())
            .limit(3)
            .all()
        )
        for rev in last_3:
            review_total += 1
            if rev.rating >= 2:
                correct_total += 1

    avg_accuracy = correct_total / review_total if review_total > 0 else 0.0
    avg_accuracy_ok = avg_accuracy > 0.85

    mastered = (
        bloom_ok and all_retrievable and all_long_interval and avg_accuracy_ok
    )

    return {
        "mastered": mastered,
        "details": {
            "bloom_ok": bloom_ok,
            "bloom_level": progress.bloom_highest_level,
            "all_retrievable": all_retrievable,
            "min_retrievability": min_retrievability,
            "all_long_interval": all_long_interval,
            "avg_accuracy": avg_accuracy,
            "avg_accuracy_ok": avg_accuracy_ok,
            "total_cards": len(latest_reviews),
        },
    }
