---
name: retention-tracker
description: "Track construction retainage/retention amounts. Monitor held amounts by subcontractor, track release conditions, and manage retainage billing."
---

# Retention Tracker

## Overview

Track retainage (retention) amounts held and released throughout construction projects. Monitor amounts by subcontractor, track release milestones, and ensure proper documentation for retention release.

## Retainage Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    RETAINAGE LIFECYCLE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Progress Billing    →    Substantial    →    Final Release    │
│  ────────────────         ───────────         ─────────────     │
│  10% withheld            50% released         50% released      │
│  Each pay app            At punch list        At final          │
│  Cumulative              completion           completion        │
│                                                                  │
│  Owner holds from GC  →  GC holds from subs  →  Flow-down      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

class RetentionStatus(Enum):
    HELD = "held"
    PARTIAL_RELEASE = "partial_release"
    PENDING_RELEASE = "pending_release"
    RELEASED = "released"

class ReleaseMilestone(Enum):
    SUBSTANTIAL_COMPLETION = "substantial_completion"
    PUNCH_LIST_COMPLETE = "punch_list_complete"
    FINAL_COMPLETION = "final_completion"
    WARRANTY_EXPIRATION = "warranty_expiration"

@dataclass
class RetentionEntry:
    pay_app_number: int
    billing_date: datetime
    gross_billing: float
    retention_rate: float
    retention_amount: float
    status: RetentionStatus = RetentionStatus.HELD

@dataclass
class RetentionRelease:
    id: str
    release_date: datetime
    milestone: ReleaseMilestone
    amount: float
    remaining_after: float
    approved_by: str
    conditions_met: List[str] = field(default_factory=list)
    lien_waivers_received: bool = False
    consent_of_surety: bool = False

@dataclass
class SubcontractorRetention:
    subcontractor_id: str
    subcontractor_name: str
    trade: str
    contract_value: float
    retention_rate: float
    entries: List[RetentionEntry] = field(default_factory=list)
    releases: List[RetentionRelease] = field(default_factory=list)
    total_billed: float = 0.0
    total_retained: float = 0.0
    total_released: float = 0.0
    balance_held: float = 0.0
    status: RetentionStatus = RetentionStatus.HELD

