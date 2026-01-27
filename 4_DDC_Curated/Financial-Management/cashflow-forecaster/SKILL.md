---
name: cashflow-forecaster
description: "Forecast construction project cash flow. Project income and expenses, identify funding gaps, and optimize payment timing for improved financial management."
---

# Cashflow Forecaster

## Overview

Forecast construction project cash flow based on schedule, billing cycles, and payment terms. Identify potential cash shortfalls, optimize payment timing, and support project financing decisions.

## Cash Flow Curve

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONSTRUCTION CASH FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  $   Income (payments received)                                 │
│  │         ╱──────────╲                                         │
│  │       ╱              ╲    Positive cash                      │
│  │     ╱                  ╲  position                           │
│  │   ╱                      ╲                                   │
│  │ ╱     Cash Gap             ╲                                 │
│  ├─────────────────────────────────────────────────────         │
│  │╲                                                             │
│  │  ╲    Expenses (costs incurred)                              │
│  │    ╲──────────╱                                              │
│  │                                                              │
│  └──────────────────────────────────────────────────────────    │
│        Time →                                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import math

class CostCategory(Enum):
    LABOR = "labor"
    MATERIALS = "materials"
    EQUIPMENT = "equipment"
    SUBCONTRACTOR = "subcontractor"
    GENERAL_CONDITIONS = "general_conditions"
    OVERHEAD = "overhead"
    OTHER = "other"

class PaymentTerms(Enum):
    NET_30 = 30
    NET_45 = 45
    NET_60 = 60
    NET_90 = 90

@dataclass
class CostItem:
    id: str
    description: str
    category: CostCategory
    amount: float
    scheduled_date: datetime
    payment_terms_days: int = 30
    paid: bool = False
    paid_date: Optional[datetime] = None

@dataclass
class IncomeItem:
    id: str
    description: str
    amount: float
    billing_date: datetime
    expected_payment_date: datetime
    received: bool = False
    received_date: Optional[datetime] = None
    received_amount: float = 0.0

@dataclass
class CashFlowPeriod:
    period_start: datetime
    period_end: datetime
    opening_balance: float
    income: float
    expenses: float
    net_cashflow: float
    closing_balance: float
    cumulative_income: float
    cumulative_expenses: float

@dataclass
class CashFlowForecast:
    project_name: str
    forecast_date: datetime
    total_contract: float
    total_costs: float
    periods: List[CashFlowPeriod]
    peak_deficit: float
    peak_deficit_date: datetime
    breakeven_date: Optional[datetime]
    financing_required: float

