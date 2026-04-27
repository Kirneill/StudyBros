"""
Gamification engine — phase detection, achievements, streaks, and analytics.

Implements a three-phase motivational scaffolding system grounded in
Self-Determination Theory (SDT):
  Phase 1: Habit Formation (full gamification)
  Phase 2: Growing Competence (reduced gamification, mastery primary)
  Phase 3: Intrinsic Motivation (minimal gamification)
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from sqlalchemy import func as sa_func
from sqlalchemy.orm import Session

from study_guide.learning.models import (
    Achievement,
    CardReview,
    GamificationState,
    StudySession,
    UserProgress,
)
from study_guide.learning.scheduler import check_mastery

PHASE_NAMES = {
    1: "Habit Formation",
    2: "Growing Competence",
    3: "Intrinsic Motivation",
}

PHASE_MESSAGES = {
    1: "Building your study habit. Consistency is key right now.",
    2: "Your habit is solid. Focus on deepening your understanding.",
    3: "You're self-motivated. The interface is streamlined for mastery.",
}

BLOOM_LABELS = {
    1: "remember",
    2: "understand",
    3: "apply",
    4: "analyze",
    5: "evaluate",
    6: "create",
}

# Achievement definitions: (type, title, description)
ACHIEVEMENT_DEFS = {
    "first_session": (
        "First Steps",
        "Completed your first study session",
    ),
    "consistency_7": (
        "Weekly Warrior",
        "Studied 5 of the last 7 days",
    ),
    "consistency_30": (
        "Monthly Dedication",
        "Studied 20 of the last 30 days",
    ),
    "accuracy_streak": (
        "Sharp Mind",
        "85%+ accuracy for 3 consecutive sessions",
    ),
    "bloom_apply": (
        "Applied Knowledge",
        "Demonstrated Bloom Level 3 (Apply) on a topic",
    ),
    "bloom_analyze": (
        "Deep Thinker",
        "Demonstrated Bloom Level 4 (Analyze) on a topic",
    ),
    "topic_mastery": (
        "Topic Mastered",
        "Fully mastered a topic with all criteria met",
    ),
    "deep_mastery": (
        "Deep Mastery",
        "Topic with 95%+ accuracy and Bloom Level 4+",
    ),
}


def detect_phase(session: Session) -> dict:
    """Detect which gamification phase the user is in.

    Phase 1: total_sessions < 20 OR consistency < 50%
    Phase 2: total_sessions >= 20 AND avg_accuracy > 70% AND no strong
             intrinsic signals
    Phase 3: total_sessions >= 40 AND strong intrinsic signals
    """
    total_sessions = session.query(sa_func.count(StudySession.id)).scalar() or 0

    # Average accuracy over last 30 days
    cutoff_30d = datetime.utcnow() - timedelta(days=30)
    avg_accuracy_30d = (
        session.query(sa_func.avg(StudySession.accuracy))
        .filter(StudySession.started_at >= cutoff_30d)
        .scalar()
    ) or 0.0

    # Intrinsic signals from existing state (if any)
    state = session.query(GamificationState).first()
    if state and state.intrinsic_signals:
        intrinsic = json.loads(state.intrinsic_signals)
    else:
        intrinsic = {
            "beyond_goal": 0,
            "voluntary_hard": 0,
            "ahead_schedule": 0,
        }

    # Phase determination
    strong_intrinsic = (
        intrinsic.get("beyond_goal", 0) >= 5
        and intrinsic.get("voluntary_hard", 0) >= 3
        and intrinsic.get("ahead_schedule", 0) >= 3
    )

    if total_sessions >= 40 and strong_intrinsic:
        phase = 3
    elif total_sessions >= 20 and avg_accuracy_30d > 0.70 and not strong_intrinsic:
        phase = 2
    else:
        phase = 1

    # Persist state
    if state is None:
        state = GamificationState(
            phase=phase,
            total_sessions=total_sessions,
            avg_accuracy_30d=avg_accuracy_30d,
            intrinsic_signals=json.dumps(intrinsic),
        )
        session.add(state)
    else:
        state.phase = phase
        state.total_sessions = total_sessions
        state.avg_accuracy_30d = avg_accuracy_30d
        state.intrinsic_signals = json.dumps(intrinsic)
    session.commit()

    return {
        "phase": phase,
        "phase_name": PHASE_NAMES[phase],
        "total_sessions": total_sessions,
        "avg_accuracy_30d": round(avg_accuracy_30d * 100, 1),
        "intrinsic_signals": intrinsic,
        "message": PHASE_MESSAGES[phase],
    }


def check_topic_completion(session: Session, topic_tag: str) -> dict:
    """Check if a topic is mastered and return celebration data."""
    mastery_result = check_mastery(session, topic_tag)
    details = mastery_result.get("details", {})

    progress = (
        session.query(UserProgress)
        .filter(UserProgress.topic_tag == topic_tag)
        .first()
    )

    if progress is None:
        return {
            "completed": False,
            "topic": topic_tag,
            "stats": {
                "total_concepts": 0,
                "accuracy_pct": 0.0,
                "avg_interval_days": 0.0,
                "bloom_breakdown": {},
            },
            "strengths": [],
            "weaknesses": [],
            "achievement_earned": None,
        }

    # Gather topic sessions for stats
    topic_sessions = (
        session.query(StudySession)
        .filter(StudySession.study_set_id.isnot(None))
        .all()
    )

    total_items = sum(s.total_items for s in topic_sessions)
    total_correct = sum(s.correct_count for s in topic_sessions)
    accuracy_pct = (total_correct / total_items * 100) if total_items > 0 else 0.0

    # Bloom breakdown from progress
    bloom_breakdown = {}
    for level, label in BLOOM_LABELS.items():
        if level <= progress.bloom_highest_level:
            bloom_breakdown[label] = 1
        else:
            bloom_breakdown[label] = 0

    avg_interval = details.get("avg_interval_days", 0.0)
    total_cards = details.get("total_cards", 0)

    # Strengths and weaknesses based on mastery criteria
    strengths = []
    weaknesses = []

    if details.get("bloom_ok"):
        strengths.append(
            f"Strong conceptual depth (Bloom Level {details.get('bloom_level', 0)})"
        )
    else:
        weaknesses.append("Needs deeper conceptual understanding (higher Bloom level)")

    if details.get("all_retrievable"):
        strengths.append("Excellent long-term retention")
    else:
        weaknesses.append("Some concepts need more review for retention")

    if details.get("avg_accuracy_ok"):
        strengths.append(
            f"High accuracy ({details.get('avg_accuracy', 0):.0%})"
        )
    else:
        weaknesses.append("Accuracy needs improvement on recent reviews")

    if details.get("all_long_interval"):
        strengths.append("Knowledge is stable over long intervals")

    # Cap to top 3 strengths, top 2 weaknesses
    strengths = strengths[:3]
    weaknesses = weaknesses[:2]

    # Award topic mastery achievement if completed
    achievement_earned = None
    if mastery_result["mastered"]:
        new_achievements = _try_award(
            session, "topic_mastery", topic_tag,
            bloom_level=progress.bloom_highest_level,
            criteria={"topic": topic_tag, "mastery": True},
        )
        if new_achievements:
            achievement_earned = new_achievements[0]

    return {
        "completed": mastery_result["mastered"],
        "topic": topic_tag,
        "stats": {
            "total_concepts": total_cards,
            "accuracy_pct": round(accuracy_pct, 1),
            "avg_interval_days": round(avg_interval, 1),
            "bloom_breakdown": bloom_breakdown,
        },
        "strengths": strengths,
        "weaknesses": weaknesses,
        "achievement_earned": achievement_earned,
    }


def get_strengths_weaknesses(session: Session) -> dict:
    """Analyze user strengths and weaknesses across all topics."""
    all_progress = session.query(UserProgress).all()

    strengths = []
    weaknesses = []

    for prog in all_progress:
        # Get accuracy from recent sessions for this topic
        topic_sessions = (
            session.query(StudySession)
            .filter(StudySession.study_set_id.isnot(None))
            .order_by(StudySession.started_at.desc())
            .limit(5)
            .all()
        )
        total_items = sum(s.total_items for s in topic_sessions)
        total_correct = sum(s.correct_count for s in topic_sessions)
        accuracy = total_correct / total_items if total_items > 0 else 0.0

        bloom = prog.bloom_highest_level
        entry = {
            "topic": prog.topic_tag,
            "accuracy": round(accuracy * 100, 1),
            "bloom_level": bloom,
        }

        if accuracy >= 0.80 and bloom >= 3:
            entry["message"] = (
                f"Strong mastery of {prog.topic_tag} "
                f"(Bloom L{bloom}, {accuracy:.0%} accuracy)"
            )
            strengths.append(entry)
        elif accuracy < 0.70 or bloom < 2:
            entry["message"] = (
                f"{prog.topic_tag} needs more work "
                f"(Bloom L{bloom}, {accuracy:.0%} accuracy)"
            )
            weaknesses.append(entry)

    # Recommendations
    recommendations = []
    for w in weaknesses[:3]:
        if w["bloom_level"] < 2:
            recommendations.append({
                "action": "Review fundamentals",
                "reason": "Bloom level indicates surface-level understanding",
                "topic": w["topic"],
            })
        elif w["accuracy"] < 70.0:
            recommendations.append({
                "action": "Increase review frequency",
                "reason": "Accuracy below 70% suggests items are slipping",
                "topic": w["topic"],
            })

    # Calibration analysis
    reviews_with_confidence = (
        session.query(CardReview)
        .filter(CardReview.confidence_rating.isnot(None))
        .all()
    )

    avg_confidence = 0.0
    avg_review_accuracy = 0.0
    overconfident = []
    underconfident = []

    if reviews_with_confidence:
        # Confidence is 1-5 scale, normalize to 0-1
        avg_confidence = sum(
            r.confidence_rating for r in reviews_with_confidence
        ) / len(reviews_with_confidence) / 5.0
        avg_review_accuracy = sum(
            1.0 for r in reviews_with_confidence if r.rating >= 2
        ) / len(reviews_with_confidence)

        # Per-topic calibration
        for prog in all_progress:
            topic_reviews = [
                r for r in reviews_with_confidence
                # We can't directly filter by topic from CardReview,
                # so this is a simplified cross-check
            ]
            if not topic_reviews:
                continue
            conf = sum(
                r.confidence_rating for r in topic_reviews
            ) / len(topic_reviews) / 5.0
            acc = sum(
                1.0 for r in topic_reviews if r.rating >= 2
            ) / len(topic_reviews)
            if conf - acc > 0.15:
                overconfident.append(prog.topic_tag)
            elif acc - conf > 0.15:
                underconfident.append(prog.topic_tag)

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "calibration": {
            "avg_confidence": round(avg_confidence * 100, 1),
            "avg_accuracy": round(avg_review_accuracy * 100, 1),
            "overconfident_topics": overconfident,
            "underconfident_topics": underconfident,
        },
    }


def get_achievements_earned(session: Session) -> list[dict]:
    """Get all earned achievements, sorted by most recent."""
    achievements = (
        session.query(Achievement)
        .order_by(Achievement.earned_at.desc())
        .all()
    )
    return [
        {
            "title": a.title,
            "description": a.description,
            "type": a.achievement_type,
            "bloom_level": a.bloom_level_required,
            "topic": a.topic_id,
            "earned_at": a.earned_at.isoformat() if a.earned_at else None,
        }
        for a in achievements
    ]


def check_and_award_achievements(
    session: Session, topic_tag: str
) -> list[dict]:
    """Check if user earned any new achievements after a study session.

    Only awards achievements not already earned.
    """
    newly_awarded: list[dict] = []

    # --- first_session ---
    total = session.query(sa_func.count(StudySession.id)).scalar() or 0
    if total >= 1:
        newly_awarded.extend(
            _try_award(session, "first_session", None, criteria={"sessions": 1})
        )

    # --- consistency_7: 5 of last 7 days ---
    consistency = calculate_consistency_streak(session, days=7)
    if consistency["days_studied"] >= 5:
        newly_awarded.extend(
            _try_award(
                session, "consistency_7", None,
                criteria={"days_studied": consistency["days_studied"], "window": 7},
            )
        )

    # --- consistency_30: 20 of last 30 days ---
    consistency_30 = calculate_consistency_streak(session, days=30)
    if consistency_30["days_studied"] >= 20:
        newly_awarded.extend(
            _try_award(
                session, "consistency_30", None,
                criteria={
                    "days_studied": consistency_30["days_studied"],
                    "window": 30,
                },
            )
        )

    # --- accuracy_streak: 85%+ for 3 consecutive sessions ---
    recent_sessions = (
        session.query(StudySession)
        .order_by(StudySession.started_at.desc())
        .limit(3)
        .all()
    )
    if (
        len(recent_sessions) >= 3
        and all(s.accuracy >= 0.85 for s in recent_sessions)
    ):
        newly_awarded.extend(
            _try_award(
                session, "accuracy_streak", None,
                criteria={"consecutive_sessions": 3, "min_accuracy": 0.85},
            )
        )

    # --- bloom_apply: Bloom Level 3+ on any topic ---
    progress = (
        session.query(UserProgress)
        .filter(UserProgress.topic_tag == topic_tag)
        .first()
    )
    if progress and progress.bloom_highest_level >= 3:
        newly_awarded.extend(
            _try_award(
                session, "bloom_apply", topic_tag,
                bloom_level=3,
                criteria={"topic": topic_tag, "bloom_level": 3},
            )
        )

    # --- bloom_analyze: Bloom Level 4+ on any topic ---
    if progress and progress.bloom_highest_level >= 4:
        newly_awarded.extend(
            _try_award(
                session, "bloom_analyze", topic_tag,
                bloom_level=4,
                criteria={"topic": topic_tag, "bloom_level": 4},
            )
        )

    # --- topic_mastery ---
    mastery_result = check_mastery(session, topic_tag)
    if mastery_result["mastered"]:
        newly_awarded.extend(
            _try_award(
                session, "topic_mastery", topic_tag,
                bloom_level=progress.bloom_highest_level if progress else None,
                criteria={"topic": topic_tag, "mastery": True},
            )
        )

    # --- deep_mastery: 95%+ accuracy AND Bloom 4+ ---
    if progress and mastery_result["mastered"]:
        details = mastery_result.get("details", {})
        avg_acc = details.get("avg_accuracy", 0.0)
        if avg_acc >= 0.95 and progress.bloom_highest_level >= 4:
            newly_awarded.extend(
                _try_award(
                    session, "deep_mastery", topic_tag,
                    bloom_level=progress.bloom_highest_level,
                    criteria={
                        "topic": topic_tag,
                        "accuracy": avg_acc,
                        "bloom_level": progress.bloom_highest_level,
                    },
                )
            )

    return newly_awarded


def calculate_consistency_streak(session: Session, days: int = 30) -> dict:
    """Calculate rolling study consistency as 'X of Y days'.

    NOT a binary streak. Uses rolling window.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(days=days)

    # Count distinct dates with at least one session
    distinct_days = (
        session.query(
            sa_func.count(
                sa_func.distinct(sa_func.date(StudySession.started_at))
            )
        )
        .filter(StudySession.started_at >= cutoff)
        .scalar()
    ) or 0

    # Current week (last 7 days)
    week_cutoff = now - timedelta(days=7)
    week_days = (
        session.query(
            sa_func.count(
                sa_func.distinct(sa_func.date(StudySession.started_at))
            )
        )
        .filter(StudySession.started_at >= week_cutoff)
        .scalar()
    ) or 0

    percentage = (distinct_days / days * 100) if days > 0 else 0.0

    return {
        "days_studied": distinct_days,
        "window_days": days,
        "percentage": round(percentage, 1),
        "current_week": {
            "days_studied": week_days,
            "total": 7,
        },
        "message": f"{week_days} of last 7 days",
    }


