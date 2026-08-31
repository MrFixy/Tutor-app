from typing import List, Literal, Optional
from pydantic import BaseModel, Field


# ---------- Phase 0: chat I/O ----------

class ChatRequest(BaseModel):
    user_id: int
    session_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    reply: str
    intent_domain: Optional[str] = None
    intent_subtopic: Optional[str] = None
    intent_confidence: Optional[float] = None
    difficulty: Optional[str] = None  # Phase 4: mastery-driven level used for `reply`
    # Redesign: set when the message was classified as a goal statement --
    # `reply` is unused in that case and the frontend renders `goal_topics`
    # as a roadmap-checklist bubble instead.
    is_goal: bool = False
    goal_topics: Optional["GoalTopicList"] = None
    # Redesign: set on a normal (non-goal) explain response so the
    # frontend can render a "read the lesson" chip pointing at the
    # matching lesson, if one exists in the library.
    related_lesson: Optional["LessonListItem"] = None


# ---------- Phase 1: intent classification schema ----------
# Two domains only, each with a fixed sub-topic vocabulary. Keeping the
# vocabulary closed (rather than free-text) makes the classifier's JSON
# easy to validate and keeps mastery_score rows consistent later on.

StatsSubtopic = Literal[
    "descriptive_stats",      # mean/median/mode/variance/std dev
    "probability",
    "distributions",
    "hypothesis_testing",
    "p_values_significance",
    "confidence_intervals",
    "correlation_regression",
    "sampling",
    "other_stats",
]

CodingSubtopic = Literal[
    "syntax_basics",
    "data_structures",
    "control_flow",
    "functions",
    "recursion",
    "algorithms",
    "debugging",
    "oop",
    "other_coding",
]


class IntentClassification(BaseModel):
    """Structured output the classifier LLM call must produce."""
    domain: Literal["stats", "coding"]
    subtopic: str  # validated against StatsSubtopic/CodingSubtopic in classifier.py
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: Optional[str] = None


# ---------- Phase 2: explanation engine ----------
# (DifficultyLevel is also reused by Phase 3's quiz/code generators and by
# Phase 4's mastery-driven difficulty adjustment.)

DifficultyLevel = Literal["beginner", "intermediate", "advanced"]


class ExplainRequest(BaseModel):
    user_id: int
    question: str
    # None = let Phase 4 pick difficulty from mastery_score history for this
    # user+domain+subtopic; pass a value to override the recommendation.
    difficulty: Optional[DifficultyLevel] = None


class ExplainResponse(BaseModel):
    domain: str
    subtopic: str
    confidence: float
    explanation: str
    difficulty: DifficultyLevel  # the level actually used, per Phase 4


# ---------- Phase 3 / Week 7: stats quiz generator ----------
# Structured output the quiz-generation LLM call must produce, mirroring
# the classifier's format=json + validate + one-retry pattern.

class QuizQuestion(BaseModel):
    """Single multiple-choice question as returned by the model."""
    stem: str
    choices: List[str] = Field(min_length=4, max_length=4)
    correct_index: int = Field(ge=0, le=3)
    explanation: str


class QuizQuestionSet(BaseModel):
    """Wrapper so the model returns one JSON object, not a bare array."""
    questions: List[QuizQuestion]


class QuizQuestionOut(BaseModel):
    """Quiz question as sent to the client -- correct_index withheld."""
    question_id: int
    stem: str
    choices: List[str]


class QuizGenerateRequest(BaseModel):
    user_id: int
    session_id: Optional[int] = None
    subtopic: StatsSubtopic
    difficulty: DifficultyLevel = "beginner"
    count: int = Field(default=3, ge=1, le=10)


class QuizGenerateResponse(BaseModel):
    subtopic: str
    questions: List[QuizQuestionOut]


class QuizSubmitRequest(BaseModel):
    user_id: int
    question_id: int
    chosen_index: int = Field(ge=0, le=3)


class QuizSubmitResponse(BaseModel):
    question_id: int
    correct: bool
    correct_index: int
    explanation: str
    feedback: str


