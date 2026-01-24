---
name: standards-compliance-checker
description: "Check data compliance with construction standards. Validate data against ISO 19650, IFC, COBie, UniFormat standards."
---

# Standards Compliance Checker

## Business Case

### Problem Statement
Construction data compliance challenges:
- Multiple standards to meet
- Complex validation rules
- Inconsistent implementations
- Manual checking is error-prone

### Solution
Automated compliance checking against major construction data standards including ISO 19650, IFC, COBie, and UniFormat.

## Technical Implementation

```python
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import re


class Standard(Enum):
    ISO_19650 = "iso_19650"
    IFC = "ifc"
    COBIE = "cobie"
    UNIFORMAT = "uniformat"
    OMNICLASS = "omniclass"
    MASTERFORMAT = "masterformat"


class ComplianceLevel(Enum):
    COMPLIANT = "compliant"
    MINOR_ISSUES = "minor_issues"
    MAJOR_ISSUES = "major_issues"
    NON_COMPLIANT = "non_compliant"


@dataclass
class ComplianceIssue:
    rule_id: str
    rule_name: str
    severity: str  # error, warning, info
    message: str
    field: str = ""
    value: Any = None


@dataclass
class ComplianceReport:
    standard: Standard
    total_rules: int
    passed: int
    failed: int
    warnings: int
    compliance_level: ComplianceLevel
    issues: List[ComplianceIssue] = field(default_factory=list)


class StandardsComplianceChecker:
    """Check compliance with construction data standards."""

    def __init__(self):
        self.rules: Dict[Standard, List[Dict]] = self._load_rules()

    def _load_rules(self) -> Dict[Standard, List[Dict]]:
        """Load compliance rules for each standard."""

        return {
            Standard.ISO_19650: [
                {"id": "ISO-001", "name": "File naming convention", "field": "filename",
                 "pattern": r"^[A-Z]{2,6}-[A-Z]{2,4}-[A-Z]{2,3}-[A-Z0-9]{2,4}-[A-Z]{2,3}-[A-Z]{2,4}-[A-Z0-9]{3,8}$"},
                {"id": "ISO-002", "name": "Status code valid", "field": "status",
                 "values": ["WIP", "S0", "S1", "S2", "S3", "S4", "A", "B", "CR"]},
                {"id": "ISO-003", "name": "Revision format", "field": "revision",
                 "pattern": r"^P[0-9]{2}|C[0-9]{2}$"},
            ],
            Standard.IFC: [
                {"id": "IFC-001", "name": "GUID format", "field": "global_id",
                 "pattern": r"^[0-9A-Za-z_$]{22}$"},
                {"id": "IFC-002", "name": "Name required", "field": "name", "required": True},
                {"id": "IFC-003", "name": "ObjectType defined", "field": "object_type", "required": True},
            ],
            Standard.COBIE: [
                {"id": "COB-001", "name": "Facility name", "field": "facility_name", "required": True},
                {"id": "COB-002", "name": "Space name format", "field": "space_name",
                 "pattern": r"^[A-Z0-9]{2,10}[-_]?[A-Z0-9]{0,10}$"},
                {"id": "COB-003", "name": "Component type", "field": "component_type", "required": True},
                {"id": "COB-004", "name": "Manufacturer info", "field": "manufacturer", "required": True},
            ],
            Standard.UNIFORMAT: [
                {"id": "UNI-001", "name": "Level 1 code", "field": "level1",
                 "values": ["A", "B", "C", "D", "E", "F", "G", "Z"]},
                {"id": "UNI-002", "name": "Code format", "field": "code",
                 "pattern": r"^[A-G][0-9]{4}$"},
            ],
            Standard.MASTERFORMAT: [
                {"id": "MF-001", "name": "Division format", "field": "division",
                 "pattern": r"^[0-9]{2}$"},
                {"id": "MF-002", "name": "Section format", "field": "section",
                 "pattern": r"^[0-9]{2}\s?[0-9]{2}\s?[0-9]{2}(\.[0-9]{2})?$"},
            ]
        }

    def check_compliance(self, data: Dict[str, Any],
                        standard: Standard) -> ComplianceReport:
        """Check data against specified standard."""

        rules = self.rules.get(standard, [])
        issues = []
        passed = 0
        failed = 0
        warnings = 0

        for rule in rules:
            result = self._check_rule(data, rule)
            if result:
                issues.append(result)
                if result.severity == "error":
                    failed += 1
                else:
                    warnings += 1
            else:
                passed += 1

        # Determine compliance level
        if failed == 0 and warnings == 0:
            level = ComplianceLevel.COMPLIANT
        elif failed == 0:
            level = ComplianceLevel.MINOR_ISSUES
        elif failed <= len(rules) * 0.3:
            level = ComplianceLevel.MAJOR_ISSUES
        else:
            level = ComplianceLevel.NON_COMPLIANT

        return ComplianceReport(
            standard=standard,
            total_rules=len(rules),
            passed=passed,
            failed=failed,
            warnings=warnings,
            compliance_level=level,
            issues=issues
        )

    def _check_rule(self, data: Dict[str, Any], rule: Dict) -> Optional[ComplianceIssue]:
        """Check single compliance rule."""

        field = rule.get('field', '')
        value = data.get(field)

        # Required check
        if rule.get('required') and (value is None or value == ''):
            return ComplianceIssue(
                rule_id=rule['id'],
                rule_name=rule['name'],
                severity="error",
                message=f"Required field '{field}' is missing",
                field=field
            )

        # Skip other checks if value is empty
        if value is None or value == '':
            return None

        # Pattern check
        if 'pattern' in rule:
            if not re.match(rule['pattern'], str(value)):
                return ComplianceIssue(
                    rule_id=rule['id'],
                    rule_name=rule['name'],
                    severity="error",
                    message=f"Field '{field}' does not match required format",
                    field=field,
                    value=value
                )

        # Allowed values check
        if 'values' in rule:
            if value not in rule['values']:
                return ComplianceIssue(
                    rule_id=rule['id'],
                    rule_name=rule['name'],
                    severity="error",
                    message=f"Field '{field}' must be one of: {rule['values']}",
                    field=field,
                    value=value
                )

        return None

    def check_multiple_standards(self, data: Dict[str, Any],
                                  standards: List[Standard]) -> Dict[str, ComplianceReport]:
        """Check data against multiple standards."""

        reports = {}
        for standard in standards:
            reports[standard.value] = self.check_compliance(data, standard)
        return reports

    def check_batch(self, records: List[Dict[str, Any]],
                    standard: Standard) -> Dict[str, Any]:
        """Check multiple records against standard."""

        all_issues = []
        compliant_count = 0

        for i, record in enumerate(records):
            report = self.check_compliance(record, standard)
            if report.compliance_level == ComplianceLevel.COMPLIANT:
                compliant_count += 1
            for issue in report.issues:
                all_issues.append({
                    'record_index': i,
                    'rule_id': issue.rule_id,
                    'field': issue.field,
                    'message': issue.message
                })

        return {
            'standard': standard.value,
            'total_records': len(records),
            'compliant_records': compliant_count,
            'compliance_rate': round(compliant_count / len(records) * 100, 1) if records else 0,
            'total_issues': len(all_issues),
            'issues': all_issues
        }

    def add_custom_rule(self, standard: Standard, rule: Dict):
        """Add custom compliance rule."""

        if standard not in self.rules:
            self.rules[standard] = []
        self.rules[standard].append(rule)

    def generate_report_summary(self, report: ComplianceReport) -> str:
        """Generate human-readable report summary."""

        lines = [
            f"Compliance Report: {report.standard.value.upper()}",
            "=" * 40,
            f"Total Rules: {report.total_rules}",
            f"Passed: {report.passed}",
            f"Failed: {report.failed}",
            f"Warnings: {report.warnings}",
            f"Status: {report.compliance_level.value.upper()}",
            "",
            "Issues:"
        ]

        for issue in report.issues:
            lines.append(f"  [{issue.severity.upper()}] {issue.rule_id}: {issue.message}")

        return "\n".join(lines)
```

