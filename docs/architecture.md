# Architecture

## Philosophy

**Build the MVP. Design for the full vision.**

The schema, state machine, event model, and API namespace are designed for
the complete asset lifecycle system. Most columns start nullable. Most future
API routes return `HTTP 501` until their milestone ships. This means no
breaking schema migrations, no URL renames, no service rewrites as features
are added.

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | **FastAPI** | Async, typed, `/docs` auto-generated |
| ORM | **SQLAlchemy 2.0 Core** | Clean SQL, async-capable, no ORM magic |
| DB driver | **aiosqlite** | Async SQLite |
| Templates | **Jinja2** | Ships with FastAPI, no build step |
| Interactivity | **HTMX 2.x** | Server-side partials, zero JS bundle |
| Client state | **Alpine.js 3.x** | Filter panel, tabs, row selection |
| Styling | **Bootstrap 5.3** | Dark mode, utilities, components |
| Tables | **Tabulator 6.x** | Virtual scroll, column visibility |
| Graph viz | **vis.js Network** | Force-directed part lineage graph |
| Charts | **Chart.js 4.x** | Dashboard widgets, spend breakdown |
| Export | **openpyxl** | Excel builder, reused as a service |
| Storage | **SQLite** | Zero infrastructure, portable, inspectable |

No build step. Bootstrap, HTMX, Alpine, Tabulator, vis.js, and Chart.js all
load from CDN. The project is a Python package with static files — nothing to
compile.

---

## Architecture Decisions

These are the answers to the open design questions, decided once, not revisited.

### 1. Source of truth

SQLite is the authoritative datastore. Excel and JSON are import/export
compatibility layers. The seed script populates SQLite from the existing
workbook once. The workbook is generated on demand from SQLite — never edited
directly.

### 2. What is a Project?

A Project is a **long-lived system** (`PC Build 2`, `HomeLab NAS`). Upgrades
are not new projects — they are events on existing assets within a project.
A version-suffixed name like "PC Build 2 V2" maps to a single project
(`type="PC Build"`, `key="2"`) with the version change captured as events,
not as a separate project or a suffix baked into the key itself.

### 3. Bundles and sub-components

Assets support a self-referential `parent_asset_uid` FK. A case contains
fans and RGB hubs as child assets. A laptop contains RAM and SSD. The column
is nullable in the schema from v0.1; the UI exposes it from M2.

### 4. Motherboard replacement semantics

Replacing a motherboard does not automatically move all installed assets.
Each asset generates its own `removed → installed` events. This preserves
per-asset history and reflects that some parts stay while others move. A
bulk-reassign helper is added in M2.

### 5. Peripherals are first-class assets

Monitors, mice, keyboards, UPS units, KVMs — all use the same Asset model.
Category codes distinguish them. No special cases or separate tables.

### 6. Compatibility model

Rule-based first. `services/compatibility.py` is a pluggable rule registry —
each rule is a function `(asset, project) -> CompatResult`. Curated metadata
(QVLs, BIOS version requirements) plugs into the same interface as a
data-backed rule in M3. Callers never change when rules are extended.

### 7. Attachments

Filesystem-backed, database-referenced. Files live at
`DATA_PATH/attachments/{part_uid}/`. The DB stores filename, type, and
description only. The SQLite file and the attachments directory travel
together as a backup unit. No binary blobs in the DB.

### 8. Automation readiness

The `events.metadata` JSON column carries event-specific structured data
(benchmark scores, firmware versions, SMART results, OCR-parsed invoice
fields). Future automation writes events and attachments via the existing
`/api/events` endpoint. No separate automation schema needed.

---

## File Structure

```
AssetForge/
├── main.py                     FastAPI app, middleware, router mounts
├── database.py                 SQLite engine, session factory
├── models.py                   SQLAlchemy table definitions (full schema)
├── schemas.py                  Pydantic request/response models
├── seed.py                     One-shot import from existing Excel
│
├── routers/
│   ├── pages.py                GET /* Jinja2 page routes
│   ├── assets.py               /api/assets  CRUD + HTMX partials
│   ├── projects.py             /api/projects
│   ├── specs.py                /api/specs
│   ├── events.py               /api/events
│   ├── graph.py                /api/graph
│   ├── locations.py            /api/locations          [M2]
│   ├── attachments.py          /api/attachments        [M2]
│   ├── benchmarks.py           /api/benchmarks         [M4]
│   ├── reports.py              /api/reports            [M4]
│   └── io.py                   /api/export and /api/import
│
├── services/
│   ├── excel.py                openpyxl workbook builder
│   ├── state_machine.py        valid transition enforcement
│   ├── compatibility.py        pluggable rule registry  [M3]
│   ├── graph_builder.py        materialise nodes + edges from DB
│   ├── power.py                power draw + cost estimation  [M3]
│   ├── ai_context.py           render context profiles as markdown
│   └── warranty.py             expiry calculation + alerts  [M2]
│
├── templates/
│   ├── base.html               Bootstrap 5 shell, nav, offcanvas scaffold
│   ├── partials/               HTMX-swappable fragments
│   └── *.html                  Full page templates
│
├── static/
│   ├── css/app.css             Bootstrap overrides, custom tokens
│   └── js/                     filters.js, graph.js, clipboard.js
│
└── data/
    ├── assetforge.db           SQLite (single source of truth)
    ├── attachments/            {part_uid}/ directories  [M2]
    └── backups/                Auto-created before any import/replace
```

---

## Deployment Topology

```
                    ┌─────────────────┐
                    │  uvicorn        │
                    │  main:app       │
                    │  :8000          │
                    └────────┬────────┘
                             │
               ┌─────────────┼─────────────┐
               │             │             │
        ┌──────▼──────┐ ┌────▼────┐ ┌─────▼──────┐
        │ tracker.db  │ │ static/ │ │attachments/│
        │  (SQLite)   │ │         │ │ [M2]       │
        └─────────────┘ └─────────┘ └────────────┘
```

Single process, single file, single machine. See [guides/running.md](guides/running.md).
