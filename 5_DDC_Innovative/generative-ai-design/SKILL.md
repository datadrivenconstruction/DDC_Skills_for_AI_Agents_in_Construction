---
name: "generative-ai-design"
description: "Generative design for construction: text-to-BIM concepts, option generation, and AI-assisted design iteration with cost and carbon feedback. Use when exploring early design options with AI."
---

# Generative AI Design for Construction (2026)

## What is real in 2026

Generative design in construction is **option generation with feedback**, not autonomous architecture: given site constraints, program and budget, an AI generates massing/typology options and scores them on cost, carbon and buildability — the human designer selects and refines.

## The loop

```
Constraints (site, program, budget)
        │
        ▼
Generate options (LLM/parametric/optimisation)
        │
        ▼
Quantify each option (BIM takeoff + CWICR cost + carbon)
        │
        ▼
Score & rank (cost/m², kgCO₂e/m², GFA efficiency)
        │
        ▼
Human selects → refine → detail
```

## Toolchain

| Stage | Tools |
|---|---|
| Massing generation | parametric tools (Rhino/Grasshopper, Dynamo) + LLM sketches |
| Text-to-concept | image models (Midjourney/DALL·E) for moodboards; text-to-BIM is early-stage (Hypar, Finch, qbiq) |
| Quantification | OpenConstructionERP BIM takeoff (`oce-bim-takeoff`) |
| Cost scoring | CWICR cost bases (`oce-load-cost-bases`) |
| Carbon scoring | `embodied-carbon-esg` |

## Prompt pattern for concept generation

```
"Generate 3 massing options for a 12,000 m² residential building on a 30×60 m
plot, 6 storeys, max 40% glazing, Berlin climate. For each: GFA, FAR,
indicative structure, kgCO₂e/m² (A1-A3), €/m² construction cost."
```

Then quantify and rank:

| Option | GFA | FAR | Cost/m² | kgCO₂e/m² | Verdict |
|---|---|---|---|---|---|
| A | 11,800 | 2.9 | 1,050 € | 310 | lowest cost |
| B | 12,400 | 3.1 | 1,180 € | 285 | lowest carbon |
| C | 12,100 | 3.0 | 1,120 € | 295 | balanced |

## Guardrails

- AI options are **starting points**, always human-reviewed and code-checked.
- Cost/carbon scores come from real databases (CWICR + EPD), not LLM guesses.
- Keep every option's inputs logged (reproducibility, AI Act transparency).
- Text-to-BIM models are not yet permit-grade — treat outputs as concepts.

## Resources

- Finch: https://finch3d.com · Hypar: https://hypar.io · qbiq: https://www.qbiq.ai
- Generative design overview: https://www.autodesk.com/solutions/generative-design
