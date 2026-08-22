---
name: "cwicr-productivity-tracker"
description: "Track actual vs planned productivity using CWICR norms. Calculate productivity rates, identify variances, and generate performance reports."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🗄️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# CWICR Productivity Tracker

## Business Case

### Problem Statement
Project performance tracking requires:
- Comparing actual vs planned productivity
- Identifying underperforming activities
- Forecasting completion dates
- Learning from historical data

### Solution
Track productivity by comparing actual hours/quantities against CWICR norms, generating variance analysis and forecasts.

### Business Value
- **Performance visibility** - Real-time productivity metrics
- **Early warning** - Identify issues before escalation
- **Continuous improvement** - Learn from variances
- **Accurate forecasting** - Data-driven predictions

## Technical Implementation

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class PerformanceStatus(Enum):
    """Performance status categories."""
    EXCELLENT = "excellent"      # >110% productivity
    ON_TARGET = "on_target"      # 90-110%
    BELOW_TARGET = "below_target"  # 70-90%
    CRITICAL = "critical"        # <70%


@dataclass
class ProductivityRecord:
    """Single productivity record."""
    work_item_code: str
    description: str
    date: datetime
    planned_hours: float
    actual_hours: float
    planned_quantity: float
    actual_quantity: float
    productivity_rate: float  # Percentage
    status: PerformanceStatus
    variance_hours: float
    labor_cost_variance: float


@dataclass
class ProductivitySummary:
    """Productivity summary for period/project."""
    period_start: datetime
    period_end: datetime
    total_planned_hours: float
    total_actual_hours: float
    overall_productivity: float
    hours_variance: float
    cost_variance: float
    records: List[ProductivityRecord]
    by_status: Dict[str, int]
    by_category: Dict[str, float]
    trend: List[float]  # Daily/weekly productivity trend


