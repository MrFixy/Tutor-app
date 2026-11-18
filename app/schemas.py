from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_id: int
    session_id: Optional[int] = None
    message: str = Field(min_length=1, max_length=20_000)


class GoalCheckRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)


class GoalCheckResponse(BaseModel):
    is_goal: bool


class PhaseTopic(BaseModel):
    phase_slug: str
    title: str
    number: int


class GoalPhaseList(BaseModel):
    topics: List[PhaseTopic] = Field(min_length=1, max_length=8)


class ChatResponse(BaseModel):
    reply: str = ""
    is_goal: bool = False
    goal_topics: Optional[GoalPhaseList] = None


class ExplainRequest(BaseModel):
    question: str = Field(min_length=1, max_length=20_000)


class ExplainResponse(BaseModel):
    explanation: str


class LessonOut(BaseModel):
    phase_slug: str
    lesson_slug: str
    title: str
    body: str
    order: int


class StudyPlanCreate(BaseModel):
    user_id: int
    goal_text: str = Field(min_length=1, max_length=2_000)
    topics: List[PhaseTopic] = Field(min_length=1, max_length=8)


class StudyPlanOut(BaseModel):
    id: int
    goal_text: str
    created_at: str
    items: List[PhaseTopic]


class StudyPlanListResponse(BaseModel):
    plans: List[StudyPlanOut]


class FeedbackCreate(BaseModel):
    user_id: Optional[int] = None
    session_id: Optional[int] = None
    category: str = Field(pattern="^(bug|ux_friction|other)$")
    view: Optional[str] = None
    severity: Optional[str] = Field(default=None, pattern="^(blocker|annoying|minor)$")
    message: str = Field(min_length=1, max_length=10_000)


class FeedbackOut(BaseModel):
    id: int
    category: str
    view: Optional[str] = None
    severity: Optional[str] = None
    message: str
    created_at: str
