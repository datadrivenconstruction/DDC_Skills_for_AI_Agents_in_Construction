---
name: change-order-processor
description: "Process and manage construction change orders. Track costs, approvals, and impact on schedule and budget."
---

# Change Order Processor

## Business Case

### Problem Statement
Change orders cause project disruption:
- Delayed processing affects cash flow
- Unclear cost impact
- Lost documentation
- Schedule impacts not tracked

### Solution
Streamlined change order processing with cost analysis, approval workflow, and impact tracking.

### Business Value
- **Faster processing** - Reduce approval cycle time
- **Cost control** - Accurate change pricing
- **Documentation** - Complete audit trail
- **Impact visibility** - Schedule and budget effects

## Technical Implementation

```python
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class ChangeOrderStatus(Enum):
    """Change order status."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    VOID = "void"


class ChangeType(Enum):
    """Type of change."""
    OWNER_REQUESTED = "owner_requested"
    DESIGN_CHANGE = "design_change"
    FIELD_CONDITION = "field_condition"
    CODE_COMPLIANCE = "code_compliance"
    VALUE_ENGINEERING = "value_engineering"
    ERROR_OMISSION = "error_omission"


class ImpactType(Enum):
    """Impact categories."""
    COST_INCREASE = "cost_increase"
    COST_DECREASE = "cost_decrease"
    TIME_INCREASE = "time_increase"
    TIME_DECREASE = "time_decrease"
    NO_IMPACT = "no_impact"


@dataclass
class CostItem:
    """Change order cost item."""
    description: str
    quantity: float
    unit: str
    unit_cost: float
    total_cost: float
    category: str  # labor, material, equipment, subcontractor
    markup_percent: float = 0.0


@dataclass
class ApprovalRecord:
    """Approval workflow record."""
    approver_name: str
    approver_role: str
    action: str  # approved, rejected, returned
    action_date: datetime
    comments: str = ""


@dataclass
class ChangeOrder:
    """Change order record."""
    co_number: str
    title: str
    description: str
    change_type: ChangeType
    status: ChangeOrderStatus
    created_date: date
    created_by: str

    # Cost
    cost_items: List[CostItem] = field(default_factory=list)
    direct_cost: float = 0.0
    overhead_cost: float = 0.0
    profit_cost: float = 0.0
    total_cost: float = 0.0

    # Schedule
    schedule_impact_days: int = 0
    affected_activities: List[str] = field(default_factory=list)

    # Workflow
    approvals: List[ApprovalRecord] = field(default_factory=list)
    approved_date: Optional[date] = None
    approved_by: str = ""

    # References
    rfi_reference: str = ""
    spec_section: str = ""
    drawing_reference: str = ""
    location: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'co_number': self.co_number,
            'title': self.title,
            'change_type': self.change_type.value,
            'status': self.status.value,
            'created_date': self.created_date.isoformat(),
            'direct_cost': self.direct_cost,
            'overhead_cost': self.overhead_cost,
            'profit_cost': self.profit_cost,
            'total_cost': self.total_cost,
            'schedule_impact': self.schedule_impact_days,
            'approved_date': self.approved_date.isoformat() if self.approved_date else None
        }


class ChangeOrderProcessor:
    """Process and manage change orders."""

    DEFAULT_OVERHEAD_RATE = 0.10
    DEFAULT_PROFIT_RATE = 0.10

    def __init__(self, project_name: str, original_contract: float,
                 overhead_rate: float = None, profit_rate: float = None):
        self.project_name = project_name
        self.original_contract = original_contract
        self.overhead_rate = overhead_rate or self.DEFAULT_OVERHEAD_RATE
        self.profit_rate = profit_rate or self.DEFAULT_PROFIT_RATE
        self.change_orders: Dict[str, ChangeOrder] = {}
        self._co_counter = 0

    def create_change_order(self,
                           title: str,
                           description: str,
                           change_type: ChangeType,
                           created_by: str,
                           rfi_reference: str = "",
                           location: str = "") -> ChangeOrder:
        """Create new change order."""
        self._co_counter += 1
        co_number = f"CO-{self._co_counter:04d}"

        co = ChangeOrder(
            co_number=co_number,
            title=title,
            description=description,
            change_type=change_type,
            status=ChangeOrderStatus.DRAFT,
            created_date=date.today(),
            created_by=created_by,
            rfi_reference=rfi_reference,
            location=location
        )

        self.change_orders[co_number] = co
        return co

    def add_cost_item(self, co_number: str,
                     description: str,
                     quantity: float,
                     unit: str,
                     unit_cost: float,
                     category: str,
                     markup_percent: float = 0.0):
        """Add cost item to change order."""
        if co_number not in self.change_orders:
            raise ValueError(f"Change order {co_number} not found")

        co = self.change_orders[co_number]

        total = quantity * unit_cost * (1 + markup_percent)
        item = CostItem(
            description=description,
            quantity=quantity,
            unit=unit,
            unit_cost=unit_cost,
            total_cost=total,
            category=category,
            markup_percent=markup_percent
        )

        co.cost_items.append(item)
        self._recalculate_totals(co)

    def _recalculate_totals(self, co: ChangeOrder):
        """Recalculate change order totals."""
        co.direct_cost = sum(item.total_cost for item in co.cost_items)
        co.overhead_cost = co.direct_cost * self.overhead_rate
        co.profit_cost = (co.direct_cost + co.overhead_cost) * self.profit_rate
        co.total_cost = co.direct_cost + co.overhead_cost + co.profit_cost

    def set_schedule_impact(self, co_number: str, days: int,
                           affected_activities: List[str] = None):
        """Set schedule impact."""
        if co_number not in self.change_orders:
            raise ValueError(f"Change order {co_number} not found")

        co = self.change_orders[co_number]
        co.schedule_impact_days = days
        co.affected_activities = affected_activities or []

    def submit_for_review(self, co_number: str):
        """Submit change order for review."""
        if co_number not in self.change_orders:
            raise ValueError(f"Change order {co_number} not found")

        co = self.change_orders[co_number]
        if co.status != ChangeOrderStatus.DRAFT:
            raise ValueError("Can only submit draft change orders")

        co.status = ChangeOrderStatus.PENDING_REVIEW

    def submit_for_approval(self, co_number: str, reviewer: str, comments: str = ""):
        """Submit for approval after review."""
        if co_number not in self.change_orders:
            raise ValueError(f"Change order {co_number} not found")

        co = self.change_orders[co_number]
        if co.status != ChangeOrderStatus.PENDING_REVIEW:
            raise ValueError("Must be in review status")

        co.approvals.append(ApprovalRecord(
            approver_name=reviewer,
            approver_role="Reviewer",
            action="reviewed",
            action_date=datetime.now(),
            comments=comments
        ))

        co.status = ChangeOrderStatus.PENDING_APPROVAL

    def approve_change_order(self, co_number: str, approver: str,
                            approver_role: str, comments: str = ""):
        """Approve change order."""
        if co_number not in self.change_orders:
            raise ValueError(f"Change order {co_number} not found")

        co = self.change_orders[co_number]

        co.approvals.append(ApprovalRecord(
            approver_name=approver,
            approver_role=approver_role,
            action="approved",
            action_date=datetime.now(),
            comments=comments
        ))

        co.status = ChangeOrderStatus.APPROVED
        co.approved_date = date.today()
        co.approved_by = approver

    def reject_change_order(self, co_number: str, rejector: str,
                           reason: str):
        """Reject change order."""
        if co_number not in self.change_orders:
            raise ValueError(f"Change order {co_number} not found")

        co = self.change_orders[co_number]

        co.approvals.append(ApprovalRecord(
            approver_name=rejector,
            approver_role="Approver",
            action="rejected",
            action_date=datetime.now(),
            comments=reason
        ))

        co.status = ChangeOrderStatus.REJECTED

    def get_summary(self) -> Dict[str, Any]:
        """Generate change order summary."""
        cos = list(self.change_orders.values())

        by_status = {}
        by_type = {}
        total_approved = 0
        total_pending = 0
        total_schedule_impact = 0

        for co in cos:
            # By status
            status = co.status.value
            by_status[status] = by_status.get(status, 0) + 1

            # By type
            change_type = co.change_type.value
            by_type[change_type] = by_type.get(change_type, 0) + co.total_cost

            # Totals
            if co.status == ChangeOrderStatus.APPROVED:
                total_approved += co.total_cost
                total_schedule_impact += co.schedule_impact_days
            elif co.status in [ChangeOrderStatus.PENDING_REVIEW, ChangeOrderStatus.PENDING_APPROVAL]:
                total_pending += co.total_cost

        current_contract = self.original_contract + total_approved

        return {
            'project': self.project_name,
            'original_contract': self.original_contract,
            'approved_changes': total_approved,
            'current_contract': current_contract,
            'pending_changes': total_pending,
            'potential_contract': current_contract + total_pending,
            'total_change_orders': len(cos),
            'by_status': by_status,
            'by_type': by_type,
            'total_schedule_impact_days': total_schedule_impact,
            'change_percent': round(total_approved / self.original_contract * 100, 1) if self.original_contract > 0 else 0
        }

    def get_pending_approvals(self) -> List[ChangeOrder]:
        """Get change orders pending approval."""
        return [co for co in self.change_orders.values()
                if co.status in [ChangeOrderStatus.PENDING_REVIEW, ChangeOrderStatus.PENDING_APPROVAL]]

    def export_log(self, output_path: str):
        """Export change order log to Excel."""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary
            summary = self.get_summary()
            summary_df = pd.DataFrame([
                {'Metric': 'Original Contract', 'Value': summary['original_contract']},
                {'Metric': 'Approved Changes', 'Value': summary['approved_changes']},
                {'Metric': 'Current Contract', 'Value': summary['current_contract']},
                {'Metric': 'Pending Changes', 'Value': summary['pending_changes']},
                {'Metric': 'Change %', 'Value': f"{summary['change_percent']}%"},
                {'Metric': 'Schedule Impact (days)', 'Value': summary['total_schedule_impact_days']}
            ])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Change order list
            co_data = [co.to_dict() for co in self.change_orders.values()]
            pd.DataFrame(co_data).to_excel(writer, sheet_name='Change Orders', index=False)

            # Cost details
            cost_data = []
            for co in self.change_orders.values():
                for item in co.cost_items:
                    cost_data.append({
                        'CO Number': co.co_number,
                        'Description': item.description,
                        'Quantity': item.quantity,
                        'Unit': item.unit,
                        'Unit Cost': item.unit_cost,
                        'Total': item.total_cost,
                        'Category': item.category
                    })
            if cost_data:
                pd.DataFrame(cost_data).to_excel(writer, sheet_name='Cost Details', index=False)

        return output_path
```