class RetentionTracker:
    """Track construction retainage amounts."""

    # Default release schedule
    DEFAULT_RELEASE_SCHEDULE = {
        ReleaseMilestone.SUBSTANTIAL_COMPLETION: 0.50,  # 50% at substantial
        ReleaseMilestone.FINAL_COMPLETION: 0.50,        # 50% at final
    }

    def __init__(self, project_name: str, default_rate: float = 0.10):
        self.project_name = project_name
        self.default_rate = default_rate
        self.subcontractors: Dict[str, SubcontractorRetention] = {}
        self.release_schedule = dict(self.DEFAULT_RELEASE_SCHEDULE)

        # Project-level retention (from owner)
        self.owner_retention = SubcontractorRetention(
            subcontractor_id="OWNER",
            subcontractor_name="Owner Retention",
            trade="GC",
            contract_value=0,
            retention_rate=default_rate
        )

    def set_release_schedule(self, schedule: Dict[ReleaseMilestone, float]):
        """Set custom release schedule."""
        self.release_schedule = schedule

    def add_subcontractor(self, id: str, name: str, trade: str,
                         contract_value: float,
                         retention_rate: float = None) -> SubcontractorRetention:
        """Add subcontractor to track."""
        sub = SubcontractorRetention(
            subcontractor_id=id,
            subcontractor_name=name,
            trade=trade,
            contract_value=contract_value,
            retention_rate=retention_rate if retention_rate else self.default_rate
        )
        self.subcontractors[id] = sub
        return sub

    def record_billing(self, subcontractor_id: str, pay_app_number: int,
                      billing_date: datetime, gross_billing: float) -> RetentionEntry:
        """Record billing and calculate retention."""
        if subcontractor_id not in self.subcontractors:
            raise ValueError(f"Subcontractor {subcontractor_id} not found")

        sub = self.subcontractors[subcontractor_id]

        retention_amount = gross_billing * sub.retention_rate

        entry = RetentionEntry(
            pay_app_number=pay_app_number,
            billing_date=billing_date,
            gross_billing=gross_billing,
            retention_rate=sub.retention_rate,
            retention_amount=retention_amount
        )

        sub.entries.append(entry)

        # Update totals
        sub.total_billed += gross_billing
        sub.total_retained += retention_amount
        sub.balance_held = sub.total_retained - sub.total_released

        return entry

    def record_owner_billing(self, pay_app_number: int, billing_date: datetime,
                            gross_billing: float) -> RetentionEntry:
        """Record owner-level retention."""
        retention_amount = gross_billing * self.owner_retention.retention_rate

        entry = RetentionEntry(
            pay_app_number=pay_app_number,
            billing_date=billing_date,
            gross_billing=gross_billing,
            retention_rate=self.owner_retention.retention_rate,
            retention_amount=retention_amount
        )

        self.owner_retention.entries.append(entry)
        self.owner_retention.total_billed += gross_billing
        self.owner_retention.total_retained += retention_amount
        self.owner_retention.balance_held = (
            self.owner_retention.total_retained - self.owner_retention.total_released
        )

        return entry

    def release_retention(self, subcontractor_id: str, milestone: ReleaseMilestone,
                         amount: float = None, approved_by: str = "",
                         conditions: List[str] = None,
                         lien_waivers: bool = False,
                         consent_of_surety: bool = False) -> RetentionRelease:
        """Release retention for subcontractor."""
        if subcontractor_id not in self.subcontractors:
            raise ValueError(f"Subcontractor {subcontractor_id} not found")

        sub = self.subcontractors[subcontractor_id]

        # Calculate release amount if not specified
        if amount is None:
            release_pct = self.release_schedule.get(milestone, 0.5)
            amount = sub.balance_held * release_pct

        if amount > sub.balance_held:
            amount = sub.balance_held

        release_id = f"REL-{subcontractor_id}-{len(sub.releases)+1:03d}"

        release = RetentionRelease(
            id=release_id,
            release_date=datetime.now(),
            milestone=milestone,
            amount=amount,
            remaining_after=sub.balance_held - amount,
            approved_by=approved_by,
            conditions_met=conditions or [],
            lien_waivers_received=lien_waivers,
            consent_of_surety=consent_of_surety
        )

        sub.releases.append(release)
        sub.total_released += amount
        sub.balance_held -= amount

        if sub.balance_held <= 0:
            sub.status = RetentionStatus.RELEASED
        elif sub.total_released > 0:
            sub.status = RetentionStatus.PARTIAL_RELEASE

        return release

    def release_owner_retention(self, milestone: ReleaseMilestone,
                               amount: float = None,
                               approved_by: str = "") -> RetentionRelease:
        """Release owner-level retention."""
        if amount is None:
            release_pct = self.release_schedule.get(milestone, 0.5)
            amount = self.owner_retention.balance_held * release_pct

        if amount > self.owner_retention.balance_held:
            amount = self.owner_retention.balance_held

        release_id = f"REL-OWNER-{len(self.owner_retention.releases)+1:03d}"

        release = RetentionRelease(
            id=release_id,
            release_date=datetime.now(),
            milestone=milestone,
            amount=amount,
            remaining_after=self.owner_retention.balance_held - amount,
            approved_by=approved_by
        )

        self.owner_retention.releases.append(release)
        self.owner_retention.total_released += amount
        self.owner_retention.balance_held -= amount

        return release

    def check_release_conditions(self, subcontractor_id: str) -> Dict:
        """Check conditions required for retention release."""
        if subcontractor_id not in self.subcontractors:
            raise ValueError(f"Subcontractor {subcontractor_id} not found")

        sub = self.subcontractors[subcontractor_id]

        conditions = {
            "punch_list_complete": False,  # Check externally
            "final_lien_waiver": False,
            "consent_of_surety": False,
            "as_builts_submitted": False,
            "warranty_documents": False,
            "training_complete": False,
            "closeout_docs": False
        }

        # Check last release for received items
        if sub.releases:
            last_release = sub.releases[-1]
            conditions["final_lien_waiver"] = last_release.lien_waivers_received
            conditions["consent_of_surety"] = last_release.consent_of_surety

        missing = [k for k, v in conditions.items() if not v]

        return {
            "subcontractor": sub.subcontractor_name,
            "balance_held": sub.balance_held,
            "conditions_status": conditions,
            "missing_conditions": missing,
            "ready_for_release": len(missing) == 0
        }

    def get_retention_summary(self) -> Dict:
        """Get overall retention summary."""
        total_retained = sum(s.total_retained for s in self.subcontractors.values())
        total_released = sum(s.total_released for s in self.subcontractors.values())
        total_held = sum(s.balance_held for s in self.subcontractors.values())

        by_status = {}
        for sub in self.subcontractors.values():
            status = sub.status.value
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "owner_retained": self.owner_retention.total_retained,
            "owner_released": self.owner_retention.total_released,
            "owner_balance": self.owner_retention.balance_held,
            "sub_total_retained": total_retained,
            "sub_total_released": total_released,
            "sub_balance_held": total_held,
            "net_retention_position": self.owner_retention.balance_held - total_held,
            "subcontractors_count": len(self.subcontractors),
            "by_status": by_status
        }

    def get_aged_retention(self) -> List[Dict]:
        """Get aged retention report."""
        aged = []

        for sub in self.subcontractors.values():
            if sub.balance_held <= 0:
                continue

            # Find oldest unreleased entry
            oldest_date = None
            for entry in sub.entries:
                if entry.status == RetentionStatus.HELD:
                    if oldest_date is None or entry.billing_date < oldest_date:
                        oldest_date = entry.billing_date

            days_held = (datetime.now() - oldest_date).days if oldest_date else 0

            aged.append({
                "subcontractor_id": sub.subcontractor_id,
                "subcontractor_name": sub.subcontractor_name,
                "trade": sub.trade,
                "balance_held": sub.balance_held,
                "oldest_entry_date": oldest_date,
                "days_held": days_held
            })

        return sorted(aged, key=lambda x: -x["days_held"])

    def forecast_releases(self, substantial_date: datetime,
                         final_date: datetime) -> List[Dict]:
        """Forecast retention releases."""
        forecasts = []

        for sub in self.subcontractors.values():
            if sub.balance_held <= 0:
                continue

            # Substantial completion release
            sub_release = sub.balance_held * self.release_schedule.get(
                ReleaseMilestone.SUBSTANTIAL_COMPLETION, 0.5
            )
            forecasts.append({
                "date": substantial_date,
                "subcontractor": sub.subcontractor_name,
                "milestone": "Substantial Completion",
                "amount": sub_release
            })

            # Final completion release
            final_release = sub.balance_held - sub_release
            forecasts.append({
                "date": final_date,
                "subcontractor": sub.subcontractor_name,
                "milestone": "Final Completion",
                "amount": final_release
            })

        return sorted(forecasts, key=lambda x: x["date"])

    def generate_report(self) -> str:
        """Generate retention status report."""
        summary = self.get_retention_summary()

        lines = [
            "# Retention Status Report",
            "",
            f"**Project:** {self.project_name}",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## Summary",
            "",
            "### Owner Retention",
            "",
            f"| Metric | Amount |",
            f"|--------|--------|",
            f"| Total Retained | ${summary['owner_retained']:,.0f} |",
            f"| Total Released | ${summary['owner_released']:,.0f} |",
            f"| **Balance Held** | **${summary['owner_balance']:,.0f}** |",
            "",
            "### Subcontractor Retention",
            "",
            f"| Metric | Amount |",
            f"|--------|--------|",
            f"| Total Retained | ${summary['sub_total_retained']:,.0f} |",
            f"| Total Released | ${summary['sub_total_released']:,.0f} |",
            f"| **Balance Held** | **${summary['sub_balance_held']:,.0f}** |",
            "",
            f"**Net Position:** ${summary['net_retention_position']:,.0f}",
            "",
            "## By Subcontractor",
            "",
            "| Subcontractor | Trade | Contract | Retained | Released | Held | Status |",
            "|---------------|-------|----------|----------|----------|------|--------|"
        ]

        for sub in sorted(self.subcontractors.values(),
                         key=lambda s: -s.balance_held):
            lines.append(
                f"| {sub.subcontractor_name} | {sub.trade} | "
                f"${sub.contract_value:,.0f} | ${sub.total_retained:,.0f} | "
                f"${sub.total_released:,.0f} | ${sub.balance_held:,.0f} | "
                f"{sub.status.value} |"
            )

        # Aged retention
        aged = self.get_aged_retention()
        if aged:
            lines.extend([
                "",
                "## Aged Retention",
                "",
                "| Subcontractor | Balance | Days Held |",
                "|---------------|---------|-----------|"
            ])
            for item in aged[:10]:
                lines.append(
                    f"| {item['subcontractor_name']} | "
                    f"${item['balance_held']:,.0f} | {item['days_held']} |"
                )

        return "\n".join(lines)