# ---------- Phase 3 / Week 8: coding exercise + Judge0 checker ----------

class CodeTestCase(BaseModel):
    """One stdin -> expected stdout pair. Kept simple (stdin/stdout) since
    that's what Judge0 grades natively, no custom test harness needed."""
    stdin: str = ""
    expected_output: str


class CodeExercise(BaseModel):
    prompt: str
    starter_code: str
    test_cases: List[CodeTestCase] = Field(min_length=1)


class CodeExerciseOut(BaseModel):
    """Coding exercise as sent to the client -- test cases withheld so the
    learner can't just hardcode outputs; they're re-fetched server-side
    from the persisted Question row when grading."""
    question_id: int
    prompt: str
    starter_code: str


class CodeExerciseGenerateRequest(BaseModel):
    user_id: int
    session_id: Optional[int] = None
    subtopic: CodingSubtopic
    difficulty: DifficultyLevel = "beginner"


class CodeExerciseGenerateResponse(BaseModel):
    subtopic: str
    exercise: CodeExerciseOut


class CodeSubmitRequest(BaseModel):
    user_id: int
    question_id: int
    source_code: str


class CodeTestResult(BaseModel):
    passed: bool
    stdin: str
    expected_output: str
    actual_output: str
    status: str  # Judge0 status description, e.g. "Accepted", "Wrong Answer"
    stderr: Optional[str] = None


class CodeSubmitResponse(BaseModel):
    question_id: int
    passed: bool
    score: float  # fraction of test cases passed, 0.0-1.0
    results: List[CodeTestResult]
    feedback: str


# ---------- Phase 4 / Week 9-10: mastery + difficulty ----------

class MasteryScoreOut(BaseModel):
    domain: str
    subtopic: str
    score: float  # rolling EMA, 0.0-1.0
    attempts_count: int
    difficulty: DifficultyLevel  # what difficulty_for_score() currently maps this to


class MasteryListResponse(BaseModel):
    user_id: int
    mastery: List[MasteryScoreOut]


# ---------- Redesign: lesson library ----------

class LessonOut(BaseModel):
    domain: str
    subtopic: str
    language: Optional[str] = None
    title: str
    body: str
    order: int


LessonStatus = Literal["not_started", "in_progress", "mastered"]


class LessonListItem(BaseModel):
    domain: str
    subtopic: str
    language: Optional[str] = None
    title: str
    order: int
    status: LessonStatus  # joined from mastery_score at read time, not stored


# ---------- Redesign: goal-driven study plans ----------

class GoalCheckRequest(BaseModel):
    message: str


class GoalCheckResponse(BaseModel):
    is_goal: bool


class GoalTopicItem(BaseModel):
    domain: Literal["stats", "coding"]
    subtopic: str  # validated against StatsSubtopic | CodingSubtopic in study_plan.py
    language: Optional[str] = None


class GoalTopicList(BaseModel):
    topics: List[GoalTopicItem]


class StudyPlanCreate(BaseModel):
    user_id: int
    goal_text: str
    topics: List[GoalTopicItem]


class StudyPlanOut(BaseModel):
    id: int
    goal_text: str
    created_at: str
    items: List[LessonListItem]


class StudyPlanListResponse(BaseModel):
    plans: List[StudyPlanOut]


# ---------- Phase 6 / Week 13: pilot feedback ----------

class FeedbackCreate(BaseModel):
    user_id: Optional[int] = None
    session_id: Optional[int] = None
    category: Literal["bug", "ux_friction", "other"]
    view: Optional[str] = None  # 'chat' | 'practice' | 'progress', best-effort
    severity: Optional[Literal["blocker", "annoying", "minor"]] = None
    message: str


class FeedbackOut(BaseModel):
    id: int
    category: str
    view: Optional[str] = None
    severity: Optional[str] = None
    message: str
    created_at: str


# ChatResponse references GoalTopicList/LessonListItem by forward-ref
# string (defined further down in this file) -- resolve now that both
# exist.
ChatResponse.model_rebuild()