## Quick Start

```python
# Initialize processor
processor = ChangeOrderProcessor(
    project_name="Office Tower",
    original_contract=50000000
)

# Create change order
co = processor.create_change_order(
    title="Additional Electrical Outlets",
    description="Add 50 electrical outlets per owner request",
    change_type=ChangeType.OWNER_REQUESTED,
    created_by="Project Manager"
)

# Add cost items
processor.add_cost_item(co.co_number, "Electrical outlets", 50, "EA", 150, "material")
processor.add_cost_item(co.co_number, "Installation labor", 25, "HR", 85, "labor")

# Set schedule impact
processor.set_schedule_impact(co.co_number, days=5)

# Submit for approval
processor.submit_for_review(co.co_number)
```

## Common Use Cases

### 1. Process Approval
```python
processor.submit_for_approval(co.co_number, "Reviewer", "Cost verified")
processor.approve_change_order(co.co_number, "Owner Rep", "Owner", "Approved per request")
```

### 2. Get Summary
```python
summary = processor.get_summary()
print(f"Contract value: ${summary['current_contract']:,.0f}")
print(f"Change %: {summary['change_percent']}%")
```

### 3. Export Log
```python
processor.export_log("change_order_log.xlsx")
```

## Resources
- **DDC Book**: Chapter 3.1 - Cost Management
- **Reference**: AIA Document G701
