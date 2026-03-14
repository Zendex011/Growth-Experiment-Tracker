# agents.md — Coding Standards & Constraints

This file defines coding standards for both human developers and AI agents
working on this codebase.

---

## Python Standards

- Python 3.11+
- Type hints on all function signatures
- Docstrings on all public functions and classes
- Max function length: 40 lines. If longer, split it.
- Max file length: 200 lines. If longer, split the module.
- No wildcard imports (`from module import *`)

## Error Handling

```python
# CORRECT — specific, logged, informative
except requests.exceptions.Timeout as exc:
    logger.warning("HuggingFace timeout: %s", exc)
    return SomeSuggestion(degraded=True, reason="Request timed out.")

# WRONG — swallows the error silently
except Exception:
    pass
```

## Database

- Never call `db.session.commit()` inside a model method
- Always commit in the service layer, after all mutations succeed
- Use `db.session.add()` for new records, never raw INSERT
- Foreign keys use `ondelete="CASCADE"` — no orphaned records

## API Responses

All success responses return JSON. Shape conventions:

```json
// Single resource
{ "id": "...", "state": "draft", ... }

// List
[ { "id": "...", ... }, ... ]

// Deleted
{ "deleted": "<id>" }

// Error (all errors)
{ "error": "ErrorClassName", "message": "Human readable.", "status": 422 }

// AI suggestion (always includes degraded flag)
{ "hypothesis": "...", "confidence": "high", "degraded": false, "reason": null }
```

## Git Commit Messages

```
feat: add hypothesis suggestion endpoint
fix: prevent verdict overwrite after lock
test: add paused-to-completed transition test
refactor: extract audit log write to helper
docs: update README with docker setup
```

## What Never Goes in Version Control

- `.env` files with real credentials
- `__pycache__/` directories
- `*.pyc` files
- Local SQLite database files (`*.db`)

---

## Dependency Policy

Before adding a new package:
1. Check if the standard library already provides it
2. Check if an existing dependency already covers it
3. If genuinely needed: add to `requirements.txt` with a pinned version

No floating versions (`requests>=2`) — always pin (`requests==2.32.2`).
