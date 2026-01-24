---
name: subcontractor-payment-tracker
description: "Track subcontractor payments, lien waivers, and compliance. Manage payment schedules and documentation."
---

# Subcontractor Payment Tracker

## Business Case

### Problem Statement
Subcontractor payments require careful management:
- Complex payment schedules
- Lien waiver tracking
- Compliance documentation
- Cash flow coordination

### Solution
Comprehensive subcontractor payment tracking with lien waiver management, compliance monitoring, and payment scheduling.

## Technical Implementation

```python
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class PaymentStatus(Enum):
    SCHEDULED = "scheduled"
    INVOICED = "invoiced"
    APPROVED = "approved"
    PAID = "paid"
    HELD = "held"
    DISPUTED = "disputed"


class WaiverType(Enum):
    CONDITIONAL_PROGRESS = "conditional_progress"
    UNCONDITIONAL_PROGRESS = "unconditional_progress"
    CONDITIONAL_FINAL = "conditional_final"
    UNCONDITIONAL_FINAL = "unconditional_final"


@dataclass
class LienWaiver:
    waiver_id: str
    waiver_type: WaiverType
    through_date: date
    amount: float
    received_date: Optional[date]
    file_path: str = ""


@dataclass
class SubcontractorPayment:
    payment_id: str
    subcontractor_id: str
    invoice_number: str
    invoice_date: date
    amount: float
    retention_held: float
    status: PaymentStatus
    scheduled_date: date
    paid_date: Optional[date] = None
    check_number: str = ""
    lien_waiver: Optional[LienWaiver] = None
    notes: str = ""


@dataclass
class Subcontractor:
    sub_id: str
    company_name: str
    contact_name: str
    email: str
    phone: str
    contract_amount: float
    retention_percent: float
    trade: str
    payments: List[SubcontractorPayment] = field(default_factory=list)
    insurance_expiry: Optional[date] = None
    license_number: str = ""

    @property
    def total_paid(self) -> float:
        return sum(p.amount for p in self.payments if p.status == PaymentStatus.PAID)

    @property
    def total_retention(self) -> float:
        return sum(p.retention_held for p in self.payments)

    @property
    def balance_remaining(self) -> float:
        return self.contract_amount - self.total_paid - self.total_retention


class SubcontractorPaymentTracker:
    """Track subcontractor payments and compliance."""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.subcontractors: Dict[str, Subcontractor] = {}
        self._payment_counter = 0

    def add_subcontractor(self, company_name: str, contact_name: str, email: str,
                         phone: str, contract_amount: float, trade: str,
                         retention_percent: float = 0.10) -> Subcontractor:
        sub_id = f"SUB-{len(self.subcontractors) + 1:03d}"
        sub = Subcontractor(
            sub_id=sub_id,
            company_name=company_name,
            contact_name=contact_name,
            email=email,
            phone=phone,
            contract_amount=contract_amount,
            retention_percent=retention_percent,
            trade=trade
        )
        self.subcontractors[sub_id] = sub
        return sub

    def record_invoice(self, sub_id: str, invoice_number: str, invoice_date: date,
                      gross_amount: float, scheduled_date: date = None) -> SubcontractorPayment:
        if sub_id not in self.subcontractors:
            raise ValueError(f"Subcontractor {sub_id} not found")

        sub = self.subcontractors[sub_id]
        self._payment_counter += 1

        retention = gross_amount * sub.retention_percent
        net_amount = gross_amount - retention

        payment = SubcontractorPayment(
            payment_id=f"PAY-{self._payment_counter:05d}",
            subcontractor_id=sub_id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            amount=net_amount,
            retention_held=retention,
            status=PaymentStatus.INVOICED,
            scheduled_date=scheduled_date or invoice_date + timedelta(days=30)
        )
        sub.payments.append(payment)
        return payment

    def approve_payment(self, payment_id: str, sub_id: str):
        sub = self.subcontractors.get(sub_id)
        if not sub:
            return
        for payment in sub.payments:
            if payment.payment_id == payment_id:
                payment.status = PaymentStatus.APPROVED
                break

    def record_payment(self, payment_id: str, sub_id: str, check_number: str,
                      paid_date: date = None):
        sub = self.subcontractors.get(sub_id)
        if not sub:
            return
        for payment in sub.payments:
            if payment.payment_id == payment_id:
                payment.status = PaymentStatus.PAID
                payment.paid_date = paid_date or date.today()
                payment.check_number = check_number
                break

    def attach_lien_waiver(self, payment_id: str, sub_id: str, waiver_type: WaiverType,
                          through_date: date, amount: float, received_date: date = None):
        sub = self.subcontractors.get(sub_id)
        if not sub:
            return
        for payment in sub.payments:
            if payment.payment_id == payment_id:
                waiver = LienWaiver(
                    waiver_id=f"LW-{payment_id}",
                    waiver_type=waiver_type,
                    through_date=through_date,
                    amount=amount,
                    received_date=received_date or date.today()
                )
                payment.lien_waiver = waiver
                break

    def get_pending_payments(self) -> List[Dict[str, Any]]:
        pending = []
        for sub in self.subcontractors.values():
            for payment in sub.payments:
                if payment.status in [PaymentStatus.INVOICED, PaymentStatus.APPROVED]:
                    pending.append({
                        'payment_id': payment.payment_id,
                        'subcontractor': sub.company_name,
                        'invoice': payment.invoice_number,
                        'amount': payment.amount,
                        'scheduled': payment.scheduled_date,
                        'status': payment.status.value,
                        'has_waiver': payment.lien_waiver is not None
                    })
        return sorted(pending, key=lambda x: x['scheduled'])

    def get_missing_waivers(self) -> List[Dict[str, Any]]:
        missing = []
        for sub in self.subcontractors.values():
            for payment in sub.payments:
                if payment.status == PaymentStatus.PAID and not payment.lien_waiver:
                    missing.append({
                        'subcontractor': sub.company_name,
                        'payment_id': payment.payment_id,
                        'amount': payment.amount,
                        'paid_date': payment.paid_date
                    })
        return missing

    def get_summary(self) -> Dict[str, Any]:
        total_contract = sum(s.contract_amount for s in self.subcontractors.values())
        total_paid = sum(s.total_paid for s in self.subcontractors.values())
        total_retention = sum(s.total_retention for s in self.subcontractors.values())

        return {
            'project': self.project_name,
            'total_subcontractors': len(self.subcontractors),
            'total_contract_value': total_contract,
            'total_paid': total_paid,
            'total_retention_held': total_retention,
            'remaining_to_pay': total_contract - total_paid - total_retention,
            'pending_payments': len(self.get_pending_payments()),
            'missing_waivers': len(self.get_missing_waivers())
        }

    def export_report(self, output_path: str):
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary by subcontractor
            sub_data = [{
                'ID': s.sub_id,
                'Company': s.company_name,
                'Trade': s.trade,
                'Contract': s.contract_amount,
                'Paid': s.total_paid,
                'Retention': s.total_retention,
                'Balance': s.balance_remaining
            } for s in self.subcontractors.values()]
            pd.DataFrame(sub_data).to_excel(writer, sheet_name='Subcontractors', index=False)

            # All payments
            pay_data = []
            for sub in self.subcontractors.values():
                for p in sub.payments:
                    pay_data.append({
                        'Payment ID': p.payment_id,
                        'Subcontractor': sub.company_name,
                        'Invoice': p.invoice_number,
                        'Amount': p.amount,
                        'Retention': p.retention_held,
                        'Status': p.status.value,
                        'Scheduled': p.scheduled_date,
                        'Paid': p.paid_date,
                        'Waiver': p.lien_waiver.waiver_type.value if p.lien_waiver else 'Missing'
                    })
            if pay_data:
                pd.DataFrame(pay_data).to_excel(writer, sheet_name='Payments', index=False)

        return output_path
```

## Quick Start

```python
tracker = SubcontractorPaymentTracker("Office Tower")

# Add subcontractor
sub = tracker.add_subcontractor(
    company_name="ABC Electrical",
    contact_name="John Smith",
    email="john@abcelectric.com",
    phone="555-1234",
    contract_amount=500000,
    trade="Electrical"
)

# Record invoice
payment = tracker.record_invoice(sub.sub_id, "INV-001", date.today(), 50000)

# Approve and pay
tracker.approve_payment(payment.payment_id, sub.sub_id)
tracker.record_payment(payment.payment_id, sub.sub_id, "CHK-12345")

# Attach waiver
tracker.attach_lien_waiver(payment.payment_id, sub.sub_id,
                          WaiverType.UNCONDITIONAL_PROGRESS, date.today(), 50000)
```

## Resources
- **DDC Book**: Chapter 3.1 - Cost Management
