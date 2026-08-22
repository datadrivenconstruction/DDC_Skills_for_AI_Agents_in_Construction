# Getting Started: Construction Company Automation Guide

**Data-Driven Construction: From Isolated Data to Automation**

> "Predictions and forecasts based on historical data allow companies to make more accurate decisions about project costs and timelines." — Data-Driven Construction, Chapter 4.5

---

## Core Concept

**Construction automation starts not with BIM, but with understanding data.**

BIM, ERP, Excel, PDF, photos — these are all **databases** in different formats. Behind every Revit file is a structured database. Behind every PDF is unstructured text. Understanding data types and their relationships is the foundation of automation.

```
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA IN CONSTRUCTION                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   STRUCTURED              SEMI-STRUCTURED          UNSTRUCTURED     │
│   ──────────              ───────────────          ────────────     │
│   • Excel spreadsheets    • IFC models             • PDF contracts  │
│   • ERP databases         • JSON/XML files         • Photos         │
│   • CSV exports           • API responses          • Emails & notes │
│   • P6 schedules          • BCF files              • Scanned docs   │
│                                                                      │
│   Easy to process         Requires parsing         Requires AI/OCR  │
│   SQL queries             Flexible schema          No schema        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Table of Contents

1. [Step 1: Assess Current Data State](#step-1-assess-current-data-state)
2. [Step 2: Detect Data Silos](#step-2-detect-data-silos)
3. [Step 3: Classify and Inventory Data](#step-3-classify-and-inventory-data)
4. [Step 4: Build ETL Pipelines](#step-4-build-etl-pipelines)
5. [Step 5: Automate Key Processes](#step-5-automate-key-processes)
6. [Real-World Cases](#real-world-cases)
7. [Roadmap by Department](#roadmap-by-department)

---

## Step 1: Assess Current Data State

**Source:** DDC Book, Chapter 1.1 — "Evolution of Data Usage in Construction"

### Digital Maturity Levels

```python
from enum import Enum

class MaturityLevel(Enum):
    LEVEL_0_PAPER = 0      # Paper-based document flow
    LEVEL_1_BASIC = 1      # Excel, email, file shares
    LEVEL_2_STRUCTURED = 2  # Specialized software, databases
    LEVEL_3_INTEGRATED = 3  # Integrated systems (ERP + PM)
    LEVEL_4_AUTOMATED = 4   # Automated workflows, ML models
    LEVEL_5_PREDICTIVE = 5  # Predictive analytics, digital twins
```

### Quick Self-Assessment

| Question | Yes (1) | No (0) |
|----------|---------|--------|
| Do you have a unified cost code database? | | |
| Is data transferred between departments automatically? | | |
| Are reports generated without manual data collection? | | |
| Do you have version history for data changes? | | |
| Is data accessible from mobile devices on site? | | |

**Results:**
- 0-1: Level 1 — Basic digitization
- 2-3: Level 2-3 — Ready for integration
- 4-5: Level 4+ — Ready for AI automation

### Practical Case: Company Assessment

```python
# 2_DDC_Book/Chapter-1.1/data-evolution-analysis/SKILL.md

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class DataFlowAssessment:
    category: str           # design, cost, schedule, quality
    source_systems: List[str]
    integration_level: float  # 0-1
    automation_level: float   # 0-1
    issues: List[str]

# Example: Typical construction company analysis
assessment = {
    "design": DataFlowAssessment(
        category="design",
        source_systems=["AutoCAD", "Revit"],
        integration_level=0.3,  # Data transferred manually
        automation_level=0.1,
        issues=["No link to estimating system", "Manual specification export"]
    ),
    "cost": DataFlowAssessment(
        category="cost",
        source_systems=["Excel", "Sage"],
        integration_level=0.2,
        automation_level=0.0,
        issues=["Estimates in different formats", "Data duplication"]
    )
}

