# AI Engineering Tutor

A focused AI Engineering learning workspace. It combines a curated, self-paced curriculum with an AI tutor that explains AI/ML concepts and creates goal-based roadmaps from the curriculum.

The project is intentionally focused on **AI Engineering**. Python, probability, statistics, linear algebra, and calculus remain part of the curriculum where they support machine learning and AI systems. They are not separate learning tracks.

## What the app does

- **AI Tutor:** Ask questions about machine learning, deep learning, computer vision, NLP, speech, transformers, generative AI, reinforcement learning, LLMs, agents, multimodal systems, production infrastructure, evaluation, safety, and related foundations.
- **AI Engineering Guides:** Browse the curated curriculum across six volumes and twenty phases. Lesson content is served from Markdown files.
- **Goal-based roadmaps:** Describe an AI Engineering learning or project goal. The tutor selects three to eight relevant phases from the existing curriculum; you can save the roadmap under My Plans.
- **Learner workspace:** Use a local username to keep a stable pilot user ID, chat session, saved plans, and feedback.
- **Optional hosted fallback:** When configured, a hosted model can be used only when the local Ollama request fails. It is disabled by default.

### Explicitly out of scope

- Standalone general Coding and Statistics learning tracks.
- In-browser code execution, Judge0, code submissions, automated code grading, and coding mastery scores.
- The old Statistics quiz and Coding exercise practice loop.

The tutor can explain Python snippets and AI-related mathematics, but it does not execute submitted code.

## Architecture

```text
Browser
  └── Static frontend (frontend/)
        ├── Dashboard
        ├── AI Tutor chat
        ├── Guides (curriculum JSON + Markdown)
        └── My Plans
              │
              ▼
        FastAPI backend (app/main.py)
          ├── AI tutor prompt (app/explain.py)
          ├── Goal detection (app/classifier.py)
          ├── AI phase roadmap generation (app/study_plan.py)
          ├── Ollama client (+ optional hosted fallback)
          └── SQLAlchemy persistence
                └── PostgreSQL
```

The frontend is a static ES-module application. It uses Preact utilities from `esm.sh`; there is no frontend build step or `package.json` script.

## Repository layout

```text
app/
  classifier.py              # detects AI Engineering learning goals
  config.py                  # environment-based settings
  content_loader.py          # indexes curated AI Engineering lessons
  db.py                      # SQLAlchemy engine and session dependency
  explain.py                 # AI Engineering tutor prompt and generation
  hosted_client.py           # optional provider fallback
  main.py                    # FastAPI routes and lifecycle
  models.py                  # users, sessions, chat, lesson, plan, feedback data
  ollama_client.py           # local Ollama HTTP client
  schemas.py                 # API request/response models
  study_plan.py              # phase-based roadmap generation and persistence
  user_service.py            # pilot user/session creation
  prompts/goal_prompts.py    # goal detection and roadmap prompts
content/lessons/phases/      # curated AI Engineering Markdown lessons
frontend/
  content/curriculum.json    # phase/lesson navigation manifest
  content/phases/            # browser-served Markdown lesson files
  src/                       # static frontend application
scripts/import_ai_eng_curriculum.py
  # refreshes the curated curriculum from its upstream repository
db/schema.sql                # current PostgreSQL schema
db/migrations/               # optional cleanup for older pilot databases
tests/                       # backend tests
```

## Requirements

- Python 3.10 or newer
- PostgreSQL 14 or newer
- Ollama installed on the backend machine
- A model available in Ollama (the default is `llama3.1:8b`)

Judge0, Redis, and a separate code-execution service are not required.

## Local setup

### 1. Start PostgreSQL

The repository's Compose file starts PostgreSQL:

```bash
docker compose up -d postgres
```

The default database URL is:

```text
postgresql+psycopg2://tutor:tutor@localhost:5432/tutor_db
```

Override it with `DATABASE_URL` when your database uses different credentials or a different host.

### 2. Start Ollama

Install Ollama natively on the backend machine, then pull the configured model:

```bash
ollama pull llama3.1:8b
```

The backend checks Ollama at `http://localhost:11434` by default. Set `OLLAMA_HOST` and `OLLAMA_MODEL` to change these values.

### 3. Install Python dependencies

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Start the API

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

On startup, the API creates missing tables and indexes the Markdown lessons from `content/lessons/phases/` into `lesson_content`.

Check the API:

```bash
curl http://localhost:8000/health
```

