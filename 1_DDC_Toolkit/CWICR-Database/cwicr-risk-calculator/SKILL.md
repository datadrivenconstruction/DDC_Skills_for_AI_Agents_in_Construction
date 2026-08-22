---
name: "cwicr-risk-calculator"
description: "Calculate risk-adjusted cost estimates using CWICR data. Apply contingencies, Monte Carlo simulation, and probability distributions to cost estimates."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🗄️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# CWICR Risk Calculator

## Business Case

### Problem Statement
Cost estimates have inherent uncertainty:
- What contingency to apply?
- What is the confidence range?
- Which items have highest risk?
- How to quantify uncertainty?

### Solution
Risk-adjusted cost calculations using contingency analysis, Monte Carlo simulation, and probability distributions based on CWICR cost data.

### Business Value
- **Informed decisions** - Understand estimate uncertainty
- **Appropriate contingency** - Data-driven risk allowance
- **Confidence intervals** - P50, P80, P90 estimates
- **Risk prioritization** - Focus on high-impact items

## Technical Implementation

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random


class RiskLevel(Enum):
    """Risk level categories."""
    LOW = "low"         # Well-defined, standard work
    MEDIUM = "medium"   # Some uncertainty
    HIGH = "high"       # Significant uncertainty
    VERY_HIGH = "very_high"  # Major unknowns


class DistributionType(Enum):
    """Probability distribution types."""
    NORMAL = "normal"
    TRIANGULAR = "triangular"
    UNIFORM = "uniform"
    PERT = "pert"
    LOGNORMAL = "lognormal"


@dataclass
class RiskParameters:
    """Risk parameters for a work item."""
    work_item_code: str
    base_cost: float
    risk_level: RiskLevel
    distribution: DistributionType
    min_factor: float  # Multiplier for minimum
    max_factor: float  # Multiplier for maximum
    most_likely_factor: float = 1.0


@dataclass
class MonteCarloResult:
    """Results of Monte Carlo simulation."""
    iterations: int
    mean: float
    std_dev: float
    p10: float  # 10th percentile
    p50: float  # Median
    p80: float  # 80th percentile
    p90: float  # 90th percentile
    min_value: float
    max_value: float
    values: List[float]


@dataclass
class RiskAnalysisResult:
    """Complete risk analysis result."""
    base_estimate: float
    risk_adjusted_mean: float
    contingency_amount: float
    contingency_percent: float
    p50_estimate: float
    p80_estimate: float
    p90_estimate: float
    high_risk_items: List[Dict[str, Any]]
    item_risks: List[RiskParameters]
    monte_carlo: Optional[MonteCarloResult] = None


# Default risk parameters by category
DEFAULT_RISK_PARAMS = {
    'CONC': {'risk': RiskLevel.LOW, 'min': 0.95, 'max': 1.15},
    'EXCV': {'risk': RiskLevel.MEDIUM, 'min': 0.85, 'max': 1.30},
    'STRL': {'risk': RiskLevel.LOW, 'min': 0.95, 'max': 1.10},
    'MECH': {'risk': RiskLevel.MEDIUM, 'min': 0.90, 'max': 1.25},
    'ELEC': {'risk': RiskLevel.MEDIUM, 'min': 0.90, 'max': 1.20},
    'FINI': {'risk': RiskLevel.HIGH, 'min': 0.85, 'max': 1.40},
    'SITE': {'risk': RiskLevel.HIGH, 'min': 0.80, 'max': 1.50},
    'DEFAULT': {'risk': RiskLevel.MEDIUM, 'min': 0.90, 'max': 1.25}
}


