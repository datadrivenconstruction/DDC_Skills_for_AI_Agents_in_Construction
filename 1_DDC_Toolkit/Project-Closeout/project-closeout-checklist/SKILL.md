---
name: project-closeout-checklist
description: "Manage project closeout activities. Track completion of documentation, warranties, and final inspections."
---

# Project Closeout Checklist

## Technical Implementation

```python
import pandas as pd
from datetime import date
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ChecklistCategory(Enum):
    DOCUMENTATION = "documentation"
    FINANCIAL = "financial"
    INSPECTIONS = "inspections"
    TRAINING = "training"
    WARRANTIES = "warranties"
    PUNCHLIST = "punchlist"
    TURNOVER = "turnover"


class ItemStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class CloseoutItem:
    item_id: str
    description: str
    category: ChecklistCategory
    responsible_party: str
    due_date: date
    status: ItemStatus
    completed_date: Optional[date] = None
    notes: str = ""
    attachments: List[str] = field(default_factory=list)


class ProjectCloseoutChecklist:
    def __init__(self, project_name: str, substantial_completion: date):
        self.project_name = project_name
        self.substantial_completion = substantial_completion
        self.items: Dict[str, CloseoutItem] = {}
        self._load_standard_items()

    def _load_standard_items(self):
        standard = [
            ("Documentation", ChecklistCategory.DOCUMENTATION, [
                "As-built drawings", "O&M manuals", "Attic stock",
                "Keying schedule", "Equipment list"
            ]),
            ("Financial", ChecklistCategory.FINANCIAL, [
                "Final payment application", "Release of liens",
                "Consent of surety", "Final change orders"
            ]),
            ("Inspections", ChecklistCategory.INSPECTIONS, [
                "Final building inspection", "Fire marshal inspection",
                "Elevator inspection", "Certificate of Occupancy"
            ]),
            ("Training", ChecklistCategory.TRAINING, [
                "HVAC system training", "Fire alarm training",
                "Security system training", "BAS training"
            ]),
            ("Warranties", ChecklistCategory.WARRANTIES, [
                "Roofing warranty", "HVAC warranty", "Elevator warranty",
                "General contractor warranty"
            ])
        ]

        counter = 0
        for category_name, category, items in standard:
            for desc in items:
                counter += 1
                item_id = f"CLO-{counter:03d}"
                self.items[item_id] = CloseoutItem(
                    item_id=item_id,
                    description=desc,
                    category=category,
                    responsible_party="Contractor",
                    due_date=self.substantial_completion,
                    status=ItemStatus.NOT_STARTED
                )

    def add_item(self, description: str, category: ChecklistCategory,
                responsible_party: str, due_date: date) -> CloseoutItem:
        item_id = f"CLO-{len(self.items) + 1:03d}"
        item = CloseoutItem(
            item_id=item_id,
            description=description,
            category=category,
            responsible_party=responsible_party,
            due_date=due_date,
            status=ItemStatus.NOT_STARTED
        )
        self.items[item_id] = item
        return item

    def update_status(self, item_id: str, status: ItemStatus, notes: str = ""):
        if item_id in self.items:
            self.items[item_id].status = status
            if status == ItemStatus.COMPLETE:
                self.items[item_id].completed_date = date.today()
            if notes:
                self.items[item_id].notes = notes

    def get_completion_percentage(self) -> float:
        applicable = [i for i in self.items.values()
                     if i.status != ItemStatus.NOT_APPLICABLE]
        complete = [i for i in applicable if i.status == ItemStatus.COMPLETE]
        return (len(complete) / len(applicable) * 100) if applicable else 0

    def get_outstanding_items(self) -> List[CloseoutItem]:
        return [i for i in self.items.values()
                if i.status in [ItemStatus.NOT_STARTED, ItemStatus.IN_PROGRESS]]

    def get_summary_by_category(self) -> Dict[str, Dict[str, int]]:
        summary = {}
        for item in self.items.values():
            cat = item.category.value
            if cat not in summary:
                summary[cat] = {'total': 0, 'complete': 0, 'outstanding': 0}
            summary[cat]['total'] += 1
            if item.status == ItemStatus.COMPLETE:
                summary[cat]['complete'] += 1
            elif item.status != ItemStatus.NOT_APPLICABLE:
                summary[cat]['outstanding'] += 1
        return summary

    def export_checklist(self, output_path: str):
        data = [{
            'ID': i.item_id,
            'Description': i.description,
            'Category': i.category.value,
            'Responsible': i.responsible_party,
            'Due': i.due_date,
            'Status': i.status.value,
            'Completed': i.completed_date,
            'Notes': i.notes
        } for i in self.items.values()]
        pd.DataFrame(data).to_excel(output_path, index=False)
```

## Quick Start

```python
checklist = ProjectCloseoutChecklist("Office Tower", date(2024, 12, 1))

# Update item status
checklist.update_status("CLO-001", ItemStatus.COMPLETE, "Received from architect")

# Check progress
print(f"Completion: {checklist.get_completion_percentage():.1f}%")

outstanding = checklist.get_outstanding_items()
print(f"Outstanding items: {len(outstanding)}")
```

## Resources
- **DDC Book**: Chapter 5 - Project Closeout
