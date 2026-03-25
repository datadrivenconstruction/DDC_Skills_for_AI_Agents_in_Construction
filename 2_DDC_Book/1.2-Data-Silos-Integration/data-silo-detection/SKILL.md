---
name: "data-silo-detection"
description: "Detect and map data silos in construction organizations by analyzing system connectivity, duplicate data, and domain relationships. Use when auditing disconnected data sources, identifying integration opportunities, evaluating system fragmentation, or planning data consolidation for construction firms."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🔗", "os": ["win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Data Silo Detection

Based on DDC methodology (Chapter 1.2), detect and map data silos in construction organizations. Analyzes system connectivity, finds duplicate data across sources, identifies missing domain integrations, and generates a prioritized integration roadmap.

**Book Reference:** "Technologies and Management Systems in Modern Construction"

## Workflow

1. **Inventory data sources** across the organization (databases, spreadsheets, cloud apps, desktop tools)
2. **Define connections** between systems (which systems share data)
3. **Validate inputs** — ensure each source has required fields (id, name, type, domain, users, data_entities)
4. **Run detection** to identify isolated sources, domain gaps, and duplicate data
5. **Review** connectivity score, prioritized silos, and action items
6. **Generate report** with phased integration roadmap

## Quick Start

```python
from data_silo_detection import DataSiloDetector, DataSource, DataSourceType, DataDomain

detector = DataSiloDetector()

# Define data sources with their connections
sources = [
    DataSource(
        id="revit", name="Revit Models",
        type=DataSourceType.DESKTOP_APP, domain=DataDomain.DESIGN,
        owner="Design Team", department="Engineering",
        users=["architect1", "engineer1", "engineer2"],
        data_entities=["building_model", "drawings", "schedules"],
        connections=["navisworks"],  # Connected to Navisworks
        has_api=True
    ),
    DataSource(
        id="excel_estimates", name="Excel Cost Estimates",
        type=DataSourceType.SPREADSHEET, domain=DataDomain.COST,
        owner="Estimator", department="Pre-construction",
        users=["estimator1"],
        data_entities=["costs", "quantities", "labor_rates"],
        connections=[],  # No connections = silo!
        access_level="personal"
    ),
    DataSource(
        id="procore", name="Procore",
        type=DataSourceType.CLOUD_APP, domain=DataDomain.SITE,
        owner="Project Manager", department="Operations",
        users=["pm1", "pm2", "super1"],
        data_entities=["daily_reports", "photos", "punch_list"],
        connections=["primavera"],
        has_api=True
    )
]

# Validate all sources have required fields
for s in sources:
    assert s.id and s.name and s.users, f"Source {s.id} missing required fields"

# Run detection
analysis = detector.detect_silos(
    organization="ABC Construction",
    data_sources=sources
)

# Review results
print(f"Connectivity Score: {analysis.connectivity_score:.0%}")
print(f"Silos Detected: {len(analysis.silos_detected)}")
print(f"Duplicate Data Issues: {len(analysis.duplicates)}")
print(f"\nPriority Actions:")
for action in analysis.priority_actions:
    print(f"  - {action}")
```

## Silo Types Detected

| Type | Severity | Description |
|------|----------|-------------|
| Isolated Source | Critical/High | System with zero connections to other tools |
| Personal Silo | Medium | Data locked in individual's personal storage |
| Domain Disconnect | High | No data flow between related domains (e.g., cost <-> design) |
| Duplicate Data | Varies | Same entity maintained in multiple sources without sync |

## Common Use Cases

### Generate Silo Report
```python
report = detector.generate_report(analysis)

# Verify report is non-empty
assert "Executive Summary" in report, "Report generation issue"

with open("silo_report.md", "w") as f:
    f.write(report)
```

### View Integration Roadmap
```python
for phase, items in analysis.integration_roadmap.items():
    print(f"\n{phase}:")
    for item in items:
        print(f"  - {item}")
```

### Analyze Duplicate Data
```python
for dup in analysis.duplicates:
    print(f"'{dup.entity_name}' found in {len(dup.sources)} sources")
    if dup.issues:
        for issue in dup.issues:
            print(f"  Issue: {issue}")
```

## Domain Relationship Map

Expected integrations between construction data domains:

| Domain | Should Connect To |
|--------|-------------------|
| Design | Cost, Schedule, Procurement, Quality |
| Cost | Design, Schedule, Financial, Procurement |
| Schedule | Design, Cost, Site, HR |
| Procurement | Cost, Design, Site, Financial |
| Site | Schedule, Safety, Quality, HR |
| Quality | Design, Site, Document |
| Safety | Site, HR, Document |
| Financial | Cost, Procurement, HR |

Missing connections between related domains are flagged as **domain disconnect** silos.

## Critical Shared Entities

Entities that must be synchronized across domains: `project`, `budget`, `schedule`, `material`, `labor`, `subcontractor`, `rfi`, `change_order`. Duplicates without a designated master source are flagged.

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `DataSiloDetector` | Main detection engine |
| `DataSource` | Define a data source with connections and metadata |
| `DataSilo` | Detected silo with severity, impact, and recommendations |
| `DuplicateData` | Duplicate entity across sources |
| `SiloAnalysis` | Complete analysis with connectivity score and roadmap |
| `SiloSeverity` | Critical / High / Medium / Low classification |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 1.2
- **Website**: https://datadrivenconstruction.io

## Next Steps

- Use [erp-integration-analysis](../erp-integration-analysis/SKILL.md) for system integration planning
- Use [data-evolution-analysis](../../1.1-Data-Evolution/data-evolution-analysis/SKILL.md) for maturity assessment
- Use [etl-pipeline](../../4.2-ETL-Automation/etl-pipeline/SKILL.md) to connect silos
