from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import content_loader, models, ollama_client, study_plan, user_service
from app.classifier import classify_goal_statement
from app.db import Base, engine, get_db
from app.explain import explain
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ExplainRequest,
    ExplainResponse,
    FeedbackCreate,
    FeedbackOut,
    GoalCheckRequest,
    GoalCheckResponse,
    GoalPhaseList,
    LessonOut,
    StudyPlanCreate,
    StudyPlanListResponse,
    StudyPlanOut,
)
from app.ollama_client import ping

app = FastAPI(title="AI Engineering Tutor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    app.state.ollama_ok = await ping()
    print(f"[startup] Ollama reachable: {app.state.ollama_ok}")
    Base.metadata.create_all(bind=engine)

    db = next(get_db())
    try:
        loaded = content_loader.load_lessons_from_disk(db)
        print(f"[startup] Loaded {loaded} AI Engineering lesson(s)")
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown():
    await ollama_client.aclose_client()


@app.get("/health")
async def health():
    from app.config import settings

    return {
        "ollama_ok": app.state.ollama_ok,
        "hosted_fallback_enabled": settings.hosted_fallback_enabled,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    user_service.get_or_create_user(db, req.user_id)
    session_id = user_service.get_or_create_session(db, req.session_id, req.user_id)

    goal_check = await classify_goal_statement(req.message)
    if goal_check.is_goal:
        topics = await study_plan.generate_topic_list(db, req.message)
        if topics.topics:
            return ChatResponse(reply="", is_goal=True, goal_topics=topics)

    reply = await explain(req.message)
    db.add(
        models.Question(
            session_id=session_id,
            user_id=req.user_id,
            raw_text=req.message,
            explanation=reply,
        )
    )
    db.commit()
    return ChatResponse(reply=reply)


@app.post("/explain", response_model=ExplainResponse)
async def explain_endpoint(req: ExplainRequest):
    return ExplainResponse(explanation=await explain(req.question))


@app.get("/lessons/phases")
async def list_ai_engineering_phases():
    return {"phases": content_loader.list_phases()}


@app.get("/lessons/phases/{phase_slug}/{lesson_slug}", response_model=LessonOut)
async def get_ai_engineering_lesson(
    phase_slug: str,
    lesson_slug: str,
    db: Session = Depends(get_db),
):
    lesson = content_loader.get_phase_lesson(db, phase_slug, lesson_slug)
    if lesson is None:
        raise HTTPException(status_code=404, detail="AI Engineering lesson not found")
    return LessonOut(
        phase_slug=phase_slug,
        lesson_slug=lesson_slug,
        title=lesson.title,
        body=lesson.body,
        order=lesson.order,
    )


@app.post("/goal/check", response_model=GoalCheckResponse)
async def goal_check(req: GoalCheckRequest):
    return await classify_goal_statement(req.message)


@app.post("/goal/topics", response_model=GoalPhaseList)
async def goal_topics(req: GoalCheckRequest, db: Session = Depends(get_db)):
    return await study_plan.generate_topic_list(db, req.message)


@app.post("/plans", response_model=StudyPlanOut, status_code=201)
async def save_plan(req: StudyPlanCreate, db: Session = Depends(get_db)):
    user_service.get_or_create_user(db, req.user_id)
    try:
        return study_plan.create_plan(db, req.user_id, req.goal_text, req.topics)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.get("/plans/{user_id}", response_model=StudyPlanListResponse)
async def get_plans(user_id: int, db: Session = Depends(get_db)):
    return StudyPlanListResponse(plans=study_plan.list_plans(db, user_id))


@app.post("/feedback", response_model=FeedbackOut, status_code=201)
async def submit_feedback(req: FeedbackCreate, db: Session = Depends(get_db)):
    if req.user_id is not None:
        user_service.get_or_create_user(db, req.user_id)

    row = models.Feedback(
        user_id=req.user_id,
        session_id=req.session_id,
        category=req.category,
        view=req.view,
        severity=req.severity,
        message=req.message,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return FeedbackOut(
        id=row.id,
        category=row.category,
        view=row.view,
        severity=row.severity,
        message=row.message,
        created_at=row.created_at.isoformat(),
    )


@app.get("/feedback", response_model=List[FeedbackOut])
async def list_feedback(db: Session = Depends(get_db)):
    rows = db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).all()
    return [
        FeedbackOut(
            id=row.id,
            category=row.category,
            view=row.view,
            severity=row.severity,
            message=row.message,
            created_at=row.created_at.isoformat(),
        )
        for row in rows
    ]
