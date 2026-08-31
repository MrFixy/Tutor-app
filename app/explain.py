"""
Phase 2 - explanation engine.

classify_question() (Phase 1) tells us domain+subtopic; this module builds
the cached system prompt for that (domain, subtopic) and asks Ollama for
an explanation. difficulty is passed through as a lightweight steer for
now -- Phase 4 (Week 10) will feed a real difficulty value here based on
mastery_score history.
"""
from app.ollama_client import generate, OllamaError
from app.prompts.cache import get_system_prompt

DIFFICULTY_HINT = {
    "beginner": "The learner is a beginner. Avoid jargon; define any term you must use.",
    "intermediate": "The learner has some background. You can use standard terminology without over-explaining basics.",
    "advanced": "The learner is advanced. Be concise, go deeper into edge cases and nuance.",
}


async def explain(domain: str, subtopic: str, question: str, difficulty: str = "beginner") -> str:
    system_prompt = get_system_prompt(domain, subtopic)
    hint = DIFFICULTY_HINT.get(difficulty, DIFFICULTY_HINT["beginner"])
    full_system = f"{system_prompt}\n\n{hint}"

    try:
        return await generate(question, system=full_system, temperature=0.4)
    except OllamaError as e:
        return f"Sorry, I couldn't generate an explanation right now ({e})."