class CashFlowForecaster:
    """Forecast construction project cash flow."""

    # Typical cost distribution curve (S-curve)
    S_CURVE = [0.05, 0.10, 0.15, 0.20, 0.20, 0.15, 0.10, 0.05]

    def __init__(self, project_name: str, contract_value: float,
                 estimated_cost: float, start_date: datetime,
                 duration_months: int):
        self.project_name = project_name
        self.contract_value = contract_value
        self.estimated_cost = estimated_cost
        self.start_date = start_date
        self.duration_months = duration_months
        self.end_date = start_date + timedelta(days=duration_months * 30)

        self.cost_items: List[CostItem] = []
        self.income_items: List[IncomeItem] = []

        self.retainage_rate = 0.10  # 10%
        self.payment_terms_income = PaymentTerms.NET_30
        self.billing_frequency = 30  # Monthly

    def set_payment_terms(self, income_terms: PaymentTerms,
                         retainage_rate: float = 0.10):
        """Set payment terms for income."""
        self.payment_terms_income = income_terms
        self.retainage_rate = retainage_rate

    def add_cost_item(self, description: str, category: CostCategory,
                     amount: float, scheduled_date: datetime,
                     payment_terms_days: int = 30) -> CostItem:
        """Add cost item to forecast."""
        item = CostItem(
            id=f"COST-{len(self.cost_items)+1:04d}",
            description=description,
            category=category,
            amount=amount,
            scheduled_date=scheduled_date,
            payment_terms_days=payment_terms_days
        )
        self.cost_items.append(item)
        return item

    def generate_cost_distribution(self, cost_breakdown: Dict[CostCategory, float] = None):
        """Generate cost items based on S-curve distribution."""
        if cost_breakdown is None:
            # Default breakdown
            cost_breakdown = {
                CostCategory.LABOR: self.estimated_cost * 0.35,
                CostCategory.MATERIALS: self.estimated_cost * 0.30,
                CostCategory.SUBCONTRACTOR: self.estimated_cost * 0.20,
                CostCategory.EQUIPMENT: self.estimated_cost * 0.05,
                CostCategory.GENERAL_CONDITIONS: self.estimated_cost * 0.07,
                CostCategory.OVERHEAD: self.estimated_cost * 0.03,
            }

        # Distribute costs over project duration using S-curve
        months = self.duration_months
        curve_months = len(self.S_CURVE)

        for category, total in cost_breakdown.items():
            for month in range(months):
                # Map to S-curve
                curve_idx = int(month / months * curve_months)
                curve_idx = min(curve_idx, curve_months - 1)
                monthly_pct = self.S_CURVE[curve_idx]

                # Adjust for number of months
                adjustment = months / curve_months
                amount = total * monthly_pct / adjustment

                cost_date = self.start_date + timedelta(days=month * 30)

                # Payment terms vary by category
                payment_days = 30
                if category == CostCategory.SUBCONTRACTOR:
                    payment_days = 45
                elif category == CostCategory.MATERIALS:
                    payment_days = 30

                self.add_cost_item(
                    f"{category.value} - Month {month+1}",
                    category,
                    amount,
                    cost_date,
                    payment_days
                )

    def generate_billing_schedule(self):
        """Generate income items based on billing schedule."""
        # Monthly billing based on progress
        months = self.duration_months

        for month in range(months):
            # Map to S-curve for progress
            curve_months = len(self.S_CURVE)
            curve_idx = int(month / months * curve_months)
            curve_idx = min(curve_idx, curve_months - 1)
            monthly_pct = self.S_CURVE[curve_idx]

            # Adjust for number of months
            adjustment = months / curve_months
            billing_amount = self.contract_value * monthly_pct / adjustment

            # Apply retainage
            retainage = billing_amount * self.retainage_rate
            net_billing = billing_amount - retainage

            billing_date = self.start_date + timedelta(days=(month + 1) * 30)
            payment_date = billing_date + timedelta(days=self.payment_terms_income.value)

            self.income_items.append(IncomeItem(
                id=f"INC-{month+1:04d}",
                description=f"Progress Billing #{month+1}",
                amount=net_billing,
                billing_date=billing_date,
                expected_payment_date=payment_date
            ))

        # Retainage release at end
        total_retainage = self.contract_value * self.retainage_rate
        final_date = self.end_date + timedelta(days=30)
        self.income_items.append(IncomeItem(
            id="INC-RET",
            description="Retainage Release",
            amount=total_retainage,
            billing_date=final_date,
            expected_payment_date=final_date + timedelta(days=self.payment_terms_income.value)
        ))

    def generate_forecast(self, period_days: int = 30,
                         opening_balance: float = 0) -> CashFlowForecast:
        """Generate cash flow forecast."""
        if not self.cost_items:
            self.generate_cost_distribution()
        if not self.income_items:
            self.generate_billing_schedule()

        periods = []
        current_date = self.start_date
        balance = opening_balance
        cumulative_income = 0
        cumulative_expenses = 0

        peak_deficit = 0
        peak_deficit_date = current_date
        breakeven_date = None

        # Extend forecast beyond project end
        forecast_end = self.end_date + timedelta(days=90)

        while current_date < forecast_end:
            period_end = current_date + timedelta(days=period_days)

            # Calculate expenses for period (when paid, not when incurred)
            period_expenses = sum(
                c.amount for c in self.cost_items
                if current_date <= c.scheduled_date + timedelta(days=c.payment_terms_days) < period_end
            )

            # Calculate income for period (when received)
            period_income = sum(
                i.amount for i in self.income_items
                if current_date <= i.expected_payment_date < period_end
            )

            net_cashflow = period_income - period_expenses
            closing_balance = balance + net_cashflow
            cumulative_income += period_income
            cumulative_expenses += period_expenses

            period = CashFlowPeriod(
                period_start=current_date,
                period_end=period_end,
                opening_balance=balance,
                income=period_income,
                expenses=period_expenses,
                net_cashflow=net_cashflow,
                closing_balance=closing_balance,
                cumulative_income=cumulative_income,
                cumulative_expenses=cumulative_expenses
            )
            periods.append(period)

            # Track peak deficit
            if closing_balance < peak_deficit:
                peak_deficit = closing_balance
                peak_deficit_date = current_date

            # Track breakeven
            if breakeven_date is None and closing_balance > 0 and balance <= 0:
                breakeven_date = current_date

            balance = closing_balance
            current_date = period_end

        financing_required = abs(peak_deficit) if peak_deficit < 0 else 0

        return CashFlowForecast(
            project_name=self.project_name,
            forecast_date=datetime.now(),
            total_contract=self.contract_value,
            total_costs=self.estimated_cost,
            periods=periods,
            peak_deficit=peak_deficit,
            peak_deficit_date=peak_deficit_date,
            breakeven_date=breakeven_date,
            financing_required=financing_required
        )

    def analyze_scenarios(self) -> Dict[str, CashFlowForecast]:
        """Analyze different payment scenarios."""
        scenarios = {}

        # Base case
        scenarios["base"] = self.generate_forecast()

        # Optimistic - faster payments
        original_terms = self.payment_terms_income
        self.payment_terms_income = PaymentTerms.NET_30
        scenarios["optimistic"] = self.generate_forecast()

        # Pessimistic - slower payments
        self.payment_terms_income = PaymentTerms.NET_60
        scenarios["pessimistic"] = self.generate_forecast()

        self.payment_terms_income = original_terms

        return scenarios

    def calculate_financing_cost(self, forecast: CashFlowForecast,
                                annual_rate: float = 0.08) -> Dict:
        """Calculate cost of financing the cash deficit."""
        if forecast.financing_required == 0:
            return {"financing_needed": False, "cost": 0}

        # Calculate weighted average deficit duration
        total_deficit_days = 0
        weighted_deficit = 0

        for period in forecast.periods:
            if period.closing_balance < 0:
                deficit = abs(period.closing_balance)
                days = (period.period_end - period.period_start).days
                total_deficit_days += days
                weighted_deficit += deficit * days

        avg_deficit = weighted_deficit / total_deficit_days if total_deficit_days else 0

        # Calculate interest cost
        daily_rate = annual_rate / 365
        interest_cost = weighted_deficit * daily_rate

        return {
            "financing_needed": True,
            "peak_deficit": forecast.peak_deficit,
            "deficit_days": total_deficit_days,
            "average_deficit": avg_deficit,
            "annual_rate": annual_rate,
            "estimated_interest": interest_cost,
            "recommendation": f"Line of credit needed: ${forecast.financing_required:,.0f}"
        }

    def generate_report(self, forecast: CashFlowForecast) -> str:
        """Generate cash flow forecast report."""
        lines = [
            "# Cash Flow Forecast Report",
            "",
            f"**Project:** {forecast.project_name}",
            f"**Forecast Date:** {forecast.forecast_date.strftime('%Y-%m-%d')}",
            "",
            "## Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Contract Value | ${forecast.total_contract:,.0f} |",
            f"| Estimated Cost | ${forecast.total_costs:,.0f} |",
            f"| Gross Margin | ${forecast.total_contract - forecast.total_costs:,.0f} ({(forecast.total_contract - forecast.total_costs)/forecast.total_contract*100:.1f}%) |",
            f"| Peak Cash Deficit | ${forecast.peak_deficit:,.0f} |",
            f"| Peak Deficit Date | {forecast.peak_deficit_date.strftime('%Y-%m-%d')} |",
            f"| Financing Required | ${forecast.financing_required:,.0f} |",
            "",
            "## Monthly Cash Flow",
            "",
            "| Period | Income | Expenses | Net | Balance |",
            "|--------|--------|----------|-----|---------|"
        ]

        for period in forecast.periods:
            if period.income > 0 or period.expenses > 0:
                lines.append(
                    f"| {period.period_start.strftime('%Y-%m')} | "
                    f"${period.income:,.0f} | ${period.expenses:,.0f} | "
                    f"${period.net_cashflow:,.0f} | ${period.closing_balance:,.0f} |"
                )

        # Financing analysis
        financing = self.calculate_financing_cost(forecast)
        if financing["financing_needed"]:
            lines.extend([
                "",
                "## Financing Analysis",
                "",
                f"- Peak Deficit: ${financing['peak_deficit']:,.0f}",
                f"- Days in Deficit: {financing['deficit_days']}",
                f"- Estimated Interest Cost: ${financing['estimated_interest']:,.0f}",
                f"- **{financing['recommendation']}**"
            ])

        return "\n".join(lines)
```

## Quick Start

```python
from datetime import datetime

# Initialize forecaster
forecaster = CashFlowForecaster(
    project_name="Office Tower",
    contract_value=5000000,
    estimated_cost=4200000,
    start_date=datetime(2024, 1, 1),
    duration_months=12
)

# Set payment terms
forecaster.set_payment_terms(
    income_terms=PaymentTerms.NET_45,
    retainage_rate=0.10
)

# Generate forecast
forecast = forecaster.generate_forecast(opening_balance=100000)

print(f"Peak Cash Deficit: ${forecast.peak_deficit:,.0f}")
print(f"Financing Required: ${forecast.financing_required:,.0f}")

# Analyze scenarios
scenarios = forecaster.analyze_scenarios()
for name, scen in scenarios.items():
    print(f"{name}: Peak deficit ${scen.peak_deficit:,.0f}")

# Generate report
print(forecaster.generate_report(forecast))
```

## Requirements

```bash
pip install (no external dependencies)
```
