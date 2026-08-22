---
name: oce-validation-engine
description: "Use the OpenConstructionERP validation engine: rule packs (BOQ quality, DIN 276, NRM, GAEB, MasterFormat, DPGF) that check estimates at import time and on demand. Use when verifying BOQ correctness or writing custom validation rules."
---

# Validation Engine in OpenConstructionERP

## Philosophy

"Validation is a first-class citizen." Every BOQ import (Excel/CSV/GAEB X83/X84) runs the configured rule packs **at import time**, so violations surface immediately — not when a user is staring at row 452.

## Built-in rule packs

| Pack | Checks |
|---|---|
| `boq_quality` | required fields, unit consistency, duplicate codes, quantity sanity |
| DIN 276 | cost-group codes valid, hierarchy consistent |
| NRM | element codes, measurement rules |
| GAEB | X83/X84 structure, item references |
| MasterFormat / DPGF | classification codes |

Configure the default set via `OE_DEFAULT_VALIDATION_RULE_SETS` (default `["boq_quality"]`); run on demand with `POST /api/v1/boqs/{id}/validate/`.

## Writing custom rules

A rule is: **condition + severity + message**. Example patterns:

```python
# pseudo-rule: labour share sanity on a BOQ line
def rule_labour_share(line):
    labour = line.components_labour_cost
    total = line.rate
    if total > 0 and labour / total > 0.95:
        return {"severity": "warning",
                "message": f"Line {line.code}: labour is {labour/total:.0%} of rate"}
```

Reconciliation rules (the ones that actually catch data problems):

- `qty × unit_price = cost` per component line (tolerance ±0.01 or rounding-aware).
- `Σ components = total_resource_cost_per_position` (markup applied on top).
- classification non-empty at every tree level.
- no negative quantities outside documented deduction lines.

## Where validation plugs in

1. **Import gate** — `import_inline_validation` (env) runs packs during upload.
2. **On demand** — `/boqs/{id}/validate/` returns violations with severity.
3. **Continuous** — the BOQ quality score updates live as the editor changes lines.

## Best practices

1. Fail imports on `error`-severity, warn on `warning` — never block a user silently.
2. Keep rule messages actionable: name the row, the expected value, the found value.
3. Version rule packs with the standards they encode (DIN 276:2018-12, NRM2, …).
4. Use validation as the QA agent's deterministic backbone (see `ai-agent-orchestration`).
