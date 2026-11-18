# Deployment

The application has three runtime pieces: PostgreSQL, the FastAPI backend, and the static frontend. Ollama runs natively on the backend machine so it can use the machine's GPU directly.

## Option A — Same machine

Run all services on one computer and let learners access it over a trusted local network.

1. Start PostgreSQL with `docker compose up -d postgres`.
2. Install Ollama natively and pull the model configured by `OLLAMA_MODEL` (default `llama3.1:8b`).
3. Install Python dependencies with `pip install -r requirements.txt`.
4. Start the backend so other devices can reach it:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
5. Serve the frontend:
   ```bash
   python -m http.server 5500 --directory frontend --bind 0.0.0.0
   ```
6. On each learner device, open `http://<backend-machine-ip>:5500` and set **Settings → API connection** to `http://<backend-machine-ip>:8000`.

This is the simplest pilot arrangement. The local GPU and `OLLAMA_MAX_CONCURRENCY` setting determine how much simultaneous model traffic the machine can handle.

## Option B — Split deployment

Run FastAPI, PostgreSQL, and Ollama on one machine and host the static frontend separately.

1. Set up PostgreSQL, Ollama, and FastAPI on the backend machine as above.
2. Serve the `frontend/` directory from your chosen static host.
3. Set **Settings → API connection** in the browser to the backend's reachable URL.
4. Restrict the CORS configuration in `app/main.py` to the actual frontend origin before using this outside a trusted pilot environment.

The frontend stores its API URL in browser `localStorage` (`tutor.apiBase`), so each browser needs this setting once.

## Operations and data

- `GET /health` reports whether Ollama is reachable and whether hosted fallback is enabled.
- PostgreSQL data lives in the `pgdata` Docker volume created by `docker-compose.yml`. Back it up before redeployments or schema changes.
- `.env` and hosted API credentials belong only on the backend machine.
- Hosted fallback is disabled by default. See [HOSTED_FALLBACK_DECISION.md](HOSTED_FALLBACK_DECISION.md) before enabling it.
- Judge0, Redis, and code-execution workers are not part of this deployment.

## Existing pilot database

For databases from the previous app version, review and back up the data before applying `db/migrations/001_remove_legacy_tracks.sql`. The migration is manual and intentionally is not run automatically.
