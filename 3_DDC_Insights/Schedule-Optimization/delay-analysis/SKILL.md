---
name: delay-analysis
description: "Analyze construction schedule delays for claims and recovery. Perform time impact analysis, identify delay causes, calculate damages, and document for disputes."
---

# Delay Analysis

## Overview

Analyze construction schedule delays for project recovery and claims. Perform time impact analysis (TIA), identify concurrent delays, calculate delay damages, and prepare documentation for dispute resolution.

> "Proper delay analysis is essential for fair resolution of construction disputes" — DDC Community

## Delay Analysis Methods

```
┌─────────────────────────────────────────────────────────────────┐
│                    DELAY ANALYSIS METHODS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  As-Planned vs As-Built    │    Time Impact Analysis (TIA)      │
│  ─────────────────────     │    ────────────────────────────    │
│  Compare original to       │    Insert delay events into        │
│  actual schedule           │    schedule to measure impact      │
│                            │                                     │
│  Windows Analysis          │    Collapsed As-Built              │
│  ────────────────          │    ─────────────────               │
│  Divide project into       │    Remove delays from as-built     │
│  time periods              │    to find "but-for" completion    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

class DelayType(Enum):
    EXCUSABLE_COMPENSABLE = "excusable_compensable"      # Owner caused - time + money
    EXCUSABLE_NON_COMPENSABLE = "excusable_non_compensable"  # Neither party - time only
    NON_EXCUSABLE = "non_excusable"                      # Contractor caused - no relief
    CONCURRENT = "concurrent"                            # Both parties - complex

class DelayCause(Enum):
    OWNER_CHANGE = "owner_change"
    LATE_INFORMATION = "late_information"
    DIFFERING_CONDITIONS = "differing_conditions"
    PERMIT_DELAY = "permit_delay"
    WEATHER = "weather"
    LABOR_SHORTAGE = "labor_shortage"
    MATERIAL_DELAY = "material_delay"
    SUBCONTRACTOR = "subcontractor"
    COORDINATION = "coordination"
    ACCESS = "access"
    FORCE_MAJEURE = "force_majeure"

@dataclass
class DelayEvent:
    id: str
    description: str
    cause: DelayCause
    delay_type: DelayType
    start_date: datetime
    end_date: datetime
    affected_activities: List[str]
    responsible_party: str
    documented: bool = True
    supporting_docs: List[str] = field(default_factory=list)
    calculated_impact: int = 0  # days
    concurrent_with: List[str] = field(default_factory=list)

@dataclass
class ScheduleVersion:
    version_id: str
    version_type: str  # baseline, update, as-built
    data_date: datetime
    completion_date: datetime
    activities: Dict[str, Dict]  # activity_id -> {start, finish, duration}

@dataclass
class WindowPeriod:
    window_id: str
    start_date: datetime
    end_date: datetime
    planned_progress: float
    actual_progress: float
    delay_days: int
    delay_events: List[str]
    responsible_parties: Dict[str, int]  # party -> delay days

@dataclass
class DelayAnalysisReport:
    project_name: str
    analysis_date: datetime
    original_completion: datetime
    actual_completion: datetime
    total_delay: int
    excusable_delay: int
    non_excusable_delay: int
    concurrent_delay: int
    delay_events: List[DelayEvent]
    delay_by_cause: Dict[str, int]
    delay_by_party: Dict[str, int]
    recommended_extension: int
    potential_damages: float

class DelayAnalyzer:
    """Analyze construction schedule delays."""

    # Daily delay costs by project size
    DEFAULT_DAILY_COSTS = {
        "small": 5000,      # < $10M
        "medium": 15000,    # $10M - $50M
        "large": 40000,     # $50M - $200M
        "mega": 100000      # > $200M
    }

    def __init__(self, project_name: str, contract_completion: datetime):
        self.project_name = project_name
        self.contract_completion = contract_completion
        self.delay_events: Dict[str, DelayEvent] = {}
        self.schedule_versions: Dict[str, ScheduleVersion] = {}
        self.window_periods: List[WindowPeriod] = []
        self.daily_cost = self.DEFAULT_DAILY_COSTS["medium"]

    def set_daily_delay_cost(self, cost: float):
        """Set daily delay cost for damages calculation."""
        self.daily_cost = cost

    def add_schedule_version(self, version_id: str, version_type: str,
                            data_date: datetime, completion_date: datetime,
                            activities: Dict[str, Dict]) -> ScheduleVersion:
        """Add schedule version for analysis."""
        version = ScheduleVersion(
            version_id=version_id,
            version_type=version_type,
            data_date=data_date,
            completion_date=completion_date,
            activities=activities
        )
        self.schedule_versions[version_id] = version
        return version

    def add_delay_event(self, id: str, description: str,
                       cause: DelayCause, delay_type: DelayType,
                       start_date: datetime, end_date: datetime,
                       affected_activities: List[str],
                       responsible_party: str,
                       supporting_docs: List[str] = None) -> DelayEvent:
        """Add delay event for analysis."""
        event = DelayEvent(
            id=id,
            description=description,
            cause=cause,
            delay_type=delay_type,
            start_date=start_date,
            end_date=end_date,
            affected_activities=affected_activities,
            responsible_party=responsible_party,
            supporting_docs=supporting_docs or []
        )
        self.delay_events[id] = event
        return event

    def perform_as_planned_vs_as_built(self) -> Dict:
        """Perform As-Planned vs As-Built analysis."""
        baseline = self.schedule_versions.get("baseline")
        as_built = self.schedule_versions.get("as_built")

        if not baseline or not as_built:
            raise ValueError("Need baseline and as-built schedules")

        total_delay = (as_built.completion_date - baseline.completion_date).days

        # Analyze each activity
        activity_delays = []
        for act_id, baseline_act in baseline.activities.items():
            if act_id in as_built.activities:
                as_built_act = as_built.activities[act_id]

                baseline_finish = baseline_act['finish']
                actual_finish = as_built_act['finish']

                if isinstance(baseline_finish, str):
                    baseline_finish = datetime.fromisoformat(baseline_finish)
                if isinstance(actual_finish, str):
                    actual_finish = datetime.fromisoformat(actual_finish)

                delay = (actual_finish - baseline_finish).days

                if delay > 0:
                    activity_delays.append({
                        'activity_id': act_id,
                        'planned_finish': baseline_finish,
                        'actual_finish': actual_finish,
                        'delay_days': delay
                    })

        return {
            'method': 'As-Planned vs As-Built',
            'baseline_completion': baseline.completion_date,
            'actual_completion': as_built.completion_date,
            'total_delay': total_delay,
            'activity_delays': sorted(activity_delays, key=lambda x: -x['delay_days'])
        }

    def perform_time_impact_analysis(self, delay_event_id: str) -> Dict:
        """Perform Time Impact Analysis for specific delay event."""
        if delay_event_id not in self.delay_events:
            raise ValueError(f"Delay event {delay_event_id} not found")

        event = self.delay_events[delay_event_id]

        # Find schedule version just before delay
        pre_delay_schedule = None
        for version in sorted(self.schedule_versions.values(),
                            key=lambda v: v.data_date, reverse=True):
            if version.data_date < event.start_date:
                pre_delay_schedule = version
                break

        if not pre_delay_schedule:
            pre_delay_schedule = self.schedule_versions.get("baseline")

        if not pre_delay_schedule:
            raise ValueError("No pre-delay schedule found")

        # Calculate impact
        original_completion = pre_delay_schedule.completion_date
        delay_duration = (event.end_date - event.start_date).days

        # Check if delay is on critical path
        critical_impact = False
        for act_id in event.affected_activities:
            if act_id in pre_delay_schedule.activities:
                act = pre_delay_schedule.activities[act_id]
                if act.get('is_critical', False):
                    critical_impact = True
                    break

        if critical_impact:
            impact_days = delay_duration
            new_completion = original_completion + timedelta(days=delay_duration)
        else:
            # Need to check float
            impact_days = max(0, delay_duration - 5)  # Simplified - assume 5 days float
            new_completion = original_completion + timedelta(days=impact_days)

        event.calculated_impact = impact_days

        return {
            'method': 'Time Impact Analysis',
            'delay_event': event.id,
            'delay_description': event.description,
            'delay_duration': delay_duration,
            'critical_path_impact': critical_impact,
            'schedule_impact_days': impact_days,
            'original_completion': original_completion,
            'impacted_completion': new_completion,
            'delay_type': event.delay_type.value,
            'responsible_party': event.responsible_party
        }

    def identify_concurrent_delays(self) -> List[Tuple[str, str, int]]:
        """Identify concurrent delay events."""
        concurrent = []

        events = list(self.delay_events.values())
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                # Check for overlap
                overlap_start = max(event1.start_date, event2.start_date)
                overlap_end = min(event1.end_date, event2.end_date)

                if overlap_start < overlap_end:
                    overlap_days = (overlap_end - overlap_start).days
                    concurrent.append((event1.id, event2.id, overlap_days))

                    event1.concurrent_with.append(event2.id)
                    event2.concurrent_with.append(event1.id)

        return concurrent

    def perform_windows_analysis(self, window_days: int = 30) -> List[WindowPeriod]:
        """Perform windows analysis by dividing project into periods."""
        baseline = self.schedule_versions.get("baseline")
        as_built = self.schedule_versions.get("as_built")

        if not baseline or not as_built:
            raise ValueError("Need baseline and as-built schedules")

        windows = []
        current_start = baseline.data_date
        window_num = 1

        while current_start < as_built.completion_date:
            window_end = min(
                current_start + timedelta(days=window_days),
                as_built.completion_date
            )

            # Find delay events in this window
            window_events = [
                e.id for e in self.delay_events.values()
                if e.start_date < window_end and e.end_date > current_start
            ]

            # Calculate delay by party
            party_delays = defaultdict(int)
            for event_id in window_events:
                event = self.delay_events[event_id]
                overlap_start = max(event.start_date, current_start)
                overlap_end = min(event.end_date, window_end)
                days = (overlap_end - overlap_start).days
                party_delays[event.responsible_party] += days

            window = WindowPeriod(
                window_id=f"W{window_num:02d}",
                start_date=current_start,
                end_date=window_end,
                planned_progress=0.0,  # Would calculate from schedule
                actual_progress=0.0,
                delay_days=sum(party_delays.values()),
                delay_events=window_events,
                responsible_parties=dict(party_delays)
            )
            windows.append(window)

            current_start = window_end
            window_num += 1

        self.window_periods = windows
        return windows

    def calculate_delay_damages(self) -> Dict:
        """Calculate potential delay damages."""
        # Summarize delays by type
        excusable_compensable = 0
        excusable_non_compensable = 0
        non_excusable = 0

        for event in self.delay_events.values():
            impact = event.calculated_impact or (event.end_date - event.start_date).days

            # Adjust for concurrency
            if event.concurrent_with:
                impact = impact // 2  # Simplified concurrency handling

            if event.delay_type == DelayType.EXCUSABLE_COMPENSABLE:
                excusable_compensable += impact
            elif event.delay_type == DelayType.EXCUSABLE_NON_COMPENSABLE:
                excusable_non_compensable += impact
            elif event.delay_type == DelayType.NON_EXCUSABLE:
                non_excusable += impact

        # Calculate damages
        contractor_damages = excusable_compensable * self.daily_cost
        owner_ld = non_excusable * self.daily_cost

        return {
            'excusable_compensable_days': excusable_compensable,
            'excusable_non_compensable_days': excusable_non_compensable,
            'non_excusable_days': non_excusable,
            'recommended_time_extension': excusable_compensable + excusable_non_compensable,
            'contractor_delay_damages': contractor_damages,
            'owner_liquidated_damages': owner_ld,
            'daily_rate_used': self.daily_cost
        }

    def generate_analysis_report(self, actual_completion: datetime) -> DelayAnalysisReport:
        """Generate comprehensive delay analysis report."""
        total_delay = (actual_completion - self.contract_completion).days

        # Categorize delays
        delay_by_cause = defaultdict(int)
        delay_by_party = defaultdict(int)
        excusable = 0
        non_excusable = 0
        concurrent = 0

        for event in self.delay_events.values():
            impact = event.calculated_impact or (event.end_date - event.start_date).days

            delay_by_cause[event.cause.value] += impact
            delay_by_party[event.responsible_party] += impact

            if event.concurrent_with:
                concurrent += impact // 2
            elif event.delay_type in [DelayType.EXCUSABLE_COMPENSABLE,
                                      DelayType.EXCUSABLE_NON_COMPENSABLE]:
                excusable += impact
            else:
                non_excusable += impact

        damages = self.calculate_delay_damages()

        return DelayAnalysisReport(
            project_name=self.project_name,
            analysis_date=datetime.now(),
            original_completion=self.contract_completion,
            actual_completion=actual_completion,
            total_delay=total_delay,
            excusable_delay=excusable,
            non_excusable_delay=non_excusable,
            concurrent_delay=concurrent,
            delay_events=list(self.delay_events.values()),
            delay_by_cause=dict(delay_by_cause),
            delay_by_party=dict(delay_by_party),
            recommended_extension=damages['recommended_time_extension'],
            potential_damages=damages['contractor_delay_damages']
        )

    def generate_report_markdown(self, report: DelayAnalysisReport) -> str:
        """Generate markdown report."""
        lines = [
            "# Delay Analysis Report",
            "",
            f"**Project:** {report.project_name}",
            f"**Analysis Date:** {report.analysis_date.strftime('%Y-%m-%d')}",
            "",
            "## Schedule Summary",
            "",
            f"| Milestone | Date |",
            f"|-----------|------|",
            f"| Contract Completion | {report.original_completion.strftime('%Y-%m-%d')} |",
            f"| Actual Completion | {report.actual_completion.strftime('%Y-%m-%d')} |",
            f"| **Total Delay** | **{report.total_delay} days** |",
            "",
            "## Delay Classification",
            "",
            f"| Category | Days |",
            f"|----------|------|",
            f"| Excusable Delay | {report.excusable_delay} |",
            f"| Non-Excusable Delay | {report.non_excusable_delay} |",
            f"| Concurrent Delay | {report.concurrent_delay} |",
            "",
            "## Delay by Cause",
            ""
        ]

        for cause, days in sorted(report.delay_by_cause.items(), key=lambda x: -x[1]):
            lines.append(f"- **{cause}**: {days} days")

        lines.extend([
            "",
            "## Delay by Responsible Party",
            ""
        ])

        for party, days in sorted(report.delay_by_party.items(), key=lambda x: -x[1]):
            lines.append(f"- **{party}**: {days} days")

        lines.extend([
            "",
            "## Recommendations",
            "",
            f"- **Recommended Time Extension:** {report.recommended_extension} days",
            f"- **Potential Delay Damages:** ${report.potential_damages:,.0f}",
            ""
        ])

        return "\n".join(lines)
```

