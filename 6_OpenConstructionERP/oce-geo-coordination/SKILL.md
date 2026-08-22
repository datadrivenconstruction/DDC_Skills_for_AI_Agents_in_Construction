---
name: oce-geo-coordination
description: "Portfolio mapping and model coordination in OpenConstructionERP: the 3D geo hub (Cesium), the coordination hub with clash AI, and geo-anchored projects. Use for multi-project portfolio views and BIM clash workflows."
---

# Geo Hub & Coordination in OpenConstructionERP

## Geo Hub (portfolio map)

- Projects anchored to real locations on a 3D globe (Cesium 3D Tiles).
- Each project card carries site map, BIM/DWG/PDF badges and live value.
- Multi-currency totals grouped by currency — never blended.

Workflow: create a project → set location/region/currency → the globe shows it; drill into the project for BOQ/BIM.

## Coordination Hub (clash AI)

- Combine models (RVT/IFC/DWG/DGN) in one coordination space.
- Clash detection: automatic clash report between disciplines (structure vs MEP vs architecture).
- Each clash becomes a task/punch item linked to the model elements — track until resolved.

Workflow: upload models → run clash detection → review clash list → convert clashes to issues → fix and re-run.

## Point clouds in the viewer

- Upload LAS/LAZ/COPC scans (E57 via optional extra) — decimated client-side for smooth viewing.
- Compare scan vs model for as-built verification.

## API patterns

```http
GET /api/v1/geo-hub/projects                # portfolio map data
POST /api/v1/coordination/models            # add model to coordination space
GET /api/v1/coordination/clashes            # clash report
```

(Endpoint names may vary by module version — check `backend/app/modules/*/router.py`.)

## Best practices

1. Anchor every project geographically — the portfolio view is the fastest status board.
2. Run clash detection early (design stage), not after procurement.
3. Convert clashes to issues immediately; an unowned clash list decays into noise.
4. Keep currency groups separate in portfolio totals.
