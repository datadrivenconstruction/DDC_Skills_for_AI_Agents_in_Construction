---
name: pdf-report-generator
description: "Automatically generate PDF reports from construction data. Create formatted project reports with charts and tables."
---

# PDF Report Generator

## Business Case

### Problem Statement
Report generation challenges:
- Manual report creation is time-consuming
- Inconsistent formatting
- Data aggregation from multiple sources
- Repetitive weekly/monthly reports

### Solution
Automated PDF report generation from project data with templates, charts, and customizable sections.

## Technical Implementation

```python
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from io import BytesIO


class ReportType(Enum):
    PROGRESS = "progress"
    COST = "cost"
    SAFETY = "safety"
    QUALITY = "quality"
    EXECUTIVE = "executive"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class SectionType(Enum):
    HEADER = "header"
    TEXT = "text"
    TABLE = "table"
    CHART = "chart"
    KPI_CARDS = "kpi_cards"
    IMAGE = "image"
    PAGE_BREAK = "page_break"


@dataclass
class ReportSection:
    section_type: SectionType
    title: str = ""
    content: Any = None
    style: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KPICard:
    name: str
    value: Any
    unit: str = ""
    target: Any = None
    status: str = "normal"  # normal, warning, critical, good


@dataclass
class ChartConfig:
    chart_type: str  # bar, line, pie
    data: Dict[str, List]
    title: str = ""
    x_label: str = ""
    y_label: str = ""


class PDFReportGenerator:
    """Generate PDF reports from construction project data."""

    def __init__(self, project_name: str, report_type: ReportType):
        self.project_name = project_name
        self.report_type = report_type
        self.sections: List[ReportSection] = []
        self.metadata: Dict[str, Any] = {
            'author': '',
            'date': date.today(),
            'version': '1.0'
        }

    def set_metadata(self, author: str = "", report_date: date = None, version: str = "1.0"):
        """Set report metadata."""
        self.metadata['author'] = author
        self.metadata['date'] = report_date or date.today()
        self.metadata['version'] = version

    def add_header(self, title: str, subtitle: str = ""):
        """Add report header section."""
        self.sections.append(ReportSection(
            section_type=SectionType.HEADER,
            title=title,
            content={'subtitle': subtitle, 'date': self.metadata['date'].isoformat()}
        ))

    def add_text(self, title: str, content: str):
        """Add text section."""
        self.sections.append(ReportSection(
            section_type=SectionType.TEXT,
            title=title,
            content=content
        ))

    def add_table(self, title: str, df: pd.DataFrame, style: Dict[str, Any] = None):
        """Add table section from DataFrame."""
        self.sections.append(ReportSection(
            section_type=SectionType.TABLE,
            title=title,
            content=df.to_dict('records'),
            style=style or {}
        ))

    def add_kpi_cards(self, title: str, kpis: List[KPICard]):
        """Add KPI cards section."""
        self.sections.append(ReportSection(
            section_type=SectionType.KPI_CARDS,
            title=title,
            content=[{
                'name': k.name,
                'value': k.value,
                'unit': k.unit,
                'target': k.target,
                'status': k.status
            } for k in kpis]
        ))

    def add_chart(self, title: str, chart_config: ChartConfig):
        """Add chart section."""
        self.sections.append(ReportSection(
            section_type=SectionType.CHART,
            title=title,
            content={
                'type': chart_config.chart_type,
                'data': chart_config.data,
                'x_label': chart_config.x_label,
                'y_label': chart_config.y_label
            }
        ))

    def add_page_break(self):
        """Add page break."""
        self.sections.append(ReportSection(section_type=SectionType.PAGE_BREAK))

    def generate_progress_report(self, data: Dict[str, Any]):
        """Generate standard progress report."""

        self.add_header(
            f"{self.project_name} - Progress Report",
            f"Report Date: {self.metadata['date']}"
        )

        # KPIs
        kpis = [
            KPICard("Overall Progress", f"{data.get('overall_progress', 0)}%", target="100%",
                   status="good" if data.get('overall_progress', 0) >= data.get('planned_progress', 0) else "warning"),
            KPICard("SPI", f"{data.get('spi', 1.0):.2f}", target="1.00",
                   status="good" if data.get('spi', 1) >= 0.95 else "critical"),
            KPICard("CPI", f"{data.get('cpi', 1.0):.2f}", target="1.00",
                   status="good" if data.get('cpi', 1) >= 0.95 else "critical"),
            KPICard("Days Remaining", str(data.get('days_remaining', 0)), "days")
        ]
        self.add_kpi_cards("Key Performance Indicators", kpis)

        # Progress summary
        self.add_text("Executive Summary", data.get('summary', 'No summary provided.'))

        # Activities table
        if 'activities' in data:
            activities_df = pd.DataFrame(data['activities'])
            self.add_table("Activity Status", activities_df)

        # Progress chart
        if 'progress_history' in data:
            self.add_chart("Progress Trend", ChartConfig(
                chart_type="line",
                data=data['progress_history'],
                title="Progress Over Time",
                x_label="Date",
                y_label="Progress %"
            ))

        # Issues
        if 'issues' in data:
            self.add_text("Current Issues", "\n".join(f"- {issue}" for issue in data['issues']))

    def generate_cost_report(self, data: Dict[str, Any]):
        """Generate cost report."""

        self.add_header(
            f"{self.project_name} - Cost Report",
            f"Period: {data.get('period', 'Current')}"
        )

        # Cost KPIs
        budget = data.get('budget', 0)
        actual = data.get('actual_cost', 0)
        variance = budget - actual

        kpis = [
            KPICard("Budget", f"${budget:,.0f}"),
            KPICard("Actual Cost", f"${actual:,.0f}"),
            KPICard("Variance", f"${variance:,.0f}",
                   status="good" if variance >= 0 else "critical"),
            KPICard("CPI", f"{data.get('cpi', 1.0):.2f}",
                   status="good" if data.get('cpi', 1) >= 0.95 else "warning")
        ]
        self.add_kpi_cards("Cost Summary", kpis)

        # Cost breakdown
        if 'cost_breakdown' in data:
            breakdown_df = pd.DataFrame(data['cost_breakdown'])
            self.add_table("Cost Breakdown by Category", breakdown_df)

        # Cost trend
        if 'cost_history' in data:
            self.add_chart("Cost Trend", ChartConfig(
                chart_type="bar",
                data=data['cost_history'],
                title="Monthly Cost",
                x_label="Month",
                y_label="Cost ($)"
            ))

    def generate_safety_report(self, data: Dict[str, Any]):
        """Generate safety report."""

        self.add_header(
            f"{self.project_name} - Safety Report",
            f"Period: {data.get('period', 'Current')}"
        )

        # Safety KPIs
        kpis = [
            KPICard("Days Without Incident", str(data.get('days_without_incident', 0)), "days"),
            KPICard("TRIR", f"{data.get('trir', 0):.2f}",
                   status="good" if data.get('trir', 0) <= 2 else "critical"),
            KPICard("Near Misses", str(data.get('near_misses', 0))),
            KPICard("Safety Observations", str(data.get('observations', 0)))
        ]
        self.add_kpi_cards("Safety Metrics", kpis)

        # Incidents
        if 'incidents' in data and data['incidents']:
            incidents_df = pd.DataFrame(data['incidents'])
            self.add_table("Incident Log", incidents_df)

        # Training
        if 'training' in data:
            self.add_text("Training Summary", data['training'])

    def to_html(self) -> str:
        """Generate HTML representation of report."""

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{self.project_name} Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2196F3; color: white; padding: 20px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ color: #333; border-bottom: 2px solid #2196F3; padding-bottom: 5px; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
        .kpi-card {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; text-align: center; }}
        .kpi-value {{ font-size: 24px; font-weight: bold; }}
        .kpi-name {{ color: #666; }}
        .status-good {{ border-left: 4px solid #4CAF50; }}
        .status-warning {{ border-left: 4px solid #FF9800; }}
        .status-critical {{ border-left: 4px solid #F44336; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f5f5f5; }}
        .page-break {{ page-break-after: always; }}
    </style>
</head>
<body>
"""

        for section in self.sections:
            if section.section_type == SectionType.HEADER:
                html += f"""
    <div class="header">
        <h1>{section.title}</h1>
        <p>{section.content.get('subtitle', '')}</p>
    </div>
"""
            elif section.section_type == SectionType.TEXT:
                html += f"""
    <div class="section">
        <h2 class="section-title">{section.title}</h2>
        <p>{section.content}</p>
    </div>
"""
            elif section.section_type == SectionType.KPI_CARDS:
                html += f"""
    <div class="section">
        <h2 class="section-title">{section.title}</h2>
        <div class="kpi-grid">
"""
                for kpi in section.content:
                    status_class = f"status-{kpi['status']}" if kpi['status'] != 'normal' else ''
                    html += f"""
            <div class="kpi-card {status_class}">
                <div class="kpi-name">{kpi['name']}</div>
                <div class="kpi-value">{kpi['value']}</div>
                <div class="kpi-target">Target: {kpi['target'] or 'N/A'}</div>
            </div>
"""
                html += "</div></div>"

            elif section.section_type == SectionType.TABLE:
                html += f"""
    <div class="section">
        <h2 class="section-title">{section.title}</h2>
        <table>
            <tr>
"""
                if section.content:
                    for key in section.content[0].keys():
                        html += f"<th>{key}</th>"
                    html += "</tr>"

                    for row in section.content:
                        html += "<tr>"
                        for value in row.values():
                            html += f"<td>{value}</td>"
                        html += "</tr>"

                html += "</table></div>"

            elif section.section_type == SectionType.PAGE_BREAK:
                html += '<div class="page-break"></div>'

        html += "</body></html>"
        return html

    def export_to_excel(self, output_path: str) -> str:
        """Export report data to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Metadata
            meta_df = pd.DataFrame([{
                'Project': self.project_name,
                'Report Type': self.report_type.value,
                'Date': self.metadata['date'],
                'Author': self.metadata['author'],
                'Version': self.metadata['version']
            }])
            meta_df.to_excel(writer, sheet_name='Metadata', index=False)

            # Each section
            table_count = 0
            for section in self.sections:
                if section.section_type == SectionType.TABLE:
                    table_count += 1
                    sheet_name = section.title[:31] if section.title else f"Table_{table_count}"
                    df = pd.DataFrame(section.content)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                elif section.section_type == SectionType.KPI_CARDS:
                    kpi_df = pd.DataFrame(section.content)
                    kpi_df.to_excel(writer, sheet_name='KPIs', index=False)

        return output_path

    def get_report_structure(self) -> Dict[str, Any]:
        """Get report structure as dictionary."""

        return {
            'project': self.project_name,
            'type': self.report_type.value,
            'metadata': self.metadata,
            'sections': [
                {
                    'type': s.section_type.value,
                    'title': s.title,
                    'content': s.content
                }
                for s in self.sections
            ]
        }
```

