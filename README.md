# AI Engineering Tutor

A self-paced **AI & ML engineering course with a built-in AI tutor**. Learners work through a curated curriculum of **20 phases and 523 lessons**, ask the tutor questions as they go, and can describe a goal to get a personalised roadmap of phases to follow.

The tutor runs on a local model through [Ollama](https://ollama.com), so a pilot can run entirely on your own hardware with no external services.

## What we teach

The curriculum takes a learner from setting up their tools all the way to building and shipping AI systems. It is organised into **6 volumes**, covering **20 phases** and **523 lessons**.

| Volume | Phases | Lessons | Covers |
|---|---|---|---|
| 1. Foundations | 00–02 | 52 | Setup & tooling, math foundations, classical machine learning |
| 2. Deep Learning | 03, 04, 06 | 58 | Neural networks, computer vision, speech & audio |
| 3. Language | 05, 07 | 45 | NLP foundations to advanced, transformers deep dive |
| 4. Large Language Models | 08–11 | 68 | Generative AI, reinforcement learning, LLMs from scratch, LLM engineering |
| 5. Agents | 12–16 | 157 | Multimodal AI, tools & protocols, agent engineering, autonomous systems, multi-agent & swarms |
| 6. Production | 17–19 | 143 | Infrastructure & production, ethics/safety/alignment, capstone projects |

<details>
<summary>All 20 phases</summary>

| # | Phase | Lessons |
|---|---|---|
| 00 | Setup and Tooling | 12 |
| 01 | Math Foundations | 22 |
| 02 | ML Fundamentals | 18 |
| 03 | Deep Learning Core | 13 |
| 04 | Computer Vision | 28 |
| 05 | NLP: Foundations to Advanced | 29 |
| 06 | Speech and Audio | 17 |
| 07 | Transformers Deep Dive | 16 |
| 08 | Generative AI | 15 |
| 09 | Reinforcement Learning | 12 |
| 10 | LLMs from Scratch | 24 |
| 11 | LLM Engineering | 17 |
| 12 | Multimodal AI | 25 |
| 13 | Tools and Protocols | 31 |
| 14 | Agent Engineering | 54 |
| 15 | Autonomous Systems | 22 |
| 16 | Multi-Agent and Swarms | 25 |
| 17 | Infrastructure and Production | 28 |
| 18 | Ethics, Safety and Alignment | 30 |
| 19 | Capstone Projects | 85 |

</details>

Python, probability, statistics, linear algebra and calculus are taught **inside** this curriculum where AI/ML needs them. They are not separate tracks.

## Features

- **AI Tutor chat.** Ask about anything in the curriculum. The tutor explains concepts from intuition up to technical detail, with equations and short Python snippets where they help.
- **Guides.** Browse the full curriculum by volume, then phase, then lesson. Lessons are Markdown files served directly to the browser.
- **Goal-based roadmaps.** Tell the tutor what you want to learn or build. It picks 3–8 relevant phases in a sensible order, and you can save the roadmap under **My Plans**. If the model is unavailable, a foundational route (phases 00–02) is suggested instead.
- **Learner workspace.** A local username gives each learner a stable ID, chat session, saved plans and feedback history.
- **In-app feedback.** A feedback widget collects pilot feedback (see [PILOT_SURVEY.md](PILOT_SURVEY.md)).
- **Optional hosted fallback.** Off by default. When enabled, a hosted model answers only if the local Ollama call fails. See [HOSTED_FALLBACK_DECISION.md](HOSTED_FALLBACK_DECISION.md).

### What it does not do

The tutor can explain and reason about code, but **it never runs it**. There is no code execution, code judging or submission grading in this app, and no separate code-execution service to deploy.

## Architecture

```text
Browser
  └── Static frontend (frontend/)          Preact + htm from esm.sh, no build step
        ├── Dashboard
        ├── AI Tutor chat
        ├── Guides (curriculum.json + Markdown lessons)
        └── My Plans
              │  HTTP/JSON
              ▼
        FastAPI backend (app/main.py)
          ├── Tutor prompt            app/explain.py
          ├── Goal detection          app/classifier.py
          ├── Roadmap generation      app/study_plan.py
          ├── Ollama client           app/ollama_client.py (+ optional app/hosted_client.py)
          └── SQLAlchemy ──► PostgreSQL
```

## Repository layout

```text
app/
  main.py                FastAPI routes and startup
  config.py              Environment-based settings
  explain.py             Tutor system prompt and generation
  classifier.py          Detects learning-goal messages
  study_plan.py          Phase-based roadmap generation and persistence
  content_loader.py      Indexes lesson Markdown into the database
  ollama_client.py       Local Ollama client (concurrency cap, optional fallback)
  hosted_client.py       Optional hosted provider fallback
  user_service.py        User and session creation
  models.py, schemas.py, db.py
  prompts/goal_prompts.py
content/lessons/phases/  Backend copy of the lessons (indexed on startup)
frontend/
  index.html
  src/                   Components, store, API client, styles
  content/
    curriculum.json      Phase and lesson navigation manifest
    phases/              Lessons served to the browser
db/
  schema.sql             PostgreSQL schema
  migrations/            Optional cleanup for older pilot databases
scripts/import_ai_eng_curriculum.py   Refreshes lessons from upstream
docs/curriculum-import.md
tests/                   Backend tests
docker-compose.yml       PostgreSQL only
```

## Requirements

- Python 3.10+
- PostgreSQL 14+ (the Compose file provides PostgreSQL 16)
- [Ollama](https://ollama.com) installed on the backend machine, with a model pulled (default `llama3.1:8b`)
- Docker, only if you want Compose to run PostgreSQL

No Node.js is needed. The frontend is plain ES modules.

## Quick start

```bash
# 1. PostgreSQL
docker compose up -d postgres

# 2. Ollama model
ollama pull llama3.1:8b

# 3. Backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 4. Frontend (second terminal)
python -m http.server 5500 --directory frontend
```

Open <http://localhost:5500>, enter a username, and start learning.

On startup the backend creates any missing tables and indexes the lessons from `content/lessons/phases/`. Check it with:

```bash
curl http://localhost:8000/health
```

The frontend defaults to `http://localhost:8000` for the API. If the backend is elsewhere, change it under **Settings → API connection**.

For running on a shared machine or splitting frontend and backend, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Configuration

Settings are read from environment variables or a `.env` file in the repository root.

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg2://tutor:tutor@localhost:5432/tutor_db` | PostgreSQL connection string |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1:8b` | Local model name |
| `OLLAMA_TIMEOUT` | `120` | Model request timeout (seconds) |
| `OLLAMA_MAX_CONCURRENCY` | `1` | Concurrent local generations |
| `HOSTED_FALLBACK_ENABLED` | `false` | Use a hosted model if local Ollama fails |
| `HOSTED_PROVIDER` | `anthropic` | `anthropic` or `openai_compatible` |
| `HOSTED_API_KEY` | empty | Required only if fallback is enabled |
| `HOSTED_API_BASE` | `https://api.anthropic.com` | Hosted API base URL |
| `HOSTED_MODEL` | `claude-3-5-haiku-20241022` | Hosted model name |
| `HOSTED_TIMEOUT` | `60` | Hosted request timeout (seconds) |

API keys belong on the backend only.

## API overview

Interactive docs are served at <http://localhost:8000/docs>.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Ollama reachability and hosted-fallback status |
| `POST` | `/chat` | Tutor reply, or a roadmap if the message states a goal |
| `POST` | `/explain` | Direct explanation, no session needed |
| `GET` | `/lessons/phases` | Phase catalogue with lesson counts |
| `GET` | `/lessons/phases/{phase_slug}/{lesson_slug}` | One indexed lesson |
| `POST` | `/goal/check` | Does this message express a learning goal? |
| `POST` | `/goal/topics` | Generate a phase roadmap for a goal |
| `POST` | `/plans` | Save a roadmap |
| `GET` | `/plans/{user_id}` | List a user's saved roadmaps |
| `POST` | `/feedback` | Submit feedback |
| `GET` | `/feedback` | List feedback |

## Curriculum content

- `frontend/content/curriculum.json` drives navigation in the Guides tab.
- `frontend/content/phases/` holds the Markdown the browser loads.
- `content/lessons/phases/` is the identical backend copy that gets indexed into PostgreSQL.

The lessons come from the MIT-licensed [AI Engineering from Scratch](https://github.com/rohitg00/ai-engineering-from-scratch) project. To refresh them:

```bash
python scripts/import_ai_eng_curriculum.py
# or, from an existing checkout:
python scripts/import_ai_eng_curriculum.py --source-dir /path/to/ai-engineering-from-scratch
```

The importer regenerates all three locations above. Keep the upstream MIT attribution when redistributing. Details are in [docs/curriculum-import.md](docs/curriculum-import.md). Phase and lesson counts in this README reflect the current bundle and will change if you refresh it.

## Tests

```bash
DATABASE_URL=sqlite:///:memory: pytest -q
```

The tests cover user/session creation, lesson indexing and roadmap validation/persistence. They use SQLite, so no PostgreSQL or Ollama is needed.

## Upgrading an older database

Databases created by the earlier Stats/Coding Tutor can be cleaned up with an optional, manual migration. **Back up first.**

```bash
psql "$DATABASE_URL" -f db/migrations/001_remove_legacy_tracks.sql
```

It drops the old exercise and mastery tables, standalone coding/stats lesson rows and obsolete plan entries, and keeps ordinary chat history. It is never run automatically. Fresh databases do not need it.

## Pilot limitations

- **Not real authentication.** Login is just a username that maps to a stable user ID. Do not treat it as secure.
- **CORS allows all origins.** Restrict it in `app/main.py` before exposing the API beyond a trusted network.
- **`GET /feedback` is unauthenticated.** Do not expose it publicly.
- **Chat does not search lesson text.** The tutor answers from its system prompt and the learner's message. Lessons are for browsing, not retrieval.
- **One local model, limited concurrency.** Throughput depends on your GPU and `OLLAMA_MAX_CONCURRENCY`.

## Licence and attribution

Lesson content is derived from *AI Engineering from Scratch* (MIT, © 2026 Rohit Ghumare). Retain its attribution and permission notice with any redistributed copies.
