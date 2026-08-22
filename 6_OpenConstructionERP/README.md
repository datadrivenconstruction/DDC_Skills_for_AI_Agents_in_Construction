# 6_OpenConstructionERP — Skills for the OpenConstructionERP platform

Skills for working with [OpenConstructionERP](https://github.com/datadrivenconstruction/OpenConstructionERP) — the open-source (AGPL-3.0) construction ERP from DataDrivenConstruction: BOQ management, CAD/BIM takeoff, 4D scheduling, 5D cost modelling, tendering, field management, 180+ modules.

| Skill | What it covers |
|---|---|
| `oce-platform-overview` | Architecture, module map, API surface, quick start, data contracts |
| `oce-load-cost-bases` | Load the 8 national bases + 30 markets, catalog import, PPP market repricing, troubleshooting |
| `oce-estimate-boq` | BOQ workflows, cost item anatomy, text/photo/BIM estimation inputs, validation, exports |
| `oce-bim-takeoff` | RVT/IFC/DWG/DGN/PDF takeoff, bulk element→BOQ linking, measurement |
| `oce-scheduling-4d5d` | Task graphs, BIM-linked sequencing, cost roll-ups over time |
| `oce-cost-browser` | Classification tree, SQL + semantic search, variants, certainty, resource catalogs |
| `oce-mcp-integration` | MCP server wrapper around the ERP API for Claude Code / Antigravity / OpenCode |
| `oce-field-ops` | Punch list, daily diary, HSE observations, site task board |
| `oce-tendering` | Tender BOQ export (GAEB), bid comparison, risk register, reports |
| `oce-validation-engine` | Rule packs (BOQ quality, DIN 276, NRM, GAEB), custom rules, import gate |
| `oce-geo-coordination` | Geo hub (Cesium portfolio map), coordination hub with clash AI |
| `oce-property-dev` | Lead → SPA → handover: feasibility budgets, sales milestones, closeout |

## The cost data behind the platform

The CWICR collection (companion repo [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)) provides:

- **8 national bases** — Turkey Birim Fiyat, China Dinge, Brazil SINAPI, Spain BCCA, Italy Prezzario Toscana, Greece GGDE, Vietnam Dinh Muc, Indonesia AHSP (78,228 positions).
- **30 global markets** (CIS/GESN-FER-TER family).
- **26 language editions** per national base and **48 PPP-repriced market catalogs** per base.
- The **95-column CWICR master schema**: `rate_code`, `rate_original_name`/`rate_final_name`, `rate_unit`, `total_cost_per_position`, classification hierarchy, `resource_*` component lines.

## Typical flows

1. **Browse/load**: `POST /api/v1/costs/load-cwicr/TR_NATIONAL` → browse the tree, search items.
2. **Estimate**: build a BOQ, link cost items, link BIM elements, validate, export GAEB.
3. **Reprice**: pick a market card → the platform applies the PPP catalog to the base region.
4. **Track**: 4D/5D roll-ups, punch list, daily diary, validation engine.
