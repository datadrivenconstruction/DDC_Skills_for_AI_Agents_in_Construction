---
name: oce-property-dev
description: "Property development lifecycle in OpenConstructionERP: lead to SPA to handover — feasibility, budgeting from cost bases, sales tracking and construction handover. Use for residential/commercial development projects."
---

# Property Development in OpenConstructionERP

## Lifecycle

```
Lead → Feasibility → Design → SPA (sale) → Construction → Handover
```

| Stage | What the platform does |
|---|---|
| Lead | land/opportunity record, key metrics |
| Feasibility | rough budget from CWICR cost bases (m² rates), margin check |
| Design | BIM model, BOQ, detailed estimate |
| SPA | sale/presale tracking, payment milestones |
| Construction | BOQ + schedule + field modules (see `oce-field-ops`) |
| Handover | closeout report, as-built docs, punch closeout |

## Feasibility estimation

Use cost-base intensity rates (per m²) from a loaded base:

```python
# rough budget: GFA × regional m² rate from CWICR items
gfa_m2 = 12_000
m2_rate = 1_050  # TRY/m², from cost-base roll-ups for residential
budget = gfa_m2 * m2_rate
```

Then refine with a real BOQ as design progresses. Early-phase estimates carry ±30% — label them.

## Sales & SPA

- Track units, price lists, sold/reserved/available.
- Payment milestones tied to construction progress (SPA installments).
- Cash-flow: sales inflow vs construction outflow over the schedule.

## Handover

- Punch-list closeout (see `oce-field-ops`).
- As-built package: final BOQ, models, docs, warranties.
- Defect liability tracking post-handover.

## Best practices

1. Keep feasibility numbers honest — they set the land price.
2. Tie SPA milestones to construction gates, not calendar guesses.
3. One project currency for the development; report to investors in their currency separately.
4. Retain the as-built package in the project record — it is the warranty baseline.
