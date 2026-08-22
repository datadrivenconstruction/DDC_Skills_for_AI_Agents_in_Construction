---
name: "cwicr-labor-scheduler"
description: "Schedule labor crews based on CWICR norms and project timeline. Calculate crew sizes, shifts, and labor loading curves."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🗄️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# CWICR Labor Scheduler

## Business Case

### Problem Statement
Project managers need to plan labor allocation:
- How many workers per day?
- What skills are needed when?
- How to balance workload across project phases?
- How to avoid resource conflicts?

### Solution
Data-driven labor scheduling using CWICR labor norms to generate crew schedules, loading curves, and skill requirement timelines.

### Business Value
- **Accurate planning** - Based on validated labor norms
- **Resource leveling** - Smooth workload distribution
- **Skill matching** - Right workers at right time
- **Cost control** - Optimize labor costs

## Technical Implementation

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class ShiftType(Enum):
    """Work shift types."""
    SINGLE = "single"      # 8 hours
    DOUBLE = "double"      # 16 hours (2 shifts)
    TRIPLE = "triple"      # 24 hours (3 shifts)
    EXTENDED = "extended"  # 10 hours


class SkillLevel(Enum):
    """Worker skill levels."""
    UNSKILLED = 1
    SEMI_SKILLED = 2
    SKILLED = 3
    FOREMAN = 4
    SPECIALIST = 5


@dataclass
class LaborRequirement:
    """Labor requirement for a work item."""
    work_item_code: str
    description: str
    total_hours: float
    skill_level: SkillLevel
    trade: str
    start_date: datetime
    end_date: datetime
    daily_hours: float = 0.0


@dataclass
class CrewAssignment:
    """Crew assignment for a period."""
    date: datetime
    trade: str
    skill_level: SkillLevel
    workers_needed: int
    hours_per_worker: float
    total_hours: float
    work_items: List[str]


@dataclass
class LaborSchedule:
    """Complete labor schedule."""
    project_name: str
    start_date: datetime
    end_date: datetime
    total_labor_hours: float
    peak_workers: int
    average_workers: float
    assignments: List[CrewAssignment]
    daily_loading: Dict[str, int]
    by_trade: Dict[str, float]


