# Features

Full feature inventory. Each feature belongs to one milestone.
Milestone docs reference features by name rather than re-describing them.

`[M1]` = MVP · `[M2]` = Lifecycle · `[M3]` = Intelligence · `[M4]` = Analytics · `[V1]` = Polish

---

## Assets Table

| Feature | Milestone |
|---|---|
| Full-width Tabulator table with virtual scroll | M1 |
| Sortable columns (click header) | M1 |
| Column visibility toggle | M1 |
| URL-synced filters — bookmarkable | M1 |
| Row click → Offcanvas detail card | M1 |
| Multi-select filters: Project, Category, State, Used By | M1 |
| Date range filter: purchased between [from]–[to] | M1 |
| Amount range filter: min/max AUD | M1 |
| Text search across name, notes, compat notes | M1 |
| Quick filter chips: Planned only · Reallocated · HomeLab · Active | M1 |
| Filter count badge on toggle button | M1 |
| Clear all filters one-click | M1 |
| Consumables filter toggle | M2 |
| Location filter | M2 |
| Warranty status filter (expiring / expired) | M2 |

## Offcanvas Detail Card

| Feature | Milestone |
|---|---|
| Full part name, Part_UID, category, project | M1 |
| All Specs fields rendered | M1 |
| Purchase link (hyperlinked) | M1 |
| Inline note editor (HTMX POST on blur) | M1 |
| State badge with one-click transition dropdown | M1 |
| Reallocation breadcrumb trail (from→to project chain) | M1 |
| Event timeline (append-only, chronological) | M1 |
| Warranty fields: expiry, serial, invoice ref, retailer | M2 |
| Attachment list with upload | M2 |
| Child assets (bundle members) | M2 |
| Location field | M2 |
| Compatibility check panel | M3 |
| Benchmark history | M4 |
| Photos carousel | M4 |

## Dashboard

| Feature | Milestone |
|---|---|
| Total spend (all projects) | M1 |
| PC Builds vs HomeLab spend breakdown (bar) | M1 |
| State counts: Planned · Installed · In Service · Stored · Retired | M1 |
| Planned spend total (sum of Planned assets) | M1 |
| Recently added assets (last 5) | M1 |
| Quick links to each project | M1 |
| Warranty expiring widget (assets expiring in < 90 days) | M2 |
| Recently moved/reallocated assets | M2 |
| Unused components (Stored > 90 days) | M2 |
| Power draw estimates per project | M3 |
| Annual running cost estimate (AUD) | M3 |
| Category spend breakdown (donut chart) | M4 |
| Largest cost categories | M4 |
| Most reused asset | M4 |

## Project Summary

| Feature | Milestone |
|---|---|
| Card grid, one card per project | M1 |
| Bought-for total vs used-by total | M1 |
| Item count + state breakdown (donut chart) | M1 |
| Budget field + spend vs budget progress bar | M1 |
| Expand card → inline asset list | M1 |
| Power draw estimate per project | M3 |
| Upgrade cost delta (planned vs current) | M3 |

## Specs Table

| Feature | Milestone |
|---|---|
| Same filter/sort pattern as Assets table | M1 |
| Highlight rows with missing fields (yellow badge) | M1 |
| Inline cell edit for empty fields | M1 |
| AI context export button (copy to clipboard) | M1 |
| Power fields (idle_watt, peak_watt) exposed | M3 |
| Physical dimension fields exposed | M3 |
| Connectivity fields (PSU connectors, headers) exposed | M3 |

## AI Context Export

See [ai-context.md](ai-context.md) for profile details.

| Feature | Milestone |
|---|---|
| Specs markdown export (copy to clipboard / download) | M1 |
| Build Planning profile | M1 |
| Upgrade Planning profile | M1 |
| HomeLab profile | M2 |
| Purchasing / Warranty profile | M2 |
| "Generate AI Context" modal with profile picker | M2 |

## Asset Lifecycle

| Feature | Milestone |
|---|---|
| State machine enforced (valid transitions only) | M1 |
| Full state machine UI (all states, not just MVP subset) | M2 |
| Warranty fields: expiry, serial, invoice ref, RMA | M2 |
| Warranty expiry dashboard widget | M2 |
| Locations model: create locations, assign assets | M2 |
| "Where is my spare PSU?" — asset search by location | M2 |
| Reallocation flow: guided event with from/to project + location | M2 |
| Bulk reassign: select multiple assets, move to new project/location | M2 |
| Attachments: upload invoice PDF or photo | M2 |
| Maintenance event types in UI (repaste, dust, firmware, BIOS, SMART) | M3 |

## Compatibility Checker

| Feature | Milestone |
|---|---|
| Socket match rule | M3 |
| RAM generation match rule | M3 |
| PCIe generation check | M3 |
| PSU headroom (sum TDP vs PSU rating) | M3 |
| CPU cooler height vs case clearance | M3 |
| GPU length vs case clearance | M3 |
| ARGB / fan header count check | M3 |
| NVMe lane sharing check | M3 |
| BIOS version compatibility note | M3 |
| Memory QVL integration | M4 |
| Compatibility check panel in detail card | M3 |
| Compatibility check across full planned project | M3 |

## Power Estimation

| Feature | Milestone |
|---|---|
| Per-project idle/peak draw from TDP fields (fallback) | M3 |
| Per-project idle/peak from measured idle_watt/peak_watt | M3 |
| Annual running cost at configurable $/kWh | M3 |
| AUD defaults (Australian average rate) | M3 |
| $/kWh configurable in Settings | M3 |

## Visualisations

| Feature | Milestone |
|---|---|
| Part lineage graph (vis.js, force-directed) | M3 |
| Graph: nodes = assets (sized by cost) + projects | M3 |
| Graph: edges = bought_for (solid) + used_by (dashed) | M3 |
| Graph: click node → offcanvas detail card | M3 |
| Graph: filter (active only, include retired, HomeLab only) | M3 |
| Build timeline: horizontal, one lane per project | M3 |
| Timeline: hover → mini popover with name + cost | M3 |

## Analytics and Benchmarks

| Feature | Milestone |
|---|---|
| Benchmark history: log Cinebench, 3DMark, CrystalDiskMark | M4 |
| Compare scores before/after upgrade | M4 |
| Spend over time (monthly chart) | M4 |
| Upgrade ROI view | M4 |
| Consumables view + restock reminders | M4 |
| Smart search (across all fields, including event notes) | M4 |
| Warranty coverage summary report | M4 |

## Import / Export

| Feature | Milestone |
|---|---|
| Excel export (5-sheet workbook) | M1 |
| JSON export (full structured dump) | M1 |
| Specs markdown export | M1 |
| JSON import (full restore) | M1 |
| Auto-backup before any import | M1 |
| SQLite snapshot download | V1 |
| OCR-assisted receipt import | M4 |

## Polish

| Feature | Milestone |
|---|---|
| Mobile responsive layout | V1 |
| Keyboard navigation | V1 |
| `prefers-reduced-motion` respect | V1 |
| Dark / light mode toggle (persisted in Settings) | V1 |
| Automated backup on schedule | V1 |
| Docker deployment docs | V1 |
| Home Assistant power monitoring integration | M4 |
