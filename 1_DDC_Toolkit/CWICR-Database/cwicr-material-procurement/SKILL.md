---
name: "cwicr-material-procurement"
description: "Generate material procurement lists from CWICR data. Calculate quantities with waste factors, group by supplier categories, and create purchase orders."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🗄️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# CWICR Material Procurement

## Business Case

### Problem Statement
Material procurement needs accurate quantity lists:
- What materials are needed?
- How much of each with waste allowance?
- When are they needed on site?
- How to group for suppliers?

### Solution
Generate procurement lists from CWICR material data with waste factors, delivery scheduling, and supplier grouping.

### Business Value
- **Accurate quantities** - Based on validated norms
- **Waste included** - Industry-standard waste factors
- **Timely delivery** - Aligned with schedule
- **Cost optimization** - Bulk ordering opportunities

## Technical Implementation

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class MaterialCategory(Enum):
    """Material categories for procurement."""
    CONCRETE = "concrete"
    STEEL = "steel"
    TIMBER = "timber"
    MASONRY = "masonry"
    FINISHES = "finishes"
    MEP = "mep"
    INSULATION = "insulation"
    ROOFING = "roofing"
    EARTHWORK = "earthwork"
    OTHER = "other"


class ProcurementPriority(Enum):
    """Procurement priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class MaterialItem:
    """Single material item for procurement."""
    material_code: str
    description: str
    category: MaterialCategory
    unit: str
    net_quantity: float
    waste_factor: float
    gross_quantity: float
    unit_price: float
    total_cost: float
    lead_time_days: int
    required_date: datetime
    order_date: datetime
    supplier: str = ""
    work_item_codes: List[str] = field(default_factory=list)


@dataclass
class ProcurementList:
    """Complete procurement list."""
    project_name: str
    generated_date: datetime
    total_items: int
    total_cost: float
    items: List[MaterialItem]
    by_category: Dict[str, float]
    by_supplier: Dict[str, List[MaterialItem]]


# Standard waste factors by material type
WASTE_FACTORS = {
    'concrete': 0.05,      # 5%
    'reinforcement': 0.03, # 3%
    'formwork': 0.10,      # 10%
    'masonry': 0.05,       # 5%
    'timber': 0.08,        # 8%
    'drywall': 0.10,       # 10%
    'tiles': 0.10,         # 10%
    'paint': 0.05,         # 5%
    'insulation': 0.05,    # 5%
    'pipes': 0.03,         # 3%
    'cables': 0.05,        # 5%
    'default': 0.05        # 5%
}

# Standard lead times by category (days)
LEAD_TIMES = {
    'concrete': 1,         # Ready-mix
    'reinforcement': 7,    # Steel delivery
    'formwork': 3,         # Standard forms
    'masonry': 5,          # Block delivery
    'timber': 5,           # Lumber
    'structural_steel': 21, # Fabrication
    'windows': 28,         # Manufacturing
    'doors': 14,           # Standard doors
    'mep': 14,             # MEP equipment
    'finishes': 7,         # Standard finishes
    'default': 7
}


class CWICRMaterialProcurement:
    """Generate procurement lists from CWICR data."""

    def __init__(self, cwicr_data: pd.DataFrame,
                 resources_data: pd.DataFrame = None):
        self.work_items = cwicr_data
        self.resources = resources_data
        self._index_data()

    def _index_data(self):
        """Index data for fast lookup."""
        if 'work_item_code' in self.work_items.columns:
            self._work_index = self.work_items.set_index('work_item_code')
        else:
            self._work_index = None

    def get_waste_factor(self, material_type: str) -> float:
        """Get waste factor for material type."""
        material_lower = str(material_type).lower()
        for key, factor in WASTE_FACTORS.items():
            if key in material_lower:
                return factor
        return WASTE_FACTORS['default']

    def get_lead_time(self, material_type: str) -> int:
        """Get lead time for material type."""
        material_lower = str(material_type).lower()
        for key, days in LEAD_TIMES.items():
            if key in material_lower:
                return days
        return LEAD_TIMES['default']

    def get_category(self, material_type: str) -> MaterialCategory:
        """Determine material category."""
        material_lower = str(material_type).lower()

        category_mapping = {
            'concrete': MaterialCategory.CONCRETE,
            'cement': MaterialCategory.CONCRETE,
            'steel': MaterialCategory.STEEL,
            'rebar': MaterialCategory.STEEL,
            'reinforcement': MaterialCategory.STEEL,
            'timber': MaterialCategory.TIMBER,
            'wood': MaterialCategory.TIMBER,
            'lumber': MaterialCategory.TIMBER,
            'masonry': MaterialCategory.MASONRY,
            'block': MaterialCategory.MASONRY,
            'brick': MaterialCategory.MASONRY,
            'paint': MaterialCategory.FINISHES,
            'tile': MaterialCategory.FINISHES,
            'floor': MaterialCategory.FINISHES,
            'electrical': MaterialCategory.MEP,
            'plumbing': MaterialCategory.MEP,
            'hvac': MaterialCategory.MEP,
            'insulation': MaterialCategory.INSULATION,
            'roof': MaterialCategory.ROOFING
        }

        for key, cat in category_mapping.items():
            if key in material_lower:
                return cat
        return MaterialCategory.OTHER

    def extract_materials(self,
                         items: List[Dict[str, Any]],
                         schedule: Dict[str, datetime] = None) -> List[MaterialItem]:
        """Extract material requirements from work items."""

        materials = defaultdict(lambda: {
            'net_quantity': 0,
            'work_items': [],
            'required_date': None
        })

        for item in items:
            code = item.get('work_item_code', item.get('code'))
            qty = item.get('quantity', 0)
            required_date = item.get('required_date')

            if self._work_index is not None and code in self._work_index.index:
                work_item = self._work_index.loc[code]

                # Get material info from work item
                material_desc = str(work_item.get('material_description',
                                                   work_item.get('description', '')))
                material_unit = str(work_item.get('material_unit',
                                                   work_item.get('unit', '')))
                material_norm = float(work_item.get('material_norm', 1) or 1)
                material_cost = float(work_item.get('material_cost', 0) or 0)

                # Calculate material quantity
                material_qty = qty * material_norm

                # Aggregate by material description
                mat_key = f"{material_desc}|{material_unit}"
                materials[mat_key]['net_quantity'] += material_qty
                materials[mat_key]['work_items'].append(code)
                materials[mat_key]['description'] = material_desc
                materials[mat_key]['unit'] = material_unit
                materials[mat_key]['unit_price'] = material_cost / material_norm if material_norm > 0 else 0

                if required_date:
                    if materials[mat_key]['required_date'] is None:
                        materials[mat_key]['required_date'] = required_date
                    else:
                        materials[mat_key]['required_date'] = min(
                            materials[mat_key]['required_date'], required_date
                        )

        # Convert to MaterialItem list
        result = []
        for mat_key, data in materials.items():
            description = data['description']
            waste_factor = self.get_waste_factor(description)
            lead_time = self.get_lead_time(description)
            net_qty = data['net_quantity']
            gross_qty = net_qty * (1 + waste_factor)
            unit_price = data.get('unit_price', 0)

            required_date = data['required_date'] or datetime.now() + timedelta(days=30)
            order_date = required_date - timedelta(days=lead_time)

            result.append(MaterialItem(
                material_code=mat_key.split('|')[0][:20],
                description=description,
                category=self.get_category(description),
                unit=data['unit'],
                net_quantity=round(net_qty, 2),
                waste_factor=waste_factor,
                gross_quantity=round(gross_qty, 2),
                unit_price=round(unit_price, 2),
                total_cost=round(gross_qty * unit_price, 2),
                lead_time_days=lead_time,
                required_date=required_date,
                order_date=order_date,
                work_item_codes=data['work_items']
            ))

        return result

    def generate_procurement_list(self,
                                  items: List[Dict[str, Any]],
                                  project_name: str = "Project") -> ProcurementList:
        """Generate complete procurement list."""

        materials = self.extract_materials(items)

        # Group by category
        by_category = defaultdict(float)
        for mat in materials:
            by_category[mat.category.value] += mat.total_cost

        # Group by supplier (placeholder - would use supplier mapping)
        by_supplier = defaultdict(list)
        for mat in materials:
            supplier = self._suggest_supplier(mat)
            mat.supplier = supplier
            by_supplier[supplier].append(mat)

        return ProcurementList(
            project_name=project_name,
            generated_date=datetime.now(),
            total_items=len(materials),
            total_cost=sum(m.total_cost for m in materials),
            items=materials,
            by_category=dict(by_category),
            by_supplier=dict(by_supplier)
        )

    def _suggest_supplier(self, material: MaterialItem) -> str:
        """Suggest supplier based on material category."""
        supplier_mapping = {
            MaterialCategory.CONCRETE: "Ready-Mix Supplier",
            MaterialCategory.STEEL: "Steel Fabricator",
            MaterialCategory.TIMBER: "Lumber Yard",
            MaterialCategory.MASONRY: "Masonry Supplier",
            MaterialCategory.MEP: "MEP Distributor",
            MaterialCategory.FINISHES: "Building Materials",
            MaterialCategory.INSULATION: "Insulation Supplier",
            MaterialCategory.ROOFING: "Roofing Supplier"
        }
        return supplier_mapping.get(material.category, "General Supplier")

    def create_purchase_order(self,
                              materials: List[MaterialItem],
                              supplier: str,
                              po_number: str) -> Dict[str, Any]:
        """Create purchase order for supplier."""

        po_items = [m for m in materials if m.supplier == supplier]

        return {
            'po_number': po_number,
            'supplier': supplier,
            'date': datetime.now().isoformat(),
            'delivery_date': min(m.required_date for m in po_items).isoformat() if po_items else None,
            'items': [
                {
                    'description': m.description,
                    'quantity': m.gross_quantity,
                    'unit': m.unit,
                    'unit_price': m.unit_price,
                    'total': m.total_cost
                }
                for m in po_items
            ],
            'subtotal': sum(m.total_cost for m in po_items),
            'item_count': len(po_items)
        }

    def export_to_excel(self,
                       procurement_list: ProcurementList,
                       output_path: str) -> str:
        """Export procurement list to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # All materials
            items_df = pd.DataFrame([
                {
                    'Description': m.description,
                    'Category': m.category.value,
                    'Unit': m.unit,
                    'Net Qty': m.net_quantity,
                    'Waste %': m.waste_factor * 100,
                    'Gross Qty': m.gross_quantity,
                    'Unit Price': m.unit_price,
                    'Total Cost': m.total_cost,
                    'Lead Time': m.lead_time_days,
                    'Order By': m.order_date.strftime('%Y-%m-%d'),
                    'Required': m.required_date.strftime('%Y-%m-%d'),
                    'Supplier': m.supplier
                }
                for m in procurement_list.items
            ])
            items_df.to_excel(writer, sheet_name='Materials', index=False)

            # By category
            cat_df = pd.DataFrame([
                {'Category': cat, 'Total Cost': cost}
                for cat, cost in procurement_list.by_category.items()
            ])
            cat_df.to_excel(writer, sheet_name='By Category', index=False)

            # Summary
            summary_df = pd.DataFrame([{
                'Project': procurement_list.project_name,
                'Generated': procurement_list.generated_date.strftime('%Y-%m-%d'),
                'Total Items': procurement_list.total_items,
                'Total Cost': procurement_list.total_cost
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        return output_path

    def get_critical_orders(self,
                           procurement_list: ProcurementList,
                           days_ahead: int = 14) -> List[MaterialItem]:
        """Get materials that need to be ordered soon."""

        cutoff = datetime.now() + timedelta(days=days_ahead)
        return [
            m for m in procurement_list.items
            if m.order_date <= cutoff
        ]

    def aggregate_by_material(self,
                              items: List[Dict[str, Any]]) -> pd.DataFrame:
        """Aggregate materials across multiple work items."""

        materials = self.extract_materials(items)

        df = pd.DataFrame([
            {
                'Material': m.description,
                'Category': m.category.value,
                'Total Qty': m.gross_quantity,
                'Unit': m.unit,
                'Total Cost': m.total_cost,
                'Work Items': len(m.work_item_codes)
            }
            for m in materials
        ])

        return df.sort_values('Total Cost', ascending=False)
```

## Quick Start

```python
# Load CWICR data
cwicr = pd.read_parquet("TR_workitems_costs_resources_DDC_CWICR.parquet")

# Initialize procurement generator
procurement = CWICRMaterialProcurement(cwicr)

# Define work items
items = [
    {'work_item_code': 'CONC-001', 'quantity': 150},
    {'work_item_code': 'REBAR-002', 'quantity': 5000},
    {'work_item_code': 'FORM-003', 'quantity': 300}
]

# Generate procurement list
proc_list = procurement.generate_procurement_list(items, "Building A")

print(f"Total Items: {proc_list.total_items}")
print(f"Total Cost: ${proc_list.total_cost:,.2f}")
```

## Common Use Cases

### 1. Get Critical Orders
```python
critical = procurement.get_critical_orders(proc_list, days_ahead=7)
print(f"Order immediately: {len(critical)} items")
```

### 2. Create Purchase Order
```python
po = procurement.create_purchase_order(
    proc_list.items,
    supplier="Steel Fabricator",
    po_number="PO-2024-001"
)
```

### 3. Export to Excel
```python
procurement.export_to_excel(proc_list, "procurement_list.xlsx")
```

### 4. Material Aggregation
```python
materials_df = procurement.aggregate_by_material(items)
print(materials_df.head(10))
```

## Resources
- **GitHub**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
- **DDC Book**: Chapter 3.1 - Material Resource Planning
