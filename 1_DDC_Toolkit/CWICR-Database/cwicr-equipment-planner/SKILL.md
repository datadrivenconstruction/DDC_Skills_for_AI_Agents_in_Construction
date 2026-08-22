---
name: "cwicr-equipment-planner"
description: "Plan equipment requirements using CWICR norms. Calculate equipment hours, scheduling, utilization rates, and rental vs purchase analysis."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🗄️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# CWICR Equipment Planner

## Business Case

### Problem Statement
Equipment is a major cost driver:
- What equipment is needed?
- For how long?
- Rent or buy?
- How to optimize utilization?

### Solution
Equipment planning using CWICR equipment norms to calculate requirements, schedule usage, and analyze rental vs purchase decisions.

### Business Value
- **Accurate requirements** - Based on validated norms
- **Optimized utilization** - Reduce idle time
- **Cost analysis** - Rent vs buy decisions
- **Scheduling** - Equipment availability planning

## Technical Implementation

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class EquipmentCategory(Enum):
    """Equipment categories."""
    EARTHMOVING = "earthmoving"
    LIFTING = "lifting"
    CONCRETE = "concrete"
    COMPACTION = "compaction"
    TRANSPORT = "transport"
    POWER_TOOLS = "power_tools"
    SCAFFOLDING = "scaffolding"
    PUMPING = "pumping"
    PILING = "piling"
    OTHER = "other"


class OwnershipType(Enum):
    """Equipment ownership types."""
    OWNED = "owned"
    RENTED = "rented"
    LEASED = "leased"


@dataclass
class EquipmentItem:
    """Equipment item requirement."""
    equipment_code: str
    description: str
    category: EquipmentCategory
    required_hours: float
    required_days: int
    daily_rate: float
    hourly_rate: float
    monthly_rate: float
    total_cost: float
    utilization_rate: float
    operator_required: bool
    operator_cost: float
    fuel_cost: float
    start_date: datetime
    end_date: datetime
    work_item_codes: List[str] = field(default_factory=list)


@dataclass
class EquipmentPlan:
    """Complete equipment plan."""
    project_name: str
    total_equipment_cost: float
    total_operator_cost: float
    total_fuel_cost: float
    total_cost: float
    equipment_items: List[EquipmentItem]
    by_category: Dict[str, float]
    schedule: Dict[str, List[str]]


# Equipment categories and typical rates
EQUIPMENT_DATA = {
    'excavator': {
        'category': EquipmentCategory.EARTHMOVING,
        'daily_rate': 450,
        'hourly_rate': 75,
        'monthly_rate': 9000,
        'fuel_per_hour': 15,  # liters
        'operator_hourly': 45
    },
    'crane': {
        'category': EquipmentCategory.LIFTING,
        'daily_rate': 800,
        'hourly_rate': 150,
        'monthly_rate': 16000,
        'fuel_per_hour': 20,
        'operator_hourly': 55
    },
    'concrete_mixer': {
        'category': EquipmentCategory.CONCRETE,
        'daily_rate': 150,
        'hourly_rate': 25,
        'monthly_rate': 3000,
        'fuel_per_hour': 8,
        'operator_hourly': 35
    },
    'compactor': {
        'category': EquipmentCategory.COMPACTION,
        'daily_rate': 200,
        'hourly_rate': 35,
        'monthly_rate': 4000,
        'fuel_per_hour': 10,
        'operator_hourly': 40
    },
    'pump': {
        'category': EquipmentCategory.PUMPING,
        'daily_rate': 300,
        'hourly_rate': 50,
        'monthly_rate': 6000,
        'fuel_per_hour': 12,
        'operator_hourly': 40
    },
    'scaffold': {
        'category': EquipmentCategory.SCAFFOLDING,
        'daily_rate': 50,
        'hourly_rate': 0,
        'monthly_rate': 1000,
        'fuel_per_hour': 0,
        'operator_hourly': 0
    },
    'loader': {
        'category': EquipmentCategory.EARTHMOVING,
        'daily_rate': 350,
        'hourly_rate': 60,
        'monthly_rate': 7000,
        'fuel_per_hour': 12,
        'operator_hourly': 40
    },
    'truck': {
        'category': EquipmentCategory.TRANSPORT,
        'daily_rate': 250,
        'hourly_rate': 40,
        'monthly_rate': 5000,
        'fuel_per_hour': 15,
        'operator_hourly': 35
    }
}


