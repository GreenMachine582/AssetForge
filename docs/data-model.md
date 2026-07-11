# Data Model

The full schema is defined at v0.1. Columns not yet exposed in the UI are
marked `-- [M2]` or later. They are nullable and do not affect MVP behaviour.

---

## Schema

```
┌──────────────────────────────────────────────────────────────────┐
│ projects                                                         │
│ (type, key) composite PK · name · date_started · budget · notes │
│ · is_active                                                      │
└────────────────────────┬─────────────────────────────────────────┘
                         │ bought_for_{type,key} / used_by_{type,key}
                         │ (composite FK × 2)
┌────────────────────────▼─────────────────────────────────────────┐
│ assets                                                           │
│                                                                  │
│ — Identity —                                                     │
│ part_uid PK · name · category · manufacturer  -- [M2]           │
│ model_number  -- [M2] · serial_number  -- [M2]                  │
│                                                                  │
│ — Ownership —                                                    │
│ bought_for_type/bought_for_key FK→projects (type,key)           │
│ used_by_type/used_by_key FK→projects (type,key)                 │
│ location_id FK→locations  -- [M2]                               │
│ parent_asset_uid FK→assets  -- [M2] (bundles)                   │
│                                                                  │
│ — Purchase —                                                     │
│ amount · purchase_date · retailer · invoice_ref  -- [M2]        │
│ link · is_consumable                                             │
│                                                                  │
│ — State —                                                        │
│ state ENUM (see state machine below)                             │
│                                                                  │
│ — Warranty — [M2]                                               │
│ warranty_months · warranty_expiry · rma_number                  │
│                                                                  │
│ — Meta —                                                         │
│ notes · created_at · updated_at                                  │
└──────┬────────────────────────────────────┬──────────────────────┘
       │                                    │
       ▼                                    ▼
┌─────────────────────┐         ┌─────────────────────────────┐
│ specs               │         │ events                      │
│ part_uid FK PK      │         │ id PK                       │
│                     │         │ part_uid FK→assets          │
│ — Interface —       │         │ event_type ENUM             │
│ socket_interface    │         │ from_project_type FK        │
│ form_factor         │         │ from_project_key FK         │
│ ram_gen             │         │ to_project_type FK          │
│ pcie_gen            │         │ to_project_key FK           │
│ chipset             │         │ from_location FK [M2]       │
│                     │         │ to_location FK [M2]         │
│ — Power —           │         │ date                        │
│ tdp_watt            │         │ notes                       │
│ idle_watt   -- [M3] │         │ metadata JSON               │
│ peak_watt   -- [M3] │         └─────────────────────────────┘
│                     │
│ — Physical —        │         ┌───────────────────────┐
│ capacity            │         │ locations       [M2]  │
│ slots_used          │         │ id PK                 │
│ slots_total         │         │ name                  │
│ speed_spec          │         │ description           │
│ cooler_height_mm    │         │ parent_id FK (nested) │
│ gpu_length_mm [M3]  │         └───────────────────────┘
│                     │
│ — Connectivity —    │         ┌───────────────────────┐
│ psu_connectors [M3] │         │ attachments     [M2]  │
│ argb_headers   [M3] │         │ id PK                 │
│ fan_headers    [M3] │         │ part_uid FK           │
│ nvme_lanes     [M3] │         │ filename              │
│                     │         │ filepath              │
│ — Notes —           │         │ file_type ENUM        │
│ compat_notes        │         │ description           │
└─────────────────────┘         │ created_at            │
                                 └───────────────────────┘
                                ┌───────────────────────┐
                                │ benchmarks      [M4]  │
                                │ id PK                 │
                                │ part_uid FK           │
                                │ tool · score · metric │
                                │ date · notes          │
                                │ event_id FK           │
                                └───────────────────────┘

                                ┌───────────────────────┐
                                │ settings              │
                                │ key PK · value · desc │
                                └───────────────────────┘
```

---

## Asset State Machine

All states and transitions are defined in the enum at schema creation.
M1 transitions are marked. The service enforces valid transitions — invalid
ones are rejected at the API layer, not in the UI.

```
  Wishlist
     │
  Planned ◄────────────────────────────── [M1]
     │
  Ordered
     │
  Delivered
     │
  Installed ◄──────────────────────────── [M1]
     │
  In Service ◄─────────────────────────── [M1]
     │           ┌─────────────────────┐
     │           │ Moved [M1] ◄──────┐ │
     │           │    │              │ │
     │           │  Removed [M1]     │ │
     │           │    │              │ │
     │           │  Stored ──────────┘ │
     │           └─────────────────────┘
     │
  Retired ─────────────────────────────── [M1] (terminal for tracker)
     │
  Sold
     │
  Disposed
```

