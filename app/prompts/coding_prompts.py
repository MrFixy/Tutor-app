"""
Phase 2 / Week 5 - coding explanation engine content.
Mirrors stats_prompts.py's structure so explain.py can dispatch generically.
"""

CODING_TOPIC_SYSTEM = {
    "syntax_basics": """Topic: basic language syntax (variables, types, printing, operators).
Use short, runnable snippets. Point out common beginner typos/pitfalls for the construct asked about.""",

    "data_structures": """Topic: data structures (lists, dicts, sets, arrays, etc).
Explain what problem the structure solves (what operation is it fast/slow at) before syntax.
Use a small runnable example showing creation, access, and one mutation.""",

    "control_flow": """Topic: control flow (if/else, loops, switch/match).
Trace through execution step-by-step with a tiny example so the learner can see the flow, not just read it.""",

    "functions": """Topic: functions (definition, parameters, return values, scope).
Explain functions as reusable "black boxes": inputs in, output out. Show one example with a
default/optional argument since that trips up beginners.""",

    "recursion": """Topic: recursion.
Always show the base case explicitly and trace at least 3 levels of the call stack in words
or a small diagram-like list, since recursion is the topic learners struggle with most.""",

    "algorithms": """Topic: algorithms (sorting, searching, complexity/Big-O).
Give the intuition first (e.g. "binary search is like guessing a number by halving the range"),
then mention time complexity in plain terms, not just notation.""",

    "debugging": """Topic: debugging a specific error or unexpected behavior.
Walk through how to read the error message / trace the bug systematically, don't just hand over
a fixed version -- teach the diagnostic process.""",

    "oop": """Topic: object-oriented programming (classes, objects, inheritance, methods).
Use a relatable real-world analogy (e.g. class = blueprint, object = house built from it) before code.""",

    "other_coding": """Topic: general coding question that doesn't fit a specific subtopic.
Answer helpfully and, if it's really about a more specific concept, name that concept explicitly.""",
}

FEW_SHOT_EXAMPLES = {
    "recursion": [
        {
            "q": "I don't understand how recursion actually works, can you explain factorial?",
            "a": (
                "Recursion = a function that calls itself, with a 'base case' that stops it.\n\n"
                "```python\n"
                "def factorial(n):\n"
                "    if n == 0:          # base case: stops the recursion\n"
                "        return 1\n"
                "    return n * factorial(n - 1)\n"
                "```\n\n"
                "Trace for factorial(3):\n"
                "  factorial(3) = 3 * factorial(2)\n"
                "  factorial(2) = 2 * factorial(1)\n"
                "  factorial(1) = 1 * factorial(0)\n"
                "  factorial(0) = 1   <- base case hit, stack starts unwinding\n"
                "So factorial(3) = 3 * 2 * 1 * 1 = 6.\n\n"
                "Every recursive function needs: (1) a base case that returns without recursing, "
                "and (2) a step that moves toward that base case.\n\n"
                "Check yourself: what happens if you forget the base case?"
            ),
        }
    ],
    "data_structures": [
        {
            "q": "When should I use a dict instead of a list?",
            "a": (
                "Lists are ordered collections you look up by position (index). Dicts are "
                "key-value pairs you look up by a meaningful key.\n\n"
                "```python\n"
                "scores_list = [90, 85, 77]        # need to remember index 0 = who?\n"
                "scores_dict = {\"alice\": 90, \"bob\": 85, \"cara\": 77}  # lookup by name, O(1)\n"
                "print(scores_dict[\"bob\"])  # 85\n"
                "```\n\n"
                "Rule of thumb: if you find yourself thinking 'I need to look this up by name/id', "
                "reach for a dict. If order and position matter, use a list.\n\n"
                "Check yourself: which would you use to store a student's grades in the order the "
                "tests were taken?"
            ),
        }
    ],
}