class CWICREquipmentPlanner:
    """Plan equipment requirements from CWICR data."""

    def __init__(self, cwicr_data: pd.DataFrame,
                 fuel_price: float = 1.5):  # USD per liter
        self.work_items = cwicr_data
        self.fuel_price = fuel_price
        self._index_data()

    def _index_data(self):
        """Index work items for fast lookup."""
        if 'work_item_code' in self.work_items.columns:
            self._work_index = self.work_items.set_index('work_item_code')
        else:
            self._work_index = None

    def _get_equipment_info(self, description: str) -> Dict[str, Any]:
        """Get equipment info from description."""
        desc_lower = str(description).lower()

        for equip_name, info in EQUIPMENT_DATA.items():
            if equip_name in desc_lower:
                return info

        # Default equipment
        return {
            'category': EquipmentCategory.OTHER,
            'daily_rate': 200,
            'hourly_rate': 35,
            'monthly_rate': 4000,
            'fuel_per_hour': 10,
            'operator_hourly': 35
        }

    def extract_equipment_requirements(self,
                                        items: List[Dict[str, Any]],
                                        project_start: datetime = None) -> List[EquipmentItem]:
        """Extract equipment requirements from work items."""

        if project_start is None:
            project_start = datetime.now()

        equipment = defaultdict(lambda: {
            'hours': 0,
            'work_items': [],
            'start_day': float('inf'),
            'end_day': 0
        })

        for item in items:
            code = item.get('work_item_code', item.get('code'))
            qty = item.get('quantity', 0)
            start_day = item.get('start_day', 0)
            duration = item.get('duration_days', 1)

            if self._work_index is not None and code in self._work_index.index:
                work_item = self._work_index.loc[code]

                equipment_norm = float(work_item.get('equipment_norm', 0) or 0)
                equipment_desc = str(work_item.get('equipment_description',
                                                    work_item.get('category', 'General')))

                equip_hours = equipment_norm * qty

                if equip_hours > 0:
                    equip_key = equipment_desc
                    equipment[equip_key]['hours'] += equip_hours
                    equipment[equip_key]['work_items'].append(code)
                    equipment[equip_key]['description'] = equipment_desc
                    equipment[equip_key]['start_day'] = min(
                        equipment[equip_key]['start_day'], start_day
                    )
                    equipment[equip_key]['end_day'] = max(
                        equipment[equip_key]['end_day'], start_day + duration
                    )

        # Convert to EquipmentItem list
        result = []
        for equip_key, data in equipment.items():
            info = self._get_equipment_info(data['description'])
            hours = data['hours']

            # Calculate days needed
            days_needed = int(np.ceil(hours / 8))  # 8-hour days

            # Dates
            start_date = project_start + timedelta(days=data.get('start_day', 0))
            actual_days = max(days_needed, data.get('end_day', 0) - data.get('start_day', 0))
            end_date = start_date + timedelta(days=actual_days)

            # Utilization
            available_hours = actual_days * 8
            utilization = hours / available_hours if available_hours > 0 else 0

            # Costs
            equipment_cost = actual_days * info['daily_rate']
            operator_cost = hours * info['operator_hourly'] if info['operator_hourly'] > 0 else 0
            fuel_cost = hours * info['fuel_per_hour'] * self.fuel_price

            result.append(EquipmentItem(
                equipment_code=equip_key[:20],
                description=data['description'],
                category=info['category'],
                required_hours=round(hours, 1),
                required_days=actual_days,
                daily_rate=info['daily_rate'],
                hourly_rate=info['hourly_rate'],
                monthly_rate=info['monthly_rate'],
                total_cost=round(equipment_cost, 2),
                utilization_rate=round(utilization * 100, 1),
                operator_required=info['operator_hourly'] > 0,
                operator_cost=round(operator_cost, 2),
                fuel_cost=round(fuel_cost, 2),
                start_date=start_date,
                end_date=end_date,
                work_item_codes=data['work_items']
            ))

        return result

    def generate_equipment_plan(self,
                                items: List[Dict[str, Any]],
                                project_name: str = "Project") -> EquipmentPlan:
        """Generate complete equipment plan."""

        equipment = self.extract_equipment_requirements(items)

        # Totals
        total_equipment = sum(e.total_cost for e in equipment)
        total_operator = sum(e.operator_cost for e in equipment)
        total_fuel = sum(e.fuel_cost for e in equipment)

        # By category
        by_category = defaultdict(float)
        for e in equipment:
            by_category[e.category.value] += e.total_cost

        # Schedule (equipment by date)
        schedule = defaultdict(list)
        for e in equipment:
            current = e.start_date
            while current < e.end_date:
                date_key = current.strftime('%Y-%m-%d')
                schedule[date_key].append(e.description)
                current += timedelta(days=1)

        return EquipmentPlan(
            project_name=project_name,
            total_equipment_cost=total_equipment,
            total_operator_cost=total_operator,
            total_fuel_cost=total_fuel,
            total_cost=total_equipment + total_operator + total_fuel,
            equipment_items=equipment,
            by_category=dict(by_category),
            schedule=dict(schedule)
        )

    def rent_vs_buy_analysis(self,
                             equipment_item: EquipmentItem,
                             purchase_price: float,
                             useful_life_months: int = 60,
                             residual_value_pct: float = 0.20) -> Dict[str, Any]:
        """Analyze rent vs buy decision."""

        # Rental cost
        rental_cost = equipment_item.required_days * equipment_item.daily_rate

        # Ownership cost (simplified)
        monthly_depreciation = (purchase_price * (1 - residual_value_pct)) / useful_life_months
        months_needed = equipment_item.required_days / 30
        ownership_cost = monthly_depreciation * months_needed

        # Break-even analysis
        break_even_days = purchase_price / equipment_item.daily_rate
        break_even_months = break_even_days / 30

        return {
            'equipment': equipment_item.description,
            'rental_cost': round(rental_cost, 2),
            'ownership_cost_period': round(ownership_cost, 2),
            'purchase_price': purchase_price,
            'recommendation': 'RENT' if rental_cost < ownership_cost else 'BUY',
            'savings': abs(rental_cost - ownership_cost),
            'break_even_months': round(break_even_months, 1),
            'utilization_rate': equipment_item.utilization_rate
        }

    def optimize_utilization(self,
                             equipment: List[EquipmentItem],
                             target_utilization: float = 80.0) -> Dict[str, Any]:
        """Analyze and suggest utilization improvements."""

        analysis = {
            'underutilized': [],
            'well_utilized': [],
            'overutilized': [],
            'recommendations': []
        }

        for e in equipment:
            if e.utilization_rate < target_utilization - 20:
                analysis['underutilized'].append({
                    'equipment': e.description,
                    'utilization': e.utilization_rate,
                    'potential_saving': e.total_cost * (1 - e.utilization_rate / 100)
                })
                analysis['recommendations'].append(
                    f"Consider shorter rental period for {e.description} "
                    f"(current utilization: {e.utilization_rate}%)"
                )
            elif e.utilization_rate > target_utilization + 20:
                analysis['overutilized'].append({
                    'equipment': e.description,
                    'utilization': e.utilization_rate
                })
                analysis['recommendations'].append(
                    f"Consider additional unit of {e.description} to reduce strain"
                )
            else:
                analysis['well_utilized'].append({
                    'equipment': e.description,
                    'utilization': e.utilization_rate
                })

        analysis['average_utilization'] = np.mean([e.utilization_rate for e in equipment]) if equipment else 0

        return analysis

    def export_to_excel(self,
                       plan: EquipmentPlan,
                       output_path: str) -> str:
        """Export equipment plan to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Equipment list
            equip_df = pd.DataFrame([
                {
                    'Description': e.description,
                    'Category': e.category.value,
                    'Hours': e.required_hours,
                    'Days': e.required_days,
                    'Daily Rate': e.daily_rate,
                    'Equipment Cost': e.total_cost,
                    'Operator Cost': e.operator_cost,
                    'Fuel Cost': e.fuel_cost,
                    'Total Cost': e.total_cost + e.operator_cost + e.fuel_cost,
                    'Utilization %': e.utilization_rate,
                    'Start': e.start_date.strftime('%Y-%m-%d'),
                    'End': e.end_date.strftime('%Y-%m-%d')
                }
                for e in plan.equipment_items
            ])
            equip_df.to_excel(writer, sheet_name='Equipment', index=False)

            # Summary
            summary_df = pd.DataFrame([{
                'Total Equipment Cost': plan.total_equipment_cost,
                'Total Operator Cost': plan.total_operator_cost,
                'Total Fuel Cost': plan.total_fuel_cost,
                'Grand Total': plan.total_cost
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        return output_path
```

## Quick Start

```python
from datetime import datetime

# Load CWICR data
cwicr = pd.read_parquet("TR_workitems_costs_resources_DDC_CWICR.parquet")

# Initialize planner
planner = CWICREquipmentPlanner(cwicr, fuel_price=1.5)

# Define work items
items = [
    {'work_item_code': 'EXCV-001', 'quantity': 500, 'start_day': 0, 'duration_days': 10},
    {'work_item_code': 'CONC-002', 'quantity': 200, 'start_day': 10, 'duration_days': 15}
]

# Generate plan
plan = planner.generate_equipment_plan(items, "Building A")

print(f"Equipment Cost: ${plan.total_equipment_cost:,.2f}")
print(f"Operator Cost: ${plan.total_operator_cost:,.2f}")
print(f"Total: ${plan.total_cost:,.2f}")
```

## Common Use Cases

### 1. Rent vs Buy Analysis
```python
for equip in plan.equipment_items:
    analysis = planner.rent_vs_buy_analysis(equip, purchase_price=50000)
    print(f"{equip.description}: {analysis['recommendation']}")
```

### 2. Utilization Optimization
```python
optimization = planner.optimize_utilization(plan.equipment_items)
for rec in optimization['recommendations']:
    print(rec)
```

### 3. Export Plan
```python
planner.export_to_excel(plan, "equipment_plan.xlsx")
```

## Resources
- **GitHub**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
- **DDC Book**: Chapter 3.1 - Equipment Resource Planning
