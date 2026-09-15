from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import get_db, Base, engine
from app import models  # noqa: F401  (registers models on Base.metadata)
from app.schemas import (
    ChatRequest,
    ChatResponse,
    CodeExerciseGenerateRequest,
    CodeExerciseGenerateResponse,
    CodeSubmitRequest,
    CodeSubmitResponse,
    ExplainRequest,
    ExplainResponse,
    FeedbackCreate,
    FeedbackOut,
    GoalCheckRequest,
    GoalCheckResponse,
    GoalTopicList,
    LessonListItem,
    LessonOut,
    MasteryListResponse,
    MasteryScoreOut,
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
    StudyPlanCreate,
    StudyPlanListResponse,
    StudyPlanOut,
)
from app.ollama_client import ping, generate
import app.ollama_client as ollama_client
from app.classifier import classify_question, classify_goal_statement
from app.explain import explain
from app import content_loader
from app import judge0_client
from app import mastery
from app import practice
from app import study_plan
from app import user_service

app = FastAPI(title="Stats/Coding Tutor", version="0.6.0")

# Phase 5 (Week 11): the frontend is served from its own origin (e.g. a
# `python -m http.server` on :5500 or a split pilot deployment), so the
# browser needs CORS to call this API. Wide open is fine for a no-auth
# pilot; tighten allow_origins before any wider rollout.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # Phase 0 deliverable: confirm Ollama at localhost:11434 responds.
    ok = await ping()
    app.state.ollama_ok = ok
    print(f"[startup] Ollama reachable: {ok}")
    # Phase 3: confirm the self-hosted Judge0 instance responds too. Not
    # fatal if it's down -- /chat and /explain don't need it -- but the
    # /practice/code/* endpoints will fail until it's up.
    judge0_ok = await judge0_client.ping()
    app.state.judge0_ok = judge0_ok
    print(f"[startup] Judge0 reachable: {judge0_ok}")
    # Convenience for local dev; in real deployments use Alembic migrations
    # or `psql -f db/schema.sql` instead of create_all().
    Base.metadata.create_all(bind=engine)

    # Redesign: load the curated lesson library from content/lessons/ into
    # LessonContent. Static/curated content, not LLM-generated -- runs
    # once here, not per-request. Needs a DB session of its own since the
    # get_db() dependency isn't wired up outside a request.
    db = next(get_db())
    try:
        n = content_loader.load_lessons_from_disk(db)
        print(f"[startup] Loaded {n} lesson(s) from content/lessons/")
    finally:
        db.close()


@app.on_event("shutdown")
async def shutdown():
    # Phase 6 (Week 14): close the pooled httpx clients cleanly instead of
    # letting them leak on reload/shutdown.
    await ollama_client.aclose_client()
    await judge0_client.aclose_client()


