---
name: interoperability-analyzer
description: "Analyze data interoperability issues in construction projects. Identify format incompatibilities and data loss points."
---

# Interoperability Analyzer

## Business Case

### Problem Statement
Data interoperability challenges:
- Multiple proprietary formats
- Data loss in conversions
- Incompatible systems
- Missing standard adoption

### Solution
Analyze data exchange patterns, identify interoperability issues, and recommend solutions for seamless data flow.

## Technical Implementation

```python
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class DataFormat(Enum):
    IFC = "ifc"
    RVT = "revit"
    DWG = "autocad"
    NWC = "navisworks"
    SKP = "sketchup"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    BCF = "bcf"
    COBIE = "cobie"


class InteroperabilityLevel(Enum):
    NATIVE = "native"           # Same format
    LOSSLESS = "lossless"       # Full data preserved
    PARTIAL = "partial"         # Some data loss
    DEGRADED = "degraded"       # Significant loss
    INCOMPATIBLE = "incompatible"


@dataclass
class FormatCapability:
    format: DataFormat
    supports_geometry: bool
    supports_properties: bool
    supports_relationships: bool
    supports_scheduling: bool
    supports_costs: bool
    open_standard: bool


@dataclass
class ExchangeAnalysis:
    source_format: DataFormat
    target_format: DataFormat
    interoperability_level: InteroperabilityLevel
    data_preserved: List[str]
    data_lost: List[str]
    recommendations: List[str]


class InteroperabilityAnalyzer:
    """Analyze data interoperability in construction projects."""

    def __init__(self):
        self.capabilities = self._define_capabilities()
        self.exchange_matrix = self._define_exchange_matrix()

    def _define_capabilities(self) -> Dict[DataFormat, FormatCapability]:
        """Define format capabilities."""

        return {
            DataFormat.IFC: FormatCapability(
                DataFormat.IFC, True, True, True, False, False, True
            ),
            DataFormat.RVT: FormatCapability(
                DataFormat.RVT, True, True, True, True, True, False
            ),
            DataFormat.DWG: FormatCapability(
                DataFormat.DWG, True, False, False, False, False, False
            ),
            DataFormat.NWC: FormatCapability(
                DataFormat.NWC, True, True, False, True, False, False
            ),
            DataFormat.EXCEL: FormatCapability(
                DataFormat.EXCEL, False, True, False, True, True, True
            ),
            DataFormat.CSV: FormatCapability(
                DataFormat.CSV, False, True, False, False, True, True
            ),
            DataFormat.JSON: FormatCapability(
                DataFormat.JSON, False, True, True, True, True, True
            ),
            DataFormat.COBIE: FormatCapability(
                DataFormat.COBIE, False, True, True, False, False, True
            ),
            DataFormat.BCF: FormatCapability(
                DataFormat.BCF, False, True, False, False, False, True
            )
        }

    def _define_exchange_matrix(self) -> Dict[tuple, InteroperabilityLevel]:
        """Define interoperability levels between formats."""

        return {
            (DataFormat.RVT, DataFormat.IFC): InteroperabilityLevel.PARTIAL,
            (DataFormat.IFC, DataFormat.RVT): InteroperabilityLevel.PARTIAL,
            (DataFormat.RVT, DataFormat.DWG): InteroperabilityLevel.DEGRADED,
            (DataFormat.DWG, DataFormat.RVT): InteroperabilityLevel.DEGRADED,
            (DataFormat.RVT, DataFormat.NWC): InteroperabilityLevel.LOSSLESS,
            (DataFormat.IFC, DataFormat.NWC): InteroperabilityLevel.PARTIAL,
            (DataFormat.EXCEL, DataFormat.CSV): InteroperabilityLevel.LOSSLESS,
            (DataFormat.CSV, DataFormat.EXCEL): InteroperabilityLevel.LOSSLESS,
            (DataFormat.JSON, DataFormat.EXCEL): InteroperabilityLevel.PARTIAL,
            (DataFormat.RVT, DataFormat.COBIE): InteroperabilityLevel.PARTIAL,
            (DataFormat.IFC, DataFormat.COBIE): InteroperabilityLevel.PARTIAL,
        }

    def analyze_exchange(self, source: DataFormat, target: DataFormat) -> ExchangeAnalysis:
        """Analyze data exchange between formats."""

        level = self.exchange_matrix.get(
            (source, target),
            InteroperabilityLevel.INCOMPATIBLE if source != target else InteroperabilityLevel.NATIVE
        )

        source_cap = self.capabilities.get(source)
        target_cap = self.capabilities.get(target)

        preserved = []
        lost = []

        if source_cap and target_cap:
            if source_cap.supports_geometry and target_cap.supports_geometry:
                preserved.append("geometry")
            elif source_cap.supports_geometry:
                lost.append("geometry")

            if source_cap.supports_properties and target_cap.supports_properties:
                preserved.append("properties")
            elif source_cap.supports_properties:
                lost.append("properties")

            if source_cap.supports_relationships and target_cap.supports_relationships:
                preserved.append("relationships")
            elif source_cap.supports_relationships:
                lost.append("relationships")

            if source_cap.supports_scheduling and target_cap.supports_scheduling:
                preserved.append("scheduling")
            elif source_cap.supports_scheduling:
                lost.append("scheduling")

            if source_cap.supports_costs and target_cap.supports_costs:
                preserved.append("costs")
            elif source_cap.supports_costs:
                lost.append("costs")

        recommendations = self._get_recommendations(source, target, level)

        return ExchangeAnalysis(
            source_format=source,
            target_format=target,
            interoperability_level=level,
            data_preserved=preserved,
            data_lost=lost,
            recommendations=recommendations
        )

    def _get_recommendations(self, source: DataFormat, target: DataFormat,
                             level: InteroperabilityLevel) -> List[str]:
        """Get recommendations for improving exchange."""

        recommendations = []

        if level == InteroperabilityLevel.INCOMPATIBLE:
            recommendations.append("Use intermediate format (IFC recommended)")
            recommendations.append("Consider manual data mapping")

        if level == InteroperabilityLevel.DEGRADED:
            recommendations.append("Export properties separately before conversion")
            recommendations.append("Document lost data for manual recreation")

        if level == InteroperabilityLevel.PARTIAL:
            recommendations.append("Verify critical properties after conversion")
            recommendations.append("Use IFC export settings optimized for target application")

        if source == DataFormat.RVT and target == DataFormat.IFC:
            recommendations.append("Configure IFC export mapping in Revit")
            recommendations.append("Use IFC 4 for better property preservation")

        if target == DataFormat.COBIE:
            recommendations.append("Populate COBie parameters before export")
            recommendations.append("Validate against COBie schema after export")

        return recommendations

    def analyze_workflow(self, formats: List[DataFormat]) -> Dict[str, Any]:
        """Analyze multi-step data workflow."""

        if len(formats) < 2:
            return {"error": "Need at least 2 formats"}

        exchanges = []
        cumulative_lost = set()

        for i in range(len(formats) - 1):
            analysis = self.analyze_exchange(formats[i], formats[i+1])
            exchanges.append({
                'step': i + 1,
                'from': formats[i].value,
                'to': formats[i+1].value,
                'level': analysis.interoperability_level.value,
                'data_lost': analysis.data_lost
            })
            cumulative_lost.update(analysis.data_lost)

        # Overall workflow rating
        levels = [e['level'] for e in exchanges]
        if 'incompatible' in levels:
            overall = 'incompatible'
        elif 'degraded' in levels:
            overall = 'degraded'
        elif 'partial' in levels:
            overall = 'partial'
        else:
            overall = 'lossless'

        return {
            'workflow': ' -> '.join(f.value for f in formats),
            'steps': len(exchanges),
            'exchanges': exchanges,
            'overall_level': overall,
            'total_data_lost': list(cumulative_lost),
            'recommendations': self._get_workflow_recommendations(formats, overall)
        }

    def _get_workflow_recommendations(self, formats: List[DataFormat],
                                       overall: str) -> List[str]:
        """Get workflow optimization recommendations."""

        recommendations = []

        if overall in ['degraded', 'incompatible']:
            recommendations.append("Consider reducing conversion steps")
            recommendations.append("Use IFC as central exchange format")

        if len(formats) > 3:
            recommendations.append("Workflow has many steps - consider simplification")

        if DataFormat.DWG in formats and DataFormat.RVT in formats:
            recommendations.append("DWG-RVT exchanges lose significant data - minimize these")

        return recommendations

    def generate_compatibility_matrix(self) -> pd.DataFrame:
        """Generate format compatibility matrix."""

        formats = list(DataFormat)
        matrix = []

        for source in formats:
            row = {'Format': source.value}
            for target in formats:
                if source == target:
                    row[target.value] = 'native'
                else:
                    level = self.exchange_matrix.get((source, target), InteroperabilityLevel.INCOMPATIBLE)
                    row[target.value] = level.value
            matrix.append(row)

        return pd.DataFrame(matrix)

    def export_analysis(self, output_path: str) -> str:
        """Export analysis to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Compatibility matrix
            matrix = self.generate_compatibility_matrix()
            matrix.to_excel(writer, sheet_name='Compatibility Matrix', index=False)

            # Format capabilities
            caps_data = [{
                'Format': cap.format.value,
                'Geometry': cap.supports_geometry,
                'Properties': cap.supports_properties,
                'Relationships': cap.supports_relationships,
                'Scheduling': cap.supports_scheduling,
                'Costs': cap.supports_costs,
                'Open Standard': cap.open_standard
            } for cap in self.capabilities.values()]
            caps_df = pd.DataFrame(caps_data)
            caps_df.to_excel(writer, sheet_name='Format Capabilities', index=False)

        return output_path
```

## Quick Start

```python
# Initialize analyzer
analyzer = InteroperabilityAnalyzer()

# Analyze single exchange
analysis = analyzer.analyze_exchange(DataFormat.RVT, DataFormat.IFC)
print(f"Level: {analysis.interoperability_level.value}")
print(f"Preserved: {analysis.data_preserved}")
print(f"Lost: {analysis.data_lost}")
```

## Common Use Cases

### 1. Workflow Analysis
```python
workflow = analyzer.analyze_workflow([
    DataFormat.RVT, DataFormat.IFC, DataFormat.NWC
])
print(f"Overall: {workflow['overall_level']}")
print(f"Total data lost: {workflow['total_data_lost']}")
```

### 2. Compatibility Matrix
```python
matrix = analyzer.generate_compatibility_matrix()
print(matrix)
```

### 3. Export Report
```python
analyzer.export_analysis("interoperability_report.xlsx")
```

## Resources
- **DDC Book**: Chapter 3.5 - Data Challenges in Construction
- **buildingSMART**: IFC Standards
- **Website**: https://datadrivenconstruction.io
