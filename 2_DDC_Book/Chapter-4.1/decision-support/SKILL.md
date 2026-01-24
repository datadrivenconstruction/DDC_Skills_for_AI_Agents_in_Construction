---
name: decision-support
description: "Provide data-driven decision support for construction. Analyze multiple factors and recommend optimal project decisions."
---

# Decision Support System

## Business Case

### Problem Statement
Construction decision-making challenges:
- Multiple conflicting criteria
- Risk and uncertainty
- Time pressure for decisions
- Lack of structured analysis

### Solution
Multi-criteria decision support system for construction projects with weighted scoring, risk analysis, and scenario comparison.

## Technical Implementation

```python
import pandas as pd
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
import math


class DecisionType(Enum):
    VENDOR_SELECTION = "vendor_selection"
    METHOD_SELECTION = "method_selection"
    SCHEDULE_OPTION = "schedule_option"
    DESIGN_ALTERNATIVE = "design_alternative"
    RISK_RESPONSE = "risk_response"
    RESOURCE_ALLOCATION = "resource_allocation"


class CriterionType(Enum):
    COST = "cost"
    TIME = "time"
    QUALITY = "quality"
    SAFETY = "safety"
    RISK = "risk"
    SUSTAINABILITY = "sustainability"


@dataclass
class Criterion:
    criterion_id: str
    name: str
    criterion_type: CriterionType
    weight: float  # 0-1
    higher_is_better: bool = True
    unit: str = ""


@dataclass
class Alternative:
    alternative_id: str
    name: str
    description: str
    scores: Dict[str, float] = field(default_factory=dict)
    risks: List[str] = field(default_factory=list)


@dataclass
class DecisionResult:
    alternative_id: str
    weighted_score: float
    rank: int
    strengths: List[str]
    weaknesses: List[str]


class DecisionSupportSystem:
    """Multi-criteria decision support for construction projects."""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.criteria: Dict[str, Criterion] = {}
        self.alternatives: Dict[str, Alternative] = {}
        self.decision_type: DecisionType = DecisionType.METHOD_SELECTION

    def set_decision_type(self, decision_type: DecisionType):
        """Set the type of decision being made."""
        self.decision_type = decision_type

    def add_criterion(self, criterion: Criterion):
        """Add evaluation criterion."""
        self.criteria[criterion.criterion_id] = criterion

    def add_standard_criteria(self, decision_type: DecisionType = None):
        """Add standard criteria based on decision type."""

        dt = decision_type or self.decision_type

        if dt == DecisionType.VENDOR_SELECTION:
            criteria = [
                Criterion("price", "Price", CriterionType.COST, 0.30, False, "$"),
                Criterion("quality", "Quality Rating", CriterionType.QUALITY, 0.25, True, "1-10"),
                Criterion("delivery", "Delivery Time", CriterionType.TIME, 0.20, False, "days"),
                Criterion("experience", "Experience", CriterionType.QUALITY, 0.15, True, "years"),
                Criterion("safety", "Safety Record", CriterionType.SAFETY, 0.10, True, "score"),
            ]
        elif dt == DecisionType.METHOD_SELECTION:
            criteria = [
                Criterion("cost", "Total Cost", CriterionType.COST, 0.25, False, "$"),
                Criterion("duration", "Duration", CriterionType.TIME, 0.25, False, "days"),
                Criterion("quality", "Quality", CriterionType.QUALITY, 0.20, True, "score"),
                Criterion("risk", "Risk Level", CriterionType.RISK, 0.15, False, "1-5"),
                Criterion("sustainability", "Sustainability", CriterionType.SUSTAINABILITY, 0.15, True, "score"),
            ]
        elif dt == DecisionType.RISK_RESPONSE:
            criteria = [
                Criterion("effectiveness", "Effectiveness", CriterionType.QUALITY, 0.35, True, "%"),
                Criterion("cost", "Implementation Cost", CriterionType.COST, 0.25, False, "$"),
                Criterion("time", "Implementation Time", CriterionType.TIME, 0.20, False, "days"),
                Criterion("feasibility", "Feasibility", CriterionType.QUALITY, 0.20, True, "1-10"),
            ]
        else:
            criteria = [
                Criterion("cost", "Cost", CriterionType.COST, 0.30, False, "$"),
                Criterion("time", "Time", CriterionType.TIME, 0.25, False, "days"),
                Criterion("quality", "Quality", CriterionType.QUALITY, 0.25, True, "score"),
                Criterion("risk", "Risk", CriterionType.RISK, 0.20, False, "score"),
            ]

        for c in criteria:
            self.add_criterion(c)

    def add_alternative(self, alternative: Alternative):
        """Add decision alternative."""
        self.alternatives[alternative.alternative_id] = alternative

    def normalize_scores(self) -> Dict[str, Dict[str, float]]:
        """Normalize scores to 0-1 scale."""

        normalized = {}

        for criterion_id, criterion in self.criteria.items():
            values = [alt.scores.get(criterion_id, 0) for alt in self.alternatives.values()]

            if not values or max(values) == min(values):
                for alt_id in self.alternatives:
                    if alt_id not in normalized:
                        normalized[alt_id] = {}
                    normalized[alt_id][criterion_id] = 0.5
                continue

            min_val, max_val = min(values), max(values)
            range_val = max_val - min_val

            for alt_id, alt in self.alternatives.items():
                if alt_id not in normalized:
                    normalized[alt_id] = {}

                raw_score = alt.scores.get(criterion_id, 0)

                # Normalize
                norm_score = (raw_score - min_val) / range_val if range_val > 0 else 0.5

                # Invert if lower is better
                if not criterion.higher_is_better:
                    norm_score = 1 - norm_score

                normalized[alt_id][criterion_id] = round(norm_score, 4)

        return normalized

    def calculate_weighted_scores(self) -> Dict[str, float]:
        """Calculate weighted scores for all alternatives."""

        normalized = self.normalize_scores()
        weighted = {}

        for alt_id, scores in normalized.items():
            total = 0
            for criterion_id, norm_score in scores.items():
                weight = self.criteria[criterion_id].weight
                total += norm_score * weight
            weighted[alt_id] = round(total, 4)

        return weighted

    def analyze_alternatives(self) -> List[DecisionResult]:
        """Analyze and rank all alternatives."""

        weighted_scores = self.calculate_weighted_scores()
        normalized = self.normalize_scores()

        # Rank alternatives
        ranked = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)

        results = []
        for rank, (alt_id, score) in enumerate(ranked, 1):
            alt = self.alternatives[alt_id]

            # Identify strengths (top 2 criteria)
            strengths = []
            weaknesses = []

            alt_scores = [(cid, normalized[alt_id][cid]) for cid in self.criteria]
            alt_scores_sorted = sorted(alt_scores, key=lambda x: x[1], reverse=True)

            for cid, nscore in alt_scores_sorted[:2]:
                if nscore >= 0.6:
                    strengths.append(f"{self.criteria[cid].name}: {nscore:.2f}")

            for cid, nscore in alt_scores_sorted[-2:]:
                if nscore <= 0.4:
                    weaknesses.append(f"{self.criteria[cid].name}: {nscore:.2f}")

            results.append(DecisionResult(
                alternative_id=alt_id,
                weighted_score=score,
                rank=rank,
                strengths=strengths,
                weaknesses=weaknesses
            ))

        return results

    def get_recommendation(self) -> Dict[str, Any]:
        """Get decision recommendation."""

        results = self.analyze_alternatives()

        if not results:
            return {"error": "No alternatives to analyze"}

        best = results[0]
        best_alt = self.alternatives[best.alternative_id]

        # Calculate confidence
        if len(results) > 1:
            score_gap = best.weighted_score - results[1].weighted_score
            confidence = min(100, int(score_gap * 200 + 50))
        else:
            confidence = 100

        return {
            'project': self.project_name,
            'decision_type': self.decision_type.value,
            'recommendation': {
                'alternative': best_alt.name,
                'alternative_id': best.alternative_id,
                'score': best.weighted_score,
                'confidence': confidence,
                'strengths': best.strengths,
                'weaknesses': best.weaknesses
            },
            'all_rankings': [
                {
                    'rank': r.rank,
                    'alternative': self.alternatives[r.alternative_id].name,
                    'score': r.weighted_score
                }
                for r in results
            ],
            'criteria_weights': {
                c.name: c.weight for c in self.criteria.values()
            }
        }

    def sensitivity_analysis(self, criterion_id: str,
                             weight_range: tuple = (0.0, 0.5, 0.1)) -> Dict[str, Any]:
        """Perform sensitivity analysis on criterion weight."""

        original_weight = self.criteria[criterion_id].weight
        results = []

        start, end, step = weight_range
        weight = start
        while weight <= end:
            # Adjust weight
            self.criteria[criterion_id].weight = weight

            # Recalculate
            scores = self.calculate_weighted_scores()
            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

            results.append({
                'weight': round(weight, 2),
                'rankings': [
                    {'alternative': self.alternatives[alt_id].name, 'score': score}
                    for alt_id, score in ranked
                ]
            })

            weight += step

        # Restore original
        self.criteria[criterion_id].weight = original_weight

        return {
            'criterion': self.criteria[criterion_id].name,
            'original_weight': original_weight,
            'analysis': results
        }

    def export_to_excel(self, output_path: str) -> str:
        """Export decision analysis to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Recommendation
            rec = self.get_recommendation()
            rec_df = pd.DataFrame([{
                'Project': rec['project'],
                'Decision Type': rec['decision_type'],
                'Recommended Alternative': rec['recommendation']['alternative'],
                'Score': rec['recommendation']['score'],
                'Confidence %': rec['recommendation']['confidence']
            }])
            rec_df.to_excel(writer, sheet_name='Recommendation', index=False)

            # All rankings
            rankings_df = pd.DataFrame(rec['all_rankings'])
            rankings_df.to_excel(writer, sheet_name='Rankings', index=False)

            # Detailed scores
            normalized = self.normalize_scores()
            details = []
            for alt_id, alt in self.alternatives.items():
                row = {'Alternative': alt.name}
                for cid, criterion in self.criteria.items():
                    row[f"{criterion.name} (Raw)"] = alt.scores.get(cid, 0)
                    row[f"{criterion.name} (Norm)"] = normalized[alt_id].get(cid, 0)
                details.append(row)
            details_df = pd.DataFrame(details)
            details_df.to_excel(writer, sheet_name='Detailed Scores', index=False)

            # Criteria
            criteria_df = pd.DataFrame([{
                'Criterion': c.name,
                'Type': c.criterion_type.value,
                'Weight': c.weight,
                'Higher is Better': c.higher_is_better,
                'Unit': c.unit
            } for c in self.criteria.values()])
            criteria_df.to_excel(writer, sheet_name='Criteria', index=False)

        return output_path
```

