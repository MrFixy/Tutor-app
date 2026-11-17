# Hosted-API Fallback — Should You Turn It On?

`HOSTED_FALLBACK_ENABLED` (default `false`, in `app/config.py`) lets
`app/ollama_client.py` fall through to a hosted API
(`app/hosted_client.py`) when the local Ollama call fails, instead of
just raising an error up to the caller.

## When it triggers

Only on a **failed local call** — a connection error, timeout, or
non-2xx from `http://localhost:11434`. It is not a general "use the
better model" switch and does not run in parallel with or race against
the local call; local is always tried first, hosted is a fallback path,
not an alternative one.

Concretely, that covers:
- Ollama isn't running / crashed
- Ollama is mid-`ollama pull` or mid-model-swap
- The local box is out of VRAM (e.g. something else grabbed the GPU)

It does **not** cover local calls that succeed but return a bad or
low-quality answer — the fallback only fires on outright failure, not
on quality.

## What it costs to turn on

- **An internet dependency the pilot didn't otherwise need.** Both the
  Same-machine and Split deploy shapes in `DEPLOYMENT.md` work fully
  offline/LAN-only until this flag is on.
- **A real API key and a real bill.** `hosted_provider` supports
  `"anthropic"` (Anthropic Messages API) or `"openai_compatible"` (any
  `/chat/completions`-shaped endpoint) — either way, `hosted_api_key`
  must be set or `hosted_client.py` raises immediately rather than
  silently no-op'ing.
- **A quieter failure mode.** Without the flag, a downed Ollama means
  `/chat` etc. return an error the learner (and the sidebar LED) will
  notice right away. With it on, the same outage instead means
  requests quietly get slower and start going to a different model —
  worth deciding whether that's actually what you want mid-pilot, since
  it changes what "the tutor" is answering with, silently, per-request.

## When it's worth it for this pilot

- Cohort size or session overlap is pushing past what
  `ollama_max_concurrency` and a single local GPU can serve without a
  learner-visible queue.
- The pilot machine's Ollama has been flaky (driver issues, thermal
  throttling, etc.) and a stopgap during Week 13-14 is more valuable
  than root-causing it immediately.
- There's a specific reason to want continuity (a live pilot session
  where you'd rather answer from a hosted model than show an error).

## When to leave it off

- Default recommendation for a small, closed pilot: leave it off.
  `local_err` alone is more diagnostic than a mixed local/hosted
  failure message, and it keeps the pilot's cost and infra surface
  (API keys, billing, external dependency) at zero.
- If local failures are rare, turning this on mostly adds an unused
  code path plus a live API key sitting in `.env` — not free from a
  security standpoint even if it never fires.

## If you do turn it on

- Set `hosted_model` deliberately — `config.py`'s current default is a
  small/fast Anthropic model, not necessarily the one you want to
  represent "the tutor" when it's standing in for local generation.
- Watch for the combined error message shape in `ollama_client.py`
  (`"{local_err}; hosted fallback also failed: {hosted_err}"`) in logs
  — seeing that pattern repeatedly means both paths are unhealthy, not
  just one.
- Treat `hosted_api_key` like any other production secret in `.env` —
  it's read only by the backend machine (see `DEPLOYMENT.md`), never
  sent to the frontend.
