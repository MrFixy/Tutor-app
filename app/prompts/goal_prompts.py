GOAL_CHECK_SYSTEM = """Classify whether the learner's message expresses a learning or building goal
within AI Engineering (for example, learning machine learning, building an RAG
application, understanding transformers, or becoming an AI engineer).

Return only JSON matching exactly: {"is_goal": true} or {"is_goal": false}.
A specific question about a concept is not a goal statement. If the request is
unrelated to AI Engineering, return false."""

GOAL_CHECK_RETRY_SUFFIX = """
Return one valid JSON object only, with exactly one boolean key: is_goal."""


def build_goal_topic_system(phases: list[dict]) -> str:
    phase_lines = "\n".join(
        f'- {phase["slug"]}: {phase["title"]}' for phase in phases
    )
    return f"""You create focused AI Engineering study roadmaps for a learner.

Choose 3 to 8 phases from the existing curriculum below. Do not invent or
rename phases. Choose only phases relevant to the learner's goal and order
them from prerequisites to advanced material. Keep foundational phases when
they are genuinely needed, but do not include the entire curriculum by default.

Available phases:
{phase_lines}

Return only JSON in this exact shape:
{{"topics": [{{"phase_slug": "one-exact-slug-from-the-list"}}]}}
The topics array must contain between 3 and 8 unique phases."""

GOAL_TOPIC_RETRY_SUFFIX = """
Your previous response was invalid. Return only a JSON object with a topics
array containing 3 to 8 unique objects. Each object must contain only
phase_slug, and every slug must exactly match one of the available phases."""
