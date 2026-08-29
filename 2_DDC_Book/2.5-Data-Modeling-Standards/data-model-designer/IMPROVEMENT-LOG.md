# Data Model Designer - Improvement Log

## Diagnosis

### Root Causes (from v0.2.0 eval, score: 6.5/10)
1. **Non-discriminating assertions**: All 8 pass both with/without. Tests check schema correctness — baseline excels at this.
2. **Huge overhead**: +83% time, +113% tokens for zero delta.
3. **Skill is a Python library, not behavioral guidance**: The entire SKILL.md is a Python class definition (ConstructionDataModel). The agent reads it and tries to use the class, generating massive output with ER diagrams, JSON schemas, and validation reports — none of which are tested by assertions.
4. **Construction-domain focus is irrelevant**: The eval tests generic data modeling (project management, equipment maintenance). The construction-specific Python code doesn't help.

### What the base model already does well
- Designs proper schemas with PKs, FKs, valid DDL
- Models entities and relationships correctly
- Actually produces MORE production-ready SQL (CHECK constraints, indexes, enums) without the skill

### What the skill COULD add but doesn't enforce
- Mandatory ER diagrams (Mermaid format)
- Requirements analysis before coding
- Validation checklists
- Standard SQL style conventions
- Sample queries to prove the model works

## Changes Made

### Removed
- Entire Python class implementation (ConstructionDataModel, Field, Entity, etc.)
- Construction-specific entity templates
- JSON Schema generation
- All Python code examples

### Added
- **Mandatory output sections**: Requirements Summary, ER Diagram, SQL DDL, Validation Checklist, Sample Queries
- **SQL style rules**: naming conventions, auto-increment PKs, NOT NULL defaults, mandatory timestamps
- **Validation checklist**: explicit verification steps the model must perform
- **"What NOT to Do" section**: explicit prohibitions

### Rationale
The original skill was essentially a Python library pasted into a SKILL.md. The model would read it and try to use the classes, burning tokens without producing better output. The improved version is a **design methodology** that mandates specific output sections the baseline doesn't produce by default.

## Expected Impact
- ER diagrams: baseline sometimes includes, skill always does → 25% delta minimum
- Validation checklist: baseline never includes → 50% delta
- Requirements summary: baseline never includes → 50% delta
- Reduced token overhead: no Python code to process
- More production-ready SQL from explicit style rules
