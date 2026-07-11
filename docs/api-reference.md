# API Reference

All routes are registered at v0.1. Unimplemented routes return `HTTP 501 Not
Implemented` until their milestone ships. This locks the URL namespace — no
breaking changes as features are added.

The full OpenAPI spec is auto-generated at `/docs` (Swagger UI) and
`/redoc` when the server is running. This document covers intent and
milestone status; `/docs` covers schemas and request/response shapes.

`[M1]` = MVP · `[M2]` = Lifecycle · `[M3]` = Intelligence · `[M4]` = Analytics

---

## Page Routes (Jinja2)

```
GET  /                          Dashboard                       [M1]
GET  /assets                    Asset table                     [M1]
GET  /projects                  Project summary                 [M1]
GET  /specs                     Specs table                     [M1]
GET  /graph                     Part lineage graph              [M3]
GET  /timeline                  Build timeline                  [M3]
```

---

## HTMX Partials

Return HTML fragments for `hx-swap` targets. Not intended for direct
browser navigation.

```
GET  /partials/assets-table             Filtered asset table    [M1]
GET  /partials/asset-card/{uid}         Offcanvas card content  [M1]
GET  /partials/filter-bar               Filter controls         [M1]
GET  /partials/state-badge/{uid}        Rendered state badge    [M1]
POST /partials/asset/{uid}/note         Save note → card section [M1]
POST /partials/asset/{uid}/state        Transition → badge      [M1]
GET  /partials/event-timeline/{uid}     Event log fragment      [M1]
GET  /partials/project-card/{type}/{key} Project summary card   [M1]
GET  /partials/attachment-list/{uid}    Attachment list         [M2]
GET  /partials/compat-panel/{uid}       Compatibility results   [M3]
```

---

## Assets

```
GET    /api/assets                      List + filter           [M1]
POST   /api/assets                      Create                  [M1]
GET    /api/assets/{uid}                Detail + specs          [M1]
PUT    /api/assets/{uid}                Update fields           [M1]
POST   /api/assets/{uid}/transition     State transition        [M1]
GET    /api/assets/{uid}/events         Event history           [M1]
GET    /api/assets/{uid}/children       Child assets (bundles)  [M2]
GET    /api/assets/{uid}/compat         Compatibility check     [M3]
GET    /api/assets/{uid}/attachments    List attachments        [M2]
GET    /api/assets/{uid}/benchmarks     Benchmark history       [M4]
```

### Filter params for `GET /api/assets`

| Param | Type | Example |
|---|---|---|
| `q` | string | `q=samsung` |
| `project` | string (multi, `type:key` pairs, or bare `type` for "any key of that type") | `project=PC Build:2-V2&project=HomeLab` |
| `category` | string (multi) | `category=GPU&category=CPU` |
| `state` | string (multi) | `state=in_service&state=planned` |
| `used_by` | string (`type:key`) | `used_by=PC Build:2-V2` |
| `location_id` | int (multi) | `location_id=3` |
| `from_date` | date | `from_date=2023-01-01` |
| `to_date` | date | `to_date=2025-12-31` |
| `min_amount` | float | `min_amount=100` |
| `max_amount` | float | `max_amount=1000` |
| `is_consumable` | bool | `is_consumable=false` |
| `warranty_expiring` | int (days) | `warranty_expiring=90` |
| `reallocated` | bool | `reallocated=true` — assets with at least one `reallocated` event |

---

## Projects

