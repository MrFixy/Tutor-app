"""
Redesign - prompts for the goal-statement detour in /chat.

Two small, cheap LLM calls:
  1. GOAL_CHECK_PROMPT: is this message a goal statement ("I want to
     learn/build/make X") vs. an ordinary question? Same
     format=json + validate + one-retry pattern as classifier.py.
  2. GOAL_TOPIC_PROMPT: given a goal statement, return an ordered
     roadmap of topics, constrained to the same closed subtopic
     vocabulary classifier.py already validates against -- so a saved
     plan's items always resolve to a real LessonContent row.
"""

GOAL_CHECK_SYSTEM = """You classify whether a learner's chat message is a GOAL STATEMENT
(they're announcing something they want to learn, build, or achieve --
e.g. "I want to learn statistics for data science", "I want to build a
web scraper", "help me get good at coding interviews") versus an
ORDINARY QUESTION about a specific concept (e.g. "what's a p-value?",
"why is my loop infinite?").

Respond with ONLY a JSON object, no prose, no markdown fences, matching exactly:
{"is_goal": true | false}

If in doubt -- the message is a specific question, even a broad one, not a
stated goal/intent to learn something over time -- answer false.
"""

GOAL_CHECK_RETRY_SUFFIX = """

Your previous response was not valid. It must be a single JSON object
with exactly the key is_goal, a boolean. Try again, JSON only.
"""


def build_goal_topic_system(stats_subtopics: list[str], coding_subtopics: list[str], languages: list[str]) -> str:
    return f"""You turn a learner's stated goal into an ordered study roadmap, drawn
strictly from this app's existing lesson topics -- never invent a topic
outside these lists.

Valid stats subtopics: {sorted(stats_subtopics)}
Valid coding subtopics: {sorted(coding_subtopics)}
Valid coding languages: {sorted(languages)}

Respond with ONLY a JSON object, no prose, no markdown fences, matching exactly:
{{"topics": [
  {{"domain": "stats" | "coding", "subtopic": "<one of the valid subtopics for that domain>", "language": "<one of the valid languages, or null if domain is stats>"}}
  ... (3-8 items, ordered from foundational to advanced)
]}}

Rules:
- Only include topics that are actually relevant to the learner's goal.
- Order topics the way a learner should study them (prerequisites first).
- For domain="coding" items, language must be one of the valid languages above, never null.
- For domain="stats" items, language must be null.
- 3 to 8 topics total -- enough to form a real roadmap, not just one item.
"""


GOAL_TOPIC_RETRY_SUFFIX = """

Your previous response was not valid JSON matching the required schema
(top-level object with a "topics" array of 3-8 items, each with
domain/subtopic/language drawn only from the valid lists given). Try
again, JSON only.
"""
