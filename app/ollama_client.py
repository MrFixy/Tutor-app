"""
Thin wrapper around Ollama's local HTTP API (http://localhost:11434).

Kept as a small isolated module so that Week 6's swap to llama.cpp/vLLM
(for real prompt-caching support) only requires rewriting this file --
everything upstream (classifier.py, explain.py, quiz.py, code_exercise.py)
talks to generate()/generate_json(), not to Ollama's wire format directly.
That same isolation is what let Phase 6 add connection pooling, a
concurrency cap, and an optional hosted-API fallback here without
touching any caller.
"""
import asyncio
import json
from typing import Optional

import httpx

from app.config import settings


class OllamaError(RuntimeError):
    pass


# Phase 6 / Week 14 (latency tuning): opening a fresh httpx.AsyncClient
# per call paid a new connection setup on every single request under
# pilot load. One shared, connection-pooled client for the app's
# lifetime instead -- created lazily so import order doesn't matter,
# closed from main.py's shutdown handler.
_client: Optional[httpx.AsyncClient] = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=settings.ollama_timeout)
    return _client


async def aclose_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


# Phase 6 / Week 14 (latency tuning): a single local Ollama instance (one
# GPU, one loaded model) doesn't parallelize across requests -- letting
# several pilot learners hit /chat at once just makes every one of their
# generations slower via VRAM/context thrashing. Serialize local calls by
# default; raise OLLAMA_MAX_CONCURRENCY only on hardware that can
# genuinely run more than one generation at a time.
_semaphore = asyncio.Semaphore(max(1, settings.ollama_max_concurrency))


async def ping() -> bool:
    """Used at startup (Phase 0 deliverable: confirm localhost:11434 responds)."""
    try:
        r = await get_client().get(f"{settings.ollama_host}/api/tags", timeout=5)
        r.raise_for_status()
        return True
    except Exception:
        return False


async def generate(
    prompt: str,
    system: Optional[str] = None,
    model: Optional[str] = None,
    json_mode: bool = False,
    temperature: float = 0.3,
) -> str:
    """
    Calls Ollama's /api/generate with stream=False and returns the raw
    text response. If json_mode=True, sets format="json" so Ollama
    constrains the model to emit valid JSON (caller still validates it).

    Phase 6 (Week 14): if the local call fails and HOSTED_FALLBACK_ENABLED
    is set, falls back to app.hosted_client instead of raising -- see
    HOSTED_FALLBACK_DECISION.md.
    """
    payload = {
        "model": model or settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system
    if json_mode:
        payload["format"] = "json"

    local_err: Optional[OllamaError] = None
    try:
        async with _semaphore:
            r = await get_client().post(f"{settings.ollama_host}/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()
        return data.get("response", "")
    except httpx.HTTPError as e:
        local_err = OllamaError(f"Ollama request failed: {e}")

    if settings.hosted_fallback_enabled:
        from app import hosted_client  # lazy: no hard dependency when unused

        try:
            return await hosted_client.generate(prompt, system=system, json_mode=json_mode, temperature=temperature)
        except hosted_client.HostedError as hosted_err:
            raise OllamaError(f"{local_err}; hosted fallback also failed: {hosted_err}") from hosted_err

    raise local_err


async def generate_json(prompt: str, system: Optional[str] = None, model: Optional[str] = None) -> dict:
    """Calls generate() in json_mode and parses the result. Raises OllamaError on bad JSON."""
    raw = await generate(prompt, system=system, model=model, json_mode=True, temperature=0.0)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise OllamaError(f"Model did not return valid JSON: {raw!r}") from e
