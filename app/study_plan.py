"""
Redesign - goal-driven study plans ("My plans").

Flow:
  1. classifier.classify_goal_statement() flags a /chat message as a
     goal statement.
  2. generate_topic_list() turns that goal into an ordered roadmap,
     drawn from the app's existing (curated) lesson subtopics -- never
     LLM-generated lesson content itself.
  3. create_plan() persists the roadmap so it survives past the chat
     bubble ("Save as my plan").
  4. list_plans() reads plans back with each item's current status
     joined live from mastery_score, so progress reflects the learner's
     actual practice history rather than a stored snapshot.
"""
from typing import get_args

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import models
from app.mastery import ADVANCED_THRESHOLD
from app.ollama_client import generate_json, OllamaError
from app.prompts.goal_prompts import (
    build_goal_topic_system,
    GOAL_TOPIC_RETRY_SUFFIX,
)
from app.schemas import (
    CodingSubtopic,
    GoalTopicItem,
    GoalTopicList,
    LessonListItem,
    LessonOut,
    LessonStatus,
    StatsSubtopic,
    StudyPlanOut,
)

STATS_SUBTOPICS = set(get_args(StatsSubtopic))
CODING_SUBTOPICS = set(get_args(CodingSubtopic))

# Conservative fallback roadmap used only if the LLM call fails twice --
# keeps "save a plan" working even with the model down, rather than
# surfacing an error for what's meant to be a light-touch feature.
FALLBACK_TOPICS = GoalTopicList(
    topics=[
        GoalTopicItem(domain="stats", subtopic="descriptive_stats", language=None),
        GoalTopicItem(domain="coding", subtopic="syntax_basics", language="python"),
    ]
)


def _known_languages(db: Session) -> list[str]:
    rows = db.query(models.LessonContent.language).filter(models.LessonContent.language.isnot(None)).distinct().all()
    langs = sorted({r[0] for r in rows if r[0]})
    return langs or ["python"]


def _validate_topics(raw: dict, valid_languages: set[str]) -> GoalTopicList:
    parsed = GoalTopicList.model_validate(raw)
    if not (3 <= len(parsed.topics) <= 8):
        raise ValueError(f"expected 3-8 topics, got {len(parsed.topics)}")
    for t in parsed.topics:
        if t.domain == "stats":
            if t.subtopic not in STATS_SUBTOPICS:
                raise ValueError(f"invalid stats subtopic {t.subtopic!r}")
            if t.language is not None:
                raise ValueError("stats topics must not have a language")
        else:
            if t.subtopic not in CODING_SUBTOPICS:
                raise ValueError(f"invalid coding subtopic {t.subtopic!r}")
            if t.language not in valid_languages:
                raise ValueError(f"invalid coding language {t.language!r}")
    return parsed


async def generate_topic_list(db: Session, goal_text: str) -> GoalTopicList:
    languages = _known_languages(db)
    system = build_goal_topic_system(sorted(STATS_SUBTOPICS), sorted(CODING_SUBTOPICS), languages)
    prompt = f"Learner's stated goal: {goal_text}"

    try:
        raw = await generate_json(prompt, system=system)
        return _validate_topics(raw, set(languages))
    except (OllamaError, ValidationError, ValueError):
        pass

    try:
        raw = await generate_json(prompt, system=system + GOAL_TOPIC_RETRY_SUFFIX)
        return _validate_topics(raw, set(languages))
    except (OllamaError, ValidationError, ValueError):
        return FALLBACK_TOPICS


def status_for(score: float | None, attempts_count: int) -> LessonStatus:
    if attempts_count == 0 or score is None:
        return "not_started"
    if score >= ADVANCED_THRESHOLD:
        return "mastered"
    return "in_progress"