class CWICRRiskCalculator:
    """Calculate risk-adjusted estimates using CWICR data."""

    def __init__(self, cwicr_data: pd.DataFrame):
        self.work_items = cwicr_data
        self._index_data()

    def _index_data(self):
        """Index work items."""
        if 'work_item_code' in self.work_items.columns:
            self._code_index = self.work_items.set_index('work_item_code')
        else:
            self._code_index = None

    def _get_risk_params(self, code: str) -> Dict[str, Any]:
        """Get default risk parameters for work item code."""
        prefix = code.split('-')[0] if '-' in code else code[:4]

        return DEFAULT_RISK_PARAMS.get(prefix, DEFAULT_RISK_PARAMS['DEFAULT'])

    def define_item_risk(self,
                          code: str,
                          base_cost: float,
                          risk_level: RiskLevel = None,
                          distribution: DistributionType = DistributionType.TRIANGULAR,
                          min_factor: float = None,
                          max_factor: float = None) -> RiskParameters:
        """Define risk parameters for a work item."""

        default_params = self._get_risk_params(code)

        if risk_level is None:
            risk_level = default_params['risk']
        if min_factor is None:
            min_factor = default_params['min']
        if max_factor is None:
            max_factor = default_params['max']

        return RiskParameters(
            work_item_code=code,
            base_cost=base_cost,
            risk_level=risk_level,
            distribution=distribution,
            min_factor=min_factor,
            max_factor=max_factor,
            most_likely_factor=1.0
        )

    def calculate_item_risk(self,
                             items: List[Dict[str, Any]]) -> List[RiskParameters]:
        """Calculate risk parameters for list of work items."""

        risk_params = []

        for item in items:
            code = item.get('work_item_code', item.get('code'))
            qty = item.get('quantity', 0)

            # Get base cost
            base_cost = 0
            if self._code_index is not None and code in self._code_index.index:
                wi = self._code_index.loc[code]
                labor = float(wi.get('labor_cost', 0) or 0)
                material = float(wi.get('material_cost', 0) or 0)
                equipment = float(wi.get('equipment_cost', 0) or 0)
                base_cost = (labor + material + equipment) * qty

            # Get risk level from item or default
            risk_level = item.get('risk_level')
            if risk_level and isinstance(risk_level, str):
                risk_level = RiskLevel[risk_level.upper()]

            params = self.define_item_risk(
                code=code,
                base_cost=base_cost,
                risk_level=risk_level,
                min_factor=item.get('min_factor'),
                max_factor=item.get('max_factor')
            )
            risk_params.append(params)

        return risk_params

    def _sample_distribution(self, params: RiskParameters) -> float:
        """Sample from probability distribution."""

        min_cost = params.base_cost * params.min_factor
        max_cost = params.base_cost * params.max_factor
        mode_cost = params.base_cost * params.most_likely_factor

        if params.distribution == DistributionType.TRIANGULAR:
            return np.random.triangular(min_cost, mode_cost, max_cost)

        elif params.distribution == DistributionType.UNIFORM:
            return np.random.uniform(min_cost, max_cost)

        elif params.distribution == DistributionType.NORMAL:
            mean = params.base_cost
            std = (max_cost - min_cost) / 6  # 99.7% within range
            return max(min_cost, min(max_cost, np.random.normal(mean, std)))

        elif params.distribution == DistributionType.PERT:
            # PERT/Beta distribution
            mean = (min_cost + 4 * mode_cost + max_cost) / 6
            std = (max_cost - min_cost) / 6
            return max(min_cost, min(max_cost, np.random.normal(mean, std)))

        elif params.distribution == DistributionType.LOGNORMAL:
            # Lognormal for skewed risks
            log_mean = np.log(params.base_cost)
            log_std = 0.1 * (params.max_factor - params.min_factor)
            return np.random.lognormal(log_mean, log_std)

        return params.base_cost

    def run_monte_carlo(self,
                         risk_params: List[RiskParameters],
                         iterations: int = 10000) -> MonteCarloResult:
        """Run Monte Carlo simulation."""

        total_costs = []

        for _ in range(iterations):
            iteration_total = sum(
                self._sample_distribution(params)
                for params in risk_params
            )
            total_costs.append(iteration_total)

        total_costs = np.array(total_costs)

        return MonteCarloResult(
            iterations=iterations,
            mean=round(float(np.mean(total_costs)), 2),
            std_dev=round(float(np.std(total_costs)), 2),
            p10=round(float(np.percentile(total_costs, 10)), 2),
            p50=round(float(np.percentile(total_costs, 50)), 2),
            p80=round(float(np.percentile(total_costs, 80)), 2),
            p90=round(float(np.percentile(total_costs, 90)), 2),
            min_value=round(float(np.min(total_costs)), 2),
            max_value=round(float(np.max(total_costs)), 2),
            values=list(total_costs)
        )

    def analyze_risk(self,
                      items: List[Dict[str, Any]],
                      run_simulation: bool = True,
                      iterations: int = 10000) -> RiskAnalysisResult:
        """Complete risk analysis of estimate."""

        risk_params = self.calculate_item_risk(items)

        # Base estimate
        base_estimate = sum(p.base_cost for p in risk_params)

        # Run Monte Carlo if requested
        monte_carlo = None
        if run_simulation:
            monte_carlo = self.run_monte_carlo(risk_params, iterations)
            risk_adjusted_mean = monte_carlo.mean
            p50 = monte_carlo.p50
            p80 = monte_carlo.p80
            p90 = monte_carlo.p90
        else:
            # Deterministic calculation
            risk_adjusted_mean = sum(
                p.base_cost * (p.min_factor + 4 * p.most_likely_factor + p.max_factor) / 6
                for p in risk_params
            )
            p50 = risk_adjusted_mean
            p80 = sum(
                p.base_cost * (p.min_factor + p.max_factor * 3) / 4
                for p in risk_params
            )
            p90 = sum(p.base_cost * p.max_factor * 0.9 for p in risk_params)

        contingency = p80 - base_estimate
        contingency_pct = (contingency / base_estimate * 100) if base_estimate > 0 else 0

        # Identify high risk items
        high_risk_items = [
            {
                'code': p.work_item_code,
                'base_cost': p.base_cost,
                'risk_level': p.risk_level.value,
                'range': f"{p.min_factor:.0%} - {p.max_factor:.0%}",
                'risk_exposure': p.base_cost * (p.max_factor - 1)
            }
            for p in risk_params
            if p.risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]
        ]

        return RiskAnalysisResult(
            base_estimate=round(base_estimate, 2),
            risk_adjusted_mean=round(risk_adjusted_mean, 2),
            contingency_amount=round(contingency, 2),
            contingency_percent=round(contingency_pct, 1),
            p50_estimate=round(p50, 2),
            p80_estimate=round(p80, 2),
            p90_estimate=round(p90, 2),
            high_risk_items=sorted(high_risk_items, key=lambda x: x['risk_exposure'], reverse=True),
            item_risks=risk_params,
            monte_carlo=monte_carlo
        )

    def calculate_contingency(self,
                               base_estimate: float,
                               project_phase: str = 'detailed',
                               complexity: str = 'medium') -> Dict[str, Any]:
        """Calculate recommended contingency based on project phase."""

        # Standard contingency ranges by phase
        contingency_ranges = {
            'concept': {'low': 0.25, 'medium': 0.35, 'high': 0.50},
            'schematic': {'low': 0.15, 'medium': 0.25, 'high': 0.35},
            'detailed': {'low': 0.08, 'medium': 0.12, 'high': 0.18},
            'construction': {'low': 0.03, 'medium': 0.05, 'high': 0.08}
        }

        phase_range = contingency_ranges.get(project_phase, contingency_ranges['detailed'])
        rate = phase_range.get(complexity, phase_range['medium'])

        return {
            'base_estimate': base_estimate,
            'contingency_rate': f"{rate:.0%}",
            'contingency_amount': round(base_estimate * rate, 2),
            'total_with_contingency': round(base_estimate * (1 + rate), 2),
            'project_phase': project_phase,
            'complexity': complexity
        }

    def sensitivity_analysis(self,
                              risk_params: List[RiskParameters],
                              base_result: MonteCarloResult) -> pd.DataFrame:
        """Analyze sensitivity of total cost to each item."""

        sensitivities = []

        for param in risk_params:
            # Calculate contribution to variance
            item_variance = (param.base_cost * (param.max_factor - param.min_factor) / 6) ** 2
            total_variance = base_result.std_dev ** 2

            contribution_pct = (item_variance / total_variance * 100) if total_variance > 0 else 0

            sensitivities.append({
                'work_item_code': param.work_item_code,
                'base_cost': param.base_cost,
                'risk_level': param.risk_level.value,
                'variance_contribution_pct': round(contribution_pct, 1),
                'cost_range_low': round(param.base_cost * param.min_factor, 2),
                'cost_range_high': round(param.base_cost * param.max_factor, 2)
            })

        return pd.DataFrame(sensitivities).sort_values('variance_contribution_pct', ascending=False)

    def export_analysis(self,
                         result: RiskAnalysisResult,
                         output_path: str) -> str:
        """Export risk analysis to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary
            summary_df = pd.DataFrame([{
                'Base Estimate': result.base_estimate,
                'Risk Adjusted Mean': result.risk_adjusted_mean,
                'Contingency Amount': result.contingency_amount,
                'Contingency %': result.contingency_percent,
                'P50 Estimate': result.p50_estimate,
                'P80 Estimate': result.p80_estimate,
                'P90 Estimate': result.p90_estimate
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Item Risks
            items_df = pd.DataFrame([
                {
                    'Work Item': p.work_item_code,
                    'Base Cost': p.base_cost,
                    'Risk Level': p.risk_level.value,
                    'Min Factor': p.min_factor,
                    'Max Factor': p.max_factor,
                    'Distribution': p.distribution.value
                }
                for p in result.item_risks
            ])
            items_df.to_excel(writer, sheet_name='Item Risks', index=False)

            # High Risk Items
            if result.high_risk_items:
                high_risk_df = pd.DataFrame(result.high_risk_items)
                high_risk_df.to_excel(writer, sheet_name='High Risk', index=False)

            # Monte Carlo distribution (sample)
            if result.monte_carlo and result.monte_carlo.values:
                mc_df = pd.DataFrame({
                    'Iteration': range(1, min(1001, len(result.monte_carlo.values) + 1)),
                    'Total Cost': result.monte_carlo.values[:1000]
                })
                mc_df.to_excel(writer, sheet_name='Monte Carlo', index=False)

        return output_path
```

## Quick Start

```python
# Load CWICR data
cwicr = pd.read_parquet("TR_workitems_costs_resources_DDC_CWICR.parquet")

# Initialize risk calculator
risk_calc = CWICRRiskCalculator(cwicr)

# Define work items
items = [
    {'work_item_code': 'CONC-001', 'quantity': 150},
    {'work_item_code': 'EXCV-002', 'quantity': 500, 'risk_level': 'high'},
    {'work_item_code': 'STRL-003', 'quantity': 25}
]

# Run risk analysis
result = risk_calc.analyze_risk(items, iterations=10000)

print(f"Base Estimate: ${result.base_estimate:,.2f}")
print(f"P50: ${result.p50_estimate:,.2f}")
print(f"P80: ${result.p80_estimate:,.2f}")
print(f"P90: ${result.p90_estimate:,.2f}")
print(f"Recommended Contingency: {result.contingency_percent}%")
```

## Common Use Cases

### 1. Phase-Based Contingency
```python
contingency = risk_calc.calculate_contingency(
    base_estimate=1000000,
    project_phase='schematic',
    complexity='high'
)
print(f"Contingency: ${contingency['contingency_amount']:,.2f}")
```

### 2. Sensitivity Analysis
```python
sensitivity = risk_calc.sensitivity_analysis(
    result.item_risks,
    result.monte_carlo
)
print(sensitivity.head(5))
```

### 3. Export Report
```python
risk_calc.export_analysis(result, "risk_analysis.xlsx")
```

## Resources
- **GitHub**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
- **DDC Book**: Chapter 3.1 - Risk-Based Estimating