# Typical result: integration_level = 0.25 → Level 2
```

---

## Step 2: Detect Data Silos

**Source:** DDC Book, Chapter 1.2 — "Technologies and Management Systems in Modern Construction"

### What are Data Silos?

**Data Silo** — an isolated data source not connected to other systems. This is the main enemy of automation.

```
┌─────────────────────────────────────────────────────────────────────┐
│                           DATA SILOS                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│    ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐ │
│    │  Excel   │     │   ERP    │     │   BIM    │     │   Site   │ │
│    │ Estimates│     │   Sage   │     │  Revit   │     │  Photos  │ │
│    └──────────┘     └──────────┘     └──────────┘     └──────────┘ │
│         ↑                ↑                ↑                ↑        │
│         │                │                │                │        │
│         └────────────────┴────────────────┴────────────────┘        │
│                    NO AUTOMATIC CONNECTION                          │
│                    Data copied manually                             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Practical Case: Detecting Silos

```python
# 2_DDC_Book/Chapter-1.2/data-silo-detection/SKILL.md

from dataclasses import dataclass
from typing import List
from enum import Enum

class SiloSeverity(Enum):
    CRITICAL = "critical"   # Critical business impact
    HIGH = "high"           # Significant inefficiency
    MEDIUM = "medium"       # Noticeable issues
    LOW = "low"             # Minor inconvenience

@dataclass
class DataSource:
    name: str
    department: str
    data_entities: List[str]  # What data it contains
    connections: List[str]    # What it's connected to (empty = silo!)
    has_api: bool             # Integration capability

# Typical picture in a construction company
sources = [
    DataSource(
        name="Excel Estimates",
        department="Estimating",
        data_entities=["costs", "quantities", "rates"],
        connections=[],  # SILO! Not connected to anything
        has_api=False
    ),
    DataSource(
        name="Sage Accounting",
        department="Accounting",
        data_entities=["invoices", "payments", "contracts"],
        connections=["bank"],
        has_api=True  # Can be integrated!
    ),
    DataSource(
        name="Revit Models",
        department="Design",
        data_entities=["geometry", "specifications", "quantities"],
        connections=[],  # SILO! Data not exported automatically
        has_api=True  # But has API for integration
    )
]

# Analysis: 2 of 3 sources are isolated silos
# Recommendation: connect Revit → Excel Estimates → Sage
```

### Silo Elimination Priorities

| Severity | Example | Action |
|----------|---------|--------|
| CRITICAL | Estimates not linked to actual costs | ETL pipeline |
| HIGH | BIM doesn't export to estimating software | API integration |
| MEDIUM | Site photos stored locally | Cloud sync |
| LOW | Subcontractor contacts in personal phones | CRM system |

---

## Step 3: Classify and Inventory Data

**Source:** DDC Book, Chapter 2.1 — "Data Types in Construction"

### Classification by Structure

```python
# 2_DDC_Book/Chapter-2.1/data-type-classifier/SKILL.md

class DataStructure(Enum):
    STRUCTURED = "structured"           # Tables, databases, Excel
    SEMI_STRUCTURED = "semi_structured" # JSON, XML, IFC
    UNSTRUCTURED = "unstructured"       # PDF, photos, video
    GEOMETRIC = "geometric"             # CAD, BIM geometry
    TEMPORAL = "temporal"               # Schedules, time series
```

### Practical Case: Data Inventory

```python
# Conduct an inventory of all data sources in your company

data_inventory = [
    {
        "name": "Project Estimates",
        "format": "Excel (.xlsx)",
        "structure": "STRUCTURED",
        "location": "Network Drive Z:",
        "volume": "500 files",
        "update_frequency": "Daily",
        "owner": "Estimating Department",
        "integration": "Manual export to Sage"
    },
    {
        "name": "BIM Models",
        "format": "Revit (.rvt), IFC",
        "structure": "SEMI_STRUCTURED",  # IFC = database!
        "location": "BIM360",
        "volume": "50 projects",
        "update_frequency": "Weekly",
        "owner": "Design Department",
        "integration": "No automatic connection"
    },
    {
        "name": "Contracts",
        "format": "PDF, Word",
        "structure": "UNSTRUCTURED",
        "location": "SharePoint",
        "volume": "2000 documents",
        "update_frequency": "As needed",
        "owner": "Legal Department",
        "integration": "Manual search"
    }
]

# Storage recommendations
storage_recommendations = {
    "STRUCTURED": "Relational Database (PostgreSQL)",
    "SEMI_STRUCTURED": "Document Database (MongoDB) or Data Lake",
    "UNSTRUCTURED": "Object Storage (S3) + Vector DB for search",
    "GEOMETRIC": "File System + IFC server",
    "TEMPORAL": "Time Series DB (InfluxDB)"
}
```