## Quick Start

```python
# Create decision support system
dss = DecisionSupportSystem("Office Building A")
dss.set_decision_type(DecisionType.VENDOR_SELECTION)

# Add standard criteria
dss.add_standard_criteria()

# Add alternatives
dss.add_alternative(Alternative(
    "V1", "Contractor A", "Large regional contractor",
    scores={"price": 500000, "quality": 8, "delivery": 90, "experience": 15, "safety": 9}
))

dss.add_alternative(Alternative(
    "V2", "Contractor B", "Local contractor",
    scores={"price": 450000, "quality": 7, "delivery": 120, "experience": 8, "safety": 8}
))

dss.add_alternative(Alternative(
    "V3", "Contractor C", "National contractor",
    scores={"price": 600000, "quality": 9, "delivery": 75, "experience": 25, "safety": 10}
))

# Get recommendation
recommendation = dss.get_recommendation()
print(f"Recommended: {recommendation['recommendation']['alternative']}")
print(f"Confidence: {recommendation['recommendation']['confidence']}%")
```

## Common Use Cases

### 1. Method Selection
```python
dss = DecisionSupportSystem("Foundation Work")
dss.set_decision_type(DecisionType.METHOD_SELECTION)
dss.add_standard_criteria()

dss.add_alternative(Alternative("M1", "Cast-in-place", "Traditional method",
    scores={"cost": 200000, "duration": 45, "quality": 9, "risk": 2, "sustainability": 6}))
dss.add_alternative(Alternative("M2", "Precast", "Prefabricated elements",
    scores={"cost": 250000, "duration": 30, "quality": 8, "risk": 3, "sustainability": 8}))
```

### 2. Sensitivity Analysis
```python
sensitivity = dss.sensitivity_analysis("cost", (0.1, 0.5, 0.1))
for result in sensitivity['analysis']:
    print(f"Weight {result['weight']}: Top choice = {result['rankings'][0]['alternative']}")
```

### 3. Export Analysis
```python
dss.export_to_excel("decision_analysis.xlsx")
```

## Resources
- **DDC Book**: Chapter 4.1 - Data Analytics and Decision Making
- **Website**: https://datadrivenconstruction.io
