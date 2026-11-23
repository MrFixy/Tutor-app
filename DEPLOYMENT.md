# Deployment

AI Engineering Tutor has four runtime pieces:

| Piece | What it is | Where it runs |
|---|---|---|
| PostgreSQL | Users, sessions, chats, saved plans, feedback, indexed lessons | Docker (via Compose) or any PostgreSQL 14+ |
| Ollama | Local model that powers the tutor | Natively on the backend machine, so it can use the GPU directly |
| FastAPI backend | The API (`app.main:app`) | Backend machine |
| Static frontend | The `frontend/` folder | Backend machine or any static host |

There is **no code-execution service** to deploy. The tutor explains code but never runs it.

## Before you start

- Python 3.10+, and Docker if you want Compose to run PostgreSQL.
- Ollama installed with the model pulled: `ollama pull llama3.1:8b` (or whatever you set in `OLLAMA_MODEL`).
- Enough GPU/VRAM for that model. The default settings serve **one generation at a time**.

## Configuration

Create a `.env` file in the repository root on the backend machine. Everything has a default, so only set what you need to change.

```env
DATABASE_URL=postgresql+psycopg2://tutor:CHANGE_ME@localhost:5432/tutor_db
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TIMEOUT=120
OLLAMA_MAX_CONCURRENCY=1

# Optional hosted fallback, off by default
HOSTED_FALLBACK_ENABLED=false
```

If you change the database password in `.env`, change it in `docker-compose.yml` too (`POSTGRES_PASSWORD`). The Compose file ships with `tutor` / `tutor`, which is fine on a laptop and not fine on a shared network.

`.env` stays on the backend machine and is already in `.gitignore`.

## Option A: Single machine (simplest pilot)

Run everything on one computer and let learners connect over a trusted local network.

```bash
# 1. Database
docker compose up -d postgres

# 2. Backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. Frontend (second terminal)
python -m http.server 5500 --directory frontend --bind 0.0.0.0
```

On each learner's device:

1. Open `http://<machine-ip>:5500`.
2. Go to **Settings → API connection** and enter `http://<machine-ip>:8000`.

Make sure ports `5500` and `8000` are allowed through the machine's firewall. Do **not** open `5432` (PostgreSQL) or `11434` (Ollama) to the network; only the backend needs them.

## Option B: Split deployment

Keep PostgreSQL, Ollama and FastAPI together on the backend machine, and host the static frontend somewhere else (Nginx, Netlify, GitHub Pages, S3 + CDN, and so on).

1. Set up the backend machine as in Option A, steps 1 and 2.
2. Upload the contents of `frontend/` to your static host. It needs no build step. Keep the `content/` folder alongside `index.html` and `src/`, since the browser loads lessons from it.
3. Edit CORS in `app/main.py` so it allows only your frontend's origin:
   ```python
   allow_origins=["https://tutor.example.com"],
   ```
4. Put the API behind HTTPS. If the frontend is served over HTTPS, the API must be too, or browsers will block the requests as mixed content.
5. In each browser, set **Settings → API connection** to the backend's public URL.

The API URL is stored in the browser's `localStorage` (`tutor.apiBase`), so each browser needs this set once.

## Keeping the backend running

For anything longer than a quick demo, run uvicorn as a service rather than in a terminal. A minimal systemd unit (`/etc/systemd/system/tutor-api.service`):

```ini
[Unit]
Description=AI Engineering Tutor API
After=network.target docker.service

[Service]
WorkingDirectory=/opt/tutor
ExecStart=/opt/tutor/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
User=tutor

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tutor-api
```

Binding to `127.0.0.1` assumes a reverse proxy (Nginx or Caddy) sits in front and handles HTTPS. Use `0.0.0.0` only on a trusted network without one.

## First start and health check

On startup the backend:

1. Checks whether Ollama is reachable.
2. Creates any missing database tables.
3. Indexes every lesson in `content/lessons/phases/` into PostgreSQL (currently 523 lessons across 20 phases).

Watch the logs for lines like:

```text
[startup] Ollama reachable: True
[startup] Loaded 523 AI Engineering lesson(s)
```

Then verify:

```bash
curl http://<backend>:8000/health
# {"ollama_ok": true, "hosted_fallback_enabled": false}
```

`ollama_ok: false` means the backend cannot reach Ollama at `OLLAMA_HOST`. The app will still load and Guides will still work, but tutor replies will return an error message. Note that this value is checked once at startup, so restart the backend after fixing Ollama.

## Data and backups

- PostgreSQL data lives in the `pgdata` Docker volume.
- `db/schema.sql` is only applied automatically when the volume is **first created**. The backend's startup `create_all()` covers missing tables after that.
- Back up before upgrades or schema changes:
  ```bash
  docker exec tutor_postgres pg_dump -U tutor tutor_db > backup_$(date +%F).sql
  ```
- Restore:
  ```bash
  docker exec -i tutor_postgres psql -U tutor tutor_db < backup_2026-01-01.sql
  ```
- Lessons are re-indexed from disk on every start, so they are safe to lose from the database. Users, chats, plans and feedback are the data worth backing up.

## Updating

```bash
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart tutor-api      # or restart your uvicorn process
```

If you refreshed the curriculum (`python scripts/import_ai_eng_curriculum.py`), copy the updated `frontend/` to your static host too, otherwise the browser and backend will show different lessons.

## Hosted fallback (optional)

Off by default. With `HOSTED_FALLBACK_ENABLED=true`, a hosted model is used only when the local Ollama request fails, never in parallel with it. Enabling it adds an internet dependency, an API key to protect and a usage bill, and it makes Ollama outages less visible. Read [HOSTED_FALLBACK_DECISION.md](HOSTED_FALLBACK_DECISION.md) first. To enable it, set `HOSTED_FALLBACK_ENABLED`, `HOSTED_API_KEY` and, if needed, `HOSTED_PROVIDER`, `HOSTED_API_BASE` and `HOSTED_MODEL` in the backend's `.env`.

## Security checklist before wider use

- [ ] Change the default PostgreSQL password and keep port `5432` closed to the network.
- [ ] Restrict CORS in `app/main.py` to your real frontend origin.
- [ ] Serve the API over HTTPS.
- [ ] Block or protect `GET /feedback`, which has no authentication.
- [ ] Remember that login is only a username, not authentication. Anyone who types a username gets that user's plans.
- [ ] Keep `.env` and any hosted API key on the backend only.

## Upgrading an older pilot database

For databases from the earlier Stats/Coding Tutor, back up first, then review and run `db/migrations/001_remove_legacy_tracks.sql` manually. It is intentionally not run by the app.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| "Couldn't reach the API" in the browser | Wrong URL in **Settings → API connection**, backend not running, firewall, or an HTTPS/HTTP mismatch |
| Browser console shows a CORS error | Frontend origin is not allowed in `app/main.py` |
| Tutor replies "couldn't generate an explanation" | Ollama is down, or the model is not pulled. Run `ollama list`, then restart the backend |
| `/health` reports `ollama_ok: false` after fixing Ollama | Status is checked at startup. Restart the backend |
| Slow replies with several learners | Local model handles one request at a time. Use a smaller model, better GPU, or enable hosted fallback |
| Guides show no lessons | `frontend/content/` was not uploaded alongside `index.html`, or the page is not served over HTTP (opening `index.html` as a file will not work) |
| `connection refused` on port 5432 | PostgreSQL container is not running. `docker compose up -d postgres` |