### Key Insight: IFC = Database

```
┌─────────────────────────────────────────────────────────────────────┐
│                    IFC ≠ Just a 3D Model                            │
│                    IFC = Structured Database                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   IFC file contains:                                                │
│   ├── IfcProject (project)                                          │
│   │   ├── IfcSite (site)                                            │
│   │   │   ├── IfcBuilding (building)                                │
│   │   │   │   ├── IfcBuildingStorey (floor)                         │
│   │   │   │   │   ├── IfcWall (wall)                                │
│   │   │   │   │   │   ├── Pset_WallCommon (properties)              │
│   │   │   │   │   │   │   ├── IsExternal: True                      │
│   │   │   │   │   │   │   ├── FireRating: "2 hour"                  │
│   │   │   │   │   │   ├── BaseQuantities (quantities)               │
│   │   │   │   │   │   │   ├── NetVolume: 15.5 m³                    │
│   │   │   │   │   │   │   ├── NetArea: 45.2 m²                      │
│                                                                      │
│   Can extract: volumes, areas, materials, relationships             │
│   And automatically transfer to estimating software!                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Step 4: Build ETL Pipelines

**Source:** DDC Book, Chapter 4.2 — "ETL and Process Automation"

> "ETL: transitioning from manual management to automation allows companies to process data without constant human intervention."

### What is ETL?

```
┌─────────┐    ┌───────────┐    ┌────────┐
│ EXTRACT │ -> │ TRANSFORM │ -> │  LOAD  │
└─────────┘    └───────────┘    └────────┘
     │               │               │
     ▼               ▼               ▼
  Sources         Process         Outputs
  - Excel         - Clean         - Excel report
  - PDF           - Validate      - PDF report
  - BIM/IFC       - Calculate     - Database
  - API           - Aggregate     - API
```

### Practical Case: ETL for Estimate Data

```python
# 2_DDC_Book/Chapter-4.2/etl-pipeline/SKILL.md

import pandas as pd
from pathlib import Path

class ConstructionETLPipeline:
    """ETL pipeline for construction data"""

    def __init__(self, config):
        self.config = config
        self.data = None
        self.errors = []

    def extract(self):
        """EXTRACT: Pull from various sources"""
        print("Extracting data...")

        all_data = []

        # From Excel files
        for file in Path(self.config['input_folder']).glob("*.xlsx"):
            df = pd.read_excel(file)
            df['_source'] = file.name
            all_data.append(df)
            print(f"  Extracted: {file.name}")

        self.data = pd.concat(all_data, ignore_index=True)
        print(f"  Total records: {len(self.data)}")
        return self

    def transform(self):
        """TRANSFORM: Clean and process"""
        print("Transforming data...")

        # Remove empty rows
        self.data = self.data.dropna(how='all')

        # Standardize names
        if 'Category' in self.data.columns:
            self.data['Category'] = self.data['Category'].str.strip().str.title()

        # Calculate totals
        if 'Quantity' in self.data.columns and 'Unit_Price' in self.data.columns:
            self.data['Total'] = self.data['Quantity'] * self.data['Unit_Price']

        # Validation
        invalid = self.data[self.data['Quantity'] <= 0]
        if len(invalid) > 0:
            self.errors.append(f"Found {len(invalid)} rows with invalid quantity")

        print(f"  Processed records: {len(self.data)}")
        print(f"  Validation errors: {len(self.errors)}")
        return self

    def load(self):
        """LOAD: Save results"""
        print("Loading results...")

        # Summary report
        summary = self.data.groupby('Category').agg({
            'Total': 'sum',
            'Quantity': 'sum'
        }).round(2)

        # Save to Excel
        output_path = self.config['output_file']
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            self.data.to_excel(writer, sheet_name='Data', index=False)
            summary.to_excel(writer, sheet_name='Summary')

        print(f"  Saved: {output_path}")
        return self

    def run(self):
        """Run complete pipeline"""
        return self.extract().transform().load()

