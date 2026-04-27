"""FSRS study routes: reviews, due cards, mastery, progress."""

import json
from datetime import datetime
from typing import TypedDict

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
    StudySessionCompleteRequest,
    StudySessionCompleteResponse,
)
from study_guide.database.operations import DatabaseOperations
from study_guide.learning.models import CardReview, StudySession, UserProgress
from study_guide.learning.scheduler import (
    calculate_retrievability,
    check_mastery,
    get_due_cards,
    schedule_card,
)

router = APIRouter()


class ScheduleCardData(TypedDict):
    card_id: int
    retrievability: float
    stability: float
    difficulty: float
    state: str
    last_review: str
    scheduled_days: float


def _get_study_items(content: dict | list) -> list[object]:
    """Normalize stored study-set content into a list of item objects."""
    if isinstance(content, list):
        return list(content)
    cards = content.get("cards")
    if isinstance(cards, list):
        return list(cards)
    questions = content.get("questions")
    if isinstance(questions, list):
        return list(questions)
    return []


def _derive_progress_topics(
    study_set_content: dict | list,
    card_index: int,
    fallback_topic: str,
) -> tuple[list[str], int]:
    """Return topic tags and bloom level for a reviewed card."""
    items = _get_study_items(study_set_content)
    if 0 <= card_index < len(items):
        item = items[card_index]
        if isinstance(item, dict):
            tags = item.get("tags")
            topic = item.get("topic")
            bloom_level = item.get("bloom_level")

            topics: list[str] = []
            if isinstance(tags, list):
                topics.extend(
                    str(tag).strip()
                    for tag in tags
                    if isinstance(tag, str) and tag.strip()
                )
            if isinstance(topic, str) and topic.strip():
                topics.append(topic.strip())

            normalized_topics = list(dict.fromkeys(topics))
            normalized_bloom = bloom_level if isinstance(bloom_level, int) else 1
            if normalized_topics:
                return normalized_topics, normalized_bloom

    return [fallback_topic], 1


def _update_user_progress(
    db: Session,
    document_id: int | None,
    topics: list[str],
    bloom_level: int,
    rating: int,
    confidence: int,
    now: datetime,
) -> None:
    """Upsert UserProgress rows for the reviewed topics."""
    mastery_sample = rating / 4.0
    calibration_sample = 0.0
    if confidence > 0:
        confidence_normalized = confidence / 5.0
        calibration_sample = max(0.0, 1.0 - abs(confidence_normalized - mastery_sample))

    for topic in topics:
        progress = (
            db.query(UserProgress)
            .filter(
                UserProgress.topic_tag == topic,
                UserProgress.document_id == document_id,
            )
            .first()
        )

        if progress is None:
            progress = UserProgress(
                document_id=document_id,
                topic_tag=topic,
                mastery_level=mastery_sample,
                bloom_highest_level=bloom_level,
                total_reviews=1,
                last_reviewed_at=now,
                calibration_score=calibration_sample,
            )
            db.add(progress)
            continue

        previous_reviews = progress.total_reviews
        progress.total_reviews += 1
        progress.last_reviewed_at = now
        progress.bloom_highest_level = max(progress.bloom_highest_level, bloom_level)
        progress.mastery_level = (
            (progress.mastery_level * previous_reviews) + mastery_sample
        ) / progress.total_reviews

        if confidence > 0:
            progress.calibration_score = (
                (progress.calibration_score * previous_reviews) + calibration_sample
            ) / progress.total_reviews


def _rebuild_progress_from_reviews(db: Session) -> None:
    """Reconstruct progress rows from historical review data."""
    ops = DatabaseOperations(db)
    study_set_cache: dict[int, tuple[int | None, str, dict | list]] = {}

    study_sets = ops.get_all_study_sets()
    for study_set in study_sets:
        study_set_cache[study_set.id] = (
            study_set.document_id,
            study_set.title or "Untitled",
            ops.get_study_set_content(study_set.id) or [],
        )

    reviews = db.query(CardReview).order_by(CardReview.id).all()
    for review in reviews:
        cached = study_set_cache.get(review.study_set_id)
        if cached is None:
            continue

        document_id, title, study_set_content = cached
        fallback_topic = title.replace("Flashcards - ", "").strip() or "Untitled"
        topics, bloom_level = _derive_progress_topics(
            study_set_content,
            review.card_id,
            fallback_topic,
        )
        _update_user_progress(
            db,
            document_id,
            topics,
            bloom_level,
            review.rating,
            review.confidence_rating or 0,
            review.reviewed_at,
        )

    db.commit()


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
    study_set_content = ops.get_study_set_content(study_set_id) or []
    fallback_topic = (study_set.title or "Untitled").replace("Flashcards - ", "").strip() or "Untitled"
    topics, bloom_level = _derive_progress_topics(
        study_set_content,
        body.card_index,
        fallback_topic,
    )

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
    _update_user_progress(
        db,
        study_set.document_id,
        topics,
        bloom_level,
        body.rating,
        body.confidence,
        now,
    )
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

    all_cards: list[ScheduleCardData] = []
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


@router.post("/{study_set_id}/session", response_model=StudySessionCompleteResponse)
def complete_study_session(
    study_set_id: int,
    body: StudySessionCompleteRequest,
    db: Session = Depends(get_db),
):
    """Persist a completed flashcard study session for progress analytics."""
    ops = DatabaseOperations(db)
    study_set = ops.get_study_set(study_set_id)
    if study_set is None:
        raise HTTPException(status_code=404, detail=f"Study set {study_set_id} not found")

    total_items = body.total_items
    correct_count = min(body.correct_count, total_items)
    accuracy = correct_count / total_items if total_items > 0 else 0.0
    session_number = (
        db.query(sa_func.count(StudySession.id))
        .filter(StudySession.study_set_id == study_set_id)
        .scalar()
        or 0
    ) + 1

    study_session = StudySession(
        study_set_id=study_set_id,
        session_type="flashcards",
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
        total_items=total_items,
        correct_count=correct_count,
        confidence_sum=body.confidence_sum,
        accuracy=accuracy,
        bloom_level_distribution=json.dumps(body.bloom_level_distribution),
        session_number=session_number,
    )
    db.add(study_session)
    db.commit()
    db.refresh(study_session)

    return StudySessionCompleteResponse(
        session_id=study_session.id,
        total_items=study_session.total_items,
        correct_count=study_session.correct_count,
        accuracy=study_session.accuracy,
    )


@router.post("/mastery/{topic}", response_model=MasteryResponse)
def check_topic_mastery(topic: str, db: Session = Depends(get_db)):
    """Check mastery status for a topic."""
    result = check_mastery(db, topic)
    return MasteryResponse(mastered=result["mastered"], details=result["details"])


@router.get("/progress", response_model=list[ProgressResponse])
def get_all_progress(db: Session = Depends(get_db)):
    """Get progress entries for all topics."""
    all_progress = db.query(UserProgress).all()
    if not all_progress and db.query(CardReview.id).first() is not None:
        _rebuild_progress_from_reviews(db)
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
