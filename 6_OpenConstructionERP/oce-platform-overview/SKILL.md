---
name: oce-platform-overview
description: "Guide to OpenConstructionERP: architecture, modules, API surface and quick start. Use when starting any OpenConstructionERP work, onboarding a user to the platform, or deciding which module/endpoint to use."
---

# OpenConstructionERP Platform Overview

## What it is

OpenConstructionERP is a self-hosted, open-source (AGPL-3.0) construction ERP by DataDrivenConstruction: BOQ management, CAD/BIM takeoff (RVT/IFC/DWG/DGN), 4D scheduling, 5D cost modelling, tendering, field management and 180+ modules in one platform. It runs embedded PostgreSQL (no Docker required) with a FastAPI backend and a Vite/React frontend.

> Homepage: https://openconstructionerp.com · Repo: https://github.com/datadrivenconstruction/OpenConstructionERP · Docs: https://openconstructionerp.com/docs

## Module map (what to use when)

| Need | Module | Key endpoints |
|---|---|---|
| Browse/load cost databases | `costs` | `GET /api/v1/costs/base-catalog`, `POST /api/v1/costs/load-cwicr/{db_id}`, `GET /api/v1/costs/?region=...&q=...` |
| Resource catalogs | `catalog` | `POST /api/v1/catalog/import/{region}`, `GET /api/v1/catalog/...` |
| Bill of quantities | `boq` | `POST /api/v1/boqs`, `GET /api/v1/boqs/{id}`, validate/import GAEB |
| BIM elements / takeoff | `bim` | upload RVT/IFC/DWG/DGN, link elements to BOQ lines |
| Schedule (4D) / cost (5D) | `scheduling` | tasks, dependencies, cost model roll-ups |
| Issues & quality | `punch_list`, `validation` | punch items, validation rule packs (DIN276/NRM/GAEB) |
| Site daily ops | `daily_diary`, `hse` | diary entries, safety observations |
| Docs / tasks / risks | `documents`, `tasks`, `risks` | file approvals, task board, risk register |
| Portfolio map | `geo_hub` | projects on a 3D globe |
| Property development | `property_dev` | lead → SPA → handover |

## Quick start (dev)

```bash
cd backend && python -m uvicorn app.main:create_app --factory --reload --port 8000
cd frontend && npm run dev   # http://localhost:5173
```

Auth: bootstrap admin (first registered user), JWT tokens, role-based permissions (viewer/editor/manager/admin). `POST /auth/register`, `POST /auth/login`.

## Data contracts to respect

- CWICR work-item parquets follow the **95-column master schema** (`rate_code`, `rate_original_name`, `rate_final_name`, `rate_unit`, `total_cost_per_position`, classification `collection/department/section/subsection/category`, resource lines `resource_*`, flags `is_material/is_machine/is_labor`).
- Region ids match `^[A-Z]{2,3}_[A-Z0-9]+$` (e.g. `TR_NATIONAL`, `ZH_CHINA`, `BR_NATIONAL`).
- The importer is idempotent on `(code, region)` — re-loading returns `already_loaded`.

## Best practices

1. Load the base first (`load-cwicr`), then swap language (automatic via `home_language_code`), then reprice markets via the catalog path.
2. Never invent prices: leave unpriced coefficient bases (VN, ID) as rate 0 and use the resource price sheet.
3. Verify an import with `GET /api/v1/costs/regions/stats/` and a sampled item's `rate` against the parquet's `total_cost_per_position`.
