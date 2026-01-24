---
name: equipment-fleet-manager
description: "Manage construction equipment fleet. Track utilization, maintenance, and assignments."
---

# Equipment Fleet Manager

## Technical Implementation

```python
import pandas as pd
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class EquipmentStatus(Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    RETIRED = "retired"


class EquipmentType(Enum):
    CRANE = "crane"
    EXCAVATOR = "excavator"
    LOADER = "loader"
    FORKLIFT = "forklift"
    GENERATOR = "generator"
    COMPRESSOR = "compressor"
    SCAFFOLDING = "scaffolding"
    OTHER = "other"


@dataclass
class MaintenanceRecord:
    record_id: str
    equipment_id: str
    maintenance_type: str
    scheduled_date: date
    completed_date: Optional[date]
    cost: float
    notes: str = ""


@dataclass
class Assignment:
    assignment_id: str
    equipment_id: str
    project: str
    location: str
    start_date: date
    end_date: Optional[date]
    operator: str = ""


@dataclass
class Equipment:
    equipment_id: str
    name: str
    equipment_type: EquipmentType
    make: str
    model: str
    year: int
    status: EquipmentStatus
    hourly_rate: float
    daily_rate: float
    current_hours: float = 0
    last_maintenance: Optional[date] = None
    next_maintenance_hours: float = 500
    assignments: List[Assignment] = field(default_factory=list)


class EquipmentFleetManager:
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.equipment: Dict[str, Equipment] = {}
        self.maintenance_records: List[MaintenanceRecord] = {}
        self._equip_counter = 0
        self._assign_counter = 0

    def add_equipment(self, name: str, equipment_type: EquipmentType,
                     make: str, model: str, year: int,
                     hourly_rate: float, daily_rate: float) -> Equipment:
        self._equip_counter += 1
        equip_id = f"EQ-{self._equip_counter:04d}"

        equip = Equipment(
            equipment_id=equip_id,
            name=name,
            equipment_type=equipment_type,
            make=make,
            model=model,
            year=year,
            status=EquipmentStatus.AVAILABLE,
            hourly_rate=hourly_rate,
            daily_rate=daily_rate
        )
        self.equipment[equip_id] = equip
        return equip

    def assign_equipment(self, equip_id: str, project: str, location: str,
                        start_date: date, operator: str = "") -> Assignment:
        if equip_id not in self.equipment:
            return None

        self._assign_counter += 1
        assign_id = f"ASN-{self._assign_counter:04d}"

        assignment = Assignment(
            assignment_id=assign_id,
            equipment_id=equip_id,
            project=project,
            location=location,
            start_date=start_date,
            end_date=None,
            operator=operator
        )

        self.equipment[equip_id].assignments.append(assignment)
        self.equipment[equip_id].status = EquipmentStatus.IN_USE
        return assignment

    def return_equipment(self, equip_id: str, hours_used: float):
        if equip_id in self.equipment:
            equip = self.equipment[equip_id]
            equip.status = EquipmentStatus.AVAILABLE
            equip.current_hours += hours_used
            if equip.assignments:
                equip.assignments[-1].end_date = date.today()

    def schedule_maintenance(self, equip_id: str, maintenance_type: str,
                            scheduled_date: date, cost: float):
        if equip_id not in self.equipment:
            return
        record_id = f"MNT-{len(self.maintenance_records) + 1:04d}"
        record = MaintenanceRecord(record_id, equip_id, maintenance_type,
                                  scheduled_date, None, cost)
        self.maintenance_records[record_id] = record

    def get_available_equipment(self, equipment_type: EquipmentType = None) -> List[Equipment]:
        available = [e for e in self.equipment.values()
                    if e.status == EquipmentStatus.AVAILABLE]
        if equipment_type:
            available = [e for e in available if e.equipment_type == equipment_type]
        return available

    def get_utilization_report(self) -> Dict[str, Any]:
        in_use = sum(1 for e in self.equipment.values()
                    if e.status == EquipmentStatus.IN_USE)
        total = len(self.equipment)
        return {
            'total_equipment': total,
            'in_use': in_use,
            'available': sum(1 for e in self.equipment.values()
                            if e.status == EquipmentStatus.AVAILABLE),
            'maintenance': sum(1 for e in self.equipment.values()
                              if e.status == EquipmentStatus.MAINTENANCE),
            'utilization_rate': round(in_use / total * 100, 1) if total > 0 else 0
        }

    def export_fleet(self, output_path: str):
        data = [{
            'ID': e.equipment_id,
            'Name': e.name,
            'Type': e.equipment_type.value,
            'Make/Model': f"{e.make} {e.model}",
            'Year': e.year,
            'Status': e.status.value,
            'Hours': e.current_hours,
            'Daily Rate': e.daily_rate
        } for e in self.equipment.values()]
        pd.DataFrame(data).to_excel(output_path, index=False)
```

## Quick Start

```python
fleet = EquipmentFleetManager("ABC Construction")

crane = fleet.add_equipment("Tower Crane #1", EquipmentType.CRANE,
                           "Liebherr", "280 EC-H", 2020, 150, 1200)

assignment = fleet.assign_equipment(crane.equipment_id, "Office Tower",
                                   "Site A", date.today(), "John Smith")

report = fleet.get_utilization_report()
print(f"Utilization: {report['utilization_rate']}%")
```

## Resources
- **DDC Book**: Chapter 3.2 - Resource Management