def calculate_session_stats(
    session: Session, study_session_id: int
) -> dict:
    """Calculate detailed stats for a completed study session."""
    study_sess = (
        session.query(StudySession)
        .filter(StudySession.id == study_session_id)
        .first()
    )
    if study_sess is None:
        return {
            "accuracy": 0.0,
            "total_items": 0,
            "correct_count": 0,
            "avg_confidence": 0.0,
            "calibration_gap": 0.0,
            "bloom_distribution": {},
            "mastery_changes": [],
            "time_spent_minutes": 0.0,
            "recommendations": [],
        }

    accuracy = study_sess.accuracy
    total_items = study_sess.total_items
    correct_count = study_sess.correct_count

    # Confidence from the session
    avg_confidence = 0.0
    if total_items > 0 and study_sess.confidence_sum > 0:
        avg_confidence = study_sess.confidence_sum / total_items / 5.0

    calibration_gap = abs(avg_confidence - accuracy)

    # Bloom distribution
    bloom_dist = {}
    if study_sess.bloom_level_distribution:
        bloom_dist = json.loads(study_sess.bloom_level_distribution)

    # Time spent
    time_spent = 0.0
    if study_sess.ended_at and study_sess.started_at:
        delta = study_sess.ended_at - study_sess.started_at
        time_spent = delta.total_seconds() / 60.0

    # Mastery state changes — cards that moved from learning to review
    mastery_changes = []
    if study_sess.study_set_id:
        reviews = (
            session.query(CardReview)
            .filter(CardReview.study_set_id == study_sess.study_set_id)
            .order_by(CardReview.id.desc())
            .limit(total_items)
            .all()
        )
        for r in reviews:
            if r.state == "review":
                mastery_changes.append(
                    f"Card {r.card_id} reached review state"
                )

    # Recommendations
    recommendations = []
    if accuracy < 0.70:
        recommendations.append(
            "Accuracy is below 70%. Consider reviewing easier material first."
        )
    elif accuracy < 0.85:
        recommendations.append(
            "Accuracy is below the 85% sweet spot. "
            "You're close to optimal difficulty."
        )

    if calibration_gap > 0.20:
        if avg_confidence > accuracy:
            recommendations.append(
                "You may be overconfident. "
                "Try rating your confidence more carefully."
            )
        else:
            recommendations.append(
                "You're underconfident! You know more than you think."
            )

    if time_spent > 0 and total_items > 0:
        per_item = time_spent / total_items
        if per_item > 3.0:
            recommendations.append(
                "You're spending a lot of time per item. "
                "Try to trust your first instinct."
            )

    return {
        "accuracy": round(accuracy * 100, 1),
        "total_items": total_items,
        "correct_count": correct_count,
        "avg_confidence": round(avg_confidence * 100, 1),
        "calibration_gap": round(calibration_gap * 100, 1),
        "bloom_distribution": bloom_dist,
        "mastery_changes": mastery_changes,
        "time_spent_minutes": round(time_spent, 1),
        "recommendations": recommendations,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _try_award(
    session: Session,
    achievement_type: str,
    topic_tag: str | None,
    *,
    bloom_level: int | None = None,
    criteria: dict | None = None,
) -> list[dict]:
    """Award an achievement if not already earned. Returns list of 0 or 1."""
    # Check for existing
    query = session.query(Achievement).filter(
        Achievement.achievement_type == achievement_type
    )
    if topic_tag is not None:
        query = query.filter(Achievement.topic_id == topic_tag)

    if query.first() is not None:
        return []

    title, description = ACHIEVEMENT_DEFS.get(
        achievement_type, ("Achievement", "Unlocked")
    )

    achievement = Achievement(
        achievement_type=achievement_type,
        title=title,
        description=description,
        criteria_json=json.dumps(criteria or {}),
        bloom_level_required=bloom_level,
        topic_id=topic_tag,
        earned_at=datetime.utcnow(),
    )
    session.add(achievement)
    session.commit()

    return [{
        "title": achievement.title,
        "description": achievement.description,
        "type": achievement.achievement_type,
        "bloom_level": achievement.bloom_level_required,
        "topic": achievement.topic_id,
        "earned_at": achievement.earned_at.isoformat(),
    }]
