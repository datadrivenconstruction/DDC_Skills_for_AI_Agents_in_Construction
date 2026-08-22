---
name: oce-estimate-boq
description: "Create bills of quantities and estimates in OpenConstructionERP: search cost items, build BOQ sections, link BIM elements in bulk, validate the BOQ, and export GAEB/XLSX/JSON. Use for any estimating workflow on the platform."
---

# BOQ & Estimation in OpenConstructionERP

## Workflow

1. **Pick a cost base** — load it (see `oce-load-cost-bases`) so items are searchable.
2. **Create the BOQ** — `POST /api/v1/boqs` with project, currency, classification standard (DIN 276 / NRM / MasterFormat / regional).
3. **Find items** — `GET /api/v1/costs/?region=TR_NATIONAL&q=duvar` (SQL search) or the semantic path (`/qdrant-search` when Qdrant is on). Every item carries a `components[]` breakdown (labour/material/machine with norm quantities and unit prices).
4. **Link quantities** — either manual entry, BIM bulk-link (`POST /api/v1/bim/elements/bulk-link` style endpoints aggregate area/volume/length per element), or PDF/DWG takeoff measurements.
5. **Validate** — `POST /api/v1/boqs/{id}/validate/` runs rule packs (BOQ quality, DIN276, NRM, GAEB) and returns violations; quality score updates live.
6. **Export** — GAEB X83/X84, XLSX, JSON for tendering.

## Cost item anatomy (what the platform stores per item)

```json
{
  "code": "15.115.1008",
  "description": "El veya kompresörle ... yumuşak kaya kazılması",
  "unit": "m³",
  "rate": 1044.5,
  "currency": "TRY",
  "classification": {"collection":"İnşaat","department":"İnşaat","section":"15.115","category":"CONSTRUCTION WORK"},
  "components": [
    {"name":"Kompresör","type":"equipment","quantity":0.2,"unit_rate":1991.73,"cost":398.35},
    {"name":"Düz işçi","type":"labor","quantity":1.25,"unit_rate":165.0,"cost":206.25}
  ],
  "metadata": {"labor_cost":437.25,"equipment_cost":398.35,"labor_hours":3.83}
}
```

## Estimation inputs the platform supports

| Input | Path | Notes |
|---|---|---|
| Natural language | `POST /api/v1/costs/match` (or AI estimate) | multi-lingual matching |
| Photo | AI photo-to-BOQ (GPT-4o + YOLO) | returns scoped BOQ with confidence |
| BIM model | element → cost matching (`/suggest-for-element`) | uses volume/area from the model |
| DWG/PDF | takeoff measurement | vectors/rooms detected, pushed into BOQ |

## Pricing notes (honest rules)

- National bases are priced in their home currency; markets are PPP-repriced upstream (no FX inside the platform).
- Coefficient bases (Vietnam Dinh Muc, Indonesia AHSP) import with `rate = 0` — attach a market resource price sheet before estimating.
- Turkey positions carry the source book's markup (e.g. 25% contractor profit) inside `total_cost_per_position`; resource sums reconcile to `total_resource_cost_per_position`.

## Best practices

1. Always verify `unit` matches your takeoff quantity (m²/m³/m/kg).
2. Check the `components[]` sum against `rate` before committing a binding estimate.
3. Keep the region currency on the BOQ; never blend currencies in one total.
4. Re-run validation after every bulk edit — the quality score is the fastest signal.