# Usage
config = {
    'input_folder': './estimates/',
    'output_file': './reports/consolidated_estimate.xlsx'
}

pipeline = ConstructionETLPipeline(config)
pipeline.run()
```

### Automation with n8n

```json
// 3_DDC_Insights/Automation-Workflows/n8n-daily-report/SKILL.md

{
  "workflow": "Daily Report",
  "trigger": "Every day at 5:00 PM",
  "nodes": [
    {
      "name": "Get Weather Data",
      "type": "HTTP Request",
      "url": "api.openweathermap.org"
    },
    {
      "name": "Get Excel Data",
      "type": "Spreadsheet File",
      "operation": "read"
    },
    {
      "name": "Process Data",
      "type": "Code",
      "code": "// Aggregation and formatting"
    },
    {
      "name": "Generate PDF",
      "type": "HTTP Request",
      "url": "pdf-service/generate"
    },
    {
      "name": "Send Email",
      "type": "Email Send",
      "to": "management@company.com"
    }
  ]
}
```

---

## Step 5: Automate Key Processes

### Process 1: Automated Estimate Creation

**Source:** DDC Book, Chapter 3.1 — "Cost Calculations and Estimates"

```python
# 2_DDC_Book/Chapter-3.1/estimate-builder/SKILL.md

from dataclasses import dataclass
from enum import Enum
from typing import List

class CostCategory(Enum):
    LABOR = "labor"
    MATERIAL = "material"
    EQUIPMENT = "equipment"
    SUBCONTRACTOR = "subcontractor"

@dataclass
class EstimateLineItem:
    code: str           # Work code (from CWICR database)
    description: str
    quantity: float
    unit: str
    unit_cost: float
    category: CostCategory

    @property
    def total(self) -> float:
        return round(self.quantity * self.unit_cost, 2)

class EstimateBuilder:
    """Build estimates from structured data"""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.items: List[EstimateLineItem] = []
        self.markups = {'overhead': 0.15, 'profit': 0.10, 'contingency': 0.05}

    def add_item(self, code, description, quantity, unit, unit_cost, category):
        item = EstimateLineItem(code, description, quantity, unit, unit_cost, category)
        self.items.append(item)
        return item

    def get_direct_cost(self) -> float:
        return sum(item.total for item in self.items)

    def get_total_cost(self) -> float:
        direct = self.get_direct_cost()
        markup_total = sum(self.markups.values())
        return direct * (1 + markup_total)

    def import_from_ifc(self, ifc_path: str, price_database: dict):
        """Import quantities from IFC and rates from database"""
        import ifcopenshell

        model = ifcopenshell.open(ifc_path)

        for wall in model.by_type("IfcWall"):
            # Extract volume from IFC
            volume = self._get_quantity(wall, "NetVolume")

            # Find rate in database
            material = self._get_material(wall)
            price_info = price_database.get(material, {})

            self.add_item(
                code=price_info.get('code', 'N/A'),
                description=f"Wall: {wall.Name}",
                quantity=volume,
                unit="m³",
                unit_cost=price_info.get('unit_cost', 0),
                category=CostCategory.MATERIAL
            )

# Example usage
estimate = EstimateBuilder("Office Building")

# Add line items
estimate.add_item("03.30.00", "Foundation Concrete", 500, "m³", 180, CostCategory.MATERIAL)
estimate.add_item("03.30.01", "Concrete Placement", 500, "m³", 50, CostCategory.LABOR)
estimate.add_item("05.12.00", "Structural Steel", 50, "ton", 4500, CostCategory.SUBCONTRACTOR)

print(f"Direct Cost: ${estimate.get_direct_cost():,.0f}")
print(f"Total with Markups: ${estimate.get_total_cost():,.0f}")
```

### Process 2: Automated Variance Tracking

```python
# Link: Planned data (estimate) ↔ Actual data (ERP)

