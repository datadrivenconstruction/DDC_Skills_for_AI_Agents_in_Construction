---
name: "digital-maturity-assessment"
description: "Assess a construction organization's digital transformation readiness across strategy, technology, data, processes, people, and culture dimensions. Use when evaluating digital maturity, benchmarking technology adoption, planning digital transformation roadmaps, or scoring an organization's data culture readiness."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🎯", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Digital Maturity Assessment

Evaluate construction organizations across six dimensions (Strategy, Technology, Data, Processes, People, Culture) using a 1-5 maturity scale with weighted scoring, gap analysis, and actionable recommendations.

## Workflow

1. **Initialize** assessment for the target organization
2. **Record responses** to standardized questions (17 questions across 6 dimensions)
3. **Validate** all required questions are answered before proceeding
4. **Calculate** dimension and overall scores
5. **Review** gaps and recommendations
6. **Export** results to Excel or markdown report

## Quick Start

```python
from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime
from enum import Enum
import pandas as pd


class MaturityLevel(Enum):
    INITIAL = 1       # Ad-hoc, reactive
    DEVELOPING = 2    # Some processes defined
    DEFINED = 3       # Standardized processes
    MANAGED = 4       # Measured and controlled
    OPTIMIZING = 5    # Continuous improvement


class AssessmentDimension(Enum):
    STRATEGY = "strategy"
    TECHNOLOGY = "technology"
    DATA = "data"
    PROCESSES = "processes"
    PEOPLE = "people"
    CULTURE = "culture"


# Create assessment
assessment = DigitalMaturityAssessment("ABC Construction Inc.")

# Record responses (score 1-5 per question)
assessment.record_response("STR-01", 3, "Strategy exists but needs updating")
assessment.record_response("STR-02", 4, "Strong executive support")
assessment.record_response("STR-03", 3)
assessment.record_response("TECH-01", 2, "Still mostly on-premise")
assessment.record_response("TECH-02", 2, "Manual data transfer between systems")
assessment.record_response("TECH-03", 3)
assessment.record_response("DATA-01", 2)
assessment.record_response("DATA-02", 2)
assessment.record_response("DATA-03", 3)
assessment.record_response("PROC-01", 3)
assessment.record_response("PROC-02", 2)
assessment.record_response("PPL-01", 3)
assessment.record_response("PPL-02", 2)
assessment.record_response("PPL-03", 3)
assessment.record_response("CUL-01", 2)
assessment.record_response("CUL-02", 3)
assessment.record_response("CUL-03", 3)

# Validate completeness before scoring
total_q = len(assessment.questions)
total_r = len(assessment.responses)
assert total_r == total_q, f"Missing {total_q - total_r} responses"

# Get overall assessment
results = assessment.get_overall_assessment()
print(f"Overall Score: {results['overall_score']}/5")
print(f"Maturity Level: {results['overall_level']}")
for rec in results['priority_recommendations']:
    print(f"  - {rec}")
```

## Common Use Cases

### Dimension-Level Analysis
```python
data_score = assessment.calculate_dimension_score(AssessmentDimension.DATA)
print(f"Data Dimension: {data_score.score}/5 ({data_score.level.name})")
print(f"Sub-scores: {data_score.sub_scores}")
print(f"Gaps: {data_score.gaps}")
```

### Export to Excel
```python
output_path = assessment.export_to_excel("maturity_assessment.xlsx")
# Verify export succeeded
import os
assert os.path.exists(output_path), "Export failed"
print(f"Report saved to {output_path}")
```

### Bulk Response Import
```python
responses_df = pd.DataFrame([
    {'question_id': 'STR-01', 'score': 3, 'notes': 'In progress'},
    {'question_id': 'STR-02', 'score': 4, 'notes': 'Strong support'}
])
assessment.record_responses_from_df(responses_df)
```

### View All Questions
```python
questions = assessment.get_questions_list()
print(questions[['Question ID', 'Dimension', 'Question', 'Weight']])
```

## Assessment Questions Reference

| ID | Dimension | Sub-Dimension | Weight |
|----|-----------|---------------|--------|
| STR-01 | Strategy | Digital Vision | 1.5 |
| STR-02 | Strategy | Leadership | 1.5 |
| STR-03 | Strategy | Investment | 1.0 |
| TECH-01 | Technology | Infrastructure | 1.0 |
| TECH-02 | Technology | Systems Integration | 1.2 |
| TECH-03 | Technology | Automation | 1.0 |
| DATA-01 | Data | Data Quality | 1.2 |
| DATA-02 | Data | Data Governance | 1.0 |
| DATA-03 | Data | Analytics | 1.3 |
| PROC-01 | Processes | Standardization | 1.0 |
| PROC-02 | Processes | Digitization | 1.2 |
| PPL-01 | People | Skills | 1.0 |
| PPL-02 | People | Training | 0.8 |
| PPL-03 | People | Adoption | 1.0 |
| CUL-01 | Culture | Innovation | 0.8 |
| CUL-02 | Culture | Collaboration | 0.8 |
| CUL-03 | Culture | Change Readiness | 1.0 |

Each question uses a 1-5 scale: 1 = Initial/ad-hoc, 2 = Developing, 3 = Defined, 4 = Managed, 5 = Optimizing.

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `DigitalMaturityAssessment` | Main assessment engine with questions and scoring |
| `MaturityLevel` | 5-level maturity scale (Initial to Optimizing) |
| `AssessmentDimension` | 6 assessment dimensions |
| `DimensionScore` | Per-dimension results with gaps and recommendations |
| `record_response()` | Record answer to a question (ID, score 1-5, notes) |
| `get_overall_assessment()` | Calculate all scores and generate recommendations |
| `export_to_excel()` | Multi-sheet Excel report (Summary, Dimensions, Responses) |

## Resources
- **DDC Book**: Chapter 5.1 - Uberization and Open Data
- **Digital Maturity Models**: Various industry frameworks (CMMI, Gartner)
- **Website**: https://datadrivenconstruction.io
