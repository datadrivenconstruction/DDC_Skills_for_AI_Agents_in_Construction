# DDC_Curated

**External skills curated for construction industry applications.**

These skills are sourced from Anthropic Official Skills and Community contributions, selected and adapted for construction use cases.

## Why Curated?

The construction industry has unique requirements:
- Heavy document workflows (RFIs, submittals, contracts)
- Complex spreadsheet calculations (estimates, schedules)
- Quality assurance and validation needs
- Multi-stakeholder collaboration
- Data security and compliance

These skills address those needs with proven, general-purpose tools.

## Skill Categories

### Document-Generation
Skills for creating and processing construction documents.

| Skill | Original Source | Construction Use |
|-------|-----------------|-----------------|
| [pdf-construction](Document-Generation/pdf-construction/) | Anthropic PDF | RFI processing, submittal packages |
| [xlsx-construction](Document-Generation/xlsx-construction/) | Anthropic XLSX | Estimates, schedules, tracking |

### Data-Processing
Skills for handling construction data.

| Skill | Original Source | Construction Use |
|-------|-----------------|-----------------|
| web-artifacts | Anthropic Web Artifacts | Project dashboards |
| data-analysis | Community | BIM data analysis |

### Quality-Assurance
Skills for construction quality control and security.

| Skill | Original Source | Construction Use |
|-------|-----------------|-----------------|
| [security-review-construction](Quality-Assurance/security-review-construction/) | everything-claude-code | Data security in construction systems |
| [verification-loop-construction](Quality-Assurance/verification-loop-construction/) | everything-claude-code | Deliverable validation for estimates, schedules |
| [continuous-learning](Quality-Assurance/continuous-learning/) | everything-claude-code | Pattern extraction from sessions |

## New Skills Added (January 2026)

### security-review-construction
Comprehensive security checklist adapted for construction software systems:
- Financial data protection (estimates, margins)
- BIM/CAD data security
- Subcontractor/vendor data handling
- Field data collection security
- CWICR database access control
- Integration security (Procore, PlanGrid)

### verification-loop-construction
Systematic verification for construction automation outputs:
- Data integrity checks
- Business logic validation (estimates, schedules)
- Standards compliance (CSI, CWICR)
- Output quality verification
- Cross-reference validation

### continuous-learning
Automatic extraction of patterns and best practices:
- Cost estimation patterns
- BIM data processing patterns
- Integration patterns
- Error resolution patterns
- Knowledge base building

## Source Repositories

### Official Anthropic Skills
- https://github.com/anthropics/skills

### Community Skills
- https://github.com/affaan-m/everything-claude-code
- https://github.com/anthropics/awesome-claude-code
- https://github.com/travisvn/awesome-claude-skills
- https://github.com/obra/superpowers

## Adaptation for Construction

Each curated skill has been reviewed for:
1. **Relevance** - Applicable to construction workflows
2. **Integration** - Compatible with DDC tools and data
3. **Customization** - Construction-specific examples added
4. **Documentation** - Clear usage instructions

## Usage

These skills can be used standalone or combined with DDC_Toolkit skills for comprehensive construction automation pipelines.

Example workflow:
```
DDC_Toolkit/CAD-Converters → DDC_Curated/xlsx-construction → DDC_Insights/n8n-cost-estimation
                           ↓
                DDC_Curated/verification-loop-construction
                           ↓
                   Validated Output
```

## Integration with Other DDC Categories

| DDC Category | Integration Point |
|--------------|-------------------|
| DDC_Toolkit | CWICR search results → security-review for data protection |
| DDC_Methodology | Estimate generation → verification-loop for validation |
| DDC_Insights | n8n workflows → continuous-learning for pattern capture |

## License

Varies by original source. See individual skill files for license information.
