---
name: oce-cost-browser
description: "Browse and search the OpenConstructionERP cost database: classification tree, SQL and semantic search, autocomplete, certainty badges, and the resource catalog. Use when a user wants to explore cost data without building a BOQ yet."
---

# Cost Browser in OpenConstructionERP

## The cost database (2026)

Eight national bases (78,228 positions) plus 30 global markets, each in the 95-column CWICR master schema, with 26 language editions and 48 PPP-repriced resource catalogs per national base.

## Browsing paths

| Path | Endpoint | Purpose |
|---|---|---|
| Base picker | `GET /api/v1/costs/base-catalog` | list families, variants, currencies, positions, loaded badge |
| List / search | `GET /api/v1/costs/?region=...&q=...&limit=...` | SQL keyword search (works without Qdrant) |
| Tree | `GET /api/v1/costs/category-tree/?region=...` | collection → department → section → subsection → category |
| Item detail | `GET /api/v1/costs/{id}` | full `components[]` breakdown + metadata + variants |
| Autocomplete | `GET /api/v1/costs/autocomplete?q=...` | fast typeahead for the BOQ editor |
| Semantic | `/qdrant-search` (Qdrant) | BGE-M3 multilingual ranking across `cwicr_<lang>_v3` collections |

## Classification tree

Every item carries `classification{}` built from the parquet:

```
collection (source, e.g. "İnşaat")
 └─ department (discipline, e.g. "İnşaat")
     └─ section (chapter, e.g. "LAVABOLAR")
         └─ subsection
             └─ category (normalized type, e.g. "CONSTRUCTION WORK")
```

Chinese positions may show partial classification (source scope) — that is honest, not a bug.

## Certainty & variants

- Some items carry **abstract-resource variants** (e.g. concrete grade pickers): the item detail exposes `variants[]` with per-variant prices; picking one replaces the BOQ line description/price.
- `certainty` badges grade how confidently an item matches a BIM element — review low-certainty picks.

## Resource catalog

The `catalog` module stores the compact per-market catalogs (`resource_code, name, type, category, unit, price_avg/min/max, currency, usage_count`, classification under `specifications`). Coefficient bases (VN, ID) seed an editable **resource price sheet** here — that is how they become estimable.

## Best practices

1. Always filter by region — the same code exists in several bases with different prices.
2. Trust the tree over free-text for browsing; use free-text for finding.
3. Treat `rate = 0` on VN/ID as "not yet priced", not as free work.