Valid transitions are defined in `services/state_machine.py` as an adjacency
map. Adding a new valid transition is one line — no service logic changes.

```python
# services/state_machine.py
TRANSITIONS = {
    "planned":    ["ordered", "installed"],
    "ordered":    ["delivered", "planned"],
    "delivered":  ["installed"],
    "installed":  ["in_service"],
    "in_service": ["moved", "removed", "retired"],
    "moved":      ["in_service", "removed"],
    "removed":    ["stored", "in_service", "retired"],
    "stored":     ["in_service", "installed", "sold", "disposed"],
    "retired":    ["stored", "sold", "disposed"],
    "sold":       [],
    "disposed":   [],
}
```

---

## Event Types

All event types are defined in the enum at schema creation. M1 triggers are
noted. Future types exist in the enum and are insertable via the API even
before the UI exposes them.

| Event Type | Trigger | Notes |
|---|---|---|
| `purchased` | Seed / create asset | [M1] |
| `installed` | State → installed | [M1] |
| `reallocated` | Change `used_by` | [M1] |
| `removed` | State → removed | [M1] |
| `noted` | Inline note save | [M1] |
| `delivered` | State → delivered | M2 |
| `stored` | State → stored | M2 |
| `sold` | State → sold | M2 |
| `disposed` | State → disposed | M2 |
| `attachment_added` | File upload | M2 |
| `warranty_claimed` | Manual | M2 |
| `rma_opened` | Manual | M2 |
| `maintained` | Manual | M3 |
| `repasted` | Manual | M3 |
| `dust_cleaned` | Manual | M3 |
| `firmware_updated` | Manual | M3 |
| `bios_updated` | Manual | M3 |
| `smart_tested` | Manual / automation | M3 |
| `benchmark_run` | Benchmark entry | M4 |
| `photo_added` | File upload | M4 |

### Event metadata examples

The `metadata` JSON column carries event-specific structured data.

```json
// benchmark_run
{ "tool": "Cinebench R23", "score": 18432, "metric": "Multi-Core" }

// firmware_updated
{ "from_version": "1.0.1", "to_version": "1.2.3", "component": "SSD firmware" }

// smart_tested
{ "reallocated_sectors": 0, "power_on_hours": 4821, "health": "Good" }

// reallocated
{ "reason": "Cascaded from PC Build 2 (key 2-V1) during 9800X3D upgrade" }
```

---

## Part_UID Format

```
PCB2V2-GPU-001
│      │   └── zero-padded sequence (001, 002…)
│      └────── category code
└───────────── project code (no hyphens, no spaces)
```

UIDs belong to the **physical asset**, not its current project or location.
They never change, even through reallocation, storage, or resale.

### Category Codes

| Code | Category | Code | Category |
|---|---|---|---|
| `CPU` | Processor | `MON` | Monitor |
| `MOB` | Motherboard | `SBC` | Single-board computer |
| `RAM` | Memory | `PWR` | Power supply (SBC) |
| `GPU` | Graphics card | `UPS` | UPS unit |
| `PSU` | PC power supply | `NET` | Networking |
| `CAS` | Case | `FAN` | Fan / cooling |
| `COL` | CPU cooler | `CON` | Controller / hub |
| `STO` | Storage | `PER` | Peripheral |
| `CBL` | Cable | `PST` | Postage |

---

## Project Identity: (type, key)

A project's identity is the composite `(type, key)` pair — there is no fixed
prefix scheme and no fixed set of types. `type` is any free-text category you
choose; `key` only needs to be unique *within* that type, not globally. This
means the same `key` can be reused across different types without collision,
and adding a new category (a third build style, a new site, whatever) never
requires inventing a new prefix convention.

```
type          key      →  identifies
─────────────────────────────────────────────────────
PC Build      1        →  PC Build 1 (original)
PC Build      1-V2     →  PC Build 1 — Version 2 (upgrade)
PC Build      2        →  PC Build 2
PC Build      2-V2     →  PC Build 2 — Version 2 (planned)
HomeLab       NAS      →  HomeLab — RPI4 NAS node
HomeLab       RPI5     →  HomeLab — RPI5 edge node
HomeLab       Rack     →  HomeLab — future rack build (example)
Laptop        Work     →  Work laptop
Server        Rack-1   →  A rack server, unrelated to the HomeLab category
```

`type` is not restricted to `PC Build` / `HomeLab` — it's whatever categories
make sense for what you're tracking.
