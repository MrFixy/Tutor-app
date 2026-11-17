"""
Phase 6 / Week 14 — optional hosted-API fallback.

See HOSTED_FALLBACK_DECISION.md for whether/why to turn this on. Off by
default (`HOSTED_FALLBACK_ENABLED=false`); ollama_client.generate() only
imports and calls into this module when the local Ollama call fails *and*
the flag is on. Keeping it a separate, lazily-imported module means a
pilot machine that never enables this has zero new dependency on an
internet connection or an API key.

Supports two wire formats so the pilot can point this at whatever's
available:
- "anthropic": Anthropic Messages API
- "openai_compatible": any /chat/completions-shaped endpoint (OpenAI
  itself, or another hosted OpenAI-compatible gateway)
"""
from typing import Optional

import httpx

from app.config import settings


class HostedError(RuntimeError):
    pass


def _require_key() -> None:
    if not settings.hosted_api_key:
        raise HostedError("HOSTED_FALLBACK_ENABLED is true but HOSTED_API_KEY is not set")


async def generate(
    prompt: str,
    system: Optional[str] = None,
    json_mode: bool = False,
    temperature: float = 0.3,
) -> str:
    _require_key()
    if settings.hosted_provider == "anthropic":
        return await _generate_anthropic(prompt, system, json_mode, temperature)
    if settings.hosted_provider == "openai_compatible":
        return await _generate_openai_compatible(prompt, system, json_mode, temperature)
    raise HostedError(f"Unknown HOSTED_PROVIDER: {settings.hosted_provider!r}")


async def _generate_anthropic(prompt: str, system: Optional[str], json_mode: bool, temperature: float) -> str:
    headers = {
        "x-api-key": settings.hosted_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    effective_system = system or ""
    if json_mode:
        effective_system = (effective_system + "\n\n" if effective_system else "") + (
            "Respond with ONLY valid JSON. No prose, no markdown code fences, no commentary."
        )
    body = {
        "model": settings.hosted_model,
        "max_tokens": 1024,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if effective_system:
        body["system"] = effective_system

    try:
        async with httpx.AsyncClient(timeout=settings.hosted_timeout) as client:
            r = await client.post(f"{settings.hosted_api_base}/v1/messages", headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPError as e:
        raise HostedError(f"Hosted API (anthropic) request failed: {e}") from e

    return "".join(part.get("text", "") for part in data.get("content", []) if part.get("type") == "text")


async def _generate_openai_compatible(
    prompt: str, system: Optional[str], json_mode: bool, temperature: float
) -> str:
    headers = {"Authorization": f"Bearer {settings.hosted_api_key}", "content-type": "application/json"}
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = {"model": settings.hosted_model, "messages": messages, "temperature": temperature}
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    try:
        async with httpx.AsyncClient(timeout=settings.hosted_timeout) as client:
            r = await client.post(f"{settings.hosted_api_base}/chat/completions", headers=headers, json=body)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPError as e:
        raise HostedError(f"Hosted API (openai_compatible) request failed: {e}") from e

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise HostedError(f"Unexpected hosted API response shape: {data!r}") from e