class BudgetVarianceAnalyzer:
    """Analyze actual vs planned variances"""

    def __init__(self, planned_df, actual_df):
        self.planned = planned_df
        self.actual = actual_df

    def calculate_variance(self):
        """Calculate variance for each line item"""
        merged = self.planned.merge(
            self.actual,
            on='Work_Code',
            suffixes=('_planned', '_actual')
        )

        merged['Variance'] = merged['Total_actual'] - merged['Total_planned']
        merged['Variance_%'] = (merged['Variance'] / merged['Total_planned']) * 100

        return merged

    def get_alerts(self, threshold=10):
        """Items with variance > threshold%"""
        variance = self.calculate_variance()
        return variance[abs(variance['Variance_%']) > threshold]

# Automatic weekly check
# n8n workflow: ERP → Analyzer → Email to management
```

### Process 3: Automated Report Generation

```python
# 3_DDC_Insights/Automation-Workflows/n8n-daily-report/SKILL.md

def generate_daily_report(project_data: dict) -> str:
    """Generate daily report"""

    report = f"""
# Daily Report: {project_data['name']}
**Date:** {project_data['date']}

## Weather
- Temperature: {project_data['weather']['temp']}°F
- Conditions: {project_data['weather']['condition']}

## Labor
| Trade | Workers | Hours |
|-------|---------|-------|
"""
    for labor in project_data['labor']:
        report += f"| {labor['trade']} | {labor['count']} | {labor['hours']} |\n"

    report += f"""
## Progress
- Completed: {project_data['progress']}%
- Schedule Variance: {project_data['schedule_variance']} days

## Issues
"""
    for issue in project_data.get('issues', []):
        report += f"- {issue}\n"

    return report
```

---

## Real-World Cases

### Case 1: From 2 Days to 2 Hours — Estimate Automation

**Problem:** Estimator spends 2 days creating estimates, manually transferring data from Revit specifications to Excel.

**Solution:**
1. Export data from Revit to IFC
2. Parse IFC using ifcopenshell
3. Automatic matching with CWICR rate database
4. Generate Excel estimate

**Result:** 2 hours instead of 2 days. 80% time savings.

```python
# Simplified example
import ifcopenshell

def ifc_to_estimate(ifc_path, price_db):
    model = ifcopenshell.open(ifc_path)
    estimate_items = []

    for element in model.by_type("IfcBuildingElement"):
        # Extract quantities
        quantities = get_element_quantities(element)

        # Classify element
        category = classify_element(element)

        # Find rate
        price = price_db.get(category)

        estimate_items.append({
            'description': element.Name,
            'quantity': quantities.get('volume'),
            'unit': 'm³',
            'unit_cost': price['unit_cost'],
            'total': quantities.get('volume') * price['unit_cost']
        })

    return estimate_items
```

### Case 2: Unified Work Database Instead of Chaos

**Problem:** Company has 5 estimators, each uses their own work names. "Concrete foundation pour", "Cast-in-place foundation concrete", "Foundation concrete work" — same work with different names.

**Solution:** CWICR Database — 8 national bases (78,228 positions) plus 30 markets in 26 languages.

```python
# 1_DDC_Toolkit/CWICR-Database/semantic-search-cwicr/SKILL.md

from qdrant_client import QdrantClient

def search_cwicr(query: str) -> list:
    """Semantic search in work items database"""
    client = QdrantClient("localhost", port=6333)

    # Vector search (understands synonyms!)
    results = client.search(
        collection_name="cwicr_en_v3",
        query_vector=get_embedding(query),
        limit=5
    )

    return [
        {
            'code': r.payload['code'],
            'description': r.payload['description'],
            'unit': r.payload['unit'],
            'confidence': r.score
        }
        for r in results
    ]

# Now any query finds the correct item
search_cwicr("concrete foundation pour")
# → [{'code': '03.30.00', 'description': 'Concrete works - foundations', ...}]

