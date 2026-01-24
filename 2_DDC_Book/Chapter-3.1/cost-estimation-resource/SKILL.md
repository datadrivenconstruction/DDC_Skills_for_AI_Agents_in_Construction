---
name: cost-estimation-resource
description: "Calculate construction costs using resource-based method. Estimate project costs from work items, physical resource norms, and current prices."
---

# Cost Estimation - Resource Method

## Business Case

### Problem Statement
Traditional costing challenges:
- Fixed unit prices become outdated
- No visibility into cost components
- Difficult to adjust for conditions
- Limited cost analysis capability

### Solution
Resource-based costing separates physical resource consumption (norms) from prices, enabling accurate, adjustable, and transparent cost estimation.

## Technical Implementation

```python
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ResourceType(Enum):
    LABOR = "labor"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    SUBCONTRACTOR = "subcontractor"


@dataclass
class Resource:
    code: str
    name: str
    resource_type: ResourceType
    unit: str
    unit_price: float
    currency: str = "USD"


@dataclass
class ResourceNorm:
    resource_code: str
    consumption: float  # Units per work item unit
    waste_factor: float = 1.0  # 1.1 = 10% waste


@dataclass
class WorkItem:
    code: str
    name: str
    unit: str
    resources: List[ResourceNorm] = field(default_factory=list)


@dataclass
class CostLineItem:
    work_item_code: str
    work_item_name: str
    quantity: float
    unit: str
    labor_cost: float
    material_cost: float
    equipment_cost: float
    subcontractor_cost: float
    total_cost: float


class ResourceBasedEstimator:
    """Calculate costs using resource-based method."""

    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.work_items: Dict[str, WorkItem] = {}
        self.overhead_rate: float = 0.15
        self.profit_rate: float = 0.10

    def add_resource(self, resource: Resource):
        """Add resource to database."""
        self.resources[resource.code] = resource

    def add_work_item(self, work_item: WorkItem):
        """Add work item with resource norms."""
        self.work_items[work_item.code] = work_item

    def load_resources_from_df(self, df: pd.DataFrame):
        """Load resources from DataFrame."""

        for _, row in df.iterrows():
            resource = Resource(
                code=row['code'],
                name=row['name'],
                resource_type=ResourceType(row['type'].lower()),
                unit=row['unit'],
                unit_price=float(row['unit_price']),
                currency=row.get('currency', 'USD')
            )
            self.add_resource(resource)

    def load_work_items_from_df(self, items_df: pd.DataFrame, norms_df: pd.DataFrame):
        """Load work items and norms from DataFrames."""

        # Group norms by work item
        norms_grouped = norms_df.groupby('work_item_code')

        for _, row in items_df.iterrows():
            code = row['code']
            resources = []

            if code in norms_grouped.groups:
                item_norms = norms_grouped.get_group(code)
                for _, norm_row in item_norms.iterrows():
                    resources.append(ResourceNorm(
                        resource_code=norm_row['resource_code'],
                        consumption=float(norm_row['consumption']),
                        waste_factor=float(norm_row.get('waste_factor', 1.0))
                    ))

            work_item = WorkItem(
                code=code,
                name=row['name'],
                unit=row['unit'],
                resources=resources
            )
            self.add_work_item(work_item)

    def calculate_work_item_cost(self, work_item_code: str, quantity: float) -> CostLineItem:
        """Calculate cost for a work item quantity."""

        if work_item_code not in self.work_items:
            raise ValueError(f"Work item {work_item_code} not found")

        work_item = self.work_items[work_item_code]

        labor_cost = 0.0
        material_cost = 0.0
        equipment_cost = 0.0
        subcontractor_cost = 0.0

        for norm in work_item.resources:
            if norm.resource_code not in self.resources:
                continue

            resource = self.resources[norm.resource_code]
            resource_qty = quantity * norm.consumption * norm.waste_factor
            resource_cost = resource_qty * resource.unit_price

            if resource.resource_type == ResourceType.LABOR:
                labor_cost += resource_cost
            elif resource.resource_type == ResourceType.MATERIAL:
                material_cost += resource_cost
            elif resource.resource_type == ResourceType.EQUIPMENT:
                equipment_cost += resource_cost
            elif resource.resource_type == ResourceType.SUBCONTRACTOR:
                subcontractor_cost += resource_cost

        total = labor_cost + material_cost + equipment_cost + subcontractor_cost

        return CostLineItem(
            work_item_code=work_item_code,
            work_item_name=work_item.name,
            quantity=quantity,
            unit=work_item.unit,
            labor_cost=round(labor_cost, 2),
            material_cost=round(material_cost, 2),
            equipment_cost=round(equipment_cost, 2),
            subcontractor_cost=round(subcontractor_cost, 2),
            total_cost=round(total, 2)
        )

    def calculate_estimate(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate full estimate from list of items."""

        line_items = []
        totals = {
            'labor': 0.0,
            'material': 0.0,
            'equipment': 0.0,
            'subcontractor': 0.0,
            'direct': 0.0
        }

        for item in items:
            code = item['work_item_code']
            qty = float(item['quantity'])

            line = self.calculate_work_item_cost(code, qty)
            line_items.append(line)

            totals['labor'] += line.labor_cost
            totals['material'] += line.material_cost
            totals['equipment'] += line.equipment_cost
            totals['subcontractor'] += line.subcontractor_cost
            totals['direct'] += line.total_cost

        # Calculate overhead and profit
        overhead = totals['direct'] * self.overhead_rate
        subtotal = totals['direct'] + overhead
        profit = subtotal * self.profit_rate
        grand_total = subtotal + profit

        return {
            'line_items': line_items,
            'totals': {
                'labor': round(totals['labor'], 2),
                'material': round(totals['material'], 2),
                'equipment': round(totals['equipment'], 2),
                'subcontractor': round(totals['subcontractor'], 2),
                'direct_cost': round(totals['direct'], 2),
                'overhead': round(overhead, 2),
                'overhead_rate': self.overhead_rate,
                'subtotal': round(subtotal, 2),
                'profit': round(profit, 2),
                'profit_rate': self.profit_rate,
                'grand_total': round(grand_total, 2)
            },
            'summary': {
                'item_count': len(line_items),
                'labor_pct': round(totals['labor'] / totals['direct'] * 100, 1) if totals['direct'] > 0 else 0,
                'material_pct': round(totals['material'] / totals['direct'] * 100, 1) if totals['direct'] > 0 else 0,
                'equipment_pct': round(totals['equipment'] / totals['direct'] * 100, 1) if totals['direct'] > 0 else 0
            }
        }

    def adjust_prices(self, factor: float, resource_type: ResourceType = None):
        """Adjust resource prices by factor."""

        for code, resource in self.resources.items():
            if resource_type is None or resource.resource_type == resource_type:
                resource.unit_price *= factor

    def apply_regional_factor(self, factor: float):
        """Apply regional cost factor to all resources."""
        self.adjust_prices(factor)

    def get_resource_breakdown(self, work_item_code: str, quantity: float) -> pd.DataFrame:
        """Get detailed resource breakdown for work item."""

        if work_item_code not in self.work_items:
            return pd.DataFrame()

        work_item = self.work_items[work_item_code]
        data = []

        for norm in work_item.resources:
            if norm.resource_code not in self.resources:
                continue

            resource = self.resources[norm.resource_code]
            resource_qty = quantity * norm.consumption * norm.waste_factor
            resource_cost = resource_qty * resource.unit_price

            data.append({
                'Resource Code': resource.code,
                'Resource Name': resource.name,
                'Type': resource.resource_type.value,
                'Unit': resource.unit,
                'Consumption': norm.consumption,
                'Waste Factor': norm.waste_factor,
                'Total Qty': round(resource_qty, 3),
                'Unit Price': resource.unit_price,
                'Total Cost': round(resource_cost, 2)
            })

        return pd.DataFrame(data)

    def export_to_excel(self, estimate: Dict[str, Any], output_path: str) -> str:
        """Export estimate to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary
            summary_df = pd.DataFrame([estimate['totals']])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Line items
            items_data = [{
                'Code': item.work_item_code,
                'Description': item.work_item_name,
                'Quantity': item.quantity,
                'Unit': item.unit,
                'Labor': item.labor_cost,
                'Material': item.material_cost,
                'Equipment': item.equipment_cost,
                'Subcontractor': item.subcontractor_cost,
                'Total': item.total_cost
            } for item in estimate['line_items']]
            items_df = pd.DataFrame(items_data)
            items_df.to_excel(writer, sheet_name='Line Items', index=False)

        return output_path
```

