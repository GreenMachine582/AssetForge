# Milestone 1 — MVP

The tracker replaces the Excel file as the working interface. Core tables,
filters, detail card, and export are functional.

**References:** [Features](../features.md) · [Data Model](../data-model.md) · [API Reference](../api-reference.md)

---

## Scope

**In scope for M1:**

- Asset table with complex filters and offcanvas detail card
- Specs table with inline editing
- Project summary with cost cards
- Dashboard with spend overview and state counts
- State machine (Planned → Installed → In Service → Removed → Retired)
- Event log per asset (purchased, installed, reallocated, removed, noted)
- Excel export (5-sheet workbook)
- JSON export + import
- Specs markdown export (copy to clipboard)
- Build Planning + Upgrade Planning AI context profiles


**Explicitly deferred to M2+:**

- Warranty tracking (fields in schema, UI not exposed)
- Locations (table in schema, FK on assets, UI not exposed)
- Attachments (table in schema, routes return 501)
- Bulk reassign
- HomeLab + Purchasing AI context profiles
- Graph visualisation
- Timeline
- Power estimation
- Compatibility checker
- All event types beyond the M1 subset

---

## Schema Notes

All tables are created at M1 with their full column set. Future columns
are nullable. No migrations needed in later milestones for schema additions
that are already defined.

See [data-model.md](../data-model.md) for the full schema. M1 enforces:
- `assets`: all core columns; warranty/location/parent columns nullable
- `specs`: socket, form_factor, tdp_watt, speed_spec, capacity, slots_used,
  slots_total, ram_gen, pcie_gen, chipset, compat_notes; dimension/power
  columns nullable
- `events`: M1 event types only; future types insertable via API
- `locations`: created but empty
- `attachments`: created but not exposed
- `benchmarks`: created but not exposed
- `settings`: seeded with defaults

---

## Implementation Order

Work in this order to stay unblocked. Each step is independently testable.

### 1. Foundation
- [x] `database.py` — engine, session factory, `create_all()`
- [x] `models.py` — all tables, full schema, all columns
- [x] `schemas.py` — Pydantic models for M1 routes
- [x] `seed.py` — dropped; data entered via web UI
- [x] `services/state_machine.py` — transition map, `validate_transition()`
- [x] `settings` table seeded with defaults

### 2. Core API
- [x] `routers/assets.py` — `GET /api/assets` with all filter params (including `reallocated` and bare-type `project` matching, added during the M1 completeness review)
- [x] `routers/assets.py` — `GET /api/assets/{uid}`, `PUT`, `POST`
- [x] `routers/assets.py` — `POST /api/assets/{uid}/transition`
- [x] `routers/events.py` — `GET /api/events`, `POST /api/events`
- [x] `routers/projects.py` — `GET /api/projects`, `POST`, `PUT`
- [x] `routers/specs.py` — `GET /api/specs`, `GET/PUT /api/specs/{uid}`
- [x] `routers/io.py` — `GET /api/export/excel`, `GET /api/export/json`
- [x] `routers/io.py` — `POST /api/import/json` (with auto-backup)
- [x] `routers/io.py` — `GET /api/export/specs-md`
- [x] `routers/io.py` — `GET /api/ai-context/specs`, `/build/{type}/{key}`, `/upgrade/{type}/{key}`
- [x] `routers/io.py` — stub all M2+ routes returning 501 (`POST /api/import/excel` stubbed — Excel import not supported; use web UI)
- [x] `routers/graph.py` — stub `/api/graph` returning 501
- [x] `routers/reports.py` — `GET /api/dashboard`, `GET /api/statistics`
- [x] `routers/settings.py` — `GET/PUT /api/settings`

### 3. Templates + HTMX
- [x] `base.html` — Bootstrap 5 shell, nav, offcanvas mount
- [x] `dashboard.html` — spend summary (incl. planned spend), state counts, spend-by-type chart, project quick links, recent assets
- [x] `assets.html` — page shell, filter bar, table mount
- [x] `partials/filter-bar.html` — all M1 filter controls (project, used by, category, state, date/amount range, text search, quick chips including HomeLab/Reallocated); drives `assets.html`'s fetch + `setData()` on change
- [x] `assets.html` — Tabulator init (once per page load), column visibility toggle, row click → offcanvas; `partials/assets-table.html` is just the static mount point
- [x] `partials/asset-card.html` — full offcanvas detail card
- [x] `partials/state-badge.html` — clickable badge + transition dropdown
- [x] `partials/event-timeline.html` — chronological event log
- [x] `projects.html` + `partials/project-card.html` — includes doughnut state-breakdown chart
- [x] `specs.html` — Tabulator, inline edit, highlight missing fields, client-side search

### 4. Services
- [x] `services/excel.py` — export-only; `build_workbook()` produces 5-sheet xlsx from DB
- [x] `services/ai_context.py` — Specs, Build Planning, Upgrade Planning profiles
- [x] `static/js/filters.js` — filter-count badge, clear-all button (URL sync + data fetch handled inline in `assets.html`)
- [x] `static/js/clipboard.js` — copy AI context to clipboard

### 5. Polish + Release
- [x] Seed approach dropped — assets added via web UI; sort verified against manually entered data
- [x] Verify Excel export matches our schema-derived layout — verified valid and complete
- [x] Verify JSON round-trip (export → import → same data)
- [x] All M1 filter combinations tested
- [x] State transitions tested (valid + invalid)
- [x] `README.md` quick start verified on clean install — seed step removed; no Excel import

---

## Acceptance Criteria

M1 is done when all of these pass:

| # | Criterion | Status |
|---|---|---|
| 1 | Assets populate correctly via web UI (POST /api/assets + /api/projects) | ✅ Verified — routes tested, UI table reflects entries |
| 2 | Asset table loads and sort by any column works | ✅ Verified |
| 3 | Filtering by project + category + state returns correct subset; URL updates | ✅ Verified |
| 4 | Text search across name + notes + compat_notes returns correct results | ✅ Verified |
| 5 | Clicking any row opens offcanvas with correct part details and specs | ✅ Verified |
| 6 | Inline note save persists and appears in event log | ✅ Verified |
| 7 | State transition (e.g. Planned → Installed) updates badge and appends event | ✅ Verified |
| 8 | Invalid state transition (e.g. Planned → Sold) returns 400 with reason | ✅ Verified |
| 9 | Excel export produces a valid 5-sheet `.xlsx` matching our schema-derived layout | ✅ Verified (no legacy workbook exists to compare against instead — see #1) |
| 10 | JSON export → JSON import round-trip produces identical data | ✅ Verified |
| 11 | Specs markdown copy-to-clipboard produces a valid markdown table with all spec fields | ✅ Verified |
| 12 | Build Planning AI context for a project (e.g. `PC Build`/`2`) includes all planned assets with specs | ✅ Verified |
| 13 | Project summary cards show correct totals (bought-for and used-by) | ✅ Verified |
| 14 | Dashboard state counts match actual asset states in DB | ✅ Verified |
| 15 | Auto-backup created in `data/backups/` before any import | ✅ Verified |
| 16 | All M2+ API routes return `HTTP 501` (not 404) | ✅ Verified |

---

## Definition of Done

- All acceptance criteria pass — 16/16 verified
- No `TODO` comments in M1 code paths
- M2+ stubs are in place (501 responses)
- `docs/milestones/02-lifecycle.md` is reviewed and ready to start
