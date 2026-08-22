---
name: "ai-act-compliance"
description: "Check construction AI systems against the EU AI Act (Regulation 2024/1689): classify risk of estimation, scheduling, CV and agent tools, document transparency, keep human oversight. Use when deploying or auditing AI in construction."
---

# EU AI Act Compliance for Construction AI (2026)

## Why it matters

The EU AI Act (2024/1689) is binding from 2025–2027 in phases. Construction AI — estimators, computer-vision site monitoring, agent assistants — mostly lands in **limited** or **minimal** risk, but misclassification or missing transparency is a compliance failure, and high-risk uses (safety-critical, worker monitoring, access decisions) bring real obligations.

## Classification quick check for construction tools

| System | Likely tier | Obligations |
|---|---|---|
| Cost estimation assistant (BOQ, unit prices) | limited / minimal | transparency (users know it is AI), basic logging |
| Schedule optimisation | minimal | none beyond general law |
| Site camera CV for progress | limited | transparency, data minimisation |
| CV for PPE/safety enforcement | **high risk (safety component?)** | full: risk management, data governance, human oversight, logs |
| Worker performance monitoring | **high risk (employment)** | prohibited or high-risk — treat carefully |
| AI agent that signs/submits binding documents | not allowed without human | human oversight mandatory |

Rule of thumb: **if a human previously had to sign it, an AI must not sign it alone.**

## Practical compliance checklist (per tool)

1. **Classify** — document the risk tier and reasoning.
2. **Transparency** — users must know they interact with AI output; mark AI-generated estimates as such.
3. **Human oversight** — a qualified human reviews binding estimates, contracts, safety decisions.
4. **Data governance** — minimal personal data in site CV; no biometric identification.
5. **Logging** — record model, inputs, outputs, version (the ERP usage-ledger pattern).
6. **Instructions for use** — document limitations (e.g. early estimates ±30–50%).

## Mapping to the DDC stack

- `oce-estimate-boq`, `cost-estimation-*`, `cost-prediction`: limited risk — add AI-output labels.
- `progress-monitoring-cv`, `defect-detection-ai`: limited — no personal data, transparency.
- `safety-compliance-checker` enforcing PPE via CV: reclassify — keep a human in the loop, document.
- `ai-agent-orchestration`: supervisor must be a human at decision gates.

## Resources

- EU AI Act text: https://artificialintelligenceact.eu
- Commission guidance & codes of practice: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
