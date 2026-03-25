---
name: "data-evolution-analysis"
description: "Analyze data evolution patterns in construction organizations from paper-based to AI-driven operations. Use when assessing digital maturity levels, evaluating data practices in construction firms, benchmarking technology adoption across departments, or building digitization roadmaps for builders and contractors."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "📚", "os": ["win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Data Evolution Analysis

Based on DDC methodology (Chapter 1.1), analyze data evolution patterns in construction organizations and assess digital maturity from paper-based workflows (Level 0) to predictive/autonomous operations (Level 5).

**Book Reference:** "Evolution of Data Usage in Construction"

## Workflow

1. **Inventory systems** in use across the organization (tools, integrations, APIs)
2. **Collect survey responses** for each data category (design, cost, schedule, etc.)
3. **Validate inputs** — ensure all required survey keys and system inventory entries are present
4. **Run assessment** to calculate category scores and overall maturity level
5. **Review** strengths, weaknesses, and phased roadmap
6. **Track over time** with quarterly reassessments to measure progress

## Quick Start

```python
from data_evolution import DataEvolutionAnalyzer, DataCategory

analyzer = DataEvolutionAnalyzer()

# Step 1: Define systems in use
systems = [
    {"name": "AutoCAD", "category": "design", "has_api": False},
    {"name": "Revit", "category": "design", "has_api": True, "integrations": ["Navisworks"]},
    {"name": "Excel", "category": "cost", "has_api": False},
    {"name": "MS Project", "category": "schedule", "has_api": False},
    {"name": "Email", "category": "communication", "has_api": False}
]

# Step 2: Survey responses (0.0-1.0 scale per category)
survey = {
    "design_tool_maturity": 0.6,
    "design_process_maturity": 0.5,
    "design_data_quality": 0.7,
    "cost_tool_maturity": 0.3,
    "cost_process_maturity": 0.4,
    "cost_data_quality": 0.5,
    "schedule_tool_maturity": 0.4,
    "schedule_process_maturity": 0.3,
    "schedule_data_quality": 0.4
}

# Step 3: Validate required keys exist
required_keys = [f"{cat.value}_{metric}" for cat in DataCategory
                 for metric in ["tool_maturity", "process_maturity", "data_quality"]]
missing = [k for k in required_keys if k not in survey]
if missing:
    print(f"Warning: missing survey keys: {missing}")

# Step 4: Run assessment
assessment = analyzer.assess_organization(
    organization_name="Construction Co",
    survey_responses=survey,
    system_inventory=systems
)

print(f"Maturity Level: {assessment.overall_level.name}")
print(f"Strengths: {assessment.strengths}")
print(f"Weaknesses: {assessment.weaknesses}")
print(f"Top Recommendations: {assessment.recommendations[:3]}")
```

## Maturity Levels

| Level | Name | Description | Typical Tools |
|-------|------|-------------|---------------|
| 0 | Paper-Based | Manual, paper-based processes | Paper forms, physical filing |
| 1 | Basic Digital | Standalone digital tools | Excel, Word, email, file shares |
| 2 | Structured | Department-specific software | CAD, estimating software, project tools |
| 3 | Integrated | Connected systems with data flow | BIM, ERP, CDE, BI dashboards |
| 4 | Automated | ML/AI and automated data collection | ML platforms, IoT, advanced analytics |
| 5 | Predictive | AI-driven, autonomous operations | Digital twins, AI/ML, autonomous systems |

## Common Use Cases

### Track Evolution Over Time
```python
from data_evolution import DataEvolutionTracker

tracker = DataEvolutionTracker("Construction Co")
tracker.add_assessment(q1_assessment)
tracker.add_assessment(q2_assessment)

summary = tracker.get_evolution_summary()
print(f"Progress: {summary['starting_level']} -> {summary['current_level']}")
print(f"Milestones achieved: {len(summary['milestones'])}")
```

### Generate Executive Report
```python
report = analyzer.generate_report(assessment)

# Verify report generated successfully
assert len(report) > 0, "Report generation failed"

with open("maturity_report.md", "w") as f:
    f.write(report)
```

### Compare Assessments
```python
comparison = analyzer.compare_assessments([q1_assessment, q2_assessment, q3_assessment])
for cat, trend in comparison["trends"].items():
    print(f"{cat}: improvement = {trend['improvement']:.0%}")
```

## Data Categories

| Category | Weight | Key Metrics |
|----------|--------|-------------|
| Design | 0.20 | model_usage, clash_detection, design_reviews |
| Cost | 0.15 | automation_level, historical_data, benchmarking |
| Schedule | 0.15 | resource_loading, progress_tracking, forecasting |
| Quality | 0.12 | inspection_digitization, defect_analytics, compliance |
| Safety | 0.12 | incident_tracking, predictive_safety, training |
| Procurement | 0.10 | vendor_management, material_tracking, integration |
| Document | 0.08 | version_control, access_control, searchability |
| Communication | 0.08 | response_time, transparency, audit_trail |

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `DataEvolutionAnalyzer` | Main assessment engine |
| `MaturityLevel` | 6 levels from paper (0) to predictive (5) |
| `DataCategory` | 8 categories (design, cost, schedule, etc.) |
| `DataFlowAssessment` | Per-category data flow analysis |
| `MaturityAssessment` | Complete assessment with roadmap |
| `DataEvolutionTracker` | Track progress across quarterly assessments |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 1.1
- **Website**: https://datadrivenconstruction.io

## Next Steps

- Use [data-silo-detection](../../1.2-Data-Silos-Integration/data-silo-detection/SKILL.md) to identify integration gaps
- Use [erp-integration-analysis](../../1.2-Data-Silos-Integration/erp-integration-analysis/SKILL.md) for system integration
- Use [digital-maturity-assessment](../../5.1-Digital-Maturity-Strategy/digital-maturity-assessment/SKILL.md) for detailed assessments
