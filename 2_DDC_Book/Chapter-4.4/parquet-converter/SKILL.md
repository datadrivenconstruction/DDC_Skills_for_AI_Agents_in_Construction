---
name: parquet-converter
description: "Convert construction data to/from Parquet format. Optimize storage, enable fast queries, and integrate with data lakehouses."
---

# Parquet Converter

## Business Case

### Problem Statement
Data storage and processing challenges:
- Large CSV files are slow to process
- Inefficient storage of typed data
- Column-oriented queries are slow
- Incompatible with modern data platforms

### Solution
Convert construction data to Parquet format for efficient columnar storage, faster queries, and compatibility with data lakehouses.

## Technical Implementation

```python
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json


class CompressionType:
    SNAPPY = "snappy"
    GZIP = "gzip"
    BROTLI = "brotli"
    ZSTD = "zstd"
    NONE = None


@dataclass
class ParquetSchema:
    columns: Dict[str, str]  # column_name: dtype
    partitions: List[str] = field(default_factory=list)
    row_group_size: int = 100000


@dataclass
class ConversionResult:
    source_path: str
    output_path: str
    source_format: str
    rows: int
    columns: int
    original_size_mb: float
    parquet_size_mb: float
    compression_ratio: float
    duration_seconds: float


class ParquetConverter:
    """Convert construction data to/from Parquet format."""

    def __init__(self, project_name: str = "Data Conversion"):
        self.project_name = project_name
        self.conversions: List[ConversionResult] = []
        self.schemas: Dict[str, ParquetSchema] = {}
        self._define_standard_schemas()

    def _define_standard_schemas(self):
        """Define standard schemas for construction data."""

        self.schemas['projects'] = ParquetSchema(
            columns={
                'project_id': 'string',
                'name': 'string',
                'project_type': 'category',
                'status': 'category',
                'start_date': 'datetime64[ns]',
                'end_date': 'datetime64[ns]',
                'budget': 'float64',
                'actual_cost': 'float64',
                'size_sf': 'float64',
                'location': 'string'
            },
            partitions=['project_type', 'status']
        )

        self.schemas['costs'] = ParquetSchema(
            columns={
                'transaction_id': 'string',
                'project_id': 'string',
                'cost_code': 'category',
                'description': 'string',
                'amount': 'float64',
                'transaction_date': 'datetime64[ns]',
                'vendor': 'string',
                'invoice_number': 'string'
            },
            partitions=['project_id']
        )

        self.schemas['schedule'] = ParquetSchema(
            columns={
                'activity_id': 'string',
                'project_id': 'string',
                'name': 'string',
                'wbs_code': 'string',
                'start_date': 'datetime64[ns]',
                'end_date': 'datetime64[ns]',
                'duration': 'int32',
                'progress': 'float32',
                'status': 'category'
            },
            partitions=['project_id']
        )

        self.schemas['qto'] = ParquetSchema(
            columns={
                'element_id': 'string',
                'project_id': 'string',
                'element_type': 'category',
                'name': 'string',
                'quantity': 'float64',
                'unit': 'category',
                'level': 'string',
                'material': 'string'
            },
            partitions=['project_id', 'element_type']
        )

    def add_schema(self, name: str, schema: ParquetSchema):
        """Add custom schema."""
        self.schemas[name] = schema

    def csv_to_parquet(self, csv_path: str, parquet_path: str,
                       schema_name: str = None,
                       compression: str = CompressionType.SNAPPY,
                       partition_cols: List[str] = None) -> ConversionResult:
        """Convert CSV to Parquet."""

        start_time = datetime.now()

        # Read CSV
        df = pd.read_csv(csv_path)

        # Apply schema if provided
        if schema_name and schema_name in self.schemas:
            schema = self.schemas[schema_name]
            df = self._apply_schema(df, schema)
            partition_cols = partition_cols or schema.partitions

        # Get original file size
        original_size = Path(csv_path).stat().st_size / (1024 * 1024)

        # Write Parquet
        if partition_cols:
            # Partitioned write
            available_partitions = [c for c in partition_cols if c in df.columns]
            if available_partitions:
                df.to_parquet(
                    parquet_path,
                    engine='pyarrow',
                    compression=compression,
                    partition_cols=available_partitions,
                    index=False
                )
            else:
                df.to_parquet(parquet_path, engine='pyarrow',
                             compression=compression, index=False)
        else:
            df.to_parquet(parquet_path, engine='pyarrow',
                         compression=compression, index=False)

        # Calculate parquet size
        if Path(parquet_path).is_dir():
            parquet_size = sum(f.stat().st_size for f in Path(parquet_path).rglob('*.parquet')) / (1024 * 1024)
        else:
            parquet_size = Path(parquet_path).stat().st_size / (1024 * 1024)

        duration = (datetime.now() - start_time).total_seconds()

        result = ConversionResult(
            source_path=csv_path,
            output_path=parquet_path,
            source_format='csv',
            rows=len(df),
            columns=len(df.columns),
            original_size_mb=round(original_size, 2),
            parquet_size_mb=round(parquet_size, 2),
            compression_ratio=round(original_size / parquet_size, 2) if parquet_size > 0 else 0,
            duration_seconds=round(duration, 2)
        )

        self.conversions.append(result)
        return result

    def excel_to_parquet(self, excel_path: str, parquet_path: str,
                         sheet_name: Union[str, int] = 0,
                         schema_name: str = None,
                         compression: str = CompressionType.SNAPPY) -> ConversionResult:
        """Convert Excel to Parquet."""

        start_time = datetime.now()

        # Read Excel
        df = pd.read_excel(excel_path, sheet_name=sheet_name)

        # Apply schema
        if schema_name and schema_name in self.schemas:
            df = self._apply_schema(df, self.schemas[schema_name])

        original_size = Path(excel_path).stat().st_size / (1024 * 1024)

        # Write Parquet
        df.to_parquet(parquet_path, engine='pyarrow',
                     compression=compression, index=False)

        parquet_size = Path(parquet_path).stat().st_size / (1024 * 1024)
        duration = (datetime.now() - start_time).total_seconds()

        result = ConversionResult(
            source_path=excel_path,
            output_path=parquet_path,
            source_format='excel',
            rows=len(df),
            columns=len(df.columns),
            original_size_mb=round(original_size, 2),
            parquet_size_mb=round(parquet_size, 2),
            compression_ratio=round(original_size / parquet_size, 2) if parquet_size > 0 else 0,
            duration_seconds=round(duration, 2)
        )

        self.conversions.append(result)
        return result

    def json_to_parquet(self, json_path: str, parquet_path: str,
                        schema_name: str = None,
                        compression: str = CompressionType.SNAPPY) -> ConversionResult:
        """Convert JSON to Parquet."""

        start_time = datetime.now()

        # Read JSON
        df = pd.read_json(json_path)

        if schema_name and schema_name in self.schemas:
            df = self._apply_schema(df, self.schemas[schema_name])

        original_size = Path(json_path).stat().st_size / (1024 * 1024)

        df.to_parquet(parquet_path, engine='pyarrow',
                     compression=compression, index=False)

        parquet_size = Path(parquet_path).stat().st_size / (1024 * 1024)
        duration = (datetime.now() - start_time).total_seconds()

        result = ConversionResult(
            source_path=json_path,
            output_path=parquet_path,
            source_format='json',
            rows=len(df),
            columns=len(df.columns),
            original_size_mb=round(original_size, 2),
            parquet_size_mb=round(parquet_size, 2),
            compression_ratio=round(original_size / parquet_size, 2) if parquet_size > 0 else 0,
            duration_seconds=round(duration, 2)
        )

        self.conversions.append(result)
        return result

    def parquet_to_csv(self, parquet_path: str, csv_path: str) -> ConversionResult:
        """Convert Parquet to CSV."""

        start_time = datetime.now()

        df = pd.read_parquet(parquet_path)

        if Path(parquet_path).is_dir():
            original_size = sum(f.stat().st_size for f in Path(parquet_path).rglob('*.parquet')) / (1024 * 1024)
        else:
            original_size = Path(parquet_path).stat().st_size / (1024 * 1024)

        df.to_csv(csv_path, index=False)

        csv_size = Path(csv_path).stat().st_size / (1024 * 1024)
        duration = (datetime.now() - start_time).total_seconds()

        result = ConversionResult(
            source_path=parquet_path,
            output_path=csv_path,
            source_format='parquet',
            rows=len(df),
            columns=len(df.columns),
            original_size_mb=round(original_size, 2),
            parquet_size_mb=round(csv_size, 2),  # Actually CSV size
            compression_ratio=round(csv_size / original_size, 2) if original_size > 0 else 0,
            duration_seconds=round(duration, 2)
        )

        self.conversions.append(result)
        return result

    def _apply_schema(self, df: pd.DataFrame, schema: ParquetSchema) -> pd.DataFrame:
        """Apply schema to DataFrame."""

        for col, dtype in schema.columns.items():
            if col in df.columns:
                try:
                    if dtype == 'category':
                        df[col] = df[col].astype('category')
                    elif dtype.startswith('datetime'):
                        df[col] = pd.to_datetime(df[col])
                    else:
                        df[col] = df[col].astype(dtype)
                except (ValueError, TypeError):
                    pass  # Keep original type if conversion fails

        return df

    def get_parquet_info(self, parquet_path: str) -> Dict[str, Any]:
        """Get information about a Parquet file."""

        import pyarrow.parquet as pq

        if Path(parquet_path).is_dir():
            # Partitioned dataset
            files = list(Path(parquet_path).rglob('*.parquet'))
            total_size = sum(f.stat().st_size for f in files) / (1024 * 1024)

            if files:
                sample = pq.read_table(str(files[0]))
                schema = sample.schema
            else:
                return {'error': 'No parquet files found'}

            return {
                'path': parquet_path,
                'type': 'partitioned',
                'num_files': len(files),
                'total_size_mb': round(total_size, 2),
                'columns': [f.name for f in schema],
                'dtypes': {f.name: str(f.type) for f in schema}
            }
        else:
            # Single file
            pf = pq.ParquetFile(parquet_path)
            metadata = pf.metadata

            return {
                'path': parquet_path,
                'type': 'single_file',
                'size_mb': round(Path(parquet_path).stat().st_size / (1024 * 1024), 2),
                'num_rows': metadata.num_rows,
                'num_columns': metadata.num_columns,
                'num_row_groups': metadata.num_row_groups,
                'columns': [pf.schema_arrow.field(i).name for i in range(metadata.num_columns)],
                'created_by': metadata.created_by
            }

    def query_parquet(self, parquet_path: str, columns: List[str] = None,
                      filters: List[tuple] = None) -> pd.DataFrame:
        """Query Parquet file with column selection and filtering."""

        return pd.read_parquet(
            parquet_path,
            columns=columns,
            filters=filters
        )

    def merge_parquet_files(self, input_paths: List[str],
                            output_path: str,
                            compression: str = CompressionType.SNAPPY) -> ConversionResult:
        """Merge multiple Parquet files into one."""

        start_time = datetime.now()

        dfs = [pd.read_parquet(p) for p in input_paths]
        merged = pd.concat(dfs, ignore_index=True)

        original_size = sum(Path(p).stat().st_size for p in input_paths) / (1024 * 1024)

        merged.to_parquet(output_path, engine='pyarrow',
                         compression=compression, index=False)

        parquet_size = Path(output_path).stat().st_size / (1024 * 1024)
        duration = (datetime.now() - start_time).total_seconds()

        return ConversionResult(
            source_path=str(input_paths),
            output_path=output_path,
            source_format='parquet_merge',
            rows=len(merged),
            columns=len(merged.columns),
            original_size_mb=round(original_size, 2),
            parquet_size_mb=round(parquet_size, 2),
            compression_ratio=round(original_size / parquet_size, 2) if parquet_size > 0 else 0,
            duration_seconds=round(duration, 2)
        )

    def get_conversion_summary(self) -> Dict[str, Any]:
        """Get summary of all conversions."""

        if not self.conversions:
            return {'total_conversions': 0}

        return {
            'total_conversions': len(self.conversions),
            'total_rows_processed': sum(c.rows for c in self.conversions),
            'original_size_mb': sum(c.original_size_mb for c in self.conversions),
            'parquet_size_mb': sum(c.parquet_size_mb for c in self.conversions),
            'avg_compression_ratio': round(
                sum(c.compression_ratio for c in self.conversions) / len(self.conversions), 2
            ),
            'total_duration_seconds': sum(c.duration_seconds for c in self.conversions)
        }

    def export_conversion_log(self, output_path: str) -> str:
        """Export conversion log to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary
            summary = self.get_conversion_summary()
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Detailed log
            log_df = pd.DataFrame([{
                'Source': c.source_path,
                'Output': c.output_path,
                'Format': c.source_format,
                'Rows': c.rows,
                'Columns': c.columns,
                'Original Size (MB)': c.original_size_mb,
                'Parquet Size (MB)': c.parquet_size_mb,
                'Compression Ratio': c.compression_ratio,
                'Duration (s)': c.duration_seconds
            } for c in self.conversions])
            log_df.to_excel(writer, sheet_name='Conversions', index=False)

        return output_path
```

