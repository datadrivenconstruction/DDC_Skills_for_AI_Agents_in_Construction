---
name: "embodied-carbon-esg"
description: "Estimate embodied carbon and produce ESG/climate reporting for construction: LCA per work item, material-based carbon factors, EU taxonomy and CSRD alignment. Use when a project needs carbon estimates or sustainability reporting."
---

# Embodied Carbon & ESG for Construction (2026)

## Why it matters now

From 2026 the EU CSRD (Corporate Sustainability Reporting Directive) and EU Taxonomy force contractors and developers to report embodied carbon (A1–A5 life-cycle modules), not just operational energy. Estimators need carbon numbers next to price numbers at the BOQ line level.

## Method

**Carbon = quantity × carbon factor**, applied per material resource line — exactly parallel to `quantity × unit price = cost`.

```
work item → components[] → material lines → quantity × EF (kg CO₂e / unit) → line carbon
BOQ roll-up: Σ line carbon = project embodied carbon (A1–A3) + transport/waste (A4–A5)
```

## Data sources for factors

| Source | Coverage | License |
|---|---|---|
| ÖKOBAUDAT (DE) | building materials | open |
| INIES (FR) FDES | products | open |
| ICE Database (UK) | embodied carbon | free registration |
| EPD libraries (ECO Platform) | manufacturer EPDs | varies |

The CWICR bases already carry per-resource **quantity** and **unit** — attach an `EF (kg CO₂e/unit)` column for the materials and the roll-up is automatic.

## What to compute per project

- **A1–A3** embodied carbon per BOQ section and per trade (from material lines).
- **A4–A5** transport + site waste assumptions (distance bands, waste rates per material).
- **kg CO₂e / m²** and **/ m³** intensity benchmarks for early design.
- **Hotspot report**: top 10 carbon lines (usually concrete, steel, aluminium, insulation).

## EU Taxonomy / CSRD alignment

- Map each work item to the taxonomy activity (construction of new buildings 7.1, renovation 7.2, …).
- Report DNSH (Do No Significant Harm) screening: circularity, waste, water for the top materials.
- Keep the evidence trail: factor source + version per line (auditors ask).

## Honest limits

- Carbon factors are regional and versioned — never mix databases without noting it.
- BIM takeoff gives geometry; carbon needs material takeoff (from CWICR `resource_name` + `resource_quantity`).
- Early-phase estimates are ±30–50%; label them as such.

## Resources

- ÖKOBAUDAT: https://oekobaudat.de
- ICE Database: https://circularecology.com/embodied-carbon-footprint-database.html
- EU CSRD: https://finance.ec.europa.eu/capital-markets-union-and-financial-markets/company-reporting-and-auditing/company-reporting/corporate-sustainability-reporting_en
