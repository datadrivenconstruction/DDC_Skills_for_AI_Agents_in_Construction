---
name: historical-data-manager
description: "Extract, clean, and organize legacy construction data from archives. Migrate historical project data, cost records, and schedules into modern formats."
---

# Historical Data Manager for Construction

## Overview

Manage legacy construction data from archives, old systems, and historical records. Extract, clean, normalize, and migrate data into modern formats for analysis and benchmarking.

## Business Case

Construction companies accumulate decades of project data in various formats:
- Paper records scanned to PDF
- Legacy database exports (Access, dBase, FoxPro)
- Old spreadsheet formats (Lotus 1-2-3, early Excel)
- Proprietary software exports
- Project closeout documentation

This skill helps extract value from historical data for:
- Cost benchmarking and trending
- Productivity analysis over time
- Risk pattern identification
- Estimating improvement

## Technical Implementation

### Historical Data Extractor

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import pandas as pd
import re
import json

@dataclass
class HistoricalRecord:
    project_id: str
    project_name: str
    year: int
    data_type: str  # cost, schedule, labor, material
    original_format: str
    extracted_data: Dict[str, Any]
    quality_score: float
    notes: List[str] = field(default_factory=list)

class HistoricalDataManager:
    """Manage extraction and normalization of historical construction data."""

    def __init__(self, archive_path: str):
        self.archive_path = Path(archive_path)
        self.records: List[HistoricalRecord] = []
        self.normalization_rules = self._load_normalization_rules()

    def scan_archive(self) -> Dict[str, int]:
        """Scan archive and categorize files by type."""
        file_types = {}

        for file_path in self.archive_path.rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1

        return file_types

    def extract_from_legacy_excel(self, file_path: str, year: int) -> List[HistoricalRecord]:
        """Extract data from legacy Excel files."""
        records = []

        try:
            # Try different engines for old formats
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
            except:
                df = pd.read_excel(file_path, engine='xlrd')

            # Detect data type from content
            data_type = self._detect_data_type(df)

            # Normalize column names
            df = self._normalize_columns(df)

            # Extract project info
            project_info = self._extract_project_info(df, file_path)

            record = HistoricalRecord(
                project_id=project_info.get('id', f'LEGACY-{year}-{hash(file_path) % 10000}'),
                project_name=project_info.get('name', Path(file_path).stem),
                year=year,
                data_type=data_type,
                original_format='excel',
                extracted_data=df.to_dict('records'),
                quality_score=self._assess_quality(df)
            )
            records.append(record)

        except Exception as e:
            print(f"Error extracting {file_path}: {e}")

        return records

    def extract_from_csv(self, file_path: str, year: int) -> HistoricalRecord:
        """Extract data from CSV files with encoding detection."""
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                break
            except:
                continue

        df = self._normalize_columns(df)
        data_type = self._detect_data_type(df)

        return HistoricalRecord(
            project_id=f'CSV-{year}-{hash(file_path) % 10000}',
            project_name=Path(file_path).stem,
            year=year,
            data_type=data_type,
            original_format='csv',
            extracted_data=df.to_dict('records'),
            quality_score=self._assess_quality(df)
        )

    def extract_from_database_export(self, file_path: str, db_type: str) -> List[HistoricalRecord]:
        """Extract data from legacy database exports."""
        records = []

        if db_type == 'access':
            # Read Access MDB/ACCDB files
            import pyodbc
            conn_str = f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={file_path}'
            conn = pyodbc.connect(conn_str)

            # Get all tables
            cursor = conn.cursor()
            tables = [row.table_name for row in cursor.tables(tableType='TABLE')]

            for table in tables:
                df = pd.read_sql(f'SELECT * FROM [{table}]', conn)
                # Process each table...

            conn.close()

        return records

    def normalize_cost_data(self, records: List[HistoricalRecord], base_year: int = 2026) -> pd.DataFrame:
        """Normalize historical cost data to current dollars."""
        # RSMeans historical cost indices (example values)
        cost_indices = {
            2015: 0.82, 2016: 0.84, 2017: 0.87, 2018: 0.90,
            2019: 0.93, 2020: 0.95, 2021: 0.98, 2022: 1.02,
            2023: 1.06, 2024: 1.10, 2025: 1.14, 2026: 1.18
        }

        normalized_data = []

        for record in records:
            if record.data_type == 'cost':
                year_index = cost_indices.get(record.year, 1.0)
                base_index = cost_indices.get(base_year, 1.18)
                escalation_factor = base_index / year_index

                for item in record.extracted_data:
                    if 'amount' in item or 'cost' in item:
                        original_cost = item.get('amount') or item.get('cost', 0)
                        normalized_item = item.copy()
                        normalized_item['original_cost'] = original_cost
                        normalized_item['normalized_cost'] = original_cost * escalation_factor
                        normalized_item['escalation_factor'] = escalation_factor
                        normalized_item['original_year'] = record.year
                        normalized_item['project_id'] = record.project_id
                        normalized_data.append(normalized_item)

        return pd.DataFrame(normalized_data)

    def _detect_data_type(self, df: pd.DataFrame) -> str:
        """Detect type of data from column names and content."""
        columns_lower = [c.lower() for c in df.columns]

        if any(c in columns_lower for c in ['cost', 'amount', 'price', 'total', 'budget']):
            return 'cost'
        elif any(c in columns_lower for c in ['start', 'finish', 'duration', 'task', 'activity']):
            return 'schedule'
        elif any(c in columns_lower for c in ['hours', 'labor', 'worker', 'crew']):
            return 'labor'
        elif any(c in columns_lower for c in ['material', 'quantity', 'unit', 'supplier']):
            return 'material'
        else:
            return 'unknown'

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to standard format."""
        column_mapping = {
            r'proj.*id': 'project_id',
            r'proj.*name': 'project_name',
            r'desc.*': 'description',
            r'qty|quantity': 'quantity',
            r'unit.*cost|unit.*price': 'unit_cost',
            r'total|amount': 'amount',
            r'start.*date': 'start_date',
            r'end.*date|finish.*date': 'end_date',
            r'dur.*': 'duration',
        }

        new_columns = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            for pattern, new_name in column_mapping.items():
                if re.match(pattern, col_lower):
                    new_columns[col] = new_name
                    break

        return df.rename(columns=new_columns)

    def _assess_quality(self, df: pd.DataFrame) -> float:
        """Assess data quality score (0-1)."""
        if df.empty:
            return 0.0

        scores = []

        # Completeness: % of non-null values
        completeness = 1 - (df.isnull().sum().sum() / df.size)
        scores.append(completeness)

        # Column quality: has meaningful column names
        meaningful_cols = sum(1 for c in df.columns if len(c) > 2 and not c.startswith('Unnamed'))
        col_quality = meaningful_cols / len(df.columns)
        scores.append(col_quality)

        # Row count: more data is better (capped at 1.0)
        row_score = min(len(df) / 100, 1.0)
        scores.append(row_score)

        return sum(scores) / len(scores)

    def _extract_project_info(self, df: pd.DataFrame, file_path: str) -> Dict[str, str]:
        """Extract project info from data or filename."""
        info = {}

        # Try to find project info in data
        for col in df.columns:
            if 'project' in col.lower() and 'id' in col.lower():
                info['id'] = str(df[col].iloc[0]) if not df[col].empty else None
            if 'project' in col.lower() and 'name' in col.lower():
                info['name'] = str(df[col].iloc[0]) if not df[col].empty else None

        # Fallback to filename
        if 'name' not in info:
            info['name'] = Path(file_path).stem

        return info

    def _load_normalization_rules(self) -> Dict:
        """Load rules for normalizing legacy data."""
        return {
            'unit_conversions': {
                'M': 1000,  # Thousand
                'C': 100,   # Hundred
                'LF': 1,    # Linear Foot
                'SF': 1,    # Square Foot
                'CY': 1,    # Cubic Yard
            },
            'date_formats': [
                '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d',
                '%d-%b-%Y', '%B %d, %Y'
            ]
        }

    def generate_migration_report(self) -> str:
        """Generate report on migrated data."""
        report = ["# Historical Data Migration Report", ""]

        # Summary
        report.append("## Summary")
        report.append(f"- Total Records: {len(self.records)}")

        by_type = {}
        by_year = {}
        for r in self.records:
            by_type[r.data_type] = by_type.get(r.data_type, 0) + 1
            by_year[r.year] = by_year.get(r.year, 0) + 1

        report.append("\n### By Data Type")
        for dt, count in sorted(by_type.items()):
            report.append(f"- {dt}: {count}")

        report.append("\n### By Year")
        for year, count in sorted(by_year.items()):
            report.append(f"- {year}: {count}")

        # Quality Assessment
        report.append("\n## Data Quality")
        avg_quality = sum(r.quality_score for r in self.records) / len(self.records) if self.records else 0
        report.append(f"- Average Quality Score: {avg_quality:.2%}")

        low_quality = [r for r in self.records if r.quality_score < 0.5]
        if low_quality:
            report.append(f"\n### Low Quality Records ({len(low_quality)})")
            for r in low_quality[:10]:
                report.append(f"- {r.project_name} ({r.year}): {r.quality_score:.2%}")

        return "\n".join(report)
```

### Legacy System Connectors

```python
class LegacySystemConnector:
    """Connect to various legacy construction systems."""

    @staticmethod
    def read_timberline_export(file_path: str) -> pd.DataFrame:
        """Read Sage Timberline (now Sage 300) export files."""
        # Timberline exports typically have specific format
        df = pd.read_csv(file_path, encoding='cp1252')

        # Map Timberline columns to standard
        column_map = {
            'JOB': 'project_id',
            'PHASE': 'phase_code',
            'CATEGORY': 'cost_code',
            'DESCRIPTION': 'description',
            'ESTIMATE': 'estimated_cost',
            'ACTUAL': 'actual_cost',
            'COMMITTED': 'committed_cost'
        }

        return df.rename(columns=column_map)

    @staticmethod
    def read_primavera_xer(file_path: str) -> Dict[str, pd.DataFrame]:
        """Read Primavera P6 XER export files."""
        tables = {}
        current_table = None
        current_data = []
        columns = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('%T'):
                    # Save previous table
                    if current_table and current_data:
                        tables[current_table] = pd.DataFrame(current_data, columns=columns)
                    # Start new table
                    current_table = line.split('\t')[1] if '\t' in line else None
                    current_data = []
                    columns = []
                elif line.startswith('%F'):
                    # Field definitions
                    columns = line.split('\t')[1:]
                elif line.startswith('%R'):
                    # Data row
                    current_data.append(line.split('\t')[1:])

        # Save last table
        if current_table and current_data:
            tables[current_table] = pd.DataFrame(current_data, columns=columns)

        return tables

    @staticmethod
    def read_mc2_ice(file_path: str) -> pd.DataFrame:
        """Read MC2 ICE estimating export."""
        # MC2 ICE format handling
        pass
```

## Quick Start

```python
# Initialize manager
manager = HistoricalDataManager('/archive/projects')

# Scan archive
file_types = manager.scan_archive()
print(f"Found: {file_types}")

# Extract from legacy Excel files
for year in range(2015, 2024):
    year_path = f'/archive/projects/{year}'
    for file in Path(year_path).glob('*.xls*'):
        records = manager.extract_from_legacy_excel(str(file), year)
        manager.records.extend(records)

# Normalize cost data to 2026 dollars
cost_records = [r for r in manager.records if r.data_type == 'cost']
normalized_costs = manager.normalize_cost_data(cost_records, base_year=2026)

# Generate migration report
report = manager.generate_migration_report()
print(report)

# Export for analysis
normalized_costs.to_excel('historical_costs_normalized.xlsx', index=False)
```

## Common Use Cases

1. **Cost Benchmarking**: Normalize historical costs for comparison
2. **Productivity Analysis**: Track labor productivity over time
3. **Risk Identification**: Find patterns in historical project issues
4. **Estimating Calibration**: Improve estimates with historical data

## Dependencies

```bash
pip install pandas openpyxl xlrd pyodbc
```

## Resources

- **RSMeans Historical Cost Index**: For cost escalation
- **ENR Construction Cost Index**: Alternative escalation source
- **Legacy Format Documentation**: Vendor-specific export formats
