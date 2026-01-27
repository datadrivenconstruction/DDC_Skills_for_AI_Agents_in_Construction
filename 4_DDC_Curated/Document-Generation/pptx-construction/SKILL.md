---
name: pptx-construction
description: "PowerPoint generation for construction: project updates, stakeholder presentations, progress reports, bid presentations. Automated slide creation with charts and data."
---

# PowerPoint Generation for Construction

## Overview

Create professional PowerPoint presentations for construction projects using python-pptx. Generate stakeholder updates, progress reports, and bid presentations with automated data visualization.

## Construction Use Cases

### 1. Project Progress Presentation

Generate monthly progress update slides.

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_progress_presentation(project_data: dict, output_path: str) -> str:
    """Create project progress presentation."""
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Title slide
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = project_data['project_name']
    title_slide.placeholders[1].text = f"Progress Report - {project_data['report_date']}"

    # Executive Summary slide
    summary_slide = prs.slides.add_slide(prs.slide_layouts[1])
    summary_slide.shapes.title.text = "Executive Summary"

    summary_text = summary_slide.placeholders[1]
    tf = summary_text.text_frame
    tf.paragraphs[0].text = f"Overall Progress: {project_data['overall_progress']}%"

    p = tf.add_paragraph()
    p.text = f"Schedule Status: {project_data['schedule_status']}"
    p = tf.add_paragraph()
    p.text = f"Budget Status: {project_data['budget_status']}"
    p = tf.add_paragraph()
    p.text = f"Safety: {project_data['safety_status']}"

    # Schedule Progress Chart
    add_schedule_chart(prs, project_data['schedule_data'])

    # Budget Chart
    add_budget_chart(prs, project_data['budget_data'])

    # Key Milestones
    add_milestones_slide(prs, project_data['milestones'])

    # Issues & Risks
    add_issues_slide(prs, project_data.get('issues', []))

    # Photos
    if project_data.get('photos'):
        add_photos_slide(prs, project_data['photos'])

    prs.save(output_path)
    return output_path


def add_schedule_chart(prs: Presentation, schedule_data: dict):
    """Add schedule progress chart."""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Schedule Progress"

    chart_data = CategoryChartData()
    chart_data.categories = schedule_data['phases']
    chart_data.add_series('Planned', schedule_data['planned'])
    chart_data.add_series('Actual', schedule_data['actual'])

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED,
        Inches(1), Inches(1.5),
        Inches(11), Inches(5),
        chart_data
    ).chart

    chart.has_legend = True
    chart.legend.include_in_layout = False


def add_budget_chart(prs: Presentation, budget_data: dict):
    """Add budget status chart."""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Budget Status"

    chart_data = CategoryChartData()
    chart_data.categories = ['Budget', 'Committed', 'Spent', 'Forecast']
    chart_data.add_series('Amount ($M)', [
        budget_data['budget'] / 1_000_000,
        budget_data['committed'] / 1_000_000,
        budget_data['spent'] / 1_000_000,
        budget_data['forecast'] / 1_000_000
    ])

    chart = slide.shapes.add_chart(
        XL_CHART_TYPE.BAR_CLUSTERED,
        Inches(1), Inches(1.5),
        Inches(11), Inches(5),
        chart_data
    ).chart


def add_milestones_slide(prs: Presentation, milestones: list):
    """Add key milestones slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Key Milestones"

    # Create table
    rows = len(milestones) + 1
    cols = 4
    table = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(1.5), Inches(12), Inches(0.5 * rows)).table

    # Headers
    headers = ['Milestone', 'Planned', 'Actual/Forecast', 'Status']
    for i, header in enumerate(headers):
        table.cell(0, i).text = header

    # Data
    for i, ms in enumerate(milestones, 1):
        table.cell(i, 0).text = ms['name']
        table.cell(i, 1).text = ms['planned_date']
        table.cell(i, 2).text = ms.get('actual_date', ms.get('forecast_date', 'TBD'))
        table.cell(i, 3).text = ms['status']


def add_issues_slide(prs: Presentation, issues: list):
    """Add issues and risks slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Issues & Risks"

    if not issues:
        slide.placeholders[1].text = "No critical issues at this time."
        return

    tf = slide.placeholders[1].text_frame
    for i, issue in enumerate(issues):
        if i == 0:
            tf.paragraphs[0].text = f"• {issue['description']} ({issue['status']})"
        else:
            p = tf.add_paragraph()
            p.text = f"• {issue['description']} ({issue['status']})"