```

## Quick Start

```python
from datetime import datetime

# Initialize tracker
tracker = RetentionTracker("Office Tower", default_rate=0.10)

# Add subcontractors
tracker.add_subcontractor("SUB-001", "ABC Mechanical", "HVAC", 500000)
tracker.add_subcontractor("SUB-002", "XYZ Electric", "Electrical", 350000)

# Record billings
tracker.record_billing("SUB-001", 1, datetime(2024, 1, 31), 50000)
tracker.record_billing("SUB-001", 2, datetime(2024, 2, 29), 75000)
tracker.record_billing("SUB-002", 1, datetime(2024, 1, 31), 35000)

# Record owner-level retention
tracker.record_owner_billing(1, datetime(2024, 1, 31), 200000)

# Check release conditions
conditions = tracker.check_release_conditions("SUB-001")
print(f"Missing conditions: {conditions['missing_conditions']}")

# Release retention at substantial completion
tracker.release_retention(
    "SUB-001",
    ReleaseMilestone.SUBSTANTIAL_COMPLETION,
    approved_by="Project Manager",
    lien_waivers=True
)

# Generate report
print(tracker.generate_report())

# Forecast releases
forecasts = tracker.forecast_releases(
    datetime(2024, 12, 1),
    datetime(2025, 1, 15)
)
for f in forecasts[:5]:
    print(f"{f['date'].strftime('%Y-%m-%d')}: {f['subcontractor']} - ${f['amount']:,.0f}")
```

## Requirements

```bash
pip install (no external dependencies)
```
