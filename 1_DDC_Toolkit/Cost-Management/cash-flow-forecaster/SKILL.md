---
name: cash-flow-forecaster
description: "Forecast project cash flow based on schedule and cost data. Generate S-curves and payment projections."
---

# Cash Flow Forecaster

## Business Case

### Problem Statement
Poor cash flow management causes issues:
- Insufficient funds for payments
- Missed early payment discounts
- Inaccurate financial projections
- Difficulty in financing negotiations

### Solution
Generate cash flow forecasts from schedule and cost data, including S-curve projections and payment timing analysis.

### Business Value
- **Financial planning** - Accurate funding requirements
- **Vendor relations** - Timely payments
- **Financing** - Support loan draw schedules
- **Decision support** - Cash position awareness

## Technical Implementation

```python
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class CashFlowType(Enum):
    """Cash flow types."""
    INFLOW = "inflow"
    OUTFLOW = "outflow"


class PaymentTerms(Enum):
    """Standard payment terms."""
    NET_30 = 30
    NET_45 = 45
    NET_60 = 60
    NET_90 = 90
    MILESTONE = 0
    PROGRESS = 0


@dataclass
class CostItem:
    """Cost item for cash flow."""
    item_id: str
    description: str
    total_amount: float
    start_date: date
    end_date: date
    payment_terms: PaymentTerms
    distribution: str = "linear"  # linear, front_loaded, back_loaded, s_curve
    retention_percent: float = 0.10
    category: str = ""


@dataclass
class PaymentSchedule:
    """Scheduled payment."""
    payment_id: str
    item_id: str
    description: str
    amount: float
    due_date: date
    payment_type: CashFlowType
    is_retention: bool = False
    paid: bool = False
    paid_date: Optional[date] = None


@dataclass
class CashFlowPeriod:
    """Cash flow for a period."""
    period_start: date
    period_end: date
    inflows: float
    outflows: float
    net_cash_flow: float
    cumulative_cash_flow: float
    opening_balance: float
    closing_balance: float


class CashFlowForecaster:
    """Forecast project cash flow."""

    def __init__(self, project_name: str, project_start: date, project_end: date,
                 initial_balance: float = 0, currency: str = "USD"):
        self.project_name = project_name
        self.project_start = project_start
        self.project_end = project_end
        self.initial_balance = initial_balance
        self.currency = currency
        self.cost_items: List[CostItem] = []
        self.revenue_items: List[CostItem] = []
        self.payments: List[PaymentSchedule] = []
        self._payment_counter = 0

    def add_cost_item(self, item_id: str, description: str, total_amount: float,
                     start_date: date, end_date: date,
                     payment_terms: PaymentTerms = PaymentTerms.NET_30,
                     distribution: str = "linear",
                     retention: float = 0.10,
                     category: str = "") -> CostItem:
        """Add cost item (outflow)."""
        item = CostItem(
            item_id=item_id,
            description=description,
            total_amount=total_amount,
            start_date=start_date,
            end_date=end_date,
            payment_terms=payment_terms,
            distribution=distribution,
            retention_percent=retention,
            category=category
        )
        self.cost_items.append(item)
        return item

    def add_revenue_item(self, item_id: str, description: str, total_amount: float,
                        start_date: date, end_date: date,
                        payment_terms: PaymentTerms = PaymentTerms.NET_30,
                        distribution: str = "linear",
                        retention: float = 0.10) -> CostItem:
        """Add revenue item (inflow)."""
        item = CostItem(
            item_id=item_id,
            description=description,
            total_amount=total_amount,
            start_date=start_date,
            end_date=end_date,
            payment_terms=payment_terms,
            distribution=distribution,
            retention_percent=retention
        )
        self.revenue_items.append(item)
        return item

    def _distribute_amount(self, total: float, start: date, end: date,
                          distribution: str, periods: int) -> List[float]:
        """Distribute amount over periods based on distribution type."""
        if periods <= 0:
            return [total]

        if distribution == "linear":
            return [total / periods] * periods
        elif distribution == "front_loaded":
            # More at the beginning
            weights = [periods - i for i in range(periods)]
            total_weight = sum(weights)
            return [total * w / total_weight for w in weights]
        elif distribution == "back_loaded":
            # More at the end
            weights = [i + 1 for i in range(periods)]
            total_weight = sum(weights)
            return [total * w / total_weight for w in weights]
        elif distribution == "s_curve":
            # S-curve distribution
            x = np.linspace(-3, 3, periods)
            weights = 1 / (1 + np.exp(-x))
            weights = weights / weights.sum()
            return [total * w for w in weights]
        else:
            return [total / periods] * periods

    def generate_payment_schedule(self, period_type: str = "monthly") -> List[PaymentSchedule]:
        """Generate payment schedule from cost items."""
        self.payments = []

        # Process cost items (outflows)
        for item in self.cost_items:
            self._generate_item_payments(item, CashFlowType.OUTFLOW, period_type)

        # Process revenue items (inflows)
        for item in self.revenue_items:
            self._generate_item_payments(item, CashFlowType.INFLOW, period_type)

        return sorted(self.payments, key=lambda x: x.due_date)

    def _generate_item_payments(self, item: CostItem, flow_type: CashFlowType,
                               period_type: str):
        """Generate payments for a single item."""
        # Calculate number of periods
        if period_type == "monthly":
            months = (item.end_date.year - item.start_date.year) * 12 + \
                    (item.end_date.month - item.start_date.month) + 1
            periods = max(1, months)
        else:  # weekly
            days = (item.end_date - item.start_date).days
            periods = max(1, days // 7)

        # Distribute amount
        net_amount = item.total_amount * (1 - item.retention_percent)
        amounts = self._distribute_amount(net_amount, item.start_date, item.end_date,
                                         item.distribution, periods)

        # Create payments
        current_date = item.start_date
        for i, amount in enumerate(amounts):
            # Calculate payment due date based on terms
            if item.payment_terms == PaymentTerms.MILESTONE:
                due_date = current_date
            else:
                due_date = current_date + timedelta(days=item.payment_terms.value)

            self._payment_counter += 1
            payment = PaymentSchedule(
                payment_id=f"PAY-{self._payment_counter:05d}",
                item_id=item.item_id,
                description=f"{item.description} - Period {i+1}",
                amount=amount,
                due_date=due_date,
                payment_type=flow_type
            )
            self.payments.append(payment)

            # Move to next period
            if period_type == "monthly":
                if current_date.month == 12:
                    current_date = date(current_date.year + 1, 1, current_date.day)
                else:
                    try:
                        current_date = date(current_date.year, current_date.month + 1, current_date.day)
                    except ValueError:
                        # Handle months with fewer days
                        current_date = date(current_date.year, current_date.month + 1, 28)
            else:
                current_date += timedelta(days=7)

        # Add retention release at project end
        if item.retention_percent > 0:
            retention_amount = item.total_amount * item.retention_percent
            self._payment_counter += 1
            retention_payment = PaymentSchedule(
                payment_id=f"PAY-{self._payment_counter:05d}",
                item_id=item.item_id,
                description=f"{item.description} - Retention Release",
                amount=retention_amount,
                due_date=self.project_end + timedelta(days=60),
                payment_type=flow_type,
                is_retention=True
            )
            self.payments.append(retention_payment)

    def generate_cash_flow_forecast(self, period_type: str = "monthly") -> List[CashFlowPeriod]:
        """Generate cash flow forecast."""
        if not self.payments:
            self.generate_payment_schedule(period_type)

        # Group payments by period
        periods = []
        current_date = self.project_start
        cumulative = 0
        balance = self.initial_balance

        while current_date <= self.project_end + timedelta(days=90):
            # Calculate period end
            if period_type == "monthly":
                if current_date.month == 12:
                    period_end = date(current_date.year + 1, 1, 1) - timedelta(days=1)
                else:
                    period_end = date(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
            else:
                period_end = current_date + timedelta(days=6)

            # Filter payments for this period
            period_payments = [p for p in self.payments
                             if current_date <= p.due_date <= period_end]

            inflows = sum(p.amount for p in period_payments
                        if p.payment_type == CashFlowType.INFLOW)
            outflows = sum(p.amount for p in period_payments
                         if p.payment_type == CashFlowType.OUTFLOW)
            net = inflows - outflows
            cumulative += net

            period = CashFlowPeriod(
                period_start=current_date,
                period_end=period_end,
                inflows=inflows,
                outflows=outflows,
                net_cash_flow=net,
                cumulative_cash_flow=cumulative,
                opening_balance=balance,
                closing_balance=balance + net
            )
            periods.append(period)

            balance = period.closing_balance

            # Move to next period
            current_date = period_end + timedelta(days=1)

        return periods

    def generate_s_curve(self) -> pd.DataFrame:
        """Generate S-curve data (cumulative costs over time)."""
        forecast = self.generate_cash_flow_forecast()

        # Costs only (outflows)
        data = []
        cumulative_cost = 0
        total_cost = sum(item.total_amount for item in self.cost_items)

        for period in forecast:
            cumulative_cost += period.outflows
            percent_complete = (cumulative_cost / total_cost * 100) if total_cost > 0 else 0

            data.append({
                'date': period.period_end,
                'period_cost': period.outflows,
                'cumulative_cost': cumulative_cost,
                'percent_complete': round(percent_complete, 1),
                'total_budget': total_cost
            })

        return pd.DataFrame(data)

    def get_funding_requirements(self, buffer_percent: float = 0.10) -> Dict[str, Any]:
        """Calculate funding requirements."""
        forecast = self.generate_cash_flow_forecast()

        # Find peak negative cash flow
        min_balance = min(p.closing_balance for p in forecast)
        peak_funding = abs(min(0, min_balance))

        # Add buffer
        required_funding = peak_funding * (1 + buffer_percent)

        # Monthly funding needs
        monthly_needs = []
        for period in forecast:
            if period.net_cash_flow < 0:
                monthly_needs.append({
                    'month': period.period_start.strftime('%Y-%m'),
                    'funding_needed': abs(period.net_cash_flow)
                })

        return {
            'peak_funding_required': round(required_funding, 2),
            'peak_funding_month': min(forecast, key=lambda x: x.closing_balance).period_start.strftime('%Y-%m'),
            'total_outflows': sum(p.outflows for p in forecast),
            'total_inflows': sum(p.inflows for p in forecast),
            'monthly_funding_needs': monthly_needs,
            'buffer_percent': buffer_percent
        }

    def export_forecast(self, output_path: str):
        """Export cash flow forecast to Excel."""
        forecast = self.generate_cash_flow_forecast()
        s_curve = self.generate_s_curve()

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Cash flow forecast
            forecast_df = pd.DataFrame([{
                'Period Start': p.period_start,
                'Period End': p.period_end,
                'Inflows': p.inflows,
                'Outflows': p.outflows,
                'Net Cash Flow': p.net_cash_flow,
                'Cumulative': p.cumulative_cash_flow,
                'Opening Balance': p.opening_balance,
                'Closing Balance': p.closing_balance
            } for p in forecast])
            forecast_df.to_excel(writer, sheet_name='Cash Flow', index=False)

            # S-curve
            s_curve.to_excel(writer, sheet_name='S-Curve', index=False)

            # Payment schedule
            payments_df = pd.DataFrame([{
                'ID': p.payment_id,
                'Item': p.item_id,
                'Description': p.description,
                'Amount': p.amount,
                'Due Date': p.due_date,
                'Type': p.payment_type.value,
                'Retention': p.is_retention
            } for p in self.payments])
            payments_df.to_excel(writer, sheet_name='Payments', index=False)

        return output_path
```

