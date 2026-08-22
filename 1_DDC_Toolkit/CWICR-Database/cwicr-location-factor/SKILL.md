---
name: "cwicr-location-factor"
description: "Apply geographic location factors to CWICR estimates. Adjust costs for regional labor rates, material prices, and market conditions."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🗄️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# CWICR Location Factor

## Business Case

### Problem Statement
Construction costs vary by location:
- Labor rates differ by region
- Material prices vary geographically
- Market conditions affect costs
- Remote locations have premiums

### Solution
Apply location-based cost factors to CWICR estimates, adjusting for regional differences in labor, materials, and overall market conditions.

### Business Value
- **Regional accuracy** - Location-specific estimates
- **Market awareness** - Current conditions
- **Comparison support** - Normalize across locations
- **Planning** - Multi-location projects

## Technical Implementation

```python
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class CostComponent(Enum):
    """Cost components for factors."""
    LABOR = "labor"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    TOTAL = "total"


@dataclass
class LocationFactor:
    """Location adjustment factor."""
    location_code: str
    location_name: str
    country: str
    region: str
    labor_factor: float
    material_factor: float
    equipment_factor: float
    total_factor: float
    currency: str
    notes: str = ""


@dataclass
class AdjustedEstimate:
    """Estimate with location adjustment."""
    base_cost: float
    base_location: str
    target_location: str
    labor_adjustment: float
    material_adjustment: float
    equipment_adjustment: float
    total_adjustment: float
    adjusted_cost: float
    adjustment_percent: float


# Location factors (relative to US national average = 1.00)
LOCATION_FACTORS = {
    # USA
    'US-NYC': LocationFactor('US-NYC', 'New York City', 'USA', 'Northeast', 1.35, 1.15, 1.10, 1.22, 'USD'),
    'US-LA': LocationFactor('US-LA', 'Los Angeles', 'USA', 'West', 1.25, 1.10, 1.05, 1.15, 'USD'),
    'US-CHI': LocationFactor('US-CHI', 'Chicago', 'USA', 'Midwest', 1.20, 1.05, 1.05, 1.12, 'USD'),
    'US-HOU': LocationFactor('US-HOU', 'Houston', 'USA', 'South', 0.95, 0.98, 0.95, 0.96, 'USD'),
    'US-PHX': LocationFactor('US-PHX', 'Phoenix', 'USA', 'Southwest', 0.90, 0.95, 0.95, 0.93, 'USD'),
    'US-DEN': LocationFactor('US-DEN', 'Denver', 'USA', 'Mountain', 1.00, 1.02, 1.00, 1.01, 'USD'),
    'US-SEA': LocationFactor('US-SEA', 'Seattle', 'USA', 'Northwest', 1.18, 1.08, 1.05, 1.12, 'USD'),
    'US-MIA': LocationFactor('US-MIA', 'Miami', 'USA', 'Southeast', 0.98, 1.05, 1.00, 1.01, 'USD'),
    'US-ATL': LocationFactor('US-ATL', 'Atlanta', 'USA', 'Southeast', 0.92, 0.98, 0.95, 0.95, 'USD'),
    'US-NAT': LocationFactor('US-NAT', 'US National Average', 'USA', 'National', 1.00, 1.00, 1.00, 1.00, 'USD'),

    # Europe
    'UK-LON': LocationFactor('UK-LON', 'London', 'UK', 'Southeast', 1.45, 1.20, 1.15, 1.30, 'GBP'),
    'DE-BER': LocationFactor('DE-BER', 'Berlin', 'Germany', 'East', 1.15, 1.10, 1.10, 1.12, 'EUR'),
    'DE-MUN': LocationFactor('DE-MUN', 'Munich', 'Germany', 'South', 1.25, 1.15, 1.12, 1.18, 'EUR'),
    'FR-PAR': LocationFactor('FR-PAR', 'Paris', 'France', 'Ile-de-France', 1.30, 1.18, 1.15, 1.22, 'EUR'),
    'NL-AMS': LocationFactor('NL-AMS', 'Amsterdam', 'Netherlands', 'North Holland', 1.20, 1.12, 1.10, 1.15, 'EUR'),

    # Middle East
    'AE-DXB': LocationFactor('AE-DXB', 'Dubai', 'UAE', 'Dubai', 0.85, 1.25, 1.10, 1.05, 'AED'),
    'SA-RIY': LocationFactor('SA-RIY', 'Riyadh', 'Saudi Arabia', 'Central', 0.80, 1.20, 1.05, 1.00, 'SAR'),
    'QA-DOH': LocationFactor('QA-DOH', 'Doha', 'Qatar', 'Qatar', 0.88, 1.30, 1.12, 1.08, 'QAR'),

    # Asia
    'SG-SIN': LocationFactor('SG-SIN', 'Singapore', 'Singapore', 'Central', 1.10, 1.15, 1.08, 1.12, 'SGD'),
    'HK-HKG': LocationFactor('HK-HKG', 'Hong Kong', 'Hong Kong', 'Hong Kong', 1.20, 1.25, 1.15, 1.20, 'HKD'),
    'JP-TKY': LocationFactor('JP-TKY', 'Tokyo', 'Japan', 'Kanto', 1.35, 1.20, 1.18, 1.25, 'JPY'),

    # Australia
    'AU-SYD': LocationFactor('AU-SYD', 'Sydney', 'Australia', 'NSW', 1.25, 1.15, 1.12, 1.18, 'AUD'),
    'AU-MEL': LocationFactor('AU-MEL', 'Melbourne', 'Australia', 'Victoria', 1.20, 1.12, 1.10, 1.15, 'AUD'),
}


class CWICRLocationFactor:
    """Apply location factors to CWICR estimates."""

    def __init__(self,
                 cwicr_data: pd.DataFrame = None,
                 base_location: str = 'US-NAT'):
        self.cwicr = cwicr_data
        self.base_location = base_location
        self._factors = LOCATION_FACTORS.copy()

        if cwicr_data is not None:
            self._index_cwicr()

    def _index_cwicr(self):
        """Index CWICR data."""
        if 'work_item_code' in self.cwicr.columns:
            self._cwicr_index = self.cwicr.set_index('work_item_code')
        else:
            self._cwicr_index = None

    def get_factor(self, location_code: str) -> Optional[LocationFactor]:
        """Get location factor."""
        return self._factors.get(location_code)

    def list_locations(self, country: str = None) -> List[Dict[str, Any]]:
        """List available locations."""
        factors = self._factors.values()

        if country:
            factors = [f for f in factors if f.country.lower() == country.lower()]

        return [
            {
                'code': f.location_code,
                'name': f.location_name,
                'country': f.country,
                'region': f.region,
                'total_factor': f.total_factor,
                'currency': f.currency
            }
            for f in factors
        ]

    def add_location(self, factor: LocationFactor):
        """Add custom location factor."""
        self._factors[factor.location_code] = factor

    def adjust_cost(self,
                    base_cost: float,
                    target_location: str,
                    cost_breakdown: Dict[str, float] = None) -> AdjustedEstimate:
        """Adjust cost from base to target location."""

        base_factor = self._factors.get(self.base_location)
        target_factor = self._factors.get(target_location)

        if not base_factor or not target_factor:
            return AdjustedEstimate(
                base_cost=base_cost,
                base_location=self.base_location,
                target_location=target_location,
                labor_adjustment=0,
                material_adjustment=0,
                equipment_adjustment=0,
                total_adjustment=0,
                adjusted_cost=base_cost,
                adjustment_percent=0
            )

        if cost_breakdown is None:
            # Default breakdown
            cost_breakdown = {
                'labor': base_cost * 0.40,
                'material': base_cost * 0.45,
                'equipment': base_cost * 0.15
            }

        # Calculate relative factors
        labor_rel = target_factor.labor_factor / base_factor.labor_factor
        material_rel = target_factor.material_factor / base_factor.material_factor
        equipment_rel = target_factor.equipment_factor / base_factor.equipment_factor

        # Apply adjustments
        labor_adjusted = cost_breakdown.get('labor', 0) * labor_rel
        material_adjusted = cost_breakdown.get('material', 0) * material_rel
        equipment_adjusted = cost_breakdown.get('equipment', 0) * equipment_rel

        adjusted_total = labor_adjusted + material_adjusted + equipment_adjusted
        total_adjustment = adjusted_total - base_cost
        adjustment_pct = (total_adjustment / base_cost * 100) if base_cost > 0 else 0

        return AdjustedEstimate(
            base_cost=round(base_cost, 2),
            base_location=self.base_location,
            target_location=target_location,
            labor_adjustment=round(labor_adjusted - cost_breakdown.get('labor', 0), 2),
            material_adjustment=round(material_adjusted - cost_breakdown.get('material', 0), 2),
            equipment_adjustment=round(equipment_adjusted - cost_breakdown.get('equipment', 0), 2),
            total_adjustment=round(total_adjustment, 2),
            adjusted_cost=round(adjusted_total, 2),
            adjustment_percent=round(adjustment_pct, 1)
        )

    def adjust_estimate(self,
                         items: List[Dict[str, Any]],
                         target_location: str) -> Dict[str, Any]:
        """Adjust entire estimate for location."""

        adjusted_items = []
        total_base = 0
        total_adjusted = 0

        for item in items:
            code = item.get('work_item_code', item.get('code'))
            qty = item.get('quantity', 0)

            # Get costs from CWICR
            labor = 0
            material = 0
            equipment = 0

            if self._cwicr_index is not None and code in self._cwicr_index.index:
                wi = self._cwicr_index.loc[code]
                labor = float(wi.get('labor_cost', 0) or 0) * qty
                material = float(wi.get('material_cost', 0) or 0) * qty
                equipment = float(wi.get('equipment_cost', 0) or 0) * qty

            base_cost = labor + material + equipment
            breakdown = {'labor': labor, 'material': material, 'equipment': equipment}

            adjustment = self.adjust_cost(base_cost, target_location, breakdown)

            adjusted_items.append({
                'code': code,
                'quantity': qty,
                'base_cost': adjustment.base_cost,
                'adjusted_cost': adjustment.adjusted_cost,
                'adjustment': adjustment.total_adjustment
            })

            total_base += base_cost
            total_adjusted += adjustment.adjusted_cost

        return {
            'items': adjusted_items,
            'base_location': self.base_location,
            'target_location': target_location,
            'total_base': round(total_base, 2),
            'total_adjusted': round(total_adjusted, 2),
            'total_adjustment': round(total_adjusted - total_base, 2),
            'adjustment_percent': round((total_adjusted - total_base) / total_base * 100, 1) if total_base > 0 else 0
        }

    def compare_locations(self,
                           base_cost: float,
                           locations: List[str]) -> pd.DataFrame:
        """Compare cost across multiple locations."""

        data = []

        for loc_code in locations:
            adjustment = self.adjust_cost(base_cost, loc_code)
            factor = self._factors.get(loc_code)

            data.append({
                'Location': factor.location_name if factor else loc_code,
                'Code': loc_code,
                'Country': factor.country if factor else '',
                'Adjusted Cost': adjustment.adjusted_cost,
                'Adjustment %': adjustment.adjustment_percent,
                'Labor Factor': factor.labor_factor if factor else 1.0,
                'Material Factor': factor.material_factor if factor else 1.0
            })

        return pd.DataFrame(data).sort_values('Adjusted Cost')

    def normalize_to_base(self,
                           cost: float,
                           source_location: str) -> float:
        """Normalize cost from source location to base location."""

        source_factor = self._factors.get(source_location)
        base_factor = self._factors.get(self.base_location)

        if not source_factor or not base_factor:
            return cost

        relative_factor = base_factor.total_factor / source_factor.total_factor
        return round(cost * relative_factor, 2)

    def export_factors(self, output_path: str) -> str:
        """Export location factors to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df = pd.DataFrame([
                {
                    'Code': f.location_code,
                    'Name': f.location_name,
                    'Country': f.country,
                    'Region': f.region,
                    'Labor Factor': f.labor_factor,
                    'Material Factor': f.material_factor,
                    'Equipment Factor': f.equipment_factor,
                    'Total Factor': f.total_factor,
                    'Currency': f.currency
                }
                for f in self._factors.values()
            ])
            df.to_excel(writer, sheet_name='Location Factors', index=False)

        return output_path
```

