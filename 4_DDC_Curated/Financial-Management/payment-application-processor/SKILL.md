---
name: payment-application-processor
description: "Process construction payment applications. Validate schedule of values, calculate retainage, track billing status, and generate G702/G703 forms."
---

# Payment Application Processor

## Overview

Process construction payment applications from creation through approval. Validate against schedule of values, calculate retainage, generate AIA G702/G703 forms, and track payment status.

## Payment Application Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                PAYMENT APPLICATION FLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Schedule of    →    Draft      →    Review    →    Approve    │
│  Values              Pay App         & Verify        & Pay      │
│  ──────────          ───────         ────────        ────────   │
│  📋 SOV items        📝 Enter %      ✓ Verify        ✅ Approve │
│  💰 Line values      📊 Calculate    📸 Field        💵 Release │
│  📅 Billing plan     📄 G702/703     📧 Submit       📄 Record  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

class PayAppStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"
    PARTIAL_PAID = "partial_paid"

class LineItemStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"

@dataclass
class SOVLineItem:
    number: str
    description: str
    scheduled_value: float
    previous_completed: float = 0.0
    current_completed: float = 0.0
    materials_stored: float = 0.0
    percent_complete: float = 0.0
    balance_to_finish: float = 0.0
    retainage: float = 0.0

    def calculate(self, retainage_rate: float = 0.10):
        """Calculate line item values."""
        self.percent_complete = (
            (self.previous_completed + self.current_completed + self.materials_stored)
            / self.scheduled_value * 100
            if self.scheduled_value > 0 else 0
        )
        self.balance_to_finish = (
            self.scheduled_value - self.previous_completed -
            self.current_completed - self.materials_stored
        )
        total_completed = self.previous_completed + self.current_completed + self.materials_stored
        self.retainage = total_completed * retainage_rate

@dataclass
class PaymentApplication:
    application_number: int
    project_name: str
    contractor: str
    period_from: datetime
    period_to: datetime

    # Contract info
    original_contract: float
    change_orders: float = 0.0
    contract_sum: float = 0.0

    # Line items
    line_items: List[SOVLineItem] = field(default_factory=list)

    # Totals
    total_scheduled: float = 0.0
    previous_completed: float = 0.0
    current_completed: float = 0.0
    materials_stored: float = 0.0
    total_completed: float = 0.0
    percent_complete: float = 0.0
    balance_to_finish: float = 0.0
    retainage: float = 0.0
    net_amount_due: float = 0.0

    # Status
    status: PayAppStatus = PayAppStatus.DRAFT
    submitted_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None
    approved_amount: float = 0.0
    paid_date: Optional[datetime] = None
    paid_amount: float = 0.0

    # Retainage rates
    work_retainage_rate: float = 0.10
    stored_retainage_rate: float = 0.10

@dataclass
class G702Data:
    """AIA G702 Application and Certificate for Payment data."""
    application_number: int
    period_to: datetime
    project_name: str
    owner: str
    contractor: str
    architect: str

    original_contract_sum: float
    net_change_orders: float
    contract_sum_to_date: float
    total_completed_stored: float
    retainage: float
    total_earned_less_retainage: float
    less_previous_certificates: float
    current_payment_due: float
    balance_to_finish: float