Project identity is the composite `(type, key)` pair — see
[data-model.md](data-model.md#project-identity-type-key). Both path segments
are required wherever a project is referenced.

```
GET    /api/projects                              List all                [M1]
POST   /api/projects                              Create                  [M1]
GET    /api/projects/{type}/{key}                 Detail                  [M1]
PUT    /api/projects/{type}/{key}                 Update (budget, notes)  [M1]
GET    /api/projects/{type}/{key}/assets          Assets for project      [M1]
GET    /api/projects/{type}/{key}/power           Power draw estimate     [M3]
GET    /api/projects/{type}/{key}/compat          Full compat check       [M3]
```

---

## Specs

```
GET    /api/specs                       List all                [M1]
GET    /api/specs/{uid}                 Single spec record      [M1]
PUT    /api/specs/{uid}                 Update fields           [M1]
```

---

## Events

```
GET    /api/events                      All events (filterable) [M1]
POST   /api/events                      Append event            [M1]
GET    /api/events/{id}                 Single event            [M1]
```

### Filter params for `GET /api/events`

| Param | Type | Example |
|---|---|---|
| `part_uid` | string | `part_uid=PCB2V2-GPU-001` |
| `event_type` | string (multi) | `event_type=reallocated` |
| `from_date` | date | |
| `to_date` | date | |

---

## Locations [M2]

```
GET    /api/locations                   List all                [M2]
POST   /api/locations                   Create                  [M2]
GET    /api/locations/{id}              Detail                  [M2]
PUT    /api/locations/{id}              Update                  [M2]
GET    /api/locations/{id}/assets       Assets at location      [M2]
```

---

## Attachments [M2]

```
GET    /api/attachments/{uid}           List for asset          [M2]
POST   /api/attachments/{uid}           Upload (multipart)      [M2]
GET    /api/attachments/{uid}/{id}      Download file           [M2]
DELETE /api/attachments/{uid}/{id}      Delete                  [M2]
```

---

## Benchmarks [M4]

```
GET    /api/benchmarks/{uid}            List for asset          [M4]
POST   /api/benchmarks/{uid}            Add result              [M4]
DELETE /api/benchmarks/{id}             Delete                  [M4]
```

---

## Graph [M3]

```
GET    /api/graph                       Nodes + edges JSON      [M3]
```

Response shape:
```json
{
  "nodes": [
    { "id": "PCB2V2-GPU-001", "label": "RTX 5070 Ti", "group": "asset", "value": 1399 },
    { "id": "PC Build:2-V2", "label": "PC Build 2 — V2", "group": "project" }
  ],
  "edges": [
    { "from": "PCB2V2-GPU-001", "to": "PC Build:2-V2", "label": "bought_for", "dashes": false },
    { "from": "PCB2V2-GPU-001", "to": "PC Build:2-V2", "label": "used_by", "dashes": true }
  ]
}
```

---

## AI Context [M1/M2]

```
GET    /api/ai-context/specs            Specs markdown          [M1]
GET    /api/ai-context/build/{type}/{key}      Build planning profile  [M1]
GET    /api/ai-context/upgrade/{type}/{key}    Upgrade planning        [M1]
GET    /api/ai-context/homelab          HomeLab nodes profile   [M2]
GET    /api/ai-context/purchasing       Budget + warranty       [M2]
```

All endpoints return `text/markdown`. Pass `?format=json` for structured
output. See [ai-context.md](ai-context.md) for profile content details.

---

## Dashboard + Reports

```
GET    /api/dashboard                   Widget data             [M1]
GET    /api/statistics                  Aggregate stats         [M1]
GET    /api/reports/spend               Spend breakdown         [M4]
GET    /api/reports/warranty            Expiry report           [M2]
GET    /api/reports/power               Power + cost estimate   [M3]
```

---

## Import / Export

```
GET    /api/export/excel                Download .xlsx          [M1]
GET    /api/export/json                 Download .json          [M1]
GET    /api/export/specs-md             Download/copy .md       [M1]
GET    /api/export/sqlite               Download .db snapshot   [V1]
POST   /api/import/excel                Upload .xlsx            [M1]
POST   /api/import/json                 Upload .json            [M1]
```

All imports auto-backup to `data/backups/assetforge_YYYYMMDD_HHMMSS.db` before
replacing.

---

## Settings

```
GET    /api/settings                    All settings            [M1]
PUT    /api/settings/{key}              Update value            [M1]
```

Default settings seeded at first run:

| Key | Default | Description |
|---|---|---|
| `electricity_rate_aud` | `0.32` | $/kWh for power cost estimates |
| `currency` | `AUD` | Display currency |
| `warranty_alert_days` | `90` | Days before expiry to show warning |
| `backup_on_import` | `true` | Auto-backup before any import |
| `data_path` | `./data` | Overridden by `DATA_PATH` env var |
