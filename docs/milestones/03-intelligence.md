# Milestone 3 — Intelligence

**Depends on:** M2 complete.

**References:** [Features](../features.md) · [Architecture](../architecture.md)

Compatibility checking, power estimation, maintenance tracking, and
visualisations. The tracker starts answering questions, not just storing data.

---

## Scope

Features from [features.md](../features.md) delivered in M3:

**Compatibility checker** (rule-based, pluggable registry)
- Socket, RAM gen, PCIe gen, PSU headroom, cooler height, GPU length,
  ARGB/fan headers, NVMe lane sharing, BIOS version note
- Compatibility panel in offcanvas detail card
- Full project compatibility check (`GET /api/projects/{key}/compat`)

**Power estimation**
- Per-project idle/peak from TDP (fallback) and measured watt fields
- Annual running cost at configurable $/kWh
- Dashboard widget + report endpoint
- `idle_watt` and `peak_watt` exposed in Specs table

**Maintenance events** exposed in UI
- Repaste, dust clean, firmware update, BIOS update, SMART test
- All append to event log; `metadata` carries structured data

**Visualisations**
- Part lineage graph (vis.js force-directed)
- Build timeline (horizontal, one lane per project)
- Physical dimension fields activated in Specs (cooler height, GPU length,
  PSU connectors, ARGB/fan headers, NVMe lanes)

---

## Key Design Notes

`services/compatibility.py` rule registry — new rules are functions, not
config. Adding a new check does not change any caller.

```python
# Example rule signature
def check_gpu_length(asset: Asset, project: Project) -> CompatResult:
    case_clearance = get_spec(project, "case", "gpu_length_mm")
    gpu_length = asset.spec.gpu_length_mm
    if not case_clearance or not gpu_length:
        return CompatResult.unknown("GPU length or case clearance not specified")
    if gpu_length > case_clearance:
        return CompatResult.fail(f"GPU {gpu_length}mm exceeds case clearance {case_clearance}mm")
    return CompatResult.ok()
```

---

## Acceptance Criteria

| # | Criterion |
|---|---|
| 1 | Socket mismatch between CPU and motherboard returns `CompatResult.fail` |
| 2 | PSU headroom check correctly sums TDP of all In Service assets vs PSU rating |
| 3 | GPU length check uses `gpu_length_mm` from specs and `gpu_length_mm` on case |
| 4 | Power estimation for HL-NAS + HL-RPI5 produces plausible idle/peak figures |
| 5 | Annual cost changes correctly when `electricity_rate_aud` setting is updated |
| 6 | Part lineage graph renders all assets + projects as nodes with correct edges |
| 7 | Clicking a graph node opens the offcanvas detail card for that asset |
| 8 | Maintenance event (e.g. repaste) appends to event log with correct metadata |
