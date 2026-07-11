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
- Seed script from existing `PC_Build_Tracker.xlsx`

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
- [ ] `database.py` — engine, session factory, `create_all()`
- [ ] `models.py` — all tables, full schema, all columns
- [ ] `schemas.py` — Pydantic models for M1 routes
- [ ] `seed.py` — read Excel, upsert assets + specs, emit `purchased` events
- [ ] `services/state_machine.py` — transition map, `validate_transition()`
- [ ] `settings` table seeded with defaults

### 2. Core API
- [ ] `routers/assets.py` — `GET /api/assets` with all filter params
- [ ] `routers/assets.py` — `GET /api/assets/{uid}`, `PUT`, `POST`
- [ ] `routers/assets.py` — `POST /api/assets/{uid}/transition`
- [ ] `routers/events.py` — `GET /api/events`, `POST /api/events`
- [ ] `routers/projects.py` — `GET /api/projects`, `POST`, `PUT`
- [ ] `routers/specs.py` — `GET /api/specs`, `GET/PUT /api/specs/{uid}`
- [ ] `routers/io.py` — `GET /api/export/excel`, `GET /api/export/json`
- [ ] `routers/io.py` — `POST /api/import/json` (with auto-backup)
- [ ] `routers/io.py` — `GET /api/export/specs-md`
- [ ] `routers/io.py` — `GET /api/ai-context/specs`, `/build/{key}`, `/upgrade/{key}`
- [ ] `routers/io.py` — stub all M2+ routes returning 501
- [ ] `routers/graph.py` — stub `/api/graph` returning 501
- [ ] `routers/reports.py` — `GET /api/dashboard`, `GET /api/statistics`
- [ ] `routers/settings.py` — `GET/PUT /api/settings`

### 3. Templates + HTMX
- [ ] `base.html` — Bootstrap 5 shell, nav, offcanvas mount
- [ ] `dashboard.html` — spend summary, state counts, recent assets
- [ ] `assets.html` — page shell, filter bar, table mount
- [ ] `partials/filter-bar.html` — all M1 filter controls
- [ ] `partials/assets-table.html` — Tabulator init, HTMX swap target
- [ ] `partials/asset-card.html` — full offcanvas detail card
- [ ] `partials/state-badge.html` — clickable badge + transition dropdown
- [ ] `partials/event-timeline.html` — chronological event log
- [ ] `projects.html` + `partials/project-card.html`
- [ ] `specs.html` — Tabulator, inline edit, highlight missing fields

### 4. Services
- [ ] `services/excel.py` — adapt existing openpyxl builder to read from DB
- [ ] `services/ai_context.py` — Specs, Build Planning, Upgrade Planning profiles
- [ ] `static/js/filters.js` — URL param sync, chip state
- [ ] `static/js/clipboard.js` — copy AI context to clipboard

### 5. Polish + Release
- [ ] Run seed on real `PC_Build_Tracker.xlsx`, verify all 52 assets load
- [ ] Verify Excel export matches existing workbook structure
- [ ] Verify JSON round-trip (export → import → same data)
- [ ] All M1 filter combinations tested
- [ ] State transitions tested (valid + invalid)
- [ ] `README.md` quick start verified on clean install

---

## Acceptance Criteria

M1 is done when all of these pass:

| # | Criterion |
|---|---|
| 1 | `seed.py` imports all 52 assets from `PC_Build_Tracker.xlsx` with correct Part_UIDs, amounts, projects, and specs |
| 2 | Asset table loads with all 52 rows; sort by any column works |
| 3 | Filtering by project + category + state returns correct subset; URL updates |
| 4 | Text search across name + notes + compat_notes returns correct results |
| 5 | Clicking any row opens offcanvas with correct part details and specs |
| 6 | Inline note save persists and appears in event log |
| 7 | State transition (e.g. Planned → Installed) updates badge and appends event |
| 8 | Invalid state transition (e.g. Planned → Sold) returns 400 with reason |
| 9 | Excel export produces a valid 5-sheet `.xlsx` matching the original workbook layout |
| 10 | JSON export → JSON import round-trip produces identical data |
| 11 | Specs markdown copy-to-clipboard produces a valid markdown table with all spec fields |
| 12 | Build Planning AI context for PCB2-V2 includes all planned assets with specs |
| 13 | Project summary cards show correct totals (bought-for and used-by) |
| 14 | Dashboard state counts match actual asset states in DB |
| 15 | Auto-backup created in `data/backups/` before any import |
| 16 | All M2+ API routes return `HTTP 501` (not 404) |

---

## Definition of Done

- All acceptance criteria pass against a seeded database
- No `TODO` comments in M1 code paths
- M2+ stubs are in place (501 responses)
- `docs/milestones/02-lifecycle.md` is reviewed and ready to start
