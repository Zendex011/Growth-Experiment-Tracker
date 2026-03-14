# claude.md — AI Agent Guidance

This file constrains how AI agents (Claude, Copilot, etc.) should behave
when generating or editing code in this repository.

---

## What This Project Is

A Growth Experiment Tracker: a small, well-structured backend API for
managing growth experiments from hypothesis → running → results → verdict.

The system must remain **correct and understandable as it evolves**.
Prefer simple and predictable over clever and compact.

---

## Absolute Rules (Never Violate)

1. **AI output is never written to the database automatically.**
   All AI suggestions are returned to the caller. The human decides what to save.

2. **Never bypass the state machine.**
   `experiment.state = "completed"` is forbidden everywhere except inside
   `app/services/state_machine.py`. All state changes go through `transition()`.

3. **Never add a state transition without a test.**
   Every new entry in `VALID_TRANSITIONS` requires both a passing test
   (transition succeeds) and a blocking test (invalid transition raises).

4. **Never silence exceptions from AI calls.**
   Always log the error with `logger.warning(...)` and return a response
   with `degraded=True`. Never return a 500 because an AI service is down.

5. **Never trust raw request data.**
   All incoming request bodies must be validated through a Pydantic schema
   before reaching the service layer. No `request.json["field"]` in services.

6. **Never write business logic in routes.**
   Routes do three things only: validate input schema, call a service function,
   return a JSON response. No DB queries, no if/else business rules in routes.

---

## Structure Rules

- **Models** → define table columns and `to_dict()`. No logic.
- **Schemas** → define input/output contracts. No DB access.
- **Services** → all business logic. No HTTP awareness (no `request`, no `jsonify`).
- **Routes** → thin HTTP layer. No business logic.
- **State Machine** → only place allowed to change `experiment.state`.

If you find yourself importing `request` in a service, stop and refactor.
If you find yourself writing a DB query in a route, stop and refactor.

---

## Naming Conventions

- Models: `PascalCase` — `Experiment`, `AuditLog`, `ExperimentResult`
- Service functions: `snake_case` verbs — `create()`, `change_state()`, `add_result()`
- Route paths: REST nouns, no verbs — `/experiments`, `/results`
  Exceptions allowed: `/state`, `/verdict`, `/ai/*`
- Schema classes: `PascalCase` + `Schema` suffix — `CreateExperimentSchema`

---

## Testing Rules

- All tests run with `pytest tests/ -v` from the `backend/` directory.
- Tests must pass with **no network access** — all external calls are mocked.
- Use `conftest.py` fixtures for test data — never hardcode IDs.
- Every AI service function test uses a mock fixture, not the real HuggingFace API.
- Do not use `unittest.TestCase` — use plain `pytest` functions or classes.

---

## Adding New Features

When adding a new feature, follow this order:
1. Add/update the model if schema changes are needed
2. Add/update the Pydantic schema
3. Write the service function with business logic
4. Write tests for the service (and state machine if relevant)
5. Write the route (thin — just calls the service)
6. Run all tests before committing

**If a new feature touches more than 4 files, reconsider the design.**

---

## What AI Should Not Do

- Do not add new dependencies without adding them to `requirements.txt`
- Do not create new database tables without a Flask-Migrate migration
- Do not add `print()` statements — use `logger.info/warning/error`
- Do not write raw SQL — use SQLAlchemy ORM methods
- Do not add `try/except Exception: pass` — always handle or re-raise
- Do not generate mock data or seed scripts that write to production DB