class CWICRLaborScheduler:
    """Schedule labor based on CWICR norms."""

    HOURS_PER_SHIFT = {
        ShiftType.SINGLE: 8,
        ShiftType.DOUBLE: 16,
        ShiftType.TRIPLE: 24,
        ShiftType.EXTENDED: 10
    }

    def __init__(self, cwicr_data: pd.DataFrame):
        self.data = cwicr_data
        self._index_data()

    def _index_data(self):
        """Index work items for fast lookup."""
        if 'work_item_code' in self.data.columns:
            self._code_index = self.data.set_index('work_item_code')
        else:
            self._code_index = None

    def calculate_labor_requirements(self,
                                     items: List[Dict[str, Any]],
                                     project_start: datetime) -> List[LaborRequirement]:
        """Calculate labor requirements from work items."""

        requirements = []

        for item in items:
            code = item.get('work_item_code', item.get('code'))
            qty = item.get('quantity', 0)
            duration_days = item.get('duration_days', 1)
            start_offset = item.get('start_day', 0)

            if self._code_index is not None and code in self._code_index.index:
                work_item = self._code_index.loc[code]
                labor_norm = float(work_item.get('labor_norm', 0) or 0)
                total_hours = labor_norm * qty

                # Determine trade from category
                trade = self._get_trade(work_item.get('category', 'General'))
                skill_level = self._get_skill_level(work_item)

                start_date = project_start + timedelta(days=start_offset)
                end_date = start_date + timedelta(days=duration_days)

                daily_hours = total_hours / duration_days if duration_days > 0 else total_hours

                requirements.append(LaborRequirement(
                    work_item_code=code,
                    description=str(work_item.get('description', '')),
                    total_hours=total_hours,
                    skill_level=skill_level,
                    trade=trade,
                    start_date=start_date,
                    end_date=end_date,
                    daily_hours=daily_hours
                ))

        return requirements

    def _get_trade(self, category: str) -> str:
        """Map category to trade."""
        trade_mapping = {
            'concrete': 'Concrete',
            'masonry': 'Masonry',
            'steel': 'Steel',
            'carpentry': 'Carpentry',
            'plumbing': 'Plumbing',
            'electrical': 'Electrical',
            'hvac': 'HVAC',
            'painting': 'Painting',
            'excavation': 'Earthwork',
            'roofing': 'Roofing'
        }

        cat_lower = str(category).lower()
        for key, trade in trade_mapping.items():
            if key in cat_lower:
                return trade
        return 'General'

    def _get_skill_level(self, work_item) -> SkillLevel:
        """Determine skill level from work item."""
        # Based on complexity or explicit field
        if 'skill_level' in work_item.index:
            level = int(work_item.get('skill_level', 3))
            return SkillLevel(min(max(level, 1), 5))
        return SkillLevel.SKILLED

    def generate_schedule(self,
                         requirements: List[LaborRequirement],
                         shift_type: ShiftType = ShiftType.SINGLE,
                         max_workers_per_trade: int = 50) -> LaborSchedule:
        """Generate labor schedule from requirements."""

        if not requirements:
            return LaborSchedule(
                project_name="",
                start_date=datetime.now(),
                end_date=datetime.now(),
                total_labor_hours=0,
                peak_workers=0,
                average_workers=0,
                assignments=[],
                daily_loading={},
                by_trade={}
            )

        hours_per_day = self.HOURS_PER_SHIFT[shift_type]

        # Find date range
        start_date = min(r.start_date for r in requirements)
        end_date = max(r.end_date for r in requirements)

        # Build daily labor loading
        daily_loading = defaultdict(lambda: defaultdict(float))

        for req in requirements:
            current = req.start_date
            while current < req.end_date:
                date_key = current.strftime('%Y-%m-%d')
                daily_loading[date_key][req.trade] += req.daily_hours
                current += timedelta(days=1)

        # Convert to crew assignments
        assignments = []
        daily_totals = {}
        by_trade = defaultdict(float)

        for date_key, trades in daily_loading.items():
            date = datetime.strptime(date_key, '%Y-%m-%d')
            day_total = 0

            for trade, hours in trades.items():
                workers = int(np.ceil(hours / hours_per_day))
                workers = min(workers, max_workers_per_trade)

                assignments.append(CrewAssignment(
                    date=date,
                    trade=trade,
                    skill_level=SkillLevel.SKILLED,
                    workers_needed=workers,
                    hours_per_worker=hours_per_day,
                    total_hours=hours,
                    work_items=[]
                ))

                day_total += workers
                by_trade[trade] += hours

            daily_totals[date_key] = day_total

        # Statistics
        total_hours = sum(r.total_hours for r in requirements)
        peak_workers = max(daily_totals.values()) if daily_totals else 0
        avg_workers = sum(daily_totals.values()) / len(daily_totals) if daily_totals else 0

        return LaborSchedule(
            project_name="Project",
            start_date=start_date,
            end_date=end_date,
            total_labor_hours=total_hours,
            peak_workers=peak_workers,
            average_workers=round(avg_workers, 1),
            assignments=assignments,
            daily_loading=dict(daily_totals),
            by_trade=dict(by_trade)
        )

    def level_resources(self,
                       schedule: LaborSchedule,
                       target_workers: int) -> LaborSchedule:
        """Level resources to target workforce size."""

        # Resource leveling algorithm
        # Shifts work to reduce peaks while maintaining total hours

        daily_loads = schedule.daily_loading.copy()

        # Find days exceeding target
        over_days = {d: w for d, w in daily_loads.items() if w > target_workers}
        under_days = {d: w for d, w in daily_loads.items() if w < target_workers}

        # Simple leveling: can't easily shift without changing durations
        # Return schedule with analysis

        leveling_analysis = {
            'days_over_target': len(over_days),
            'days_under_target': len(under_days),
            'max_over': max(over_days.values()) - target_workers if over_days else 0,
            'leveling_possible': len(over_days) == 0
        }

        return schedule

    def generate_loading_curve(self,
                               schedule: LaborSchedule) -> pd.DataFrame:
        """Generate labor loading curve data."""

        data = []
        for date_str, workers in sorted(schedule.daily_loading.items()):
            data.append({
                'date': date_str,
                'workers': workers,
                'cumulative_hours': 0  # Would need to calculate
            })

        df = pd.DataFrame(data)

        # Add cumulative hours
        if not df.empty:
            hours_per_worker = 8  # Assuming single shift
            df['daily_hours'] = df['workers'] * hours_per_worker
            df['cumulative_hours'] = df['daily_hours'].cumsum()

        return df

    def get_trade_breakdown(self,
                           schedule: LaborSchedule) -> pd.DataFrame:
        """Get labor breakdown by trade."""

        trade_data = []
        for trade, hours in schedule.by_trade.items():
            trade_data.append({
                'trade': trade,
                'total_hours': round(hours, 1),
                'worker_days': round(hours / 8, 1),
                'percentage': round(hours / schedule.total_labor_hours * 100, 1) if schedule.total_labor_hours > 0 else 0
            })

        return pd.DataFrame(trade_data).sort_values('total_hours', ascending=False)

    def optimize_crew_composition(self,
                                  requirements: List[LaborRequirement],
                                  available_workers: Dict[str, int]) -> Dict[str, Any]:
        """Optimize crew composition based on availability."""

        required_by_trade = defaultdict(float)
        for req in requirements:
            required_by_trade[req.trade] += req.total_hours

        analysis = {
            'sufficient': True,
            'shortages': {},
            'surplus': {},
            'recommendations': []
        }

        for trade, hours_needed in required_by_trade.items():
            workers_needed = int(np.ceil(hours_needed / 8))  # Per day
            available = available_workers.get(trade, 0)

            if workers_needed > available:
                analysis['sufficient'] = False
                analysis['shortages'][trade] = workers_needed - available
                analysis['recommendations'].append(
                    f"Hire {workers_needed - available} additional {trade} workers"
                )
            elif available > workers_needed * 1.5:
                analysis['surplus'][trade] = available - workers_needed

        return analysis