## Quick Start

```python
# Initialize with base location
loc_factor = CWICRLocationFactor(base_location='US-NAT')

# Adjust single cost
adjustment = loc_factor.adjust_cost(
    base_cost=1000000,
    target_location='US-NYC'
)

print(f"Base: ${adjustment.base_cost:,.2f}")
print(f"NYC: ${adjustment.adjusted_cost:,.2f}")
print(f"Adjustment: {adjustment.adjustment_percent:+.1f}%")
```

## Common Use Cases

### 1. Multi-Location Comparison
```python
comparison = loc_factor.compare_locations(
    base_cost=5000000,
    locations=['US-NYC', 'US-HOU', 'US-LA', 'UK-LON', 'AE-DXB']
)
print(comparison)
```

### 2. Adjust Estimate
```python
cwicr = pd.read_parquet("TR_workitems_costs_resources_DDC_CWICR.parquet")
loc_factor = CWICRLocationFactor(cwicr, base_location='US-NAT')

items = [
    {'work_item_code': 'CONC-001', 'quantity': 200},
    {'work_item_code': 'STRL-002', 'quantity': 50}
]

dubai_estimate = loc_factor.adjust_estimate(items, 'AE-DXB')
print(f"Dubai Cost: ${dubai_estimate['total_adjusted']:,.2f}")
```

### 3. Custom Location
```python
loc_factor.add_location(LocationFactor(
    'US-REMOTE',
    'Remote Alaska',
    'USA',
    'Alaska',
    labor_factor=1.50,
    material_factor=1.40,
    equipment_factor=1.35,
    total_factor=1.42,
    currency='USD',
    notes='Remote location premium'
))
```

## Resources
- **GitHub**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
- **DDC Book**: Chapter 3.1 - Location Cost Adjustments