## Quick Start

```python
# Create converter
converter = ParquetConverter("Project Data Migration")

# Convert CSV to Parquet
result = converter.csv_to_parquet(
    "costs.csv",
    "costs.parquet",
    schema_name="costs",
    compression="snappy"
)

print(f"Converted {result.rows} rows")
print(f"Compression ratio: {result.compression_ratio}x")
print(f"Size: {result.original_size_mb}MB -> {result.parquet_size_mb}MB")
```

## Common Use Cases

### 1. Excel to Parquet
```python
result = converter.excel_to_parquet(
    "project_data.xlsx",
    "project_data.parquet",
    schema_name="projects"
)
```

### 2. Query Parquet
```python
# Select specific columns with filter
df = converter.query_parquet(
    "costs.parquet",
    columns=['project_id', 'amount', 'transaction_date'],
    filters=[('amount', '>', 10000)]
)
```

### 3. Get File Info
```python
info = converter.get_parquet_info("costs.parquet")
print(f"Rows: {info['num_rows']}")
print(f"Columns: {info['columns']}")
```

### 4. Merge Files
```python
result = converter.merge_parquet_files(
    ["costs_2023.parquet", "costs_2024.parquet"],
    "costs_all.parquet"
)
```

## Resources
- **DDC Book**: Chapter 4.4 - Modern Data Technologies
- **Apache Parquet**: https://parquet.apache.org/
- **PyArrow**: https://arrow.apache.org/docs/python/
- **Website**: https://datadrivenconstruction.io
