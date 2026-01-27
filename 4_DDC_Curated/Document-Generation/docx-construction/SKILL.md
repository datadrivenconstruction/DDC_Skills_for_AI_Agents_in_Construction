---
name: docx-construction
description: "Word document generation for construction: contracts, proposals, reports, specifications, transmittals. Template-based with dynamic content insertion."
---

# Word Document Generation for Construction

## Overview

Create professional Word documents for construction workflows using python-docx. Generate contracts, proposals, reports, and specifications from templates with dynamic data.

## Construction Use Cases

### 1. Contract Generation

Generate construction contracts from templates with project-specific data.

```python
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime

def generate_subcontract(template_path: str, contract_data: dict, output_path: str) -> str:
    """Generate subcontract from template."""
    doc = Document(template_path)

    # Replace placeholders
    replacements = {
        '{{PROJECT_NAME}}': contract_data['project_name'],
        '{{CONTRACT_NUMBER}}': contract_data['contract_number'],
        '{{SUBCONTRACTOR_NAME}}': contract_data['subcontractor'],
        '{{SCOPE_OF_WORK}}': contract_data['scope'],
        '{{CONTRACT_VALUE}}': f"${contract_data['value']:,.2f}",
        '{{START_DATE}}': contract_data['start_date'],
        '{{END_DATE}}': contract_data['end_date'],
        '{{RETENTION_PERCENT}}': f"{contract_data['retention']}%",
    }

    for paragraph in doc.paragraphs:
        for key, value in replacements.items():
            if key in paragraph.text:
                paragraph.text = paragraph.text.replace(key, value)

    # Also check tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for key, value in replacements.items():
                    if key in cell.text:
                        cell.text = cell.text.replace(key, value)

    doc.save(output_path)
    return output_path
```

### 2. Proposal Document

Create professional project proposals.

```python
def create_proposal(project_info: dict, scope_items: list, pricing: dict) -> Document:
    """Create construction proposal document."""
    doc = Document()

    # Title
    title = doc.add_heading('Project Proposal', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Project Info
    doc.add_heading('Project Information', level=1)
    doc.add_paragraph(f"Project: {project_info['name']}")
    doc.add_paragraph(f"Location: {project_info['location']}")
    doc.add_paragraph(f"Client: {project_info['client']}")
    doc.add_paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}")

    # Scope of Work
    doc.add_heading('Scope of Work', level=1)
    for item in scope_items:
        doc.add_paragraph(item, style='List Bullet')

    # Pricing Table
    doc.add_heading('Pricing Summary', level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = 'Table Grid'

    # Headers
    headers = table.rows[0].cells
    headers[0].text = 'Description'
    headers[1].text = 'Quantity'
    headers[2].text = 'Amount'

    # Add line items
    for item in pricing['line_items']:
        row = table.add_row().cells
        row[0].text = item['description']
        row[1].text = str(item['quantity'])
        row[2].text = f"${item['amount']:,.2f}"

    # Total row
    total_row = table.add_row().cells
    total_row[0].text = 'TOTAL'
    total_row[2].text = f"${pricing['total']:,.2f}"

    # Terms
    doc.add_heading('Terms & Conditions', level=1)
    doc.add_paragraph(f"Payment Terms: {pricing.get('payment_terms', 'Net 30')}")
    doc.add_paragraph(f"Validity: {pricing.get('validity', '30 days')}")

    return doc
```

### 3. Daily Report Generation

Generate daily construction reports.

```python
def generate_daily_report(report_data: dict, output_path: str) -> str:
    """Generate daily construction report."""
    doc = Document()

    # Header
    doc.add_heading(f"Daily Construction Report", 0)
    doc.add_paragraph(f"Project: {report_data['project_name']}")
    doc.add_paragraph(f"Date: {report_data['date']}")
    doc.add_paragraph(f"Report #: {report_data['report_number']}")
    doc.add_paragraph(f"Weather: {report_data['weather']}")

    # Workforce
    doc.add_heading('Workforce On-Site', level=1)
    workforce_table = doc.add_table(rows=1, cols=3)
    workforce_table.style = 'Table Grid'

    headers = workforce_table.rows[0].cells
    headers[0].text = 'Trade'
    headers[1].text = 'Company'
    headers[2].text = 'Headcount'

    for crew in report_data['workforce']:
        row = workforce_table.add_row().cells
        row[0].text = crew['trade']
        row[1].text = crew['company']
        row[2].text = str(crew['count'])

    # Work Completed
    doc.add_heading('Work Completed Today', level=1)
    for item in report_data['work_completed']:
        doc.add_paragraph(f"• {item}")

    # Issues/Delays
    if report_data.get('issues'):
        doc.add_heading('Issues & Delays', level=1)
        for issue in report_data['issues']:
            p = doc.add_paragraph()
            p.add_run(f"{issue['type']}: ").bold = True
            p.add_run(issue['description'])

    # Safety
    doc.add_heading('Safety', level=1)
    doc.add_paragraph(f"Incidents: {report_data.get('incidents', 'None')}")
    doc.add_paragraph(f"Near Misses: {report_data.get('near_misses', 'None')}")

    # Photos placeholder
    if report_data.get('photos'):
        doc.add_heading('Site Photos', level=1)
        for photo in report_data['photos']:
            doc.add_picture(photo['path'], width=Inches(5))
            doc.add_paragraph(photo.get('caption', ''), style='Caption')

    doc.save(output_path)
    return output_path
```