class CWICRProductivityTracker:
    """Track productivity against CWICR norms."""

    def __init__(self, cwicr_data: pd.DataFrame,
                 labor_rate: float = 35.0):
        self.work_items = cwicr_data
        self.labor_rate = labor_rate
        self._index_data()

    def _index_data(self):
        """Index work items for fast lookup."""
        if 'work_item_code' in self.work_items.columns:
            self._work_index = self.work_items.set_index('work_item_code')
        else:
            self._work_index = None

    def _get_status(self, productivity_rate: float) -> PerformanceStatus:
        """Determine performance status from productivity rate."""
        if productivity_rate >= 110:
            return PerformanceStatus.EXCELLENT
        elif productivity_rate >= 90:
            return PerformanceStatus.ON_TARGET
        elif productivity_rate >= 70:
            return PerformanceStatus.BELOW_TARGET
        else:
            return PerformanceStatus.CRITICAL

    def calculate_productivity(self,
                               work_item_code: str,
                               actual_hours: float,
                               actual_quantity: float,
                               date: datetime = None) -> ProductivityRecord:
        """Calculate productivity for single work item."""

        if date is None:
            date = datetime.now()

        if self._work_index is not None and work_item_code in self._work_index.index:
            work_item = self._work_index.loc[work_item_code]
            labor_norm = float(work_item.get('labor_norm', 0) or 0)
            planned_hours = labor_norm * actual_quantity

            # Productivity rate (planned/actual * 100)
            productivity_rate = (planned_hours / actual_hours * 100) if actual_hours > 0 else 0

            # Variances
            hours_variance = planned_hours - actual_hours
            cost_variance = hours_variance * self.labor_rate

            return ProductivityRecord(
                work_item_code=work_item_code,
                description=str(work_item.get('description', '')),
                date=date,
                planned_hours=round(planned_hours, 2),
                actual_hours=actual_hours,
                planned_quantity=actual_quantity,  # Using actual as target
                actual_quantity=actual_quantity,
                productivity_rate=round(productivity_rate, 1),
                status=self._get_status(productivity_rate),
                variance_hours=round(hours_variance, 2),
                labor_cost_variance=round(cost_variance, 2)
            )
        else:
            return ProductivityRecord(
                work_item_code=work_item_code,
                description="NOT FOUND",
                date=date,
                planned_hours=0,
                actual_hours=actual_hours,
                planned_quantity=actual_quantity,
                actual_quantity=actual_quantity,
                productivity_rate=0,
                status=PerformanceStatus.CRITICAL,
                variance_hours=0,
                labor_cost_variance=0
            )

    def track_daily_production(self,
                                records: List[Dict[str, Any]]) -> ProductivitySummary:
        """Track daily production from multiple records."""

        productivity_records = []

        for record in records:
            prod = self.calculate_productivity(
                work_item_code=record.get('work_item_code', record.get('code')),
                actual_hours=record.get('actual_hours', 0),
                actual_quantity=record.get('actual_quantity', 0),
                date=record.get('date', datetime.now())
            )
            productivity_records.append(prod)

        # Aggregate
        total_planned = sum(r.planned_hours for r in productivity_records)
        total_actual = sum(r.actual_hours for r in productivity_records)

        overall_productivity = (total_planned / total_actual * 100) if total_actual > 0 else 0

        # By status
        by_status = defaultdict(int)
        for r in productivity_records:
            by_status[r.status.value] += 1

        # Get date range
        dates = [r.date for r in productivity_records if r.date]
        period_start = min(dates) if dates else datetime.now()
        period_end = max(dates) if dates else datetime.now()

        return ProductivitySummary(
            period_start=period_start,
            period_end=period_end,
            total_planned_hours=round(total_planned, 2),
            total_actual_hours=round(total_actual, 2),
            overall_productivity=round(overall_productivity, 1),
            hours_variance=round(total_planned - total_actual, 2),
            cost_variance=round((total_planned - total_actual) * self.labor_rate, 2),
            records=productivity_records,
            by_status=dict(by_status),
            by_category={},
            trend=[]
        )

    def forecast_completion(self,
                            remaining_work: List[Dict[str, Any]],
                            current_productivity: float,
                            available_hours_per_day: float = 80) -> Dict[str, Any]:
        """Forecast completion based on current productivity."""

        # Calculate remaining planned hours
        total_planned = 0
        for item in remaining_work:
            code = item.get('work_item_code', item.get('code'))
            qty = item.get('quantity', 0)

            if self._work_index is not None and code in self._work_index.index:
                work_item = self._work_index.loc[code]
                labor_norm = float(work_item.get('labor_norm', 0) or 0)
                total_planned += labor_norm * qty

        # Adjust for productivity
        if current_productivity > 0:
            actual_hours_needed = total_planned / (current_productivity / 100)
        else:
            actual_hours_needed = total_planned

        # Days to complete
        days_to_complete = actual_hours_needed / available_hours_per_day if available_hours_per_day > 0 else 0

        return {
            'remaining_planned_hours': round(total_planned, 1),
            'estimated_actual_hours': round(actual_hours_needed, 1),
            'current_productivity': current_productivity,
            'days_to_complete': int(np.ceil(days_to_complete)),
            'forecasted_completion': datetime.now() + timedelta(days=int(np.ceil(days_to_complete))),
            'productivity_impact': round(actual_hours_needed - total_planned, 1)
        }

    def analyze_variance(self,
                         summary: ProductivitySummary) -> Dict[str, Any]:
        """Analyze productivity variances in detail."""

        # Get critical items
        critical = [r for r in summary.records if r.status == PerformanceStatus.CRITICAL]
        below_target = [r for r in summary.records if r.status == PerformanceStatus.BELOW_TARGET]

        # Top impact items (by cost variance)
        sorted_by_impact = sorted(summary.records, key=lambda x: x.labor_cost_variance)
        top_negative = [r for r in sorted_by_impact[:5] if r.labor_cost_variance < 0]
        top_positive = [r for r in sorted_by_impact[-5:] if r.labor_cost_variance > 0]

        return {
            'overall_productivity': summary.overall_productivity,
            'total_hours_variance': summary.hours_variance,
            'total_cost_variance': summary.cost_variance,
            'critical_items_count': len(critical),
            'below_target_count': len(below_target),
            'critical_items': [
                {'code': r.work_item_code, 'productivity': r.productivity_rate, 'variance': r.labor_cost_variance}
                for r in critical
            ],
            'top_negative_impact': [
                {'code': r.work_item_code, 'variance': r.labor_cost_variance}
                for r in top_negative
            ],
            'top_positive_impact': [
                {'code': r.work_item_code, 'variance': r.labor_cost_variance}
                for r in top_positive
            ],
            'recommendations': self._generate_recommendations(critical, below_target)
        }

    def _generate_recommendations(self,
                                   critical: List[ProductivityRecord],
                                   below_target: List[ProductivityRecord]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []

        if len(critical) > 0:
            recommendations.append(
                f"Immediate attention needed for {len(critical)} critical items"
            )

        if len(below_target) > 3:
            recommendations.append(
                "Consider crew training or method review for underperforming activities"
            )

        # Check for patterns
        critical_codes = [r.work_item_code for r in critical]
        if any('CONC' in code for code in critical_codes):
            recommendations.append("Review concrete work methods and crew composition")
        if any('EXCV' in code for code in critical_codes):
            recommendations.append("Check equipment availability and operator skills for excavation")

        return recommendations

    def export_report(self,
                      summary: ProductivitySummary,
                      output_path: str) -> str:
        """Export productivity report to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Details
            details_df = pd.DataFrame([
                {
                    'Work Item': r.work_item_code,
                    'Description': r.description,
                    'Date': r.date.strftime('%Y-%m-%d'),
                    'Planned Hours': r.planned_hours,
                    'Actual Hours': r.actual_hours,
                    'Productivity %': r.productivity_rate,
                    'Status': r.status.value,
                    'Hours Variance': r.variance_hours,
                    'Cost Variance': r.labor_cost_variance
                }
                for r in summary.records
            ])
            details_df.to_excel(writer, sheet_name='Details', index=False)

            # Summary
            summary_df = pd.DataFrame([{
                'Period Start': summary.period_start.strftime('%Y-%m-%d'),
                'Period End': summary.period_end.strftime('%Y-%m-%d'),
                'Total Planned Hours': summary.total_planned_hours,
                'Total Actual Hours': summary.total_actual_hours,
                'Overall Productivity %': summary.overall_productivity,
                'Hours Variance': summary.hours_variance,
                'Cost Variance': summary.cost_variance
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # By Status
            status_df = pd.DataFrame([
                {'Status': status, 'Count': count}
                for status, count in summary.by_status.items()
            ])
            status_df.to_excel(writer, sheet_name='By Status', index=False)

        return output_path


class ProductivityDashboard:
    """Generate productivity dashboard data."""

    def __init__(self, tracker: CWICRProductivityTracker):
        self.tracker = tracker

    def get_kpis(self, summary: ProductivitySummary) -> Dict[str, Any]:
        """Get key performance indicators."""
        return {
            'overall_productivity': summary.overall_productivity,
            'productivity_status': 'Good' if summary.overall_productivity >= 90 else 'Needs Attention',
            'hours_saved': max(0, summary.hours_variance),
            'hours_over': abs(min(0, summary.hours_variance)),
            'cost_impact': summary.cost_variance,
            'items_on_target': summary.by_status.get('on_target', 0) + summary.by_status.get('excellent', 0),
            'items_below_target': summary.by_status.get('below_target', 0) + summary.by_status.get('critical', 0)
        }

    def get_trend_data(self,
                       historical_summaries: List[ProductivitySummary]) -> pd.DataFrame:
        """Get productivity trend data for charting."""
        data = []
        for s in historical_summaries:
            data.append({
                'date': s.period_end.strftime('%Y-%m-%d'),
                'productivity': s.overall_productivity,
                'planned_hours': s.total_planned_hours,
                'actual_hours': s.total_actual_hours
            })
        return pd.DataFrame(data)
```

## Quick Start

```python
# Load CWICR data
cwicr = pd.read_parquet("TR_workitems_costs_resources_DDC_CWICR.parquet")

# Initialize tracker
tracker = CWICRProductivityTracker(cwicr, labor_rate=35.0)

# Track daily production
records = [
    {'work_item_code': 'CONC-001', 'actual_hours': 45, 'actual_quantity': 50},
    {'work_item_code': 'REBAR-002', 'actual_hours': 32, 'actual_quantity': 2000},
    {'work_item_code': 'EXCV-003', 'actual_hours': 28, 'actual_quantity': 100}
]

summary = tracker.track_daily_production(records)

print(f"Overall Productivity: {summary.overall_productivity}%")
print(f"Hours Variance: {summary.hours_variance}")
print(f"Cost Variance: ${summary.cost_variance:,.2f}")
```

## Common Use Cases

### 1. Variance Analysis
```python
analysis = tracker.analyze_variance(summary)
for rec in analysis['recommendations']:
    print(rec)
```

### 2. Completion Forecast
```python
remaining = [
    {'work_item_code': 'CONC-001', 'quantity': 100},
    {'work_item_code': 'REBAR-002', 'quantity': 5000}
]
forecast = tracker.forecast_completion(remaining, current_productivity=85.0)
print(f"Days to Complete: {forecast['days_to_complete']}")
```

### 3. Export Report
```python
tracker.export_report(summary, "productivity_report.xlsx")
```

## Resources
- **GitHub**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
- **DDC Book**: Chapter 3.1 - Productivity Management
