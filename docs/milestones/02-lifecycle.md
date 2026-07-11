# Milestone 2 — Asset Lifecycle

**Depends on:** M1 complete and all acceptance criteria passing.

**References:** [Features](../features.md) · [Data Model](../data-model.md)

The tracker becomes a true asset manager. Parts have identity, location,
warranty, and attachments — not just a project and a price.

---

## Scope

Features from [features.md](../features.md) delivered in M2:

- Full state machine UI (all states exposed, not just M1 subset)
- Warranty fields: expiry, serial number, invoice ref, retailer
- Warranty expiry dashboard widget (< 90 days alert)
- Locations model: create locations, assign assets to locations
- Asset search by location ("Where is my spare PSU?")
- Location filter on asset table
- Reallocation flow: guided event UI (from/to project + location)
- Bulk reassign: select multiple assets, move to new project/location
- Attachments: upload + list for each asset (invoice PDF, photo)
- HomeLab + Purchasing AI context profiles
- "Generate AI Context" modal with full profile picker
- `warranty_expiring` filter param on `GET /api/assets`

---

## Schema Activations

No new tables or columns. M2 activates columns that were nullable in M1:

- `assets.warranty_months`, `assets.warranty_expiry`, `assets.rma_number`
- `assets.serial_number`, `assets.model_number`, `assets.manufacturer`
- `assets.invoice_ref`, `assets.location_id`
- `locations` table populated via UI
- `attachments` table and file routes go live

---

## Acceptance Criteria

| # | Criterion |
|---|---|
| 1 | Warranty expiry date calculated correctly from purchase_date + warranty_months |
| 2 | Dashboard widget shows assets expiring within `warranty_alert_days` setting |
| 3 | Location can be created, edited, and assigned to an asset |
| 4 | Asset table filters by location correctly |
| 5 | Reallocation flow appends a `reallocated` event with from/to project and location |
| 6 | Bulk reassign moves selected assets and appends events for each |
| 7 | PDF/image upload stores file in `data/attachments/{part_uid}/` and records DB entry |
| 8 | Attachment list shows in offcanvas card with download link |
| 9 | HomeLab AI context profile includes all assets in any `type="HomeLab"` project, with power specs |
| 10 | Purchasing profile includes budget remaining and warranty expiry dates |
