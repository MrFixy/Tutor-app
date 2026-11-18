from pydantic import ValidationError

from app.ollama_client import generate_json, OllamaError
from app.prompts.goal_prompts import GOAL_CHECK_SYSTEM, GOAL_CHECK_RETRY_SUFFIX
from app.schemas import GoalCheckResponse


async def classify_goal_statement(text: str) -> GoalCheckResponse:
    prompt = f"Learner message: {text}"
    for system in (GOAL_CHECK_SYSTEM, GOAL_CHECK_SYSTEM + GOAL_CHECK_RETRY_SUFFIX):
        try:
            raw = await generate_json(prompt, system=system)
            return GoalCheckResponse.model_validate(raw)
        except (OllamaError, ValidationError):
            continue
    return GoalCheckResponse(is_goal=False)