## Quick Start

```python
# Initialize estimator
estimator = ResourceBasedEstimator()

# Add resources
estimator.add_resource(Resource("L001", "Carpenter", ResourceType.LABOR, "MH", 55.00))
estimator.add_resource(Resource("L002", "Laborer", ResourceType.LABOR, "MH", 35.00))
estimator.add_resource(Resource("M001", "Concrete C30", ResourceType.MATERIAL, "CY", 150.00))
estimator.add_resource(Resource("M002", "Rebar #4", ResourceType.MATERIAL, "TON", 1200.00))
estimator.add_resource(Resource("E001", "Concrete Pump", ResourceType.EQUIPMENT, "HR", 250.00))

# Add work item with resource norms
estimator.add_work_item(WorkItem(
    code="03.01.01",
    name="Cast-in-place Concrete Foundation",
    unit="CY",
    resources=[
        ResourceNorm("L001", 1.5),      # 1.5 carpenter hours per CY
        ResourceNorm("L002", 2.0),      # 2.0 laborer hours per CY
        ResourceNorm("M001", 1.0, 1.05),# 1.0 CY concrete with 5% waste
        ResourceNorm("M002", 0.08),     # 0.08 ton rebar per CY
        ResourceNorm("E001", 0.25)      # 0.25 pump hours per CY
    ]
))

# Calculate estimate
estimate = estimator.calculate_estimate([
    {"work_item_code": "03.01.01", "quantity": 100}
])

print(f"Direct Cost: ${estimate['totals']['direct_cost']:,.2f}")
print(f"Grand Total: ${estimate['totals']['grand_total']:,.2f}")
```

## Common Use Cases

### 1. Resource Breakdown
```python
breakdown = estimator.get_resource_breakdown("03.01.01", quantity=100)
print(breakdown)
```

### 2. Regional Adjustment
```python
# Apply 15% regional factor
estimator.apply_regional_factor(1.15)
```

### 3. Labor Only Adjustment
```python
# Increase labor costs by 10%
estimator.adjust_prices(1.10, ResourceType.LABOR)
```

## Resources
- **DDC Book**: Chapter 3.1 - Resource-Based Costing
- **Website**: https://datadrivenconstruction.io
