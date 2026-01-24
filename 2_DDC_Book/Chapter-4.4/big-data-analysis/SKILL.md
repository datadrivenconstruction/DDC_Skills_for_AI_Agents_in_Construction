---
name: big-data-analysis
description: "Analyze large-scale construction datasets. Process thousands of projects for patterns, benchmarks, and predictive insights."
---

# Big Data Analysis

## Business Case

### Problem Statement
Large-scale data analysis challenges:
- Processing millions of records
- Cross-project benchmarking
- Pattern recognition at scale
- Memory and performance constraints

### Solution
Scalable big data analysis framework for construction data using efficient data structures and parallel processing patterns.

## Technical Implementation

```python
import pandas as pd
from typing import Dict, Any, List, Optional, Callable, Iterator
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
import json


class AnalysisType(Enum):
    BENCHMARK = "benchmark"
    TREND = "trend"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    CLUSTERING = "clustering"
    AGGREGATION = "aggregation"


class MetricType(Enum):
    COST_PER_SF = "cost_per_sf"
    DURATION_PER_SF = "duration_per_sf"
    PRODUCTIVITY = "productivity"
    CHANGE_ORDER_RATE = "change_order_rate"
    SAFETY_RATE = "safety_rate"
    QUALITY_SCORE = "quality_score"


@dataclass
class ProjectRecord:
    project_id: str
    name: str
    project_type: str
    location: str
    size_sf: float
    duration_days: int
    total_cost: float
    start_date: date
    metrics: Dict[str, float] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    metric: str
    mean: float
    median: float
    std: float
    min_val: float
    max_val: float
    percentile_25: float
    percentile_75: float
    sample_size: int


class BigDataAnalyzer:
    """Analyze large-scale construction datasets."""

    def __init__(self, name: str = "Construction Analytics"):
        self.name = name
        self.projects: List[ProjectRecord] = []
        self.df: Optional[pd.DataFrame] = None
        self.benchmarks: Dict[str, BenchmarkResult] = {}

    def load_from_dataframe(self, df: pd.DataFrame):
        """Load project data from DataFrame."""

        self.df = df.copy()
        self.projects = []

        for _, row in df.iterrows():
            project = ProjectRecord(
                project_id=str(row.get('project_id', '')),
                name=str(row.get('name', '')),
                project_type=str(row.get('project_type', '')),
                location=str(row.get('location', '')),
                size_sf=float(row.get('size_sf', 0)),
                duration_days=int(row.get('duration_days', 0)),
                total_cost=float(row.get('total_cost', 0)),
                start_date=pd.to_datetime(row.get('start_date')).date() if pd.notna(row.get('start_date')) else date.today()
            )
            # Add calculated metrics
            if project.size_sf > 0:
                project.metrics['cost_per_sf'] = project.total_cost / project.size_sf
                project.metrics['duration_per_1000sf'] = project.duration_days / (project.size_sf / 1000)

            self.projects.append(project)

    def load_from_parquet(self, path: str):
        """Load data from Parquet file."""
        df = pd.read_parquet(path)
        self.load_from_dataframe(df)

    def stream_process(self, file_path: str, chunk_size: int = 10000,
                       processor: Callable = None) -> Iterator[Dict[str, Any]]:
        """Process large file in chunks."""

        for chunk in pd.read_csv(file_path, chunksize=chunk_size):
            if processor:
                result = processor(chunk)
                yield result
            else:
                yield {'rows': len(chunk), 'columns': list(chunk.columns)}

    def calculate_benchmarks(self, metric_column: str,
                             group_by: str = None) -> Dict[str, BenchmarkResult]:
        """Calculate benchmarks for a metric."""

        if self.df is None or self.df.empty:
            return {}

        results = {}

        if group_by and group_by in self.df.columns:
            groups = self.df.groupby(group_by)
            for group_name, group_df in groups:
                values = group_df[metric_column].dropna()
                if len(values) > 0:
                    results[str(group_name)] = self._calculate_stats(values, metric_column)
        else:
            values = self.df[metric_column].dropna()
            if len(values) > 0:
                results['all'] = self._calculate_stats(values, metric_column)

        self.benchmarks.update(results)
        return results

    def _calculate_stats(self, values: pd.Series, metric: str) -> BenchmarkResult:
        """Calculate statistics for a series."""

        return BenchmarkResult(
            metric=metric,
            mean=round(values.mean(), 2),
            median=round(values.median(), 2),
            std=round(values.std(), 2),
            min_val=round(values.min(), 2),
            max_val=round(values.max(), 2),
            percentile_25=round(values.quantile(0.25), 2),
            percentile_75=round(values.quantile(0.75), 2),
            sample_size=len(values)
        )

    def find_anomalies(self, metric_column: str,
                       threshold_std: float = 2.0) -> pd.DataFrame:
        """Find anomalies based on standard deviation threshold."""

        if self.df is None or self.df.empty:
            return pd.DataFrame()

        values = self.df[metric_column]
        mean = values.mean()
        std = values.std()

        lower = mean - (threshold_std * std)
        upper = mean + (threshold_std * std)

        anomalies = self.df[(values < lower) | (values > upper)].copy()
        anomalies['anomaly_type'] = anomalies[metric_column].apply(
            lambda x: 'high' if x > upper else 'low'
        )
        anomalies['deviation'] = ((anomalies[metric_column] - mean) / std).round(2)

        return anomalies

    def analyze_trends(self, metric_column: str,
                       date_column: str,
                       period: str = 'Y') -> pd.DataFrame:
        """Analyze trends over time."""

        if self.df is None or self.df.empty:
            return pd.DataFrame()

        df = self.df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        df['period'] = df[date_column].dt.to_period(period)

        trends = df.groupby('period').agg({
            metric_column: ['mean', 'median', 'count', 'std']
        }).round(2)

        trends.columns = ['mean', 'median', 'count', 'std']
        trends = trends.reset_index()
        trends['period'] = trends['period'].astype(str)

        # Calculate year-over-year change
        trends['yoy_change'] = trends['mean'].pct_change().round(4) * 100

        return trends

    def calculate_correlations(self, columns: List[str]) -> pd.DataFrame:
        """Calculate correlations between metrics."""

        if self.df is None or self.df.empty:
            return pd.DataFrame()

        available_cols = [c for c in columns if c in self.df.columns]
        return self.df[available_cols].corr().round(3)

    def segment_analysis(self, metric_column: str,
                         segment_column: str) -> pd.DataFrame:
        """Analyze metric by segments."""

        if self.df is None or self.df.empty:
            return pd.DataFrame()

        results = self.df.groupby(segment_column).agg({
            metric_column: ['count', 'mean', 'median', 'std', 'min', 'max']
        }).round(2)

        results.columns = ['count', 'mean', 'median', 'std', 'min', 'max']
        results = results.reset_index()

        # Calculate percentage of total
        total_count = results['count'].sum()
        results['pct_of_total'] = (results['count'] / total_count * 100).round(1)

        return results.sort_values('count', ascending=False)

    def percentile_rank(self, project_id: str, metric_column: str) -> Dict[str, Any]:
        """Get percentile rank for a specific project."""

        if self.df is None or self.df.empty:
            return {}

        project = self.df[self.df['project_id'] == project_id]
        if project.empty:
            return {'error': 'Project not found'}

        value = project[metric_column].values[0]
        all_values = self.df[metric_column].dropna()

        percentile = (all_values < value).sum() / len(all_values) * 100

        benchmark = self.benchmarks.get('all') or self._calculate_stats(all_values, metric_column)

        return {
            'project_id': project_id,
            'metric': metric_column,
            'value': round(value, 2),
            'percentile': round(percentile, 1),
            'comparison': {
                'mean': benchmark.mean,
                'median': benchmark.median,
                'vs_mean': round((value / benchmark.mean - 1) * 100, 1),
                'vs_median': round((value / benchmark.median - 1) * 100, 1)
            }
        }

    def generate_summary_stats(self) -> Dict[str, Any]:
        """Generate summary statistics for the dataset."""

        if self.df is None or self.df.empty:
            return {}

        numeric_cols = self.df.select_dtypes(include=['number']).columns

        return {
            'total_projects': len(self.df),
            'date_range': {
                'min': str(self.df['start_date'].min()) if 'start_date' in self.df.columns else None,
                'max': str(self.df['start_date'].max()) if 'start_date' in self.df.columns else None
            },
            'project_types': self.df['project_type'].nunique() if 'project_type' in self.df.columns else 0,
            'locations': self.df['location'].nunique() if 'location' in self.df.columns else 0,
            'total_value': self.df['total_cost'].sum() if 'total_cost' in self.df.columns else 0,
            'total_sf': self.df['size_sf'].sum() if 'size_sf' in self.df.columns else 0,
            'numeric_columns': list(numeric_cols)
        }

    def export_analysis(self, output_path: str,
                        metrics: List[str] = None) -> str:
        """Export analysis results to Excel."""

        metrics = metrics or ['cost_per_sf', 'duration_days']

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary
            summary = self.generate_summary_stats()
            summary_df = pd.DataFrame([{
                'Total Projects': summary.get('total_projects', 0),
                'Project Types': summary.get('project_types', 0),
                'Locations': summary.get('locations', 0),
                'Total Value ($)': summary.get('total_value', 0),
                'Total SF': summary.get('total_sf', 0)
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Benchmarks
            for metric in metrics:
                if metric in self.df.columns:
                    benchmarks = self.calculate_benchmarks(metric, 'project_type')
                    if benchmarks:
                        bench_data = [{
                            'Segment': k,
                            'Mean': v.mean,
                            'Median': v.median,
                            'Std': v.std,
                            'Min': v.min_val,
                            'Max': v.max_val,
                            'P25': v.percentile_25,
                            'P75': v.percentile_75,
                            'Count': v.sample_size
                        } for k, v in benchmarks.items()]
                        bench_df = pd.DataFrame(bench_data)
                        sheet_name = f"Benchmark_{metric}"[:31]
                        bench_df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Anomalies
            for metric in metrics:
                if metric in self.df.columns:
                    anomalies = self.find_anomalies(metric)
                    if not anomalies.empty:
                        sheet_name = f"Anomalies_{metric}"[:31]
                        anomalies.to_excel(writer, sheet_name=sheet_name, index=False)

        return output_path
```