## Quick Start

```python
# Create report generator
report = PDFReportGenerator("Office Building A", ReportType.PROGRESS)
report.set_metadata(author="Project Manager", version="1.0")

# Generate progress report
report.generate_progress_report({
    'overall_progress': 65,
    'planned_progress': 60,
    'spi': 1.08,
    'cpi': 0.97,
    'days_remaining': 120,
    'summary': 'Project is ahead of schedule but slightly over budget.',
    'activities': [
        {'Activity': 'Foundation', 'Status': 'Complete', 'Progress': 100},
        {'Activity': 'Structure', 'Status': 'In Progress', 'Progress': 80},
        {'Activity': 'MEP', 'Status': 'In Progress', 'Progress': 45}
    ],
    'issues': ['Material delivery delay', 'Weather impact on exterior work']
})

# Generate HTML
html = report.to_html()
with open("report.html", "w") as f:
    f.write(html)
```

## Common Use Cases

### 1. Cost Report
```python
report = PDFReportGenerator("Project X", ReportType.COST)
report.generate_cost_report({
    'period': 'January 2024',
    'budget': 5000000,
    'actual_cost': 4800000,
    'cpi': 1.04,
    'cost_breakdown': [
        {'Category': 'Labor', 'Budget': 2000000, 'Actual': 1950000},
        {'Category': 'Materials', 'Budget': 2500000, 'Actual': 2400000},
        {'Category': 'Equipment', 'Budget': 500000, 'Actual': 450000}
    ]
})
```

### 2. Safety Report
```python
report = PDFReportGenerator("Project X", ReportType.SAFETY)
report.generate_safety_report({
    'days_without_incident': 45,
    'trir': 1.2,
    'near_misses': 3,
    'observations': 25
})
```

### 3. Custom Report
```python
report = PDFReportGenerator("Project X", ReportType.WEEKLY)
report.add_header("Weekly Status Report", "Week 15")
report.add_kpi_cards("Summary", [
    KPICard("Tasks Completed", "15"),
    KPICard("Hours Worked", "480")
])
report.add_text("Notes", "Key accomplishments this week...")
```

## Resources
- **DDC Book**: Chapter 4.2 - ETL and Process Automation
- **Website**: https://datadrivenconstruction.io
