---
name: "few-shot-examples"
description: "Curated few-shot examples for construction AI tasks including CSI MasterFormat classification, RFI categorization, cost validation, schedule analysis, and BIM data extraction. Use when building prompts for construction document classification, cost estimate review, schedule validation, or BIM property interpretation."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "💡", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# Few-Shot Examples for Construction AI

Curated few-shot example sets for construction industry AI tasks. Provides domain-specific context for LLM prompts covering CSI classification, RFI routing, cost validation, schedule review, and BIM data extraction.

## Workflow

1. **Select** an example set matching your task type (classification, analysis, extraction)
2. **Filter** examples by difficulty or tags as needed
3. **Format** examples into your prompt using `format_for_prompt()`
4. **Validate** LLM output against expected formats from the examples
5. **Extend** the library with project-specific examples as edge cases arise

## Quick Start

```python
from few_shot_examples import ConstructionExampleLibrary

library = ConstructionExampleLibrary()

# Get CSI classification examples
csi_examples = library.get("csi_classification")
examples_text = csi_examples.format_for_prompt(n=3)

# Build prompt with few-shot context
prompt = f"""Classify the following line items to CSI MasterFormat.

{examples_text}

Now classify these items:
1. Aluminum storefront framing
2. Acoustic ceiling tiles
3. Elevator cab finishes
"""

# Filter by difficulty or get random variety
easy_examples = csi_examples.get_examples(n=2, difficulty="easy")
random_examples = csi_examples.get_random_examples(n=3)
```

## Available Example Sets

### CSI MasterFormat Classification (`csi_classification`)
Classify construction line items to CSI divisions and sections.

| Input Example | Division | Section |
|---------------|----------|---------|
| "4000 PSI structural concrete for foundations" | 03 | 03 30 00 Cast-in-Place Concrete |
| "Grade 60 #5 reinforcing steel" | 03 | 03 20 00 Concrete Reinforcing |
| "8\" CMU block wall with vertical rebar" | 04 | 04 22 00 Concrete Unit Masonry |
| "W12x26 structural steel beams" | 05 | 05 12 00 Structural Steel Framing |
| "Fire sprinkler system - ordinary hazard" | 21 | 21 13 00 Fire-Suppression Sprinkler |
| "277/480V electrical distribution panel" | 26 | 26 24 00 Switchboards/Panelboards |
| "Site excavation and grading - 5000 CY" | 31 | 31 20 00 Earth Moving |

15 examples total covering Divisions 03-33.

### RFI Classification (`rfi_classification`)
Classify RFI type, urgency, and routing.

| Scenario | Type | Urgency | Routing |
|----------|------|---------|---------|
| Drawing conflict between disciplines | conflict_clarification | high | architect |
| Material substitution request | substitution_request | low | architect |
| Unforeseen rock during excavation | field_condition | critical | structural_engineer |
| Missing fire rating information | clarification | medium | architect |
| MEP penetration through structure | coordination | high | structural_engineer |

### Cost Validation (`cost_analysis`)
Validate unit costs against typical ranges.

| Item | Unit Cost | Assessment | Action |
|------|-----------|------------|--------|
| Concrete, NYC | $850/CY | High (+21%) | Review labor/access assumptions |
| Steel erection, Houston | $1200/TON | Reasonable | No action |
| Gypsum partition, Phoenix | $3.50/SF | Low (-42%) | Verify scope includes framing/finish |

### Schedule Analysis (`schedule_analysis`)
Validate activity durations and logic.

| Activity | Duration | Assessment | Note |
|----------|----------|------------|------|
| Foundation pour, 2500 CY | 45 days | Long | Typical: 17-25 days at 100-150 CY/day |
| Steel erection, 500 tons | 60 days | Reasonable | 8-12 tons/day/crew |
| Foundation -> Steel, -5 day lag | N/A | Aggressive | Negative lag risks structural integrity |

### BIM Data Extraction (`bim_extraction`)
Extract and interpret BIM properties for construction quantities.

| Element | Key Extractions |
|---------|----------------|
| IfcWall (interior partition) | Fire rating, thickness (mm->in), gross/net area (m2->SF) |
| IfcDoor (D-01) | Size conversion (metric->imperial), ADA compliance check |
| IfcSpace (conference room) | Occupancy validation against IBC code requirements |

## Adding Custom Examples

```python
from few_shot_examples import ExampleSet, FewShotExample

my_examples = ExampleSet(
    name="my_project_classification",
    description="Project-specific classification examples",
    task_type="classification",
    examples=[
        FewShotExample(
            input="Your specific input",
            output="Expected output",
            explanation="Why this classification",
            tags=["custom"],
            difficulty="medium"
        )
    ]
)

library.register(my_examples)
```

## Best Practices

1. **Use 3-5 examples** per prompt — enough for pattern recognition without token waste
2. **Include edge cases** — ambiguous items (e.g., rebar in Division 03, not 05) teach important distinctions
3. **Add explanations** for complex examples so the LLM learns the reasoning
4. **Mix difficulties** — easy examples establish the pattern, hard ones handle ambiguity
5. **Update regularly** — add new examples when the model misclassifies in production

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `ConstructionExampleLibrary` | Registry of all example sets |
| `ExampleSet` | Named collection of examples for a task type |
| `FewShotExample` | Single input/output pair with tags and difficulty |
| `format_for_prompt(n)` | Format n examples as prompt text |
| `get_examples(n, difficulty)` | Filter by difficulty level |
| `get_random_examples(n)` | Random selection for variety |

## Resources

- **Few-Shot Learning**: https://www.promptingguide.ai/techniques/fewshot
- **CSI MasterFormat**: Complete division listings
- **Construction Terminology**: Industry glossaries and standards
- **Website**: https://datadrivenconstruction.io