### 4. Transmittal Letter

Generate transmittal documents for submittals.

```python
def create_transmittal(transmittal_data: dict) -> Document:
    """Create transmittal letter for submittals."""
    doc = Document()

    # Header info
    doc.add_paragraph(f"Date: {transmittal_data['date']}")
    doc.add_paragraph(f"Transmittal No: {transmittal_data['number']}")
    doc.add_paragraph()

    # To/From
    doc.add_paragraph(f"To: {transmittal_data['to']}")
    doc.add_paragraph(f"From: {transmittal_data['from']}")
    doc.add_paragraph(f"Project: {transmittal_data['project']}")
    doc.add_paragraph(f"Subject: {transmittal_data['subject']}")
    doc.add_paragraph()

    # Items transmitted
    doc.add_paragraph("We are transmitting the following:")

    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'

    headers = table.rows[0].cells
    headers[0].text = 'No.'
    headers[1].text = 'Description'
    headers[2].text = 'Copies'
    headers[3].text = 'Action'

    for i, item in enumerate(transmittal_data['items'], 1):
        row = table.add_row().cells
        row[0].text = str(i)
        row[1].text = item['description']
        row[2].text = str(item.get('copies', 1))
        row[3].text = item.get('action', 'For Review')

    doc.add_paragraph()

    # Remarks
    if transmittal_data.get('remarks'):
        doc.add_paragraph(f"Remarks: {transmittal_data['remarks']}")

    return doc
```

### 5. Specification Section Writer

Generate specification sections.

```python
def generate_spec_section(spec_data: dict) -> Document:
    """Generate CSI-formatted specification section."""
    doc = Document()

    # Section header
    doc.add_heading(f"SECTION {spec_data['number']}", 0)
    doc.add_heading(spec_data['title'].upper(), level=1)

    # Part 1 - General
    doc.add_heading('PART 1 - GENERAL', level=1)

    doc.add_heading('1.1 SUMMARY', level=2)
    doc.add_paragraph(f"A. Section includes: {spec_data['summary']}")

    doc.add_heading('1.2 RELATED SECTIONS', level=2)
    for section in spec_data.get('related_sections', []):
        doc.add_paragraph(f"A. Section {section['number']}: {section['title']}")

    doc.add_heading('1.3 SUBMITTALS', level=2)
    for submittal in spec_data.get('submittals', []):
        doc.add_paragraph(f"A. {submittal}")

    # Part 2 - Products
    doc.add_heading('PART 2 - PRODUCTS', level=1)

    doc.add_heading('2.1 MANUFACTURERS', level=2)
    for mfr in spec_data.get('manufacturers', []):
        doc.add_paragraph(f"A. {mfr}")

    doc.add_heading('2.2 MATERIALS', level=2)
    for material in spec_data.get('materials', []):
        p = doc.add_paragraph(f"A. {material['name']}")
        for prop in material.get('properties', []):
            doc.add_paragraph(f"   1. {prop}", style='List Number')

    # Part 3 - Execution
    doc.add_heading('PART 3 - EXECUTION', level=1)

    doc.add_heading('3.1 INSTALLATION', level=2)
    for step in spec_data.get('installation', []):
        doc.add_paragraph(f"A. {step}")

    doc.add_heading('3.2 QUALITY CONTROL', level=2)
    for qc in spec_data.get('quality_control', []):
        doc.add_paragraph(f"A. {qc}")

    return doc
```

## Integration with DDC Pipeline

```python
# Example: Generate contract from estimate data
import pandas as pd

# Load estimate
estimate = pd.read_excel("project_estimate.xlsx")

# Prepare contract data
contract_data = {
    'project_name': 'Downtown Office Tower',
    'contract_number': 'SC-2026-001',
    'subcontractor': 'ABC Electrical Inc.',
    'scope': 'Complete electrical installation per Division 26',
    'value': estimate[estimate['division'] == '26']['total'].sum(),
    'start_date': '2026-03-01',
    'end_date': '2026-09-30',
    'retention': 10
}

# Generate contract
generate_subcontract('templates/subcontract.docx', contract_data, 'contracts/SC-2026-001.docx')
```

## Dependencies

```bash
pip install python-docx
```

## Resources

- **python-docx**: https://python-docx.readthedocs.io/
- **ConsensusDocs Templates**: https://www.consensusdocs.org/
- **AIA Contract Documents**: https://www.aiacontracts.org/
