---
name: xlsx-construction
description: "Excel/spreadsheet processing for construction: estimates, schedules, tracking logs, quantity takeoffs. Formulas, formatting, analysis."
---

# Excel Processing for Construction

## Overview

Adapted from Anthropic's XLSX skill for construction spreadsheet workflows.

## Construction Use Cases

### 1. Cost Estimate Template

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

def create_estimate_template(output_path: str, project_name: str):
    """Create construction cost estimate template."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Cost Estimate"

    # Styles
    header_font = Font(bold=True, size=12)
    currency_format = '$#,##0.00'
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

    # Project header
    ws['A1'] = "CONSTRUCTION COST ESTIMATE"
    ws['A1'].font = Font(bold=True, size=16)
    ws['A2'] = f"Project: {project_name}"
    ws['A3'] = "Date:"
    ws['B3'] = "=TODAY()"

    # Column headers (row 5)
    headers = ['CSI Code', 'Description', 'Quantity', 'Unit', 'Unit Cost',
               'Labor', 'Material', 'Equipment', 'Total']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=header)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.border = thin_border
        cell.alignment = Alignment(horizontal='center')

    # Set column widths
    widths = [12, 40, 10, 8, 12, 12, 12, 12, 14]
    for i, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Sample data rows with formulas
    for row in range(6, 26):  # 20 empty rows
        # Total formula: Labor + Material + Equipment
        ws.cell(row=row, column=9,
                value=f"=SUM(F{row}:H{row})")

        # Apply borders
        for col in range(1, 10):
            ws.cell(row=row, column=col).border = thin_border

    # Currency formatting
    for col in [5, 6, 7, 8, 9]:  # Cost columns
        for row in range(6, 26):
            ws.cell(row=row, column=col).number_format = currency_format

    # Subtotals section
    ws['G27'] = "SUBTOTAL"
    ws['I27'] = "=SUM(I6:I25)"
    ws['I27'].number_format = currency_format

    ws['G28'] = "Contingency (10%)"
    ws['I28'] = "=I27*0.10"

    ws['G29'] = "TOTAL"
    ws['I29'] = "=I27+I28"
    ws['I29'].font = Font(bold=True, size=14)

    wb.save(output_path)
    return output_path
```

### 2. Schedule Tracker

```python
def create_schedule_tracker(output_path: str, tasks: list):
    """Create construction schedule tracking spreadsheet."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Schedule"

    # Headers
    headers = ['ID', 'Task', 'Start Date', 'End Date', 'Duration',
               'Progress', 'Status', 'Predecessor', 'Notes']

    # Status dropdown options
    from openpyxl.worksheet.datavalidation import DataValidation
    status_dv = DataValidation(
        type="list",
        formula1='"Not Started,In Progress,Complete,On Hold,Delayed"',
        allow_blank=True
    )
    ws.add_data_validation(status_dv)

    # Header row
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)

    # Add tasks with formulas
    for i, task in enumerate(tasks, 2):
        ws.cell(row=i, column=1, value=task.get('id', i-1))
        ws.cell(row=i, column=2, value=task.get('name', ''))
        ws.cell(row=i, column=3, value=task.get('start', ''))
        ws.cell(row=i, column=4, value=task.get('end', ''))

        # Duration formula
        ws.cell(row=i, column=5, value=f"=D{i}-C{i}")

        # Progress bar (0-100%)
        ws.cell(row=i, column=6, value=task.get('progress', 0))
        ws.cell(row=i, column=6).number_format = '0%'

        # Status with validation
        status_cell = ws.cell(row=i, column=7, value=task.get('status', 'Not Started'))
        status_dv.add(status_cell)

    wb.save(output_path)
    return output_path
```

### 3. RFI Log Template

```python
def create_rfi_log(output_path: str):
    """Create RFI tracking log."""
    wb = Workbook()
    ws = wb.active
    ws.title = "RFI Log"

    headers = [
        'RFI #', 'Date Submitted', 'Subject', 'Spec Section',
        'Drawing Ref', 'Submitted By', 'Assigned To',
        'Response Due', 'Date Responded', 'Status', 'Days Open'
    ]

    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header)

    # Days Open formula (in column K)
    for row in range(2, 100):
        ws.cell(row=row, column=11,
                value=f'=IF(I{row}="",TODAY()-B{row},I{row}-B{row})')

    # Conditional formatting for overdue items
    from openpyxl.formatting.rule import FormulaRule
    from openpyxl.styles import PatternFill

    red_fill = PatternFill(bgColor="FFC7CE")
    ws.conditional_formatting.add(
        'K2:K100',
        FormulaRule(formula=['K2>7'], fill=red_fill)
    )

    wb.save(output_path)
    return output_path
```

### 4. Quantity Takeoff Processing

```python
import pandas as pd

def process_qto_from_bim(bim_xlsx: str, output_path: str):
    """Process BIM export for quantity takeoff."""
    # Read BIM export
    df = pd.read_excel(bim_xlsx)

    # Group by category and type
    qto = df.groupby(['Category', 'Type']).agg({
        'Volume': 'sum',
        'Area': 'sum',
        'Length': 'sum',
        'Count': 'count'
    }).reset_index()

    # Rename columns for clarity
    qto.columns = ['Category', 'Type', 'Total Volume (m³)',
                   'Total Area (m²)', 'Total Length (m)', 'Element Count']

    # Create workbook with formatting
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        qto.to_excel(writer, sheet_name='QTO Summary', index=False)

        # Get workbook to apply formatting
        wb = writer.book
        ws = wb['QTO Summary']

        # Format numeric columns
        for col in ['C', 'D', 'E']:
            for row in range(2, len(qto) + 2):
                ws[f'{col}{row}'].number_format = '#,##0.00'

    return output_path
```

## Best Practices for Construction Spreadsheets

### Color Coding (Industry Standard)
- **Blue text**: Input values (quantities, rates)
- **Black text**: Formulas and calculations
- **Green text**: Links from other sheets
- **Yellow highlight**: Assumptions to verify

### Formula Guidelines
1. Never hardcode values in formulas
2. Create separate assumption cells
3. Use named ranges for clarity
4. Include unit checks

### Error Prevention
```python
# Add error handling to formulas
formula_with_error_check = "=IFERROR(B5/C5, 0)"
```

## Integration with DDC

```python
# Convert BIM export to estimate
from ddc_toolkit import RevitExporter, CWICRSemanticSearch

# Export BIM data
exporter = RevitExporter()
bim_data = exporter.read_elements("project.xlsx")

# Process QTO
qto = process_qto_from_bim("project.xlsx", "qto_output.xlsx")

# Match to cost database
search = CWICRSemanticSearch()
for category in bim_data['Category'].unique():
    prices = search.search_work_items(category)
    # Apply prices to QTO...
```

## Dependencies

```bash
pip install openpyxl pandas xlrd
```

## Resources

- **Original**: Anthropic XLSX Skill
- **OpenPyXL Docs**: https://openpyxl.readthedocs.io/
