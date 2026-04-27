"""FSRS study routes: reviews, due cards, mastery, progress."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import (
    DueCardResponse,
    MasteryResponse,
    ProgressResponse,
    ReviewRequest,
    ReviewResponse,
    ScheduleResponse,
)
from study_guide.database.operations import DatabaseOperations
from study_guide.learning.models import CardReview, UserProgress
from study_guide.learning.scheduler import (
    calculate_retrievability,
    check_mastery,
    get_due_cards,
    schedule_card,
)

router = APIRouter()


@router.post("/{study_set_id}/review", response_model=ReviewResponse)
def record_review(
    study_set_id: int,
    body: ReviewRequest,
    db: Session = Depends(get_db),
):
    """Record a card review and return FSRS scheduling result."""
    # Verify study set exists
    ops = DatabaseOperations(db)
    study_set = ops.get_study_set(study_set_id)
    if study_set is None:
        raise HTTPException(status_code=404, detail=f"Study set {study_set_id} not found")

    now = datetime.utcnow()

    # Build history for this card
    history = (
        db.query(CardReview)
        .filter(
            CardReview.study_set_id == study_set_id,
            CardReview.card_id == body.card_index,
        )
        .order_by(CardReview.id)
        .all()
    )

    result = schedule_card(history if history else None, body.rating, now)

    elapsed = 0.0
    if history:
        elapsed = (now - history[-1].reviewed_at).total_seconds() / 86400.0
        elapsed = max(elapsed, 0.0)

    review = CardReview(
        card_id=body.card_index,
        study_set_id=study_set_id,
        rating=body.rating,
        elapsed_days=elapsed,
        scheduled_days=result["scheduled_days"],
        stability=result["stability"],
        difficulty=result["difficulty"],
        retrievability=result["retrievability"],
        state=result["state"],
        reviewed_at=now,
        confidence_rating=body.confidence if body.confidence > 0 else None,
    )
    db.add(review)
    db.commit()

    return ReviewResponse(
        stability=result["stability"],
        difficulty=result["difficulty"],
        retrievability=result["retrievability"],
        state=result["state"],
        scheduled_days=result["scheduled_days"],
        next_review=result["next_review"],
    )


@router.get("/{study_set_id}/due", response_model=list[DueCardResponse])
def get_due(study_set_id: int, db: Session = Depends(get_db)):
    """Get cards due for review, sorted by lowest retrievability."""
    ops = DatabaseOperations(db)
    study_set = ops.get_study_set(study_set_id)
    if study_set is None:
        raise HTTPException(status_code=404, detail=f"Study set {study_set_id} not found")

    due = get_due_cards(db, study_set_id)
    return [
        DueCardResponse(
            card_id=c["card_id"],
            retrievability=c["retrievability"],
            state=c["state"],
            last_review=c["last_review"],
        )
        for c in due
    ]


@router.get("/{study_set_id}/schedule", response_model=ScheduleResponse)
def get_schedule(study_set_id: int, db: Session = Depends(get_db)):
    """Full schedule with retrievability for all reviewed cards."""
    ops = DatabaseOperations(db)
    study_set = ops.get_study_set(study_set_id)
    if study_set is None:
        raise HTTPException(status_code=404, detail=f"Study set {study_set_id} not found")

    now = datetime.utcnow()

    latest_sub = (
        db.query(
            CardReview.card_id,
            sa_func.max(CardReview.id).label("max_id"),
        )
        .filter(CardReview.study_set_id == study_set_id)
        .group_by(CardReview.card_id)
        .subquery()
    )
    latest_reviews = (
        db.query(CardReview)
        .join(
            latest_sub,
            and_(
                CardReview.card_id == latest_sub.c.card_id,
                CardReview.id == latest_sub.c.max_id,
            ),
        )
        .all()
    )

    all_cards = []
    for rev in latest_reviews:
        elapsed = max((now - rev.reviewed_at).total_seconds() / 86400.0, 0.0)
        r = calculate_retrievability(elapsed, rev.stability)
        all_cards.append({
            "card_id": rev.card_id,
            "retrievability": round(r, 4),
            "stability": round(rev.stability, 2),
            "difficulty": round(rev.difficulty, 2),
            "state": rev.state,
            "last_review": rev.reviewed_at.isoformat(),
            "scheduled_days": rev.scheduled_days,
        })

    all_cards.sort(key=lambda c: c["retrievability"])

    due = get_due_cards(db, study_set_id)
    return {
        "study_set_id": study_set_id,
        "due_count": len(due),
        "total_reviewed": len(all_cards),
        "cards": all_cards,
    }


@router.post("/mastery/{topic}", response_model=MasteryResponse)
def check_topic_mastery(topic: str, db: Session = Depends(get_db)):
    """Check mastery status for a topic."""
    result = check_mastery(db, topic)
    return MasteryResponse(mastered=result["mastered"], details=result["details"])


@router.get("/progress", response_model=list[ProgressResponse])
def get_all_progress(db: Session = Depends(get_db)):
    """Get progress entries for all topics."""
    all_progress = db.query(UserProgress).all()
    return [
        ProgressResponse(
            topic=p.topic_tag,
            mastery_level=p.mastery_level,
            bloom_highest_level=p.bloom_highest_level,
            total_reviews=p.total_reviews,
        )
        for p in all_progress
    ]