### 5. Serve the frontend

In a second terminal, from the repository root:

```bash
python -m http.server 5500 --directory frontend
```

Open <http://localhost:5500>. The frontend's default API URL is `http://localhost:8000`. For a split deployment, use **Settings → API connection** to enter the backend URL.

## Configuration

All settings are environment variables. A `.env` file in the repository root is also read.

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg2://tutor:tutor@localhost:5432/tutor_db` | PostgreSQL connection string |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1:8b` | Local model name |
| `OLLAMA_TIMEOUT` | `120` | Model request timeout in seconds |
| `OLLAMA_MAX_CONCURRENCY` | `1` | Maximum concurrent local generations |
| `HOSTED_FALLBACK_ENABLED` | `false` | Enable hosted fallback after local Ollama failure |
| `HOSTED_PROVIDER` | `anthropic` | `anthropic` or `openai_compatible` |
| `HOSTED_API_KEY` | empty | Hosted provider key; required only when fallback is enabled |
| `HOSTED_API_BASE` | `https://api.anthropic.com` | Hosted API base URL |
| `HOSTED_MODEL` | `claude-3-5-haiku-20241022` | Hosted model name |
| `HOSTED_TIMEOUT` | `60` | Hosted request timeout in seconds |

See [HOSTED_FALLBACK_DECISION.md](HOSTED_FALLBACK_DECISION.md) before enabling hosted fallback. API keys belong only on the backend.

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Ollama and hosted-fallback status |
| `POST` | `/chat` | AI tutor response or goal-based roadmap |
| `POST` | `/explain` | Direct AI Engineering explanation |
| `GET` | `/lessons/phases` | AI Engineering phase catalogue |
| `GET` | `/lessons/phases/{phase_slug}/{lesson_slug}` | Retrieve one indexed lesson |
| `POST` | `/goal/check` | Check whether a message expresses an AI Engineering goal |
| `POST` | `/goal/topics` | Generate a phase-based AI Engineering roadmap |
| `POST` | `/plans` | Save a roadmap for a user |
| `GET` | `/plans/{user_id}` | List that user's saved roadmaps |
| `POST` | `/feedback` | Submit in-app feedback |
| `GET` | `/feedback` | List pilot feedback |

Interactive API documentation is available at <http://localhost:8000/docs> while the backend is running.

## Curriculum content

The Guides tab uses the checked-in curriculum bundle:

- `frontend/content/curriculum.json` defines phase and lesson navigation.
- `frontend/content/phases/` contains the Markdown files served to the browser.
- `content/lessons/phases/` contains the backend copy used for indexing and API lesson retrieval.

Refresh the content from the upstream [AI Engineering from Scratch](https://github.com/rohitg00/ai-engineering-from-scratch) repository with:

```bash
python scripts/import_ai_eng_curriculum.py
```

Or use an existing source checkout:

```bash
python scripts/import_ai_eng_curriculum.py --source-dir /path/to/ai-engineering-from-scratch
```

The curriculum importer preserves the upstream MIT attribution and imports lesson documentation only. See [docs/curriculum-import.md](docs/curriculum-import.md).

## Tests

Run the backend test suite from the repository root:

```bash
DATABASE_URL=sqlite:///:memory: pytest -q
```

The tests cover user/session creation, phase lesson indexing, and AI Engineering roadmap validation and persistence. They use SQLite and do not require a live PostgreSQL or Ollama service.

## Existing database migration

If you are upgrading a database created by the previous Stats/Coding Tutor version, back it up first. Then review and run the optional cleanup script:

```bash
psql "$DATABASE_URL" -f db/migrations/001_remove_legacy_tracks.sql
```

This removes the old exercise and mastery tables, standalone track lesson rows, obsolete plan entries, and old classification columns while retaining ordinary chat history. The migration is not run automatically by the application.

Fresh databases can be created from the current `db/schema.sql` or by SQLAlchemy's startup `create_all()` call.

## Pilot limitations and security

- This is still a pilot, not a production multi-user service. Login is a username-based convenience layer, not authentication.
- CORS currently allows all origins. Restrict it before exposing the API beyond a trusted local network.
- The feedback listing endpoint has no authentication; do not expose it publicly.
- The lesson files and browser curriculum are checked-in static content. The app does not perform semantic retrieval across all lesson text when answering chat questions; the tutor uses its AI Engineering system prompt and the learner's message.
- The application explains Python and AI-related code but does not run it.
