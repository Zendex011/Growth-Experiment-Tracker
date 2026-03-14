# Growth Experiment Tracker

A lightweight internal tool for managing growth experiments —
from hypothesis through results to a locked, audited decision.

Built as a submission for the Bettr HQ engineering assessment.

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + Flask |
| Database | PostgreSQL (SQLite for tests) |
| Validation | Pydantic v2 |
| AI | HuggingFace Inference API (Mistral-7B) |
| Frontend | React 18 + Vite + Tailwind |
| Testing | pytest + pytest-flask |

---

## Quick Start

### Option A — Docker (recommended)

```bash
cp backend/.env.example backend/.env
# Add your HUGGINGFACE_TOKEN to backend/.env

docker-compose up
```

Backend runs at `http://localhost:5000`

### Option B — Local

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env          # fill in your values
flask db upgrade
flask run

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

### Run Tests

```bash
cd backend
pytest tests/ -v
```

Tests use SQLite in-memory. No database or network connection required.

---

## Architecture

```
Request → Route (validates schema)
              ↓
         Service (business logic)
              ↓
       State Machine (transition rules)
              ↓
         SQLAlchemy (DB write)
              ↓
         Audit Log (append-only record)
```

The state machine is the single source of truth for valid transitions.
No other code is allowed to change `experiment.state` directly.

---

## Experiment Lifecycle

```
draft → running → paused → completed (terminal)
                ↑_______↗
```

Rules:
- `completed` requires at least one result logged
- `completed` is terminal — no exits
- Verdict can only be set on a completed experiment
- Verdict is locked once set — cannot be overwritten
- Deleting an experiment is only allowed in `draft` state

---

## AI Features

Three advisory AI features powered by HuggingFace (Mistral-7B):

| Feature | Endpoint | Saves Automatically? |
|---|---|---|
| Hypothesis Generator | `POST /api/ai/hypothesis` | No — user accepts |
| Verdict Suggestion | `POST /api/ai/suggest-verdict` | No — user accepts |
| Experiment Summary | `POST /api/ai/summarize/:id` | No — user copies |

AI failures (timeout, 503, bad JSON) always return `degraded: true`
with a human-readable reason. They never cause a 500 error.

---

## Key Technical Decisions

**Why Pydantic v2 for validation?**
Schema-first validation at the API boundary. Invalid data is rejected
before it reaches the service layer. The error messages are structured
and consistent — no ad-hoc `if not data.get("field")` checks.

**Why store metadata as JSON text instead of JSONB?**
JSONB is PostgreSQL-specific. Using `Text` with `json.dumps/loads` keeps
the model compatible with SQLite in tests without any dialect-specific code.

**Why is the state machine a separate module?**
It is the most critical logic in the system. Isolating it means it can be
unit-tested with no Flask, no database, and no fixtures. Transitions are
tested in pure Python — fast and unambiguous.

**Why does AI output never auto-save?**
AI models are non-deterministic. Saving output without human review
introduces incorrect data silently. The human is always the last gate.

**Why SQLite for tests instead of PostgreSQL?**
Speed and isolation. Each test gets a fresh in-memory DB with no setup cost.
The small dialect differences (no JSONB, no UUID type) are handled in the
model layer so tests remain valid.

---

## Known Weaknesses & Tradeoffs

- **No authentication** — this is a single-team internal tool. Adding auth
  (JWT or session-based) is the first extension point.

- **HuggingFace free tier is slow** — the Mistral-7B model can take 20-40s
  on a cold start. A paid tier or a smaller always-warm model would fix this.

- **No pagination on list endpoints** — acceptable for small teams.
  Would add cursor-based pagination before scaling.

- **Verdict is locked but not cryptographically sealed** — a direct DB edit
  could change it. Acceptable for an internal tool; would add event sourcing
  for a high-stakes audit requirement.

---

## Project Structure

```
growth-experiment-tracker/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── routes/          # Flask blueprints (thin HTTP layer)
│   │   └── services/        # Business logic + state machine + AI
│   └── tests/               # pytest test suite
├── frontend/                # React + Vite
├── claude.md                # AI agent guidance
├── agents.md                # Coding standards
└── docker-compose.yml
```

---

## Demonstration

<video src="https://github.com/user/repo/raw/main/demonstration.mp4" controls="controls" style="max-width: 100%;">
  Your browser does not support the video tag.
</video>

Or view it directly: https://drive.google.com/file/d/1X7nHZCTRP-F9obpBtAs6bncdF6ZX0Ltp/view?usp=drivesdk

Topics covered:
- Architecture and folder structure
- State machine design and testing
- AI integration and graceful degradation
- Tradeoffs and extension approach
