# Stats/Coding Tutor

A local-first tutoring app built around a self-hosted LLM (Ollama). A
learner chats in, the message gets classified as **stats** or
**coding** (plus a specific subtopic), they get a topic-tuned
explanation back, and then they can practice what they just learned —
a generated quiz for stats topics, or a coding exercise auto-graded
against real test cases for coding topics. Difficulty adapts over time
based on a rolling mastery score per subtopic, so explanations and
practice get harder as a learner demonstrates they've got it.

This build has gone through a full pilot round: the frontend has
mobile/loading/error polish, the backend can optionally fall back to a
hosted API if the local model goes down, and there's a real deployment
guide and feedback loop for running it with actual learners. See
[What's included](#whats-included) for the full feature list, or jump
straight to [Getting started](#getting-started).

## Contents

- [What's included](#whats-included)
- [Project layout](#project-layout)
- [Getting started](#getting-started)
- [Configuration](#configuration)
- [Running the frontend](#running-the-frontend)
- [How it works](#how-it-works)
- [API reference](#api-reference)
- [Testing](#testing)
- [Deploying a pilot](#deploying-a-pilot)
- [Optional: hosted-API fallback](#optional-hosted-api-fallback)
- [Known limitations](#known-limitations)

## What's included

- **Chat → classify → explain.** Every message is classified by
  domain + subtopic before a topic-tuned explanation is generated, so
  the tutor answers in the right "voice" for the topic.
- **Practice loops for both domains.** Stats topics get an
  auto-generated multiple-choice quiz; coding topics get an
  auto-generated exercise that's graded by actually running the
  learner's code against test cases (via a self-hosted Judge0).
- **Adaptive difficulty.** A rolling mastery score per `(domain,
  subtopic)` decides whether a learner sees beginner, intermediate, or
  advanced material next.
- **A working frontend** (chat, practice, progress dashboard) with no
  build step required.
- **Pilot-ready backend**: health checks, an optional hosted-API
  fallback for outages, an in-app feedback widget, and a deployment
  guide for running this with real learners on a LAN.

## Project layout

```
tutor-app/
├── app/
│   ├── main.py                     # FastAPI app: all routes live here
│   ├── config.py                   # env-based settings (Ollama, Judge0, hosted fallback)
│   ├── db.py                       # SQLAlchemy engine/session
│   ├── models.py                   # users, sessions, questions, attempts, mastery_score, feedback
│   ├── schemas.py                  # Pydantic request/response models
│   ├── ollama_client.py            # wrapper around the local Ollama API
│   ├── hosted_client.py            # optional hosted-API fallback (off by default)
│   ├── judge0_client.py            # wrapper around the self-hosted Judge0 API
│   ├── classifier.py               # intent classification (domain + subtopic + confidence)
│   ├── explain.py                  # explanation engine, dispatches by topic
│   ├── quiz.py                     # stats quiz generator
│   ├── code_exercise.py            # coding exercise generator
│   ├── code_checker.py             # runs a submission's test cases via Judge0
│   ├── practice.py                 # ties generation + persistence + grading + mastery together
│   ├── mastery.py                  # rolling mastery score + difficulty mapping
│   ├── user_service.py             # get-or-create user helper
│   └── prompts/
│       ├── stats_prompts.py        # per-subtopic system prompt + few-shot examples (stats)
│       ├── coding_prompts.py       # same, for coding
│       ├── cache.py                # memoizes each fixed system prompt so it's built once
│       ├── quiz_prompts.py         # JSON-output prompt for quiz generation
│       └── code_exercise_prompts.py # JSON-output prompt for exercise generation
├── db/schema.sql                   # reference Postgres schema (mirrors models.py)
├── tests/
│   ├── sample_questions.json       # labeled questions used by the classifier test
│   ├── test_classifier.py          # classification accuracy report
│   ├── test_mastery.py             # mastery scoring unit tests
│   ├── test_user_service.py        # user helper unit tests
│   ├── test_practice_grading.py    # grading/validation unit tests (no live services needed)
│   └── test_practice_e2e.py        # full loop smoke test (needs Ollama + Judge0 + Postgres)
├── frontend/                       # Preact-based UI, no build step (see below)
├── docker-compose.yml              # Postgres only (Ollama runs natively for GPU access)
├── docker-compose.judge0.yml       # self-hosted Judge0 (own Postgres + Redis)
├── judge0.conf.example             # copy to judge0.conf before starting Judge0
├── requirements.txt
├── DEPLOYMENT.md                   # pilot deployment guide (same-machine or split)
├── HOSTED_FALLBACK_DECISION.md     # whether to turn on the hosted-API fallback
└── PILOT_SURVEY.md                 # end-of-pilot exit survey template
```

## Getting started

### 1. Postgres

```bash
docker compose up -d postgres
```

The app also runs `Base.metadata.create_all()` on startup, so tables
are created automatically the first time you run `uvicorn` — handy for
local dev. For anything beyond local dev, apply `db/schema.sql`
directly or move to a real migration tool (e.g. Alembic).

### 2. Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh   # or the macOS/Windows installer
ollama pull llama3.1:8b                          # pick a model per the hardware table below
```

**Hardware sizing:**

| VRAM / unified memory | Suggested model             | Notes                                         |
|------------------------|------------------------------|------------------------------------------------|
| ≤ 8 GB                 | `phi3:mini`, `qwen2.5:3b`    | Fast, weaker reasoning                          |
| 8–16 GB                | `llama3.1:8b`, `qwen2.5:7b`  | Good default balance                            |
| 16–24 GB               | `qwen2.5:14b`                | Noticeably better classification/explanations   |
| 24 GB+                 | `llama3.1:70b` (quantized) or hosted-API fallback | Best quality; watch latency |

### 3. Install and run the backend

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. Smoke test

```bash
curl http://localhost:11434/api/tags           # confirm Ollama is up
curl http://localhost:8000/health               # confirm FastAPI can see Ollama (and Judge0, if running)
curl -X POST http://localhost:8000/chat/raw \
     -H "Content-Type: application/json" \
     -d '{"user_id": 1, "message": "hello"}'
```

### 5. (Optional) Coding practice — Judge0

Coding exercises are graded by running submissions through a
self-hosted [Judge0](https://judge0.com/) instance:

```bash
cp judge0.conf.example judge0.conf   # edit the passwords in it first
docker compose -f docker-compose.judge0.yml up -d
curl http://localhost:2358/languages  # smoke test
```

Skip this step if you only care about the stats side for now — the
rest of the app works fine without it, and `/health` will just report
`judge0_ok: false`.

## Configuration

There's no `.env` file included, so create one in the project root if
you want to override any default. All settings and their defaults live
in `app/config.py`:

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg2://tutor:tutor@localhost:5432/tutor_db` | Postgres connection string |
| `OLLAMA_HOST` | `http://localhost:11434` | Where the local Ollama server is running |
| `OLLAMA_MODEL` | `llama3.1:8b` | Model tag to use for chat/classification/generation |
| `OLLAMA_TIMEOUT` | `120` | Seconds before an Ollama request times out |
| `OLLAMA_MAX_CONCURRENCY` | `1` | Concurrent local generations allowed; raise only if your hardware can actually parallelize |
| `APP_ENV` | `dev` | Free-form environment label |
| `JUDGE0_URL` | `http://localhost:2358` | Where the self-hosted Judge0 instance is running |
| `JUDGE0_TIMEOUT` | `30` | Seconds before a Judge0 request times out |
| `JUDGE0_PYTHON_LANGUAGE_ID` | `71` | Judge0 language id for Python 3 — confirm via `GET {JUDGE0_URL}/languages` |
| `HOSTED_FALLBACK_ENABLED` | `false` | Turn on the hosted-API fallback (see [below](#optional-hosted-api-fallback)) |
| `HOSTED_PROVIDER` | `anthropic` | `anthropic` or `openai_compatible` |
| `HOSTED_API_KEY` | *(empty)* | Required if the fallback is enabled |
| `HOSTED_API_BASE` | `https://api.anthropic.com` | Base URL for the hosted provider |
| `HOSTED_MODEL` | `claude-3-5-haiku-20241022` | Model to use for the hosted fallback |
| `HOSTED_TIMEOUT` | `60` | Seconds before a hosted-API request times out |

## Running the frontend

The frontend is Preact + [htm](https://github.com/developit/htm) +
`@preact/signals`, loaded straight from esm.sh in the browser — no npm
install, no bundler, no build step.

```bash
# terminal 1 — backend (see Getting started above)
uvicorn app.main:app --reload

# terminal 2 — frontend, any static file server works
cd frontend
python3 -m http.server 5500
# open http://localhost:5500
```

A plain `file://` open won't work — browsers block ES module imports
from `file://` origins, hence the static server.

**Logging in** is just a username; there's no password. `user_id` is a
deterministic hash of the name, so the same name always resumes the
same mastery history — intentional, since this is meant for a small
closed pilot, not public deployment.

If the backend isn't on `localhost:8000` (e.g. a split deployment —
see [Deploying a pilot](#deploying-a-pilot)), open the gear icon in the
sidebar (**Settings**) and point it at the right URL. It's saved in the
browser's `localStorage`, so it's a one-time setup per browser.

```
frontend/
├── index.html            # loads src/main.js as a module, links styles.css
└── src/
    ├── main.js            # mounts <App/>
    ├── lib.js             # single import point for preact/htm/hooks
    ├── store.js           # signals: username→user_id, session_id, apiBase, nav
    ├── api.js             # one function per backend route, matches schemas.py
    ├── styles.css
    └── components/
        ├── App.js            # auth gate + router + health polling
        ├── Login.js          # username-only "login", no auth (per the pilot brief)
        ├── Sidebar.js        # Chat / Practice / Progress nav + health LEDs
        ├── SettingsModal.js  # editable API base URL (for split deployment)
        ├── Badge.js          # domain/subtopic/difficulty tag chips
        ├── ChatView.js       # chat UI + "Practice this" handoff
        ├── PracticeView.js   # Quiz/Code subtabs
        ├── QuizPanel.js      # quiz generation + grading UI
        ├── CodePanel.js      # code exercise + grading UI
        ├── ProgressView.js   # mastery bar + badge per row
        ├── Skeleton.js       # loading-skeleton components
        ├── ErrorBanner.js    # retryable error banner
        └── FeedbackWidget.js # in-app bug/UX feedback form
```

**How the pieces connect to the API:**

- **Chat** posts to `/chat` and shows `intent_domain` / `intent_subtopic`
  / `difficulty` as badges under each reply. A "Practice this →" button
  carries that same domain/subtopic/difficulty into Practice, so the
  learner doesn't have to re-select it.
- **Practice → Quiz** hits `/practice/quiz/generate` (stats subtopics
  only), shows one question at a time, and grades each via
  `/practice/quiz/submit`.
- **Practice → Code** hits `/practice/code/generate` (coding subtopics
  only), pre-fills starter code into an editable text editor, and
  "Run" posts to `/practice/code/submit`, showing a per-test-case
  pass/fail table plus an overall score.
- **Progress** calls `GET /mastery/{user_id}` and renders a bar plus
  the current difficulty badge per `(domain, subtopic)`.
- The sidebar polls `GET /health` every 30 seconds and shows LEDs for
  `ollama_ok` / `judge0_ok`, so "the model's not responding" is visible
  before a learner burns a turn finding out the hard way.
- The **feedback widget** posts to `/feedback` so a learner can flag a
  bug or confusing moment without leaving the app.

## How it works

**Classification** (`app/classifier.py`) — every message gets a
`domain` (`stats`|`coding`), a closed-vocabulary `subtopic`, and a
`confidence`, forced into JSON by the Ollama call and validated with
Pydantic. One retry is issued on invalid JSON before falling back to a
low-confidence result, so a bad response never crashes `/chat`.

**Explanations** (`app/explain.py`, `app/prompts/`) — each subtopic has
its own system prompt and few-shot examples in `stats_prompts.py` /
`coding_prompts.py`. `prompts/cache.py` memoizes the fully-rendered
system prompt per `(domain, subtopic)` so it's built once, not on every
request — keep those prompt strings byte-identical across calls if you
switch to a backend with real prefix caching (llama.cpp, vLLM).

**Practice** (`app/quiz.py`, `app/code_exercise.py`,
`app/code_checker.py`, `app/practice.py`) — quizzes and coding
exercises are generated the same way as classification (generate →
validate → retry once → fall back to a canned example rather than
error out). Quiz answers are graded server-side by re-looking-up the
correct answer; code submissions are graded by actually running them
against test cases via Judge0, with a normalized stdout-diff fallback
so trailing whitespace doesn't unfairly fail a correct answer.

**Mastery** (`app/mastery.py`) — every practice attempt rolls into a
per-`(domain, subtopic)` mastery score via an exponential moving
average (seeded at a neutral 0.5, so one early miss doesn't read as
"knows nothing"). The score maps to `beginner` / `intermediate` /
`advanced`, but a subtopic is held at `beginner` until at least 3
attempts exist, so one lucky or unlucky answer can't swing it. Both
`/chat` and `/explain` use this to pick the difficulty automatically
(`/explain` can still take an explicit override).

## API reference

| Endpoint | Purpose |
|---|---|
| `GET /health` | Confirms Ollama and Judge0 are reachable |
| `POST /chat/raw` | Raw echo of the local model, no classification |
| `POST /chat` | Full pipeline: classify → explain → persist to `questions` |
| `POST /explain` | Classify → explain only, no DB write (useful for prompt tuning) |
| `POST /practice/quiz/generate` | Generate + persist a stats quiz for a subtopic |
| `POST /practice/quiz/submit` | Grade a quiz answer, write an `attempts` row |
| `POST /practice/code/generate` | Generate + persist a coding exercise for a subtopic |
| `POST /practice/code/submit` | Run a submission via Judge0, grade it, write an `attempts` row |
| `GET /mastery/{user_id}` | Every `(domain, subtopic)` mastery row and its current difficulty |
| `POST /feedback` | Record in-app feedback (bug/UX/other) from the widget |
| `GET /feedback` | List all recorded feedback, newest first |

## Testing

```bash
pytest tests/test_practice_grading.py     # unit tests, no live services needed
pytest tests/test_mastery.py              # mastery scoring unit tests
pytest tests/test_user_service.py         # user helper unit tests
pytest tests/test_classifier.py           # classification accuracy gate (needs Ollama running)
pytest tests/test_practice_e2e.py -v      # full loop; needs Ollama + Judge0 + Postgres up
```

You can also run the classifier report directly for a more readable
breakdown of where it's misclassifying:

```bash
python -m tests.test_classifier
```

## Deploying a pilot

Two supported shapes: everything on one GPU machine that learners hit
over the LAN, or the backend and frontend split across machines (CORS
is already wide open in `main.py` for this — narrow it before any
wider-than-pilot rollout, since there's still no auth). Full
walkthrough, including which `docker-compose` file to run where and
what to check via `/health` when something looks broken:
see [`DEPLOYMENT.md`](DEPLOYMENT.md).

**Gathering feedback during a pilot** — two channels meant to
complement each other: the in-app feedback widget (tied to `user_id` +
`session_id`, captured in the moment) and a short end-of-week exit
survey for the whole-experience view once moment-to-moment friction has
faded. Survey template: [`PILOT_SURVEY.md`](PILOT_SURVEY.md).

## Optional: hosted-API fallback

`app/hosted_client.py` lets the backend fall through to a hosted API
(Anthropic's Messages API, or any OpenAI-compatible endpoint) if the
local Ollama call fails outright — a crash, a timeout, or an
out-of-VRAM error. It does **not** trigger on a local call that
succeeds but gives a low-quality answer, and it's off by default so a
pilot machine that never enables it has zero new dependency on the
internet or an API key.

Turning it on adds a real internet dependency, a real API key/bill, and
a quieter failure mode (an outage becomes "slower and answered by a
different model" instead of a visible error). For the tradeoffs and
when it's actually worth enabling for a given pilot, see
[`HOSTED_FALLBACK_DECISION.md`](HOSTED_FALLBACK_DECISION.md).

## Known limitations

- The code editor is a styled `<textarea>` — no syntax highlighting or
  bracket matching. Fine for short exercises; swap in CodeMirror or
  Monaco if that becomes a real complaint.
- Chat history is in-memory only and resets on refresh — there's no
  endpoint yet to rehydrate it from the `questions` table.
- There's no authentication. `allow_origins=["*"]` on the backend and
  the username→user_id hash are both fine for a closed, trusted pilot
  and both worth revisiting before anything wider (see
  [`DEPLOYMENT.md`](DEPLOYMENT.md)).
