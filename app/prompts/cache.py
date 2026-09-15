"""
Phase 2 / Week 6 - prompt caching for fixed system prompts.

Ollama (as of this writing) does not expose a public prefix/prompt-caching
API the way llama.cpp (--prompt-cache) or vLLM (automatic prefix caching)
do. What we CAN cheaply do today, and what actually matters for latency
here, is:

  1. Never re-render the same system prompt string from scratch per request
     -- build each topic's full system prompt ONCE at process startup and
     reuse the string object (`get_system_prompt` below memoizes this).
  2. Keep the fixed (system + few-shot) portion and the variable (learner
     question) portion as separate strings, so that IF we move to
     llama.cpp/vLLM, the fixed portion maps directly onto their prefix-cache
     key and only the question needs to be appended per-request.

If/when this project switches inference servers (Week 6 note in the plan):
  - llama.cpp server: start with `--prompt-cache <file>` and send the fixed
    system+few-shot block as the leading, byte-identical prefix every call.
  - vLLM: enable `--enable-prefix-caching`; again keep the fixed prefix
    byte-identical across calls so the KV cache hits.

This module is intentionally the ONLY place that knows the caching
strategy, so swapping backends later means editing here + ollama_client.py,
not the classifier/explain call sites.
"""
from functools import lru_cache

from app.prompts.stats_prompts import (
    BASE_SYSTEM as STATS_BASE_SYSTEM,
    STATS_TOPIC_SYSTEM,
    FEW_SHOT_EXAMPLES as STATS_FEW_SHOT,
)
from app.prompts.coding_prompts import (
    CODING_TOPIC_SYSTEM,
    FEW_SHOT_EXAMPLES as CODING_FEW_SHOT,
)

# Coding topics share the same base persona as stats for consistency.
CODING_BASE_SYSTEM = STATS_BASE_SYSTEM


def _render_few_shot(domain: str, subtopic: str) -> str:
    bank = STATS_FEW_SHOT if domain == "stats" else CODING_FEW_SHOT
    examples = bank.get(subtopic, [])
    if not examples:
        return ""
    blocks = []
    for ex in examples:
        blocks.append(f"Example question: {ex['q']}\nExample answer:\n{ex['a']}")
    return "\n\n---\n\n".join(blocks)


@lru_cache(maxsize=64)
def get_system_prompt(domain: str, subtopic: str) -> str:
    """
    Builds (once, then memoizes) the full fixed system prompt for a given
    domain+subtopic: base persona + topic-specific instructions + few-shot
    examples. This is the string that should stay byte-identical across
    requests so a real prompt cache (llama.cpp/vLLM) can hit on it.
    """
    if domain == "stats":
        base = STATS_BASE_SYSTEM
        topic_instructions = STATS_TOPIC_SYSTEM.get(subtopic, STATS_TOPIC_SYSTEM["other_stats"])
    else:
        base = CODING_BASE_SYSTEM
        topic_instructions = CODING_TOPIC_SYSTEM.get(subtopic, CODING_TOPIC_SYSTEM["other_coding"])

    few_shot = _render_few_shot(domain, subtopic)
    parts = [base.strip(), topic_instructions.strip()]
    if few_shot:
        parts.append("Here are examples of the tone and format to match:\n\n" + few_shot)

    return "\n\n".join(parts)


def cache_info():
    """Expose lru_cache stats, useful for confirming the cache is actually hit in Week 6 tuning."""
    return get_system_prompt.cache_info()
