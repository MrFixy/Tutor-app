# Deployment — Week 13-14 Pilot

Two supported shapes for the pilot. Pick one; don't mix them mid-pilot,
since the frontend's API URL is set once per browser (see below).

## Option A — Same machine

Everything (Postgres, Ollama, Judge0, FastAPI, the static frontend)
runs on one box — a spare desktop with a GPU, most likely — and
learners connect to it over the local network.

1. Follow `README.md` Week 1 setup on that machine (Postgres via
   `docker compose up -d postgres`, Ollama installed natively, `pip
   install -r requirements.txt`).
2. Bring up Judge0 if coding exercises are in scope for this pilot
   (`docker compose -f docker-compose.judge0.yml up -d`, per
   `judge0.conf.example`).
3. Run the backend bound to all interfaces, not just localhost, so
   other machines on the network can reach it:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
4. Serve the frontend the same way described in the README (any
   static file server), also bound to `0.0.0.0`.
5. On each learner's laptop/phone, open the frontend's network URL
   (`http://<host-machine-ip>:5500`), then set **Settings → API
   connection** to `http://<host-machine-ip>:8000` — the default of
   `http://localhost:8000` only works if backend and browser are on the
   same machine.

Simplest to operate — one machine to watch, one Ollama instance so
`OLLAMA_MAX_CONCURRENCY` behaves as documented in `config.py`. The
tradeoff is that machine's GPU is the hard ceiling on how many learners
can be mid-generation at once; see `HOSTED_FALLBACK_DECISION.md` if
that ceiling is a concern for this cohort's size.

## Option B — Split deploy

Backend (FastAPI + Postgres + Ollama + Judge0) on one machine, frontend
served separately (e.g. a lightweight static host, or a different
machine on the same network) — different origins, so CORS matters here
specifically.

1. Backend machine: same as Option A steps 1-3.
2. `main.py` already sets `allow_origins=["*"]` (see the comment above
   the `CORSMiddleware` block), so the browser is not blocked calling
   across origins. That's fine for a closed, no-auth pilot; before
   anything wider, narrow it to the actual frontend origin(s).
3. Frontend: build/serve from wherever is convenient — it only needs
   network access to the backend's port, not to be co-located with it.
4. Same as Option A step 5: whoever opens the frontend sets **Settings
   → API connection** to the backend machine's reachable URL. This is
   stored client-side (`frontend/src/store.js`, `localStorage` key
   `tutor.apiBase`), so it's a one-time per-browser setup, not
   per-session.

Use this shape if the GPU machine isn't reliably reachable from where
learners actually are (e.g. it's on a different subnet than a hosted
static frontend), or if multiple pilot cohorts should share one backend.

## Either way

- `GET /health` reports `ollama_ok` / `judge0_ok` — the same booleans
  the sidebar LEDs poll every 30s. Worth curling directly when
  diagnosing a report of "it's not working," since the sidebar view
  won't distinguish "backend is down" from "backend is up but Ollama
  isn't."
- Postgres data (users, mastery scores, feedback) lives in the
  `pgdata` docker volume on whichever machine runs `docker-compose.yml`
  — back it up before any redeploy that might touch that volume.
- `.env` (`hosted_fallback_enabled`, `hosted_api_key`, etc.) lives on
  the backend machine only; it's never sent to or read by the
  frontend.