## Quick Start

```python
from datetime import date

# Initialize forecaster
forecaster = CashFlowForecaster(
    project_name="Office Tower",
    project_start=date(2024, 1, 1),
    project_end=date(2025, 12, 31),
    initial_balance=5000000
)

# Add costs
forecaster.add_cost_item("CONC", "Concrete Work", 8000000,
                         date(2024, 3, 1), date(2024, 9, 30),
                         distribution="s_curve")

# Add revenue
forecaster.add_revenue_item("DRAW", "Owner Draws", 50000000,
                            date(2024, 1, 1), date(2025, 12, 31),
                            distribution="s_curve")

# Generate forecast
forecast = forecaster.generate_cash_flow_forecast()
print(f"Peak cash requirement: ${min(p.closing_balance for p in forecast):,.0f}")
```

## Common Use Cases

### 1. S-Curve Analysis
```python
s_curve = forecaster.generate_s_curve()
# Plot cumulative cost over time
```

### 2. Funding Requirements
```python
funding = forecaster.get_funding_requirements(buffer_percent=0.15)
print(f"Required funding: ${funding['peak_funding_required']:,.0f}")
```

### 3. Export Report
```python
forecaster.export_forecast("cash_flow_forecast.xlsx")
```

## Resources
- **DDC Book**: Chapter 3.1 - Cost Management
- **Reference**: Project Financial Management