@app.get("/health")
async def health():
    from app.config import settings

    return {
        "ollama_ok": app.state.ollama_ok,
        "judge0_ok": app.state.judge0_ok,
        # Phase 6 (Week 14): surfaced so the frontend's status LEDs (and
        # anyone reading logs during the pilot) can tell whether a
        # hosted-API fallback is even configured to kick in on failure.
        "hosted_fallback_enabled": settings.hosted_fallback_enabled,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Phase 0: originally just echoed a raw model response.
    Phase 1: now classifies intent first.
    Phase 2: now routes to the topic-specific explanation engine and
    persists the question + classification + explanation.
    Phase 4 (Week 10): difficulty is no longer hardcoded -- it's pulled
    from this user's mastery_score history for (domain, subtopic), so
    explanations get harder as they demonstrate mastery via the practice
    loop, and stay at "beginner" until there's enough attempt history.
    Phase 6 (Week 14): get_or_create_user/_session fix the FK-violation
    bug described in user_service.py -- must run before any write below.
    Redesign: a goal-statement message ("I want to learn X") short-
    circuits to a roadmap-checklist response instead of the normal
    explain path; a normal explain response gets a `related_lesson`
    chip attached when one exists in the curated library.
    """
    user_service.get_or_create_user(db, req.user_id)
    session_id = user_service.get_or_create_session(db, req.session_id, req.user_id)

    goal_check = await classify_goal_statement(req.message)
    if goal_check.is_goal:
        topics = await study_plan.generate_topic_list(db, req.message)
        return ChatResponse(reply="", is_goal=True, goal_topics=topics)

    intent = await classify_question(req.message)
    difficulty = mastery.get_recommended_difficulty(db, req.user_id, intent.domain, intent.subtopic)
    reply = await explain(intent.domain, intent.subtopic, req.message, difficulty=difficulty)

    question_row = models.Question(
        session_id=session_id,
        user_id=req.user_id,
        raw_text=req.message,
        intent_domain=intent.domain,
        intent_subtopic=intent.subtopic,
        intent_confidence=intent.confidence,
        classified_json=intent.model_dump(),
        explanation=reply,
    )
    db.add(question_row)
    db.commit()

    # Redesign: attach the matching lesson (if the library has one) so the
    # frontend can render a "read the lesson" chip. Coding subtopics are
    # only curated for python today, so that's the language looked up;
    # stats topics have no language.
    lesson_language = "python" if intent.domain == "coding" else None
    lesson = study_plan.get_lesson(db, intent.domain, intent.subtopic, lesson_language)
    related_lesson = None
    if lesson is not None:
        mastery_row = mastery.get_all_mastery(db, req.user_id)
        m = next((r for r in mastery_row if r.domain == lesson.domain and r.subtopic == lesson.subtopic), None)
        status = study_plan.status_for(m.score if m else None, m.attempts_count if m else 0)
        related_lesson = LessonListItem(
            domain=lesson.domain,
            subtopic=lesson.subtopic,
            language=lesson.language,
            title=lesson.title,
            order=lesson.order,
            status=status,
        )

    return ChatResponse(
        reply=reply,
        intent_domain=intent.domain,
        intent_subtopic=intent.subtopic,
        intent_confidence=intent.confidence,
        difficulty=difficulty,
        related_lesson=related_lesson,
    )


@app.post("/chat/raw")
async def chat_raw(req: ChatRequest):
    """
    Kept from the Week 1 deliverable: a plain echo of the local model's
    response, with no classification/DB write. Useful for smoke-testing
    the Ollama connection in isolation.
    """
    reply = await generate(req.message)
    return {"reply": reply}


@app.post("/explain", response_model=ExplainResponse)
async def explain_endpoint(req: ExplainRequest, db: Session = Depends(get_db)):
    """
    Direct access to the Phase 2 explanation engine, bypassing /chat's DB
    write. Phase 4: req.difficulty is now an override -- omit it (or send
    null) to get the mastery-driven recommendation instead.
    """
    intent = await classify_question(req.question)
    difficulty = req.difficulty or mastery.get_recommended_difficulty(
        db, req.user_id, intent.domain, intent.subtopic
    )
    reply = await explain(intent.domain, intent.subtopic, req.question, difficulty=difficulty)
    return ExplainResponse(
        domain=intent.domain,
        subtopic=intent.subtopic,
        confidence=intent.confidence,
        explanation=reply,
        difficulty=difficulty,
    )


# ---------- Phase 3 / Week 7: stats quiz ----------

@app.post("/practice/quiz/generate", response_model=QuizGenerateResponse)
async def quiz_generate(req: QuizGenerateRequest, db: Session = Depends(get_db)):
    """
    Generates a stats quiz for a subtopic (typically the subtopic the
    learner was just given an /explain response for) and persists it so
    /practice/quiz/submit can grade against it later.
    """
    questions = await practice.start_quiz(
        db, req.user_id, req.session_id, req.subtopic, req.difficulty, req.count
    )
    return QuizGenerateResponse(subtopic=req.subtopic, questions=questions)


@app.post("/practice/quiz/submit", response_model=QuizSubmitResponse)
async def quiz_submit(req: QuizSubmitRequest, db: Session = Depends(get_db)):
    try:
        return await practice.submit_quiz_answer(db, req.user_id, req.question_id, req.chosen_index)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------- Phase 3 / Week 8: coding exercise + Judge0 checker ----------

@app.post("/practice/code/generate", response_model=CodeExerciseGenerateResponse)
async def code_exercise_generate(req: CodeExerciseGenerateRequest, db: Session = Depends(get_db)):
    """Generates a coding exercise for a subtopic and persists it (test
    cases included, but not sent to the client) for grading later."""
    exercise = await practice.start_code_exercise(
        db, req.user_id, req.session_id, req.subtopic, req.difficulty
    )
    return CodeExerciseGenerateResponse(subtopic=req.subtopic, exercise=exercise)


@app.post("/practice/code/submit", response_model=CodeSubmitResponse)
async def code_exercise_submit(req: CodeSubmitRequest, db: Session = Depends(get_db)):
    """Runs the learner's submission against the exercise's test cases via
    Judge0 and grades it. Requires docker-compose.judge0.yml to be up."""
    try:
        return await practice.submit_code_answer(db, req.user_id, req.question_id, req.source_code)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ---------- Redesign: lesson library ----------

@app.get("/lessons/{domain}")
async def list_lessons(domain: str, user_id: int, language: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Statistics tab: GET /lessons/stats -> list[LessonListItem] (subtopic
    grid, status joined from mastery_score).

        Programming and AI Engineering tabs, two steps:
      GET /lessons/coding (no language)      -> {"languages": [...]}
      GET /lessons/coding?language=python    -> list[LessonListItem]
            GET /lessons/phases (no language)      -> {"languages": [...]}
            GET /lessons/phases?language=...      -> list[LessonListItem]
    """
    if language is None and domain == "coding":
        return {"languages": study_plan.list_coding_languages(db)}
    if language is None and domain == "phases":
        return {"languages": study_plan.list_phase_groups(db)}
    return study_plan.list_lesson_items(db, user_id, domain, language)


@app.get("/lessons/{domain}/{subtopic}", response_model=LessonOut)
async def get_lesson(domain: str, subtopic: str, language: Optional[str] = None, db: Session = Depends(get_db)):
    """Static lesson read, no LLM -- curated content only."""
    lesson = study_plan.get_lesson(db, domain, subtopic, language)
    if lesson is None:
        raise HTTPException(status_code=404, detail=f"no lesson found for {domain}/{subtopic} (language={language})")
    return lesson


# ---------- Redesign: goal statements + study plans ----------

@app.post("/goal/check", response_model=GoalCheckResponse)
async def goal_check(req: GoalCheckRequest):
    """Exposed directly for testing -- /chat already runs this internally
    before deciding whether to route into the goal/roadmap path."""
    return await classify_goal_statement(req.message)


@app.post("/goal/topics", response_model=GoalTopicList)
async def goal_topics(req: GoalCheckRequest, db: Session = Depends(get_db)):
    return await study_plan.generate_topic_list(db, req.message)


@app.post("/plans", response_model=StudyPlanOut, status_code=201)
async def save_plan(req: StudyPlanCreate, db: Session = Depends(get_db)):
    user_service.get_or_create_user(db, req.user_id)
    return study_plan.create_plan(db, req.user_id, req.goal_text, req.topics)


@app.get("/plans/{user_id}", response_model=StudyPlanListResponse)
async def get_plans(user_id: int, db: Session = Depends(get_db)):
    return StudyPlanListResponse(plans=study_plan.list_plans(db, user_id))


# ---------- Phase 4 / Week 9-10: mastery + difficulty ----------

@app.get("/mastery/{user_id}", response_model=MasteryListResponse)
async def get_mastery(user_id: int, db: Session = Depends(get_db)):
    """
    Every (domain, subtopic) mastery_score row for a user, with the
    difficulty level each currently maps to. Read-only view over Phase 4's
    scoring -- useful for the Week 11 pilot dashboard / feedback review.
    """
    rows = mastery.get_all_mastery(db, user_id)
    out = [
        MasteryScoreOut(
            domain=r.domain,
            subtopic=r.subtopic,
            score=r.score,
            attempts_count=r.attempts_count,
            difficulty=mastery.difficulty_for_score(r.score, r.attempts_count),
        )
        for r in rows
    ]
    return MasteryListResponse(user_id=user_id, mastery=out)


# ---------- Phase 6 / Week 13: pilot feedback ----------

@app.post("/feedback", response_model=FeedbackOut, status_code=201)
async def submit_feedback(req: FeedbackCreate, db: Session = Depends(get_db)):
    """Written from the in-app feedback widget so a pilot learner can flag
    a bug or a confusing moment without leaving the app or filling out a
    separate form. No auth, matching the rest of the pilot build."""
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
        id=row.id, category=row.category, view=row.view, severity=row.severity,
        message=row.message, created_at=row.created_at.isoformat(),
    )


@app.get("/feedback", response_model=List[FeedbackOut])
async def list_feedback(db: Session = Depends(get_db)):
    """Raw feedback list for reviewing after the Week 13 pilot session.
    No auth (matches the rest of the no-auth pilot build) -- fine for a
    closed pilot; don't expose this route beyond it."""
    rows = db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).all()
    return [
        FeedbackOut(
            id=r.id, category=r.category, view=r.view, severity=r.severity,
            message=r.message, created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]