## Quick Start

```python
from datetime import datetime, timedelta

# Initialize analyzer
analyzer = DelayAnalyzer(
    "Office Tower",
    contract_completion=datetime(2024, 12, 31)
)

# Add schedule versions
analyzer.add_schedule_version(
    "baseline", "baseline",
    datetime(2024, 1, 1),
    datetime(2024, 12, 31),
    activities={"A100": {"finish": datetime(2024, 6, 30), "is_critical": True}}
)

analyzer.add_schedule_version(
    "as_built", "as_built",
    datetime(2025, 3, 15),
    datetime(2025, 3, 15),
    activities={"A100": {"finish": datetime(2024, 8, 15)}}
)

# Add delay events
analyzer.add_delay_event(
    "D001",
    "Owner-directed design change to HVAC system",
    DelayCause.OWNER_CHANGE,
    DelayType.EXCUSABLE_COMPENSABLE,
    datetime(2024, 4, 1),
    datetime(2024, 5, 15),
    ["A100", "A101"],
    "Owner"
)

analyzer.add_delay_event(
    "D002",
    "Unexpected rock encountered in excavation",
    DelayCause.DIFFERING_CONDITIONS,
    DelayType.EXCUSABLE_COMPENSABLE,
    datetime(2024, 3, 15),
    datetime(2024, 4, 30),
    ["A050"],
    "Owner"
)

# Perform analyses
tia = analyzer.perform_time_impact_analysis("D001")
print(f"TIA Impact: {tia['schedule_impact_days']} days")

concurrent = analyzer.identify_concurrent_delays()
print(f"Concurrent delays found: {len(concurrent)}")

# Generate report
report = analyzer.generate_analysis_report(datetime(2025, 3, 15))
print(analyzer.generate_report_markdown(report))
```

## Requirements

```bash
pip install (no external dependencies)
```
