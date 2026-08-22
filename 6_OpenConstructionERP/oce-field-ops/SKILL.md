---
name: oce-field-ops
description: "Field operations in OpenConstructionERP: punch list, daily diary, HSE observations and task tracking on site. Use when automating construction site workflows (deficiencies, diaries, safety, site tasks)."
---

# Field Operations in OpenConstructionERP

## Modules for the site

| Module | Purpose | Typical flow |
|---|---|---|
| `punch_list` | Deficiencies / snag items | create item → assign → verify → close |
| `daily_diary` | Daily site reports | weather, workforce, progress, incidents |
| `hse` | Health, safety, environment | observations, incidents, checklists |
| `tasks` | Site task board | Kanban, issues linked to BIM elements |

## Punch list workflow

1. Inspector (or a photo) creates a punch item: location, trade, priority, due date, photo attachment.
2. Item auto-assigns to the responsible trade (routing rules).
3. Contractor marks fixed → inspector verifies → item closes.
4. Closeout report: open vs closed per trade/zone, aging.

## Daily diary automation

- Prefill from the schedule: planned activities of the day.
- Inputs: weather (integrated), workforce counts, deliveries, issues, photos.
- Auto-summary to the weekly progress report (see `oce-scheduling-4d5d` roll-ups).

## HSE

- Safety observations: classify (PPE, fall protection, housekeeping…), severity, follow-up.
- Incident reports with photo evidence and root-cause fields.
- Checklists per trade and per regulation (OSHA / local).

## API patterns

```http
POST /api/v1/punch-list/          # create punch item
PATCH /api/v1/punch-list/{id}     # status/assignee
POST /api/v1/daily-diary/         # diary entry
GET  /api/v1/tasks/?project=...   # site tasks
```

(Endpoint names may vary by module version — check `backend/app/modules/*/router.py` for the authoritative surface.)

## Best practices

1. Link punch items to BIM elements — the 3D view shows open deficiencies in place.
2. Make the daily diary the single source of actuals (it feeds variance reports).
3. Photos on every issue: evidence beats memory in disputes.
4. Close the loop — every observation ends in an action, not a note.
