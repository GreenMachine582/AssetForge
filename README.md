# AssetForge

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/storage-SQLite-003B57.svg)](https://www.sqlite.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](docs/guides/running.md)
[![Status: MVP in progress](https://img.shields.io/badge/status-MVP%20in%20progress-yellow.svg)](docs/milestones/01-mvp.md)

> A modern hardware asset tracker for PC builders and homelab enthusiasts.
> Manage components, projects, compatibility, budgets, and part history with
> a lightweight local-first web app.

Single-user, file-based, no cloud. One SQLite file, one `uvicorn` process.
Tracks hardware across builds and machines from purchase through retirement,
with structured spec data ready to paste into any AI for compatibility
research and upgrade planning.

---

## Quick Start

```bash
pip install -r requirements.txt

# Run
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

See [docs/guides/running.md](docs/guides/running.md) for Docker deployment.

---

## Status

| Milestone | Status |
|---|---|
| [M1 — MVP](docs/milestones/01-mvp.md) | ✅ Done |
| [M2 — Asset Lifecycle](docs/milestones/02-lifecycle.md) | ⚪ Planned |
| [M3 — Intelligence](docs/milestones/03-intelligence.md) | ⚪ Planned |
| [M4 — Analytics](docs/milestones/04-analytics.md) | ⚪ Planned |
| [V1 — Release](docs/milestones/05-v1-release.md) | ⚪ Planned |

---

## Documentation

| Doc | What it covers |
|---|---|
| [Architecture](docs/architecture.md) | Design decisions, tech stack, ADRs, file structure |
| [Data Model](docs/data-model.md) | Schema, state machine, event types, Part_UID format |
| [Features](docs/features.md) | Full feature inventory across all phases |
| [API Reference](docs/api-reference.md) | All routes — pages, partials, JSON API |
| [AI Context](docs/ai-context.md) | Export profiles and how to use them |
| [Running](docs/guides/running.md) | Install, run, deploy, backup |

---

## Project Layout

```
AssetForge/
├── main.py               FastAPI app entry point
├── database.py           SQLite engine and session factory
├── models.py             SQLAlchemy table definitions
├── schemas.py            Pydantic request/response models
├── routers/              Page + API route handlers
├── services/             Business logic (state machine, compat, export)
├── templates/            Jinja2 + HTMX page and partial templates
├── static/               CSS and JS (no build step)
├── data/                 assetforge.db + attachments/ + backups/
└── docs/                 This documentation
```

---

## Principles

- **SQLite is the source of truth.** Excel and JSON are import/export formats only.
- **Schema is designed for the full vision.** MVP exposes a subset; no breaking migrations later.
- **No build pipeline.** HTMX + Alpine.js + Bootstrap 5 from CDN.
- **AI-assisted, not AI-dependent.** Export structured context; decisions stay with you.