def add_photos_slide(prs: Presentation, photos: list):
    """Add site photos slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Site Progress Photos"

    # Arrange up to 4 photos in grid
    positions = [
        (Inches(0.5), Inches(1.5)),
        (Inches(6.5), Inches(1.5)),
        (Inches(0.5), Inches(4)),
        (Inches(6.5), Inches(4))
    ]

    for i, photo in enumerate(photos[:4]):
        left, top = positions[i]
        slide.shapes.add_picture(photo['path'], left, top, width=Inches(5.5))
```

### 2. Bid Presentation

Create bid/proposal presentations.

```python
def create_bid_presentation(bid_data: dict, output_path: str) -> str:
    """Create bid presentation for client."""
    prs = Presentation()

    # Title
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = bid_data['project_name']
    title_slide.placeholders[1].text = f"Proposal by {bid_data['company_name']}"

    # Company Overview
    overview_slide = prs.slides.add_slide(prs.slide_layouts[1])
    overview_slide.shapes.title.text = "About Us"
    tf = overview_slide.placeholders[1].text_frame
    tf.paragraphs[0].text = f"Years in Business: {bid_data['company']['years']}"
    for qual in bid_data['company']['qualifications']:
        p = tf.add_paragraph()
        p.text = f"• {qual}"

    # Project Understanding
    understanding_slide = prs.slides.add_slide(prs.slide_layouts[1])
    understanding_slide.shapes.title.text = "Project Understanding"
    tf = understanding_slide.placeholders[1].text_frame
    for i, point in enumerate(bid_data['understanding']):
        if i == 0:
            tf.paragraphs[0].text = f"• {point}"
        else:
            p = tf.add_paragraph()
            p.text = f"• {point}"

    # Approach
    approach_slide = prs.slides.add_slide(prs.slide_layouts[1])
    approach_slide.shapes.title.text = "Our Approach"
    tf = approach_slide.placeholders[1].text_frame
    for i, step in enumerate(bid_data['approach']):
        if i == 0:
            tf.paragraphs[0].text = f"{i+1}. {step}"
        else:
            p = tf.add_paragraph()
            p.text = f"{i+1}. {step}"

    # Team
    team_slide = prs.slides.add_slide(prs.slide_layouts[1])
    team_slide.shapes.title.text = "Project Team"
    tf = team_slide.placeholders[1].text_frame
    for i, member in enumerate(bid_data['team']):
        if i == 0:
            tf.paragraphs[0].text = f"{member['role']}: {member['name']}"
        else:
            p = tf.add_paragraph()
            p.text = f"{member['role']}: {member['name']}"

    # Pricing Summary
    pricing_slide = prs.slides.add_slide(prs.slide_layouts[5])
    pricing_slide.shapes.title.text = "Investment Summary"

    # Add pricing table
    rows = len(bid_data['pricing']['items']) + 2
    table = pricing_slide.shapes.add_table(rows, 2, Inches(2), Inches(2), Inches(8), Inches(0.5 * rows)).table

    table.cell(0, 0).text = "Description"
    table.cell(0, 1).text = "Amount"

    for i, item in enumerate(bid_data['pricing']['items'], 1):
        table.cell(i, 0).text = item['description']
        table.cell(i, 1).text = f"${item['amount']:,.2f}"

    table.cell(rows-1, 0).text = "TOTAL"
    table.cell(rows-1, 1).text = f"${bid_data['pricing']['total']:,.2f}"

    # Schedule
    schedule_slide = prs.slides.add_slide(prs.slide_layouts[1])
    schedule_slide.shapes.title.text = "Proposed Schedule"
    tf = schedule_slide.placeholders[1].text_frame
    tf.paragraphs[0].text = f"Duration: {bid_data['schedule']['duration']}"
    p = tf.add_paragraph()
    p.text = f"Start: {bid_data['schedule']['start']}"
    p = tf.add_paragraph()
    p.text = f"Completion: {bid_data['schedule']['end']}"

    prs.save(output_path)
    return output_path
```

### 3. Safety Report Presentation

Generate safety meeting presentations.

```python
def create_safety_presentation(safety_data: dict, output_path: str) -> str:
    """Create safety meeting presentation."""
    prs = Presentation()

    # Title
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = "Safety Report"
    title_slide.placeholders[1].text = f"{safety_data['project_name']} - {safety_data['period']}"

    # KPIs
    kpi_slide = prs.slides.add_slide(prs.slide_layouts[5])
    kpi_slide.shapes.title.text = "Safety KPIs"

    # Add KPI boxes
    kpis = [
        ('Days Without Incident', str(safety_data['days_without_incident'])),
        ('Total Recordable Rate', f"{safety_data['trir']:.2f}"),
        ('Near Misses Reported', str(safety_data['near_misses'])),
        ('Toolbox Talks', str(safety_data['toolbox_talks']))
    ]

    for i, (label, value) in enumerate(kpis):
        left = Inches(0.5 + (i % 2) * 6)
        top = Inches(1.5 + (i // 2) * 2.5)

        shape = kpi_slide.shapes.add_shape(1, left, top, Inches(5), Inches(2))
        shape.text = f"{value}\n{label}"

    # Incidents (if any)
    if safety_data.get('incidents'):
        incident_slide = prs.slides.add_slide(prs.slide_layouts[1])
        incident_slide.shapes.title.text = "Incidents This Period"
        tf = incident_slide.placeholders[1].text_frame
        for i, incident in enumerate(safety_data['incidents']):
            if i == 0:
                tf.paragraphs[0].text = f"• {incident['date']}: {incident['description']}"
            else:
                p = tf.add_paragraph()
                p.text = f"• {incident['date']}: {incident['description']}"

    # Focus Areas
    focus_slide = prs.slides.add_slide(prs.slide_layouts[1])
    focus_slide.shapes.title.text = "Focus Areas This Week"
    tf = focus_slide.placeholders[1].text_frame
    for i, focus in enumerate(safety_data['focus_areas']):
        if i == 0:
            tf.paragraphs[0].text = f"• {focus}"
        else:
            p = tf.add_paragraph()
            p.text = f"• {focus}"

    prs.save(output_path)
    return output_path
```

### 4. Lookahead Schedule Presentation

Generate 3-week lookahead slides.

```python
def create_lookahead_presentation(lookahead_data: dict, output_path: str) -> str:
    """Create 3-week lookahead presentation."""
    prs = Presentation()

    # Title
    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = "3-Week Lookahead"
    title_slide.placeholders[1].text = f"{lookahead_data['project_name']}"

    # Week by week slides
    for week_num, week_data in enumerate(lookahead_data['weeks'], 1):
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        slide.shapes.title.text = f"Week {week_num}: {week_data['date_range']}"

        # Activities table
        rows = len(week_data['activities']) + 1
        table = slide.shapes.add_table(rows, 4, Inches(0.3), Inches(1.5), Inches(12.5), Inches(0.4 * rows)).table

        # Headers
        for i, header in enumerate(['Activity', 'Area', 'Crew', 'Status']):
            table.cell(0, i).text = header

        # Data
        for i, activity in enumerate(week_data['activities'], 1):
            table.cell(i, 0).text = activity['name']
            table.cell(i, 1).text = activity['area']
            table.cell(i, 2).text = activity['crew']
            table.cell(i, 3).text = activity['status']

    # Resource Needs
    resource_slide = prs.slides.add_slide(prs.slide_layouts[1])
    resource_slide.shapes.title.text = "Resource Needs"
    tf = resource_slide.placeholders[1].text_frame
    for i, need in enumerate(lookahead_data.get('resource_needs', [])):
        if i == 0:
            tf.paragraphs[0].text = f"• {need}"
        else:
            p = tf.add_paragraph()
            p.text = f"• {need}"

    prs.save(output_path)
    return output_path
```

## Integration with DDC Pipeline

```python
# Example: Generate monthly progress presentation from project data
import pandas as pd

# Load project data
schedule_df = pd.read_excel("schedule_data.xlsx")
budget_df = pd.read_excel("budget_data.xlsx")

# Prepare presentation data
project_data = {
    'project_name': 'Downtown Office Tower',
    'report_date': 'January 2026',
    'overall_progress': 67,
    'schedule_status': 'On Track',
    'budget_status': '2.3% Under Budget',
    'safety_status': '45 Days Without Incident',
    'schedule_data': {
        'phases': schedule_df['phase'].tolist(),
        'planned': schedule_df['planned_pct'].tolist(),
        'actual': schedule_df['actual_pct'].tolist()
    },
    'budget_data': {
        'budget': budget_df['budget'].sum(),
        'committed': budget_df['committed'].sum(),
        'spent': budget_df['spent'].sum(),
        'forecast': budget_df['forecast'].sum()
    },
    'milestones': [
        {'name': 'Foundation Complete', 'planned_date': '2025-06-01', 'actual_date': '2025-05-28', 'status': 'Complete'},
        {'name': 'Structure Complete', 'planned_date': '2025-12-15', 'actual_date': '2025-12-10', 'status': 'Complete'},
        {'name': 'Envelope Complete', 'planned_date': '2026-03-01', 'forecast_date': '2026-02-28', 'status': 'On Track'}
    ]
}

create_progress_presentation(project_data, 'reports/monthly_progress_jan2026.pptx')
```

## Dependencies

```bash
pip install python-pptx
```

## Resources

- **python-pptx**: https://python-pptx.readthedocs.io/
- **Chart Types**: https://python-pptx.readthedocs.io/en/latest/user/charts.html
