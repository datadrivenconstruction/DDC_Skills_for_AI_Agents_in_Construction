---
name: budget-variance-analyzer
description: "Analyze budget vs actual cost variances. Identify overruns, forecast final costs, and generate variance reports."
---

# Budget Variance Analyzer

## Business Case

### Problem Statement
Cost overruns surprise project teams:
- Late detection of budget issues
- No systematic variance analysis
- Difficult to forecast final costs
- Unclear root causes

### Solution
Systematic budget variance analysis that tracks costs against budget, identifies trends, and forecasts final project costs.

### Business Value
- **Early warning** - Detect overruns early
- **Forecasting** - Predict final costs
- **Accountability** - Track variance causes
- **Decision support** - Informed cost decisions

## Technical Implementation

```python
import pandas as pd
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class VarianceStatus(Enum):
    """Variance status."""
    UNDER_BUDGET = "under_budget"
    ON_BUDGET = "on_budget"
    OVER_BUDGET = "over_budget"
    CRITICAL = "critical"


class CostCategory(Enum):
    """Cost categories."""
    LABOR = "labor"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    SUBCONTRACTOR = "subcontractor"
    OVERHEAD = "overhead"
    CONTINGENCY = "contingency"
    OTHER = "other"


class VarianceCause(Enum):
    """Common variance causes."""
    SCOPE_CHANGE = "scope_change"
    QUANTITY_CHANGE = "quantity_change"
    PRICE_ESCALATION = "price_escalation"
    PRODUCTIVITY = "productivity"
    REWORK = "rework"
    DELAY = "delay"
    UNFORESEEN = "unforeseen"
    ESTIMATE_ERROR = "estimate_error"
    OTHER = "other"


@dataclass
class BudgetItem:
    """Single budget line item."""
    item_code: str
    description: str
    category: CostCategory
    original_budget: float
    current_budget: float  # After approved changes
    committed_cost: float  # Contracts, POs
    actual_cost: float     # Paid/invoiced
    forecast_cost: float   # Estimate at completion
    percent_complete: float
    notes: str = ""

    @property
    def variance_amount(self) -> float:
        """Budget variance (negative = over budget)."""
        return self.current_budget - self.forecast_cost

    @property
    def variance_percent(self) -> float:
        """Variance as percentage."""
        if self.current_budget == 0:
            return 0
        return (self.variance_amount / self.current_budget) * 100

    @property
    def status(self) -> VarianceStatus:
        """Determine variance status."""
        pct = self.variance_percent
        if pct > 5:
            return VarianceStatus.UNDER_BUDGET
        elif pct >= -5:
            return VarianceStatus.ON_BUDGET
        elif pct >= -15:
            return VarianceStatus.OVER_BUDGET
        else:
            return VarianceStatus.CRITICAL


@dataclass
class VarianceRecord:
    """Record of budget variance."""
    record_id: str
    item_code: str
    variance_amount: float
    cause: VarianceCause
    explanation: str
    recorded_date: date
    recorded_by: str
    approved: bool = False
    approval_date: Optional[date] = None


@dataclass
class ForecastScenario:
    """Cost forecast scenario."""
    name: str
    description: str
    adjustments: Dict[str, float]  # item_code: adjustment amount
    total_forecast: float
    variance_from_budget: float


class BudgetVarianceAnalyzer:
    """Analyze budget vs actual cost variances."""

    VARIANCE_THRESHOLD_WARNING = -0.05  # -5%
    VARIANCE_THRESHOLD_CRITICAL = -0.15  # -15%

    def __init__(self, project_name: str, original_budget: float, currency: str = "USD"):
        self.project_name = project_name
        self.original_budget = original_budget
        self.currency = currency
        self.items: Dict[str, BudgetItem] = {}
        self.variance_records: List[VarianceRecord] = []
        self.history: List[Dict[str, Any]] = []

    def add_budget_item(self,
                       item_code: str,
                       description: str,
                       category: CostCategory,
                       budget: float,
                       committed: float = 0,
                       actual: float = 0,
                       percent_complete: float = 0) -> BudgetItem:
        """Add budget line item."""
        forecast = max(committed, actual / percent_complete * 100) if percent_complete > 0 else budget

        item = BudgetItem(
            item_code=item_code,
            description=description,
            category=category,
            original_budget=budget,
            current_budget=budget,
            committed_cost=committed,
            actual_cost=actual,
            forecast_cost=forecast,
            percent_complete=percent_complete
        )

        self.items[item_code] = item
        return item

    def update_costs(self, item_code: str,
                    committed: float = None,
                    actual: float = None,
                    percent_complete: float = None,
                    forecast: float = None):
        """Update item costs."""
        if item_code not in self.items:
            raise ValueError(f"Item {item_code} not found")

        item = self.items[item_code]

        if committed is not None:
            item.committed_cost = committed
        if actual is not None:
            item.actual_cost = actual
        if percent_complete is not None:
            item.percent_complete = percent_complete
        if forecast is not None:
            item.forecast_cost = forecast
        else:
            # Auto-calculate forecast
            if item.percent_complete > 0:
                item.forecast_cost = item.actual_cost / item.percent_complete * 100
            else:
                item.forecast_cost = max(item.committed_cost, item.current_budget)

        self._record_history()

    def adjust_budget(self, item_code: str, amount: float, reason: str):
        """Adjust current budget (approved change)."""
        if item_code not in self.items:
            raise ValueError(f"Item {item_code} not found")

        self.items[item_code].current_budget += amount
        self.items[item_code].notes += f"\nBudget adjusted by {amount}: {reason}"

    def record_variance(self,
                       item_code: str,
                       cause: VarianceCause,
                       explanation: str,
                       recorded_by: str) -> VarianceRecord:
        """Record variance explanation."""
        item = self.items.get(item_code)
        if not item:
            raise ValueError(f"Item {item_code} not found")

        record_id = f"VAR-{len(self.variance_records) + 1:04d}"

        record = VarianceRecord(
            record_id=record_id,
            item_code=item_code,
            variance_amount=item.variance_amount,
            cause=cause,
            explanation=explanation,
            recorded_date=date.today(),
            recorded_by=recorded_by
        )

        self.variance_records.append(record)
        return record

    def _record_history(self):
        """Record current state to history."""
        snapshot = {
            'date': date.today().isoformat(),
            'total_budget': sum(i.current_budget for i in self.items.values()),
            'total_committed': sum(i.committed_cost for i in self.items.values()),
            'total_actual': sum(i.actual_cost for i in self.items.values()),
            'total_forecast': sum(i.forecast_cost for i in self.items.values())
        }
        self.history.append(snapshot)

    def calculate_summary(self) -> Dict[str, Any]:
        """Calculate overall budget summary."""
        total_budget = sum(i.current_budget for i in self.items.values())
        total_committed = sum(i.committed_cost for i in self.items.values())
        total_actual = sum(i.actual_cost for i in self.items.values())
        total_forecast = sum(i.forecast_cost for i in self.items.values())

        variance = total_budget - total_forecast
        variance_pct = (variance / total_budget * 100) if total_budget > 0 else 0

        # By category
        by_category = {}
        for item in self.items.values():
            cat = item.category.value
            if cat not in by_category:
                by_category[cat] = {
                    'budget': 0, 'actual': 0, 'forecast': 0, 'variance': 0
                }
            by_category[cat]['budget'] += item.current_budget
            by_category[cat]['actual'] += item.actual_cost
            by_category[cat]['forecast'] += item.forecast_cost
            by_category[cat]['variance'] += item.variance_amount

        # Items needing attention
        critical = [i for i in self.items.values() if i.status == VarianceStatus.CRITICAL]
        over_budget = [i for i in self.items.values() if i.status == VarianceStatus.OVER_BUDGET]

        return {
            'project': self.project_name,
            'currency': self.currency,
            'original_budget': self.original_budget,
            'current_budget': total_budget,
            'committed': total_committed,
            'actual': total_actual,
            'forecast': total_forecast,
            'variance': variance,
            'variance_percent': round(variance_pct, 1),
            'status': 'ON_TRACK' if variance >= 0 else 'OVER_BUDGET',
            'by_category': by_category,
            'critical_items': len(critical),
            'over_budget_items': len(over_budget),
            'contingency_used': total_budget - self.original_budget
        }

    def get_critical_items(self) -> List[BudgetItem]:
        """Get items with critical variances."""
        return [i for i in self.items.values()
                if i.status in [VarianceStatus.CRITICAL, VarianceStatus.OVER_BUDGET]]

    def forecast_completion(self,
                           optimistic_factor: float = 0.95,
                           pessimistic_factor: float = 1.15) -> Dict[str, ForecastScenario]:
        """Generate forecast scenarios."""
        current_forecast = sum(i.forecast_cost for i in self.items.values())
        current_budget = sum(i.current_budget for i in self.items.values())

        scenarios = {
            'optimistic': ForecastScenario(
                name="Optimistic",
                description="Best case with no further overruns",
                adjustments={},
                total_forecast=current_forecast * optimistic_factor,
                variance_from_budget=current_budget - (current_forecast * optimistic_factor)
            ),
            'most_likely': ForecastScenario(
                name="Most Likely",
                description="Current trend continues",
                adjustments={},
                total_forecast=current_forecast,
                variance_from_budget=current_budget - current_forecast
            ),
            'pessimistic': ForecastScenario(
                name="Pessimistic",
                description="Additional overruns expected",
                adjustments={},
                total_forecast=current_forecast * pessimistic_factor,
                variance_from_budget=current_budget - (current_forecast * pessimistic_factor)
            )
        }

        return scenarios

    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze cost trends from history."""
        if len(self.history) < 2:
            return {'trend': 'insufficient_data'}

        forecasts = [h['total_forecast'] for h in self.history]
        actuals = [h['total_actual'] for h in self.history]

        # Calculate trend direction
        forecast_trend = forecasts[-1] - forecasts[0]
        actual_trend = actuals[-1] - actuals[0]

        return {
            'forecast_trend': 'increasing' if forecast_trend > 0 else 'decreasing',
            'forecast_change': forecast_trend,
            'actual_trend': 'increasing' if actual_trend > 0 else 'stable',
            'actual_change': actual_trend,
            'data_points': len(self.history)
        }

    def export_variance_report(self, output_path: str):
        """Export detailed variance report to Excel."""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary
            summary = self.calculate_summary()
            summary_df = pd.DataFrame([
                {'Metric': k, 'Value': v}
                for k, v in summary.items()
                if not isinstance(v, dict)
            ])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Line items
            items_data = []
            for item in self.items.values():
                items_data.append({
                    'Code': item.item_code,
                    'Description': item.description,
                    'Category': item.category.value,
                    'Budget': item.current_budget,
                    'Committed': item.committed_cost,
                    'Actual': item.actual_cost,
                    'Forecast': item.forecast_cost,
                    'Variance $': item.variance_amount,
                    'Variance %': round(item.variance_percent, 1),
                    'Status': item.status.value,
                    '% Complete': item.percent_complete
                })

            pd.DataFrame(items_data).to_excel(writer, sheet_name='Line Items', index=False)

            # Variance records
            if self.variance_records:
                records_df = pd.DataFrame([{
                    'ID': r.record_id,
                    'Item': r.item_code,
                    'Amount': r.variance_amount,
                    'Cause': r.cause.value,
                    'Explanation': r.explanation,
                    'Date': r.recorded_date,
                    'By': r.recorded_by
                } for r in self.variance_records])
                records_df.to_excel(writer, sheet_name='Variance Records', index=False)

        return output_path
```