class PaymentApplicationProcessor:
    """Process construction payment applications."""

    def __init__(self, project_name: str, contractor: str,
                 original_contract: float):
        self.project_name = project_name
        self.contractor = contractor
        self.original_contract = original_contract
        self.change_orders_total = 0.0

        self.schedule_of_values: List[SOVLineItem] = []
        self.pay_apps: Dict[int, PaymentApplication] = {}
        self.next_app_number = 1

        self.work_retainage_rate = 0.10
        self.stored_retainage_rate = 0.10

    def set_retainage_rates(self, work_rate: float, stored_rate: float = None):
        """Set retainage rates."""
        self.work_retainage_rate = work_rate
        self.stored_retainage_rate = stored_rate if stored_rate else work_rate

    def add_sov_item(self, number: str, description: str,
                    scheduled_value: float) -> SOVLineItem:
        """Add line item to schedule of values."""
        item = SOVLineItem(
            number=number,
            description=description,
            scheduled_value=scheduled_value
        )
        self.schedule_of_values.append(item)
        return item

    def import_sov(self, items: List[Dict]) -> int:
        """Import schedule of values from list."""
        count = 0
        for item in items:
            self.add_sov_item(
                item['number'],
                item['description'],
                item['value']
            )
            count += 1
        return count

    def add_change_order(self, amount: float, description: str = ""):
        """Add approved change order to contract."""
        self.change_orders_total += amount

        # Add as new SOV item
        co_number = f"CO-{len([i for i in self.schedule_of_values if 'CO-' in i.number])+1:03d}"
        self.add_sov_item(co_number, description or f"Change Order", amount)

    def create_pay_app(self, period_from: datetime,
                      period_to: datetime) -> PaymentApplication:
        """Create new payment application."""
        app_number = self.next_app_number

        # Copy SOV with previous values
        line_items = []
        for sov_item in self.schedule_of_values:
            # Get previous completed from last pay app
            prev_completed = 0.0
            if app_number > 1:
                prev_app = self.pay_apps.get(app_number - 1)
                if prev_app:
                    prev_item = next(
                        (i for i in prev_app.line_items if i.number == sov_item.number),
                        None
                    )
                    if prev_item:
                        prev_completed = (prev_item.previous_completed +
                                        prev_item.current_completed +
                                        prev_item.materials_stored)

            line_items.append(SOVLineItem(
                number=sov_item.number,
                description=sov_item.description,
                scheduled_value=sov_item.scheduled_value,
                previous_completed=prev_completed
            ))

        pay_app = PaymentApplication(
            application_number=app_number,
            project_name=self.project_name,
            contractor=self.contractor,
            period_from=period_from,
            period_to=period_to,
            original_contract=self.original_contract,
            change_orders=self.change_orders_total,
            contract_sum=self.original_contract + self.change_orders_total,
            line_items=line_items,
            work_retainage_rate=self.work_retainage_rate,
            stored_retainage_rate=self.stored_retainage_rate
        )

        self.pay_apps[app_number] = pay_app
        self.next_app_number += 1

        return pay_app

    def update_line_item(self, app_number: int, line_number: str,
                        current_completed: float = None,
                        materials_stored: float = None) -> SOVLineItem:
        """Update line item progress."""
        if app_number not in self.pay_apps:
            raise ValueError(f"Pay app {app_number} not found")

        pay_app = self.pay_apps[app_number]
        item = next((i for i in pay_app.line_items if i.number == line_number), None)

        if not item:
            raise ValueError(f"Line item {line_number} not found")

        if current_completed is not None:
            item.current_completed = current_completed
        if materials_stored is not None:
            item.materials_stored = materials_stored

        item.calculate(pay_app.work_retainage_rate)

        # Recalculate pay app totals
        self._calculate_totals(pay_app)

        return item

    def update_by_percentage(self, app_number: int, line_number: str,
                            percent_complete: float) -> SOVLineItem:
        """Update line item by percentage complete."""
        if app_number not in self.pay_apps:
            raise ValueError(f"Pay app {app_number} not found")

        pay_app = self.pay_apps[app_number]
        item = next((i for i in pay_app.line_items if i.number == line_number), None)

        if not item:
            raise ValueError(f"Line item {line_number} not found")

        # Calculate current completed from percentage
        total_earned = item.scheduled_value * (percent_complete / 100)
        item.current_completed = total_earned - item.previous_completed - item.materials_stored

        if item.current_completed < 0:
            item.current_completed = 0

        item.calculate(pay_app.work_retainage_rate)
        self._calculate_totals(pay_app)

        return item

    def _calculate_totals(self, pay_app: PaymentApplication):
        """Calculate pay app totals."""
        pay_app.total_scheduled = sum(i.scheduled_value for i in pay_app.line_items)
        pay_app.previous_completed = sum(i.previous_completed for i in pay_app.line_items)
        pay_app.current_completed = sum(i.current_completed for i in pay_app.line_items)
        pay_app.materials_stored = sum(i.materials_stored for i in pay_app.line_items)

        pay_app.total_completed = (
            pay_app.previous_completed +
            pay_app.current_completed +
            pay_app.materials_stored
        )

        pay_app.percent_complete = (
            pay_app.total_completed / pay_app.total_scheduled * 100
            if pay_app.total_scheduled > 0 else 0
        )

        pay_app.balance_to_finish = pay_app.contract_sum - pay_app.total_completed

        # Calculate retainage
        work_retainage = (pay_app.previous_completed + pay_app.current_completed) * pay_app.work_retainage_rate
        stored_retainage = pay_app.materials_stored * pay_app.stored_retainage_rate
        pay_app.retainage = work_retainage + stored_retainage

        # Previous certificates
        previous_certs = 0
        if pay_app.application_number > 1:
            prev_app = self.pay_apps.get(pay_app.application_number - 1)
            if prev_app:
                previous_certs = prev_app.total_completed - prev_app.retainage

        # Net amount due
        pay_app.net_amount_due = (
            pay_app.total_completed - pay_app.retainage - previous_certs
        )

    def submit_pay_app(self, app_number: int) -> PaymentApplication:
        """Submit pay app for review."""
        if app_number not in self.pay_apps:
            raise ValueError(f"Pay app {app_number} not found")

        pay_app = self.pay_apps[app_number]
        pay_app.status = PayAppStatus.SUBMITTED
        pay_app.submitted_date = datetime.now()

        return pay_app

    def approve_pay_app(self, app_number: int,
                       approved_amount: float = None) -> PaymentApplication:
        """Approve pay app."""
        if app_number not in self.pay_apps:
            raise ValueError(f"Pay app {app_number} not found")

        pay_app = self.pay_apps[app_number]
        pay_app.status = PayAppStatus.APPROVED
        pay_app.approved_date = datetime.now()
        pay_app.approved_amount = approved_amount if approved_amount else pay_app.net_amount_due

        return pay_app

    def record_payment(self, app_number: int, paid_amount: float,
                      paid_date: datetime = None) -> PaymentApplication:
        """Record payment received."""
        if app_number not in self.pay_apps:
            raise ValueError(f"Pay app {app_number} not found")

        pay_app = self.pay_apps[app_number]
        pay_app.paid_date = paid_date or datetime.now()
        pay_app.paid_amount = paid_amount

        if paid_amount >= pay_app.approved_amount:
            pay_app.status = PayAppStatus.PAID
        else:
            pay_app.status = PayAppStatus.PARTIAL_PAID

        return pay_app

    def generate_g702(self, app_number: int, owner: str,
                     architect: str) -> G702Data:
        """Generate AIA G702 data."""
        if app_number not in self.pay_apps:
            raise ValueError(f"Pay app {app_number} not found")

        pay_app = self.pay_apps[app_number]

        # Previous certificates
        previous_certs = 0
        if app_number > 1:
            prev_app = self.pay_apps.get(app_number - 1)
            if prev_app:
                previous_certs = prev_app.total_completed - prev_app.retainage

        return G702Data(
            application_number=pay_app.application_number,
            period_to=pay_app.period_to,
            project_name=pay_app.project_name,
            owner=owner,
            contractor=pay_app.contractor,
            architect=architect,
            original_contract_sum=pay_app.original_contract,
            net_change_orders=pay_app.change_orders,
            contract_sum_to_date=pay_app.contract_sum,
            total_completed_stored=pay_app.total_completed,
            retainage=pay_app.retainage,
            total_earned_less_retainage=pay_app.total_completed - pay_app.retainage,
            less_previous_certificates=previous_certs,
            current_payment_due=pay_app.net_amount_due,
            balance_to_finish=pay_app.balance_to_finish
        )

    def generate_g703(self, app_number: int) -> str:
        """Generate AIA G703 continuation sheet."""
        if app_number not in self.pay_apps:
            return "Pay app not found"

        pay_app = self.pay_apps[app_number]

        lines = [
            "# AIA G703 - Continuation Sheet",
            "",
            f"**Application Number:** {pay_app.application_number}",
            f"**Period To:** {pay_app.period_to.strftime('%Y-%m-%d')}",
            "",
            "| Item | Description | Scheduled | Previous | This Period | Stored | Total | % | Balance | Retainage |",
            "|------|-------------|-----------|----------|-------------|--------|-------|---|---------|-----------|"
        ]

        for item in pay_app.line_items:
            lines.append(
                f"| {item.number} | {item.description[:20]} | "
                f"${item.scheduled_value:,.0f} | ${item.previous_completed:,.0f} | "
                f"${item.current_completed:,.0f} | ${item.materials_stored:,.0f} | "
                f"${item.previous_completed + item.current_completed + item.materials_stored:,.0f} | "
                f"{item.percent_complete:.0f}% | ${item.balance_to_finish:,.0f} | "
                f"${item.retainage:,.0f} |"
            )

        lines.extend([
            "",
            f"| **TOTALS** | | ${pay_app.total_scheduled:,.0f} | "
            f"${pay_app.previous_completed:,.0f} | ${pay_app.current_completed:,.0f} | "
            f"${pay_app.materials_stored:,.0f} | ${pay_app.total_completed:,.0f} | "
            f"{pay_app.percent_complete:.0f}% | ${pay_app.balance_to_finish:,.0f} | "
            f"${pay_app.retainage:,.0f} |"
        ])

        return "\n".join(lines)

    def get_billing_summary(self) -> Dict:
        """Get billing summary across all pay apps."""
        total_billed = sum(pa.total_completed for pa in self.pay_apps.values())
        total_paid = sum(pa.paid_amount for pa in self.pay_apps.values())
        total_retainage = sum(pa.retainage for pa in self.pay_apps.values())

        pending = [pa for pa in self.pay_apps.values()
                   if pa.status in [PayAppStatus.SUBMITTED, PayAppStatus.UNDER_REVIEW, PayAppStatus.APPROVED]]

        return {
            "contract_sum": self.original_contract + self.change_orders_total,
            "total_billed": total_billed,
            "total_paid": total_paid,
            "total_retainage": total_retainage,
            "outstanding": total_billed - total_paid - total_retainage,
            "pending_apps": len(pending),
            "pending_amount": sum(pa.net_amount_due for pa in pending),
            "percent_billed": total_billed / (self.original_contract + self.change_orders_total) * 100
        }
