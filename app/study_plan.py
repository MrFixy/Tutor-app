"""AI Engineering goal roadmaps backed by the curated phase curriculum."""
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import content_loader, models
from app.ollama_client import generate_json, OllamaError
from app.prompts.goal_prompts import build_goal_topic_system, GOAL_TOPIC_RETRY_SUFFIX
from app.schemas import GoalPhaseList, PhaseTopic, StudyPlanOut


def _phase_map() -> dict[str, dict]:
    return {phase["slug"]: phase for phase in content_loader.list_phases()}


def _validate_topics(raw: dict) -> GoalPhaseList:
    phases = _phase_map()
    raw_topics = raw.get("topics") if isinstance(raw, dict) else None
    if not isinstance(raw_topics, list) or not 3 <= len(raw_topics) <= 8:
        raise ValueError("expected 3-8 roadmap phases")

    topics = []
    seen = set()
    for item in raw_topics:
        if not isinstance(item, dict):
            raise ValueError("each roadmap topic must be an object")
        slug = item.get("phase_slug")
        if slug not in phases:
            raise ValueError(f"unknown AI Engineering phase: {slug!r}")
        if slug in seen:
            raise ValueError(f"duplicate phase: {slug!r}")
        seen.add(slug)
        phase = phases[slug]
        topics.append(PhaseTopic(phase_slug=slug, title=phase["title"], number=phase["number"]))
    return GoalPhaseList(topics=topics)


async def generate_topic_list(db: Session, goal_text: str) -> GoalPhaseList:
    del db  # roadmap candidates come from the checked-in curriculum, not learner history
    phases = content_loader.list_phases()
    if not phases:
        return GoalPhaseList(topics=[])
    system = build_goal_topic_system(phases)
    prompt = f"Learner's AI Engineering goal: {goal_text}"

    for suffix in ("", GOAL_TOPIC_RETRY_SUFFIX):
        try:
            raw = await generate_json(prompt, system=system + suffix)
            return _validate_topics(raw)
        except (OllamaError, ValidationError, ValueError):
            continue

    # A deterministic foundational route keeps planning usable when the model is offline.
    fallback = [phase for phase in phases if phase["number"] in (0, 1, 2)]
    if len(fallback) < 3:
        fallback = phases[:3]
    return GoalPhaseList(
        topics=[PhaseTopic(phase_slug=p["slug"], title=p["title"], number=p["number"]) for p in fallback[:3]]
    )


def create_plan(db: Session, user_id: int, goal_text: str, topics: list[PhaseTopic]) -> StudyPlanOut:
    phases = _phase_map()
    plan = models.StudyPlan(user_id=user_id, goal_text=goal_text)
    db.add(plan)
    db.flush()

    seen_phases = set()
    for index, topic in enumerate(topics):
        if topic.phase_slug in seen_phases:
            raise ValueError(f"Duplicate AI Engineering phase: {topic.phase_slug}")
        seen_phases.add(topic.phase_slug)
        phase = phases.get(topic.phase_slug)
        if phase is None:
            raise ValueError(f"Unknown AI Engineering phase: {topic.phase_slug}")
        db.add(
            models.StudyPlanItem(
                plan_id=plan.id,
                curriculum="phases",
                phase_slug=phase["slug"],
                order=index,
            )
        )

    db.commit()
    db.refresh(plan)
    return StudyPlanOut(
        id=plan.id,
        goal_text=plan.goal_text,
        created_at=plan.created_at.isoformat(),
        items=_plan_items(plan.items),
    )


def _plan_items(items) -> list[PhaseTopic]:
    phases = _phase_map()
    result = []
    for item in sorted(items, key=lambda row: row.order):
        if item.curriculum != "phases":
            continue  # ignore plan items stored in an obsolete format
        phase = phases.get(item.phase_slug)
        if phase is None:
            continue
        result.append(PhaseTopic(phase_slug=phase["slug"], title=phase["title"], number=phase["number"]))
    return result


def list_plans(db: Session, user_id: int) -> list[StudyPlanOut]:
    saved_plans = (
        db.query(models.StudyPlan)
        .filter_by(user_id=user_id)
        .order_by(models.StudyPlan.created_at.desc())
        .all()
    )
    result = []
    for plan in saved_plans:
        items = _plan_items(plan.items)
        if not items:
            continue
        result.append(
            StudyPlanOut(
                id=plan.id,
                goal_text=plan.goal_text,
                created_at=plan.created_at.isoformat(),
                items=items,
            )
        )
    return result