## Quick Start

```python
# Initialize analyzer
analyzer = BudgetVarianceAnalyzer(
    project_name="Office Tower",
    original_budget=50000000,
    currency="USD"
)

# Add budget items
analyzer.add_budget_item("01-SITE", "Site Work", CostCategory.SUBCONTRACTOR, 2000000)
analyzer.add_budget_item("03-CONC", "Concrete", CostCategory.SUBCONTRACTOR, 8000000)
analyzer.add_budget_item("05-STEEL", "Structural Steel", CostCategory.SUBCONTRACTOR, 6000000)

# Update with actuals
analyzer.update_costs("03-CONC", committed=8500000, actual=4000000, percent_complete=45)

# Get summary
summary = analyzer.calculate_summary()
print(f"Variance: ${summary['variance']:,.0f} ({summary['variance_percent']}%)")
```

## Common Use Cases

### 1. Monthly Cost Review
```python
summary = analyzer.calculate_summary()
critical = analyzer.get_critical_items()
print(f"Items needing attention: {len(critical)}")
```

### 2. Record Variance Cause
```python
analyzer.record_variance(
    item_code="03-CONC",
    cause=VarianceCause.PRICE_ESCALATION,
    explanation="Steel rebar prices increased 15%",
    recorded_by="Cost Manager"
)
```

### 3. Forecast Scenarios
```python
scenarios = analyzer.forecast_completion()
for name, scenario in scenarios.items():
    print(f"{scenario.name}: ${scenario.total_forecast:,.0f}")
```

## Resources
- **DDC Book**: Chapter 3.1 - Cost Management
- **Reference**: PMI Cost Management
