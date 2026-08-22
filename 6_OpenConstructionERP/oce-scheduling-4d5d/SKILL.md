---
name: oce-scheduling-4d5d
description: "4D scheduling and 5D cost modelling in OpenConstructionERP: build task schedules, link tasks to BIM elements and BOQ lines, roll up the cost model over time, and export Gantt/sequence views. Use for schedule-cost integration workflows."
---

# 4D Scheduling & 5D Cost Model in OpenConstructionERP

## Concepts

- **4D** = schedule + BIM: every task can reference BIM elements so the sequence is visual.
- **5D** = schedule + cost: cost roll-ups per task/phase from linked BOQ lines.
- Both live on the same task graph — one source of truth for time and money.

## Workflow

1. **Build the task graph** — tasks, durations, dependencies (FS/SS/FF), milestones, critical path.
2. **Link BIM elements** to tasks (from `oce-bim-takeoff`) — visual sequencing and progress colouring.
3. **Link BOQ lines** to tasks (from `oce-estimate-boq`) — each task carries its direct cost.
4. **Roll up** — phase/project totals, cash-flow curves (cost over time), SPI/CPI views.
5. **Track** — daily diary entries and punch items update actuals; variance reports compare plan vs actual.

## Key endpoints

- tasks: create/update, dependencies, assignees, status board
- scheduling: timeline data for the Gantt, milestone markers
- cost model: `GET`-side roll-ups per task/phase; export to XLSX/PDF reports

## Integration rules

- One region/currency per project — the cost model never blends currencies.
- Quantity changes from BIM re-link update BOQ line quantities, which update the cost model in turn.
- Re-validate the BOQ after bulk changes; schedule conflicts surface in the timeline.

## Best practices

1. Keep dependencies explicit — the critical path is only as good as the logic.
2. Use milestones for payments/tender gates, not for activity progress.
3. Compare plan vs actual weekly; adjust the forecast, not history.
4. For multi-project portfolios, roll up by project and by currency group (never blended).
