---
name: "ai-agent-orchestration"
description: "Orchestrate multiple AI agents for construction workflows: estimator, scheduler, document, QA and safety agents coordinated by a supervisor agent, with human checkpoints. Use when automating end-to-end project processes with agentic AI."
---

# AI Agent Orchestration for Construction (2026)

## Why agents now

2026 construction automation is agentic: not single prompts, but specialized agents that own a domain (estimating, scheduling, documents, QA, safety), share a common data spine (the ERP + CWICR cost bases), and are coordinated by a supervisor with human checkpoints.

## Agent roles

| Agent | Owns | Tools it calls |
|---|---|---|
| **Estimator agent** | BOQ + cost | CWICR search, QTO, market catalogs, `costs` API |
| **Scheduler agent** | Time (4D) | task graph, dependencies, critical path, resource leveling |
| **Document agent** | Specs & contracts | PDF/OCR extraction, clause NER, submittal/RFI routing |
| **QA agent** | Quality | validation rule packs (DIN276/NRM/GAEB), reconciliation checks |
| **Safety agent** | HSE | checklist generation, incident classification, regulations lookup |
| **Supervisor agent** | Orchestration | routes tasks, resolves conflicts, escalates to humans |

## Coordination patterns

```
Supervisor ──► Estimator ──► BOQ draft ──► human approves
    │              ▲
    ├──► Document ──► scope extracted (specs) ─┘
    ├──► Scheduler ──► draft schedule from BOQ quantities
    └──► QA ──► validate BOQ + schedule, report violations
```

1. **Data spine first** — all agents read/write the same ERP data (BOQ, tasks, cost items); no agent keeps private state.
2. **Human checkpoints** — binding numbers (prices, contracts) always pass a human gate.
3. **Deterministic validation** — QA uses arithmetic and rules, not LLM judgement, for reconciliation (e.g. `qty × price = cost`, markup conventions).
4. **Idempotent actions** — every agent action is re-runnable (the ERP import is idempotent on `(code, region)`; use it as the model).

## Guardrails

- Never let an agent invent a price: unpriced bases stay rate 0 until a market sheet exists.
- Confidence-scored matches below threshold go to a human.
- Log every agent decision with its inputs (the ERP's usage ledger pattern).
- EU AI Act (2024/1689): construction estimation assistance is low/limited risk, but keep human oversight for safety-critical decisions.

## Resources

- OpenConstructionERP: https://github.com/datadrivenconstruction/OpenConstructionERP
- CWICR cost bases: https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR
- Anthropic multi-agent patterns: https://www.anthropic.com/engineering/building-effective-agents
