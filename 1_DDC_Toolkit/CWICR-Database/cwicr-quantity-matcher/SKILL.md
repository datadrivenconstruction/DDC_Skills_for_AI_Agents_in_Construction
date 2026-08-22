---
name: "cwicr-quantity-matcher"
description: "Match BIM quantities to CWICR work items. Map element categories to cost codes, validate quantities, and generate cost-linked QTOs."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🗄️", "os": ["win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# CWICR Quantity Matcher

## Business Case

### Problem Statement
BIM exports contain quantities but:
- Element categories don't match cost codes
- Manual mapping is error-prone
- Different naming conventions
- Need consistent code assignment

### Solution
Intelligent matching of BIM element quantities to CWICR work items using category mapping, semantic matching, and rule-based assignment.

### Business Value
- **Automation** - Reduce manual mapping effort
- **Consistency** - Standard code assignment
- **Accuracy** - Validated quantity linkage
- **Integration** - BIM-to-cost data flow

## Technical Implementation

```python
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
from difflib import SequenceMatcher


class MatchMethod(Enum):
    """Methods for matching BIM elements to work items."""
    EXACT = "exact"
    CATEGORY = "category"
    SEMANTIC = "semantic"
    RULE_BASED = "rule_based"
    MANUAL = "manual"


class MatchConfidence(Enum):
    """Confidence level of match."""
    HIGH = "high"       # >90% confidence
    MEDIUM = "medium"   # 70-90%
    LOW = "low"         # 50-70%
    MANUAL = "manual"   # <50% - needs review


@dataclass
class QuantityMatch:
    """Single quantity match result."""
    bim_element_id: str
    bim_category: str
    bim_description: str
    bim_quantity: float
    bim_unit: str
    matched_work_item: str
    work_item_description: str
    work_item_unit: str
    match_method: MatchMethod
    confidence: MatchConfidence
    confidence_score: float
    unit_conversion_factor: float = 1.0


@dataclass
class MatchingResult:
    """Complete matching result."""
    total_elements: int
    matched: int
    unmatched: int
    high_confidence: int
    needs_review: int
    matches: List[QuantityMatch]
    unmatched_elements: List[Dict[str, Any]]


# Category to work item mapping rules
CATEGORY_MAPPING = {
    # Revit categories to CWICR prefixes
    'walls': ['WALL', 'MSNR', 'PART'],
    'floors': ['CONC', 'FLOOR', 'SLAB'],
    'columns': ['CONC', 'STRL', 'COLM'],
    'beams': ['CONC', 'STRL', 'BEAM'],
    'foundations': ['CONC', 'FNDN', 'EXCV'],
    'roofs': ['ROOF', 'INSUL'],
    'doors': ['DOOR', 'CARP'],
    'windows': ['WIND', 'GLAZ'],
    'stairs': ['STAIR', 'CONC'],
    'railings': ['RAIL', 'METL'],
    'ceilings': ['CEIL', 'FINI'],
    'structural framing': ['STRL', 'STEE'],
    'structural columns': ['STRL', 'COLM'],
    'pipes': ['PLMB', 'PIPE'],
    'ducts': ['HVAC', 'DUCT'],
    'conduits': ['ELEC', 'COND'],
    'cable trays': ['ELEC', 'CABL'],
    'concrete': ['CONC'],
    'rebar': ['REBAR', 'RENF'],
    'formwork': ['FORM', 'CONC'],
}

# Unit conversion mapping
UNIT_CONVERSIONS = {
    ('sf', 'm2'): 0.092903,
    ('m2', 'sf'): 10.7639,
    ('cy', 'm3'): 0.764555,
    ('m3', 'cy'): 1.30795,
    ('lf', 'm'): 0.3048,
    ('m', 'lf'): 3.28084,
    ('lb', 'kg'): 0.453592,
    ('kg', 'lb'): 2.20462,
}


class CWICRQuantityMatcher:
    """Match BIM quantities to CWICR work items."""

    def __init__(self, cwicr_data: pd.DataFrame):
        self.work_items = cwicr_data
        self._index_data()
        self._build_search_index()

    def _index_data(self):
        """Index work items."""
        if 'work_item_code' in self.work_items.columns:
            self._code_index = self.work_items.set_index('work_item_code')
        else:
            self._code_index = None

    def _build_search_index(self):
        """Build search index for semantic matching."""
        self._search_index = {}

        if 'description' in self.work_items.columns:
            for _, row in self.work_items.iterrows():
                code = row.get('work_item_code', '')
                desc = str(row.get('description', '')).lower()

                # Index by keywords
                words = re.findall(r'\w+', desc)
                for word in words:
                    if len(word) > 3:
                        if word not in self._search_index:
                            self._search_index[word] = []
                        self._search_index[word].append(code)

    def _get_category_codes(self, category: str) -> List[str]:
        """Get potential work item prefixes for BIM category."""
        cat_lower = category.lower().strip()

        for key, prefixes in CATEGORY_MAPPING.items():
            if key in cat_lower:
                return prefixes

        return []

    def _semantic_match(self, description: str, category: str) -> List[Tuple[str, float]]:
        """Find work items using semantic matching."""
        desc_lower = description.lower()
        words = re.findall(r'\w+', desc_lower)

        # Find candidate codes
        candidates = {}
        for word in words:
            if word in self._search_index:
                for code in self._search_index[word]:
                    if code not in candidates:
                        candidates[code] = 0
                    candidates[code] += 1

        # Score candidates
        scored = []
        for code, count in candidates.items():
            if self._code_index is not None and code in self._code_index.index:
                item_desc = str(self._code_index.loc[code].get('description', ''))
                similarity = SequenceMatcher(None, desc_lower, item_desc.lower()).ratio()
                score = (count * 0.4) + (similarity * 0.6)
                scored.append((code, score))

        return sorted(scored, key=lambda x: x[1], reverse=True)[:5]

    def _get_confidence(self, score: float) -> MatchConfidence:
        """Determine confidence level from score."""
        if score >= 0.9:
            return MatchConfidence.HIGH
        elif score >= 0.7:
            return MatchConfidence.MEDIUM
        elif score >= 0.5:
            return MatchConfidence.LOW
        else:
            return MatchConfidence.MANUAL

    def _get_unit_conversion(self, from_unit: str, to_unit: str) -> float:
        """Get unit conversion factor."""
        from_norm = from_unit.lower().strip()
        to_norm = to_unit.lower().strip()

        if from_norm == to_norm:
            return 1.0

        return UNIT_CONVERSIONS.get((from_norm, to_norm), 1.0)

    def match_element(self,
                      element: Dict[str, Any],
                      element_id_col: str = 'ElementId',
                      category_col: str = 'Category',
                      description_col: str = 'Description',
                      quantity_col: str = 'Quantity',
                      unit_col: str = 'Unit') -> Optional[QuantityMatch]:
        """Match single BIM element to work item."""

        element_id = str(element.get(element_id_col, ''))
        category = str(element.get(category_col, ''))
        description = str(element.get(description_col, ''))
        quantity = float(element.get(quantity_col, 0) or 0)
        unit = str(element.get(unit_col, ''))

        # Try category-based matching first
        category_prefixes = self._get_category_codes(category)

        best_match = None
        best_score = 0
        match_method = MatchMethod.CATEGORY

        if category_prefixes:
            # Filter work items by prefix
            for prefix in category_prefixes:
                matches = self.work_items[
                    self.work_items['work_item_code'].str.startswith(prefix)
                ]

                for _, item in matches.iterrows():
                    item_desc = str(item.get('description', ''))
                    similarity = SequenceMatcher(None, description.lower(), item_desc.lower()).ratio()

                    if similarity > best_score:
                        best_score = similarity
                        best_match = item

        # If no good match, try semantic matching
        if best_score < 0.5:
            semantic_matches = self._semantic_match(description, category)
            if semantic_matches:
                top_code, top_score = semantic_matches[0]
                if top_score > best_score:
                    best_match = self._code_index.loc[top_code]
                    best_score = top_score
                    match_method = MatchMethod.SEMANTIC

        if best_match is None or best_score < 0.3:
            return None

        # Get unit conversion
        work_item_unit = str(best_match.get('unit', ''))
        conversion = self._get_unit_conversion(unit, work_item_unit)

        return QuantityMatch(
            bim_element_id=element_id,
            bim_category=category,
            bim_description=description,
            bim_quantity=quantity,
            bim_unit=unit,
            matched_work_item=str(best_match.get('work_item_code', best_match.name)),
            work_item_description=str(best_match.get('description', '')),
            work_item_unit=work_item_unit,
            match_method=match_method,
            confidence=self._get_confidence(best_score),
            confidence_score=round(best_score, 2),
            unit_conversion_factor=conversion
        )

    def match_quantities(self,
                         bim_data: pd.DataFrame,
                         element_id_col: str = 'ElementId',
                         category_col: str = 'Category',
                         description_col: str = 'Description',
                         quantity_col: str = 'Quantity',
                         unit_col: str = 'Unit') -> MatchingResult:
        """Match all BIM quantities to work items."""

        matches = []
        unmatched = []

        for _, row in bim_data.iterrows():
            element = row.to_dict()

            match = self.match_element(
                element,
                element_id_col,
                category_col,
                description_col,
                quantity_col,
                unit_col
            )

            if match:
                matches.append(match)
            else:
                unmatched.append(element)

        return MatchingResult(
            total_elements=len(bim_data),
            matched=len(matches),
            unmatched=len(unmatched),
            high_confidence=len([m for m in matches if m.confidence == MatchConfidence.HIGH]),
            needs_review=len([m for m in matches if m.confidence == MatchConfidence.MANUAL]),
            matches=matches,
            unmatched_elements=unmatched
        )

    def apply_custom_mapping(self,
                              result: MatchingResult,
                              mapping: Dict[str, str]) -> MatchingResult:
        """Apply custom category to work item mapping."""

        updated_matches = []

        for match in result.matches:
            if match.bim_category in mapping:
                # Override with custom mapping
                code = mapping[match.bim_category]
                if self._code_index is not None and code in self._code_index.index:
                    item = self._code_index.loc[code]
                    match.matched_work_item = code
                    match.work_item_description = str(item.get('description', ''))
                    match.work_item_unit = str(item.get('unit', ''))
                    match.match_method = MatchMethod.RULE_BASED
                    match.confidence = MatchConfidence.HIGH
                    match.confidence_score = 1.0

            updated_matches.append(match)

        result.matches = updated_matches
        return result

    def export_matches(self,
                        result: MatchingResult,
                        output_path: str) -> str:
        """Export matching results to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary
            summary_df = pd.DataFrame([{
                'Total Elements': result.total_elements,
                'Matched': result.matched,
                'Unmatched': result.unmatched,
                'High Confidence': result.high_confidence,
                'Needs Review': result.needs_review,
                'Match Rate %': round(result.matched / result.total_elements * 100, 1) if result.total_elements > 0 else 0
            }])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Matches
            matches_df = pd.DataFrame([
                {
                    'BIM Element ID': m.bim_element_id,
                    'BIM Category': m.bim_category,
                    'BIM Description': m.bim_description,
                    'BIM Quantity': m.bim_quantity,
                    'BIM Unit': m.bim_unit,
                    'Work Item Code': m.matched_work_item,
                    'Work Item Description': m.work_item_description,
                    'Work Item Unit': m.work_item_unit,
                    'Converted Quantity': m.bim_quantity * m.unit_conversion_factor,
                    'Match Method': m.match_method.value,
                    'Confidence': m.confidence.value,
                    'Score': m.confidence_score
                }
                for m in result.matches
            ])
            matches_df.to_excel(writer, sheet_name='Matches', index=False)

            # Needs Review
            review_df = matches_df[matches_df['Confidence'].isin(['low', 'manual'])]
            review_df.to_excel(writer, sheet_name='Needs Review', index=False)

            # Unmatched
            unmatched_df = pd.DataFrame(result.unmatched_elements)
            unmatched_df.to_excel(writer, sheet_name='Unmatched', index=False)

        return output_path

    def generate_cost_linked_qto(self,
                                   result: MatchingResult) -> pd.DataFrame:
        """Generate cost-linked QTO from matches."""

        data = []
        for match in result.matches:
            if self._code_index is not None and match.matched_work_item in self._code_index.index:
                item = self._code_index.loc[match.matched_work_item]

                converted_qty = match.bim_quantity * match.unit_conversion_factor

                labor = float(item.get('labor_cost', 0) or 0)
                material = float(item.get('material_cost', 0) or 0)
                equipment = float(item.get('equipment_cost', 0) or 0)
                unit_cost = labor + material + equipment

                data.append({
                    'Work Item Code': match.matched_work_item,
                    'Description': match.work_item_description,
                    'Unit': match.work_item_unit,
                    'Quantity': round(converted_qty, 2),
                    'Unit Cost': round(unit_cost, 2),
                    'Total Cost': round(converted_qty * unit_cost, 2),
                    'BIM Elements': 1,
                    'Confidence': match.confidence.value
                })

        df = pd.DataFrame(data)

        # Aggregate by work item
        if not df.empty:
            aggregated = df.groupby(['Work Item Code', 'Description', 'Unit']).agg({
                'Quantity': 'sum',
                'Unit Cost': 'first',
                'BIM Elements': 'sum'
            }).reset_index()
            aggregated['Total Cost'] = aggregated['Quantity'] * aggregated['Unit Cost']
            return aggregated

        return df
```

## Quick Start

```python
# Load CWICR data
cwicr = pd.read_parquet("TR_workitems_costs_resources_DDC_CWICR.parquet")

# Initialize matcher
matcher = CWICRQuantityMatcher(cwicr)

# Load BIM quantities
bim_qto = pd.read_excel("revit_quantities.xlsx")

# Match quantities
result = matcher.match_quantities(bim_qto)

print(f"Matched: {result.matched}/{result.total_elements}")
print(f"High Confidence: {result.high_confidence}")
print(f"Needs Review: {result.needs_review}")
```

## Common Use Cases

### 1. Generate Cost-Linked QTO
```python
qto_with_costs = matcher.generate_cost_linked_qto(result)
print(f"Total Cost: ${qto_with_costs['Total Cost'].sum():,.2f}")
```

### 2. Custom Mapping Rules
```python
custom_mapping = {
    'Walls': 'WALL-001',
    'Floors': 'CONC-002',
    'Structural Columns': 'STRL-003'
}
result = matcher.apply_custom_mapping(result, custom_mapping)
```

### 3. Export Results
```python
matcher.export_matches(result, "quantity_matching.xlsx")
```

## Resources
- **GitHub**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
- **DDC Book**: Chapter 2.3 - BIM-to-Cost Integration
