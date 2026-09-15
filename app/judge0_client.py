"""
Thin wrapper around a self-hosted Judge0 instance (see
docker-compose.judge0.yml). Kept isolated the same way ollama_client.py is,
so code_checker.py doesn't need to know Judge0's wire format.

Uses the synchronous submission endpoint (wait=true) rather than the
submit-then-poll flow: exercise scripts here are tiny and short-running,
and wait=true keeps code_checker.py simple. If exercises grow to need
longer sandboxed runtime, switch to submit + poll /submissions/{token}.
"""
from typing import Optional

import httpx

from app.config import settings


class Judge0Error(RuntimeError):
    pass


# Phase 6 / Week 14 (latency tuning): same fix as ollama_client.py -- reuse
# one pooled client instead of opening a fresh connection per submission.
_client: Optional[httpx.AsyncClient] = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=settings.judge0_timeout)
    return _client


async def aclose_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


# Judge0 status.id groups: 1-2 = queued/processing (shouldn't happen with
# wait=true), 3 = Accepted, 4 = Wrong Answer, 5 = Time Limit Exceeded,
# 6 = Compilation Error, 7-12 = various runtime errors, 13 = Internal
# Error, 14 = Exec Format Error. We only special-case "Accepted" vs not.
ACCEPTED_STATUS_ID = 3


async def ping() -> bool:
    """Confirm the self-hosted Judge0 instance is reachable."""
    try:
        r = await get_client().get(f"{settings.judge0_url}/languages", timeout=5)
        r.raise_for_status()
        return True
    except Exception:
        return False


async def run_submission(
    source_code: str,
    stdin: str = "",
    expected_output: Optional[str] = None,
    language_id: Optional[int] = None,
) -> dict:
    """
    Submits source_code to Judge0 and waits for the result (wait=true).
    If expected_output is given, Judge0 does the stdout comparison itself
    and reports status "Accepted" / "Wrong Answer" accordingly; we also
    return raw stdout so the caller can show a diff.
    """
    payload = {
        "source_code": source_code,
        "language_id": language_id or settings.judge0_python_language_id,
        "stdin": stdin,
    }
    if expected_output is not None:
        payload["expected_output"] = expected_output

    params = {"base64_encoded": "false", "wait": "true"}

    try:
        r = await get_client().post(
            f"{settings.judge0_url}/submissions",
            params=params,
            json=payload,
        )
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as e:
        raise Judge0Error(f"Judge0 request failed: {e}") from e