search_cwicr("cast-in-place foundation")
# → [{'code': '03.30.00', 'description': 'Concrete works - foundations', ...}]
```

### Case 3: Automated Schedule Tracking

**Problem:** Schedule variances discovered too late.

**Solution:** ETL pipeline that daily compares planned vs actual.

```python
# Daily check (runs via n8n or Airflow)

def check_schedule_variance(project_id):
    # Extract data
    planned = get_planned_schedule(project_id)  # From P6/MS Project
    actual = get_actual_progress(project_id)     # From Procore/photos

    # Analyze
    for task in planned:
        actual_progress = actual.get(task['id'], {})

        if actual_progress['completion'] < task['planned_completion']:
            variance = task['planned_completion'] - actual_progress['completion']

            if variance > 5:  # Variance > 5%
                send_alert(
                    to="pm@company.com",
                    subject=f"Delay: {task['name']}",
                    body=f"Variance: {variance}%. Action required."
                )
```

---

## Roadmap by Department

### Estimating Department

| Week | Action | Skill |
|------|--------|-------|
| 1 | Implement unified cost code database | `semantic-search-cwicr` |
| 2 | Automated quantity import from IFC | `bim-qto` |
| 3-4 | ETL pipeline: IFC → Estimate | `etl-pipeline` |
| 5+ | Automated estimate generation | `estimate-builder` |

### Project Management

| Week | Action | Skill |
|------|--------|-------|
| 1 | Digitize daily reports | `n8n-daily-report` |
| 2 | Automated site photo collection | `n8n-photo-report` |
| 3-4 | Link schedule to actuals | `schedule-delay-analyzer` |
| 5+ | Predictive schedule analytics | `duration-prediction` |

### Finance Department

| Week | Action | Skill |
|------|--------|-------|
| 1 | Automated budget tracking | `budget-variance-analyzer` |
| 2 | Cash flow forecasting | `cash-flow-forecaster` |
| 3-4 | ERP integration | `erp-data-extractor` |
| 5+ | ML cost prediction model | `cost-prediction` |

### Executive Team

| Week | Action | Skill |
|------|--------|-------|
| 1 | Digital maturity assessment | `data-evolution-analysis` |
| 2 | Data silo detection | `data-silo-detection` |
| 3-4 | KPI dashboard | `kpi-dashboard` |
| 5+ | Digital transformation strategy | `digital-maturity-assessment` |

---

## ROI of Automation

### Time Savings by Process

| Process | Manual Time | Automated Time | Savings |
|---------|-------------|----------------|---------|
| Estimate Creation | 16 hours | 2 hours | 87% |
| Daily Report | 2 hours | 10 min | 92% |
| Budget Tracking | 4 hours/week | 30 min | 87% |
| Rate Lookup | 15 min/item | 10 sec | 99% |

### Key Benefits

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AUTOMATION BENEFITS                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  BEFORE                           AFTER                             │
│  ──────                           ─────                             │
│  • Manual data entry              • Automatic data flow             │
│  • Excel copy-paste               • ETL pipelines                   │
│  • Searching through manuals      • Semantic search (10 sec)        │
│  • Weekly variance reports        • Real-time alerts                │
│  • Errors from manual transfer    • Validated data quality          │
│                                                                      │
│  RESULT: Teams focus on decisions, not data collection              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Day 1: Installation

```bash
pip install pandas openpyxl ifcopenshell pdfplumber qdrant-client
git clone https://github.com/datadrivenconstruction/DDC_Skills.git
```

### Day 2-3: Data Inventory

```python
# List all data sources
# Use data-silo-detection for analysis
python analyze_data_sources.py
```

### Day 4-5: First ETL Pipeline

```python
# Connect at least 2 data sources
# Example: Excel estimates → Summary report
python run_etl.py
```

### Week 2+: Scale Up

```python
# Add new data sources
# Automate new processes
# Measure ROI
```

---

## Resources

- **Book:** "Data-Driven Construction" by Artem Boiko (ISBN 978-3-9826255-9-1)
- **Website:** https://datadrivenconstruction.io
- **CWICR Database:** https://openconstructionestimate.com
- **GitHub:** https://github.com/datadrivenconstruction

---

**Start today. Construction automation is data automation.**
