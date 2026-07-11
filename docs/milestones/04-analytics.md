# Milestone 4 — Analytics

**Depends on:** M3 complete.

**References:** [Features](../features.md)

Benchmarks, consumables, smart search, reports, and automation hooks.
The tracker accumulates a performance history and starts to reduce manual work.

---

## Scope

- Benchmark history: log + compare Cinebench, 3DMark, CrystalDiskMark
- Compare scores before/after upgrade (chart)
- Consumables view + restock reminder logic
- Smart search across all fields including event notes and metadata
- Reports: spend over time, upgrade ROI, warranty coverage summary
- OCR-assisted receipt import (upload PDF → pre-fill asset fields)
- Home Assistant integration: read real power draw from HA sensors

---

## Notes

OCR receipt import uses a pluggable parser. The initial parser targets PCCG
and Core Electronics invoice PDFs (Matt's primary retailers). Others are
added without changing the import flow.

Home Assistant integration is read-only. The power estimation service checks
for a configured HA webhook/sensor; if absent, it falls back to TDP estimates.
No Home Assistant dependency is introduced into the core app.
