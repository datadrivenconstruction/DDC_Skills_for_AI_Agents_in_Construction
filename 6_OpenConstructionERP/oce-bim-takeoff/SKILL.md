---
name: oce-bim-takeoff
description: "CAD/BIM takeoff in OpenConstructionERP: upload Revit/IFC/DWG/DGN models, browse elements, bulk-link them to BOQ lines, measure DWG drawings and PDF plans, and push quantities into the estimate. Use for any model-based quantification workflow."
---

# BIM & CAD Takeoff in OpenConstructionERP

## Supported formats

| Format | In | Out |
|---|---|---|
| RVT (Revit) | upload | canonical JSON, GLB, thumbnails |
| IFC | upload (no IfcOpenShell required) | JSON/GLB |
| DWG | upload + layer browse | measured entities |
| DGN | upload | JSON/GLB |
| PDF | plan upload | vector/room measurements, dimension text (OCR optional) |
| LAS/LAZ/COPC | point-cloud viewer | decimated THREE.Points buffers |

Conversions run in-process via the bundled DDC converters; artifacts persist under `data/bim/{project_id}/{model_id}/`.

## Workflow

1. **Upload** the model to a project (`POST /api/v1/bim/...`).
2. **Browse** elements (walls, slabs, doors…) with quantities computed from the model geometry (area / volume / length).
3. **Bulk-link to BOQ** — select 100 wall elements → one BOQ line with aggregated area; the element↔cost links are stored, so changes flow both ways.
4. **Measure drawings** — DWG layers (vector entities) and PDF plans (rooms/walls) measure in place; results push into BOQ rows.
5. **Verify** — the linked quantities appear in the BOQ grid; the estimate quality score updates.

## Matching elements to cost items

- `POST /api/v1/costs/suggest-for-element` ranks cost items for a BIM element body (type, material, dimensions, classification).
- Matches carry confidence/certainty badges — review low-certainty picks before binding.

## 4D/5D hand-off

- Element quantities → BOQ (5D cost model).
- Task links → schedule (4D): each task can carry linked BIM elements for visual sequencing.

## Honest limitations

- The platform does not run FX/PPP conversions at takeoff time — markets are pre-priced upstream.
- RVT/IFC extraction uses the bundled converters; exotic family data may need the converter repo (`cad2data-Revit-IFC-DWG-DGN-pipeline`).
- Point-cloud ingestion supports LAS/LAZ/COPC (E57 via the optional extra).

## Best practices

1. Link elements in bulk, not one-by-one — the platform aggregates per BOQ line.
2. Keep original CAD only when you need re-conversion (`keep_original_cad`); artifacts are always retained.
3. Verify takeoff quantities against the model's own dimensions, then re-run BOQ validation.