def _lesson_items_for(db: Session, user_id: int, topics: list) -> list[LessonListItem]:
    """Joins each (domain, subtopic, language) topic against LessonContent
    (for title/order) and mastery_score (for status), in one query each
    rather than N+1 per item."""
    mastery_rows = {
        (m.domain, m.subtopic): m
        for m in db.query(models.MasteryScore).filter_by(user_id=user_id).all()
    }
    content_rows = {
        (c.domain, c.subtopic, c.language): c for c in db.query(models.LessonContent).all()
    }

    items: list[LessonListItem] = []
    for t in topics:
        domain = t.domain if hasattr(t, "domain") else t["domain"]
        subtopic = t.subtopic if hasattr(t, "subtopic") else t["subtopic"]
        language = t.language if hasattr(t, "language") else t.get("language")

        content = content_rows.get((domain, subtopic, language))
        title = content.title if content else subtopic.replace("_", " ").title()
        order = content.order if content else 0

        m = mastery_rows.get((domain, subtopic))
        status = status_for(m.score if m else None, m.attempts_count if m else 0)

        items.append(
            LessonListItem(
                domain=domain,
                subtopic=subtopic,
                language=language,
                title=title,
                order=order,
                status=status,
            )
        )
    return items


def list_lesson_items(
    db: Session, user_id: int, domain: str, language: str | None = None
) -> list[LessonListItem]:
    """Backs GET /lessons/{domain} -- every curated LessonContent row for
    a domain (optionally filtered to one coding language), with status
    joined live from mastery_score. Used by the Lessons tab, independent
    of any saved study plan."""
    q = db.query(models.LessonContent).filter_by(domain=domain)
    if language is not None:
        q = q.filter_by(language=language)
    rows = q.order_by(models.LessonContent.order).all()

    mastery_rows = {
        (m.domain, m.subtopic): m
        for m in db.query(models.MasteryScore).filter_by(user_id=user_id).all()
    }

    out = []
    for row in rows:
        m = mastery_rows.get((row.domain, row.subtopic))
        status = status_for(m.score if m else None, m.attempts_count if m else 0)
        out.append(
            LessonListItem(
                domain=row.domain,
                subtopic=row.subtopic,
                language=row.language,
                title=row.title,
                order=row.order,
                status=status,
            )
        )
    return out


def get_lesson(db: Session, domain: str, subtopic: str, language: str | None = None) -> LessonOut | None:
    """Backs GET /lessons/{domain}/{subtopic} -- a single static lesson
    read straight from LessonContent. No LLM involved."""
    row = (
        db.query(models.LessonContent)
        .filter_by(domain=domain, subtopic=subtopic, language=language)
        .one_or_none()
    )
    if row is None:
        return None
    return LessonOut(
        domain=row.domain,
        subtopic=row.subtopic,
        language=row.language,
        title=row.title,
        body=row.body,
        order=row.order,
    )


def list_coding_languages(db: Session) -> list[str]:
    """Distinct coding languages that have at least one curated lesson --
    backs the Lessons tab's Programming -> language grid."""
    return _known_languages(db)


def create_plan(db: Session, user_id: int, goal_text: str, topics: list[GoalTopicItem]) -> StudyPlanOut:
    plan = models.StudyPlan(user_id=user_id, goal_text=goal_text)
    db.add(plan)
    db.flush()  # populate plan.id

    for i, t in enumerate(topics):
        db.add(
            models.StudyPlanItem(
                plan_id=plan.id,
                domain=t.domain,
                subtopic=t.subtopic,
                language=t.language,
                order=i,
            )
        )
    db.commit()
    db.refresh(plan)

    items = _lesson_items_for(db, user_id, plan.items)
    return StudyPlanOut(
        id=plan.id,
        goal_text=plan.goal_text,
        created_at=plan.created_at.isoformat(),
        items=items,
    )


def list_plans(db: Session, user_id: int) -> list[StudyPlanOut]:
    plans = (
        db.query(models.StudyPlan)
        .filter_by(user_id=user_id)
        .order_by(models.StudyPlan.created_at.desc())
        .all()
    )
    out = []
    for plan in plans:
        sorted_items = sorted(plan.items, key=lambda i: i.order)
        items = _lesson_items_for(db, user_id, sorted_items)
        out.append(
            StudyPlanOut(
                id=plan.id,
                goal_text=plan.goal_text,
                created_at=plan.created_at.isoformat(),
                items=items,
            )
        )
    return out