```

## Quick Start

```python
from datetime import datetime

# Initialize processor
processor = PaymentApplicationProcessor(
    project_name="Office Tower",
    contractor="ABC Construction",
    original_contract=5000000
)

# Import schedule of values
processor.import_sov([
    {"number": "01", "description": "General Conditions", "value": 250000},
    {"number": "02", "description": "Sitework", "value": 300000},
    {"number": "03", "description": "Concrete", "value": 800000},
    {"number": "04", "description": "Structural Steel", "value": 1200000},
    {"number": "05", "description": "MEP", "value": 1500000},
    {"number": "06", "description": "Finishes", "value": 950000},
])

# Create pay application
pay_app = processor.create_pay_app(
    period_from=datetime(2024, 1, 1),
    period_to=datetime(2024, 1, 31)
)

# Update progress
processor.update_by_percentage(pay_app.application_number, "01", 100)  # GC 100%
processor.update_by_percentage(pay_app.application_number, "02", 75)   # Site 75%
processor.update_by_percentage(pay_app.application_number, "03", 50)   # Concrete 50%
processor.update_line_item(pay_app.application_number, "04",
                          current_completed=200000, materials_stored=300000)

# Submit and approve
processor.submit_pay_app(pay_app.application_number)
processor.approve_pay_app(pay_app.application_number)

# Generate G703
print(processor.generate_g703(pay_app.application_number))

# Get summary
summary = processor.get_billing_summary()
print(f"Percent Billed: {summary['percent_billed']:.1f}%")
```

## Requirements

```bash
pip install (no external dependencies)
```