## Quick Start

```python
# Create analyzer
analyzer = BigDataAnalyzer("Multi-Project Analysis")

# Load data
df = pd.DataFrame([
    {'project_id': 'P001', 'name': 'Office A', 'project_type': 'Office',
     'location': 'NYC', 'size_sf': 50000, 'duration_days': 365,
     'total_cost': 15000000, 'start_date': '2023-01-01'},
    {'project_id': 'P002', 'name': 'Office B', 'project_type': 'Office',
     'location': 'LA', 'size_sf': 75000, 'duration_days': 400,
     'total_cost': 20000000, 'start_date': '2023-03-01'},
    {'project_id': 'P003', 'name': 'Warehouse', 'project_type': 'Industrial',
     'location': 'Chicago', 'size_sf': 100000, 'duration_days': 200,
     'total_cost': 12000000, 'start_date': '2023-06-01'}
])

# Add calculated metric
df['cost_per_sf'] = df['total_cost'] / df['size_sf']

analyzer.load_from_dataframe(df)

# Calculate benchmarks
benchmarks = analyzer.calculate_benchmarks('cost_per_sf', 'project_type')
for segment, stats in benchmarks.items():
    print(f"{segment}: ${stats.mean:.2f}/SF (median: ${stats.median:.2f}/SF)")
```

## Common Use Cases

### 1. Find Anomalies
```python
anomalies = analyzer.find_anomalies('cost_per_sf', threshold_std=2.0)
print(f"Found {len(anomalies)} anomalous projects")
```

### 2. Trend Analysis
```python
trends = analyzer.analyze_trends('cost_per_sf', 'start_date', 'Y')
print(trends)
```

### 3. Project Ranking
```python
ranking = analyzer.percentile_rank('P001', 'cost_per_sf')
print(f"Project is at {ranking['percentile']}th percentile")
```

### 4. Segment Analysis
```python
segments = analyzer.segment_analysis('cost_per_sf', 'project_type')
print(segments)
```

## Resources
- **DDC Book**: Chapter 4.4 - Modern Data Technologies
- **Apache Parquet**: https://parquet.apache.org/
- **Website**: https://datadrivenconstruction.io