## Quick Start

```python
# Initialize checker
checker = StandardsComplianceChecker()

# Check ISO 19650 compliance
data = {
    "filename": "PRJ-ARC-MOD-0001-DWG-PLAN-001",
    "status": "S3",
    "revision": "P01"
}

report = checker.check_compliance(data, Standard.ISO_19650)
print(f"Compliance: {report.compliance_level.value}")
print(f"Passed: {report.passed}/{report.total_rules}")
```

## Common Use Cases

### 1. COBie Validation
```python
cobie_data = {
    "facility_name": "Building A",
    "space_name": "OFFICE-101",
    "component_type": "HVAC_Unit",
    "manufacturer": "Carrier"
}
report = checker.check_compliance(cobie_data, Standard.COBIE)
```

### 2. Batch Validation
```python
records = [{"filename": "...", "status": "..."}, ...]
batch_report = checker.check_batch(records, Standard.ISO_19650)
print(f"Compliance rate: {batch_report['compliance_rate']}%")
```

### 3. Multiple Standards
```python
reports = checker.check_multiple_standards(
    data,
    [Standard.ISO_19650, Standard.IFC]
)
```

## Resources
- **DDC Book**: Chapter 2.5 - Data Models and Standards
- **ISO 19650**: Information management using BIM
- **Website**: https://datadrivenconstruction.io
