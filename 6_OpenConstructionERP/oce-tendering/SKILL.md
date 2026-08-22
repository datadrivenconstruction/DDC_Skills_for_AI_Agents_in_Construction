---
name: oce-tendering
description: "Tendering and reporting in OpenConstructionERP: prepare tender BOQs, compare bids, manage risks, and generate reports (weekly, monthly, closeout). Use when a project goes to tender or needs reporting."
---

# Tendering, Risk & Reporting in OpenConstructionERP

## Tendering workflow

1. **Prepare the tender BOQ** — from the estimate (see `oce-estimate-boq`), export GAEB X83/X84 for the market.
2. **Issue to bidders** — track who received, who responded, deadlines.
3. **Bid comparison** — normalize bids to the BOQ structure (same items, same units), compare line-by-line and totals; flag outliers per line.
4. **Risk review** — attach risks (cost, schedule, contractual) to BOQ sections; score likelihood × impact.
5. **Award** — convert the winning bid to the contract baseline (BOQ + schedule freeze).

## Risk management

- Risk register per project: description, owner, probability, impact, mitigation, status.
- Risks linked to BOQ lines and tasks — a risk accepted changes the estimate and schedule together.
- Reports: top risks, exposure (risk × contingency), trend.

## Report generation

| Report | Frequency | Content |
|---|---|---|
| Weekly progress | weekly | done vs planned, issues, photos, punch stats |
| Monthly cost | monthly | budget vs actual per section, forecast |
| Cash-flow forecast | monthly | schedule × cost roll-up |
| Closeout | at completion | as-built BOQ, punch closeout, docs |

## API patterns

```http
GET  /api/v1/boqs/{id}/export?format=gaeb    # tender export
POST /api/v1/risks/                          # risk register
GET  /api/v1/reports/...                     # report endpoints (module-specific)
```

## Best practices

1. Freeze the tender BOQ version — compare bids against the SAME structure.
2. Normalize currencies before comparing bids (never blend).
3. Track bidder clarifications (RFIs) in the tender record, not in email.
4. Keep the risk register alive: review weekly, close or escalate.