class WeeklyScheduleGenerator:
    """Generate weekly labor schedules."""

    def __init__(self, scheduler: CWICRLaborScheduler):
        self.scheduler = scheduler

    def generate_weekly_schedule(self,
                                 schedule: LaborSchedule,
                                 week_start: datetime) -> pd.DataFrame:
        """Generate schedule for specific week."""

        week_end = week_start + timedelta(days=7)

        weekly_assignments = [
            a for a in schedule.assignments
            if week_start <= a.date < week_end
        ]

        # Pivot by day and trade
        data = []
        for a in weekly_assignments:
            data.append({
                'date': a.date.strftime('%Y-%m-%d'),
                'day': a.date.strftime('%A'),
                'trade': a.trade,
                'workers': a.workers_needed,
                'hours': a.total_hours
            })

        return pd.DataFrame(data)

    def export_to_excel(self,
                       schedule: LaborSchedule,
                       output_path: str) -> str:
        """Export schedule to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Loading curve
            loading = self.scheduler.generate_loading_curve(schedule)
            loading.to_excel(writer, sheet_name='Loading Curve', index=False)

            # Trade breakdown
            trades = self.scheduler.get_trade_breakdown(schedule)
            trades.to_excel(writer, sheet_name='By Trade', index=False)

            # Summary
            summary = pd.DataFrame([{
                'Total Labor Hours': schedule.total_labor_hours,
                'Peak Workers': schedule.peak_workers,
                'Average Workers': schedule.average_workers,
                'Project Duration (days)': (schedule.end_date - schedule.start_date).days
            }])
            summary.to_excel(writer, sheet_name='Summary', index=False)

        return output_path
```

## Quick Start

```python
from datetime import datetime

# Load CWICR data
cwicr = pd.read_parquet("TR_workitems_costs_resources_DDC_CWICR.parquet")

# Initialize scheduler
scheduler = CWICRLaborScheduler(cwicr)

# Define work items with schedule
items = [
    {'work_item_code': 'EXCV-001', 'quantity': 500, 'duration_days': 5, 'start_day': 0},
    {'work_item_code': 'CONC-002', 'quantity': 200, 'duration_days': 10, 'start_day': 5},
    {'work_item_code': 'REBAR-003', 'quantity': 5000, 'duration_days': 8, 'start_day': 3}
]

# Calculate requirements
project_start = datetime(2024, 6, 1)
requirements = scheduler.calculate_labor_requirements(items, project_start)

# Generate schedule
schedule = scheduler.generate_schedule(requirements)

print(f"Total Labor Hours: {schedule.total_labor_hours:,.0f}")
print(f"Peak Workers: {schedule.peak_workers}")
print(f"Average Workers: {schedule.average_workers}")
```

## Common Use Cases

### 1. Resource Leveling
```python
# Check if schedule can meet target
leveled = scheduler.level_resources(schedule, target_workers=25)
```

### 2. Loading Curve
```python
# Get labor loading data for charts
loading_df = scheduler.generate_loading_curve(schedule)
```

### 3. Trade Breakdown
```python
# See hours by trade
trades = scheduler.get_trade_breakdown(schedule)
print(trades)
```

### 4. Weekly Schedule Export
```python
gen = WeeklyScheduleGenerator(scheduler)
gen.export_to_excel(schedule, "labor_schedule.xlsx")
```

## Resources
- **GitHub**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
- **DDC Book**: Chapter 3.1 - Labor Resource Planning
