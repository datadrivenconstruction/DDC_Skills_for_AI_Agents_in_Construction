---
name: ids-checker
description: "Check BIM data against IDS (Information Delivery Specification). Validate model information requirements and compliance."
---

# IDS Checker

## Business Case

### Problem Statement
BIM data validation challenges:
- Inconsistent model information
- Missing required properties
- Non-compliant data deliveries
- Manual validation is time-consuming

### Solution
Automated IDS (Information Delivery Specification) checking system to validate BIM models against defined requirements.

## Technical Implementation

```python
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re


class RequirementType(Enum):
    PROPERTY = "property"
    CLASSIFICATION = "classification"
    MATERIAL = "material"
    ATTRIBUTE = "attribute"
    RELATION = "relation"


class Facet(Enum):
    ENTITY = "entity"
    PROPERTY_SET = "property_set"
    PROPERTY = "property"
    CLASSIFICATION = "classification"
    MATERIAL = "material"
    PART_OF = "part_of"


class Cardinality(Enum):
    REQUIRED = "required"
    OPTIONAL = "optional"
    PROHIBITED = "prohibited"


class CheckResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    NOT_APPLICABLE = "n/a"


@dataclass
class IDSRequirement:
    req_id: str
    name: str
    description: str
    applicability: Dict[str, Any]  # Which elements this applies to
    requirements: List[Dict[str, Any]]  # What is required
    cardinality: Cardinality = Cardinality.REQUIRED


@dataclass
class ValidationResult:
    element_id: str
    element_type: str
    requirement_id: str
    result: CheckResult
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IDSSpecification:
    spec_id: str
    name: str
    version: str
    purpose: str
    requirements: List[IDSRequirement] = field(default_factory=list)


class IDSChecker:
    """Check BIM data against IDS (Information Delivery Specification)."""

    def __init__(self, spec_name: str):
        self.spec_name = spec_name
        self.specifications: Dict[str, IDSSpecification] = {}
        self.results: List[ValidationResult] = []

    def create_specification(self, spec_id: str, name: str,
                             version: str = "1.0", purpose: str = "") -> IDSSpecification:
        """Create new IDS specification."""

        spec = IDSSpecification(
            spec_id=spec_id,
            name=name,
            version=version,
            purpose=purpose
        )
        self.specifications[spec_id] = spec
        return spec

    def add_requirement(self, spec_id: str, requirement: IDSRequirement):
        """Add requirement to specification."""

        if spec_id in self.specifications:
            self.specifications[spec_id].requirements.append(requirement)

    def add_property_requirement(self, spec_id: str, req_id: str, name: str,
                                  entity_type: str, property_set: str,
                                  property_name: str, data_type: str = None,
                                  value_pattern: str = None,
                                  cardinality: Cardinality = Cardinality.REQUIRED):
        """Add property requirement."""

        requirement = IDSRequirement(
            req_id=req_id,
            name=name,
            description=f"Property {property_name} in {property_set}",
            applicability={'entity': entity_type},
            requirements=[{
                'type': RequirementType.PROPERTY.value,
                'property_set': property_set,
                'property_name': property_name,
                'data_type': data_type,
                'value_pattern': value_pattern
            }],
            cardinality=cardinality
        )
        self.add_requirement(spec_id, requirement)

    def add_classification_requirement(self, spec_id: str, req_id: str, name: str,
                                        entity_type: str, system: str,
                                        value_pattern: str = None,
                                        cardinality: Cardinality = Cardinality.REQUIRED):
        """Add classification requirement."""

        requirement = IDSRequirement(
            req_id=req_id,
            name=name,
            description=f"Classification from {system}",
            applicability={'entity': entity_type},
            requirements=[{
                'type': RequirementType.CLASSIFICATION.value,
                'system': system,
                'value_pattern': value_pattern
            }],
            cardinality=cardinality
        )
        self.add_requirement(spec_id, requirement)

    def create_standard_cobie_spec(self) -> str:
        """Create standard COBie specification."""

        spec = self.create_specification(
            "COBIE_BASIC",
            "COBie Basic Requirements",
            "1.0",
            "Basic COBie data requirements for facility handover"
        )

        # Space requirements
        self.add_property_requirement("COBIE_BASIC", "CB-SP-01", "Space Name",
                                       "IfcSpace", "Pset_SpaceCommon", "Name")
        self.add_property_requirement("COBIE_BASIC", "CB-SP-02", "Space Number",
                                       "IfcSpace", "COBie_Space", "SpaceNumber")
        self.add_property_requirement("COBIE_BASIC", "CB-SP-03", "Room Tag",
                                       "IfcSpace", "COBie_Space", "RoomTag")

        # Component requirements
        self.add_property_requirement("COBIE_BASIC", "CB-CO-01", "Component Name",
                                       "IfcElement", "COBie_Component", "Name")
        self.add_property_requirement("COBIE_BASIC", "CB-CO-02", "Component Type",
                                       "IfcElement", "COBie_Component", "TypeName")
        self.add_property_requirement("COBIE_BASIC", "CB-CO-03", "Serial Number",
                                       "IfcElement", "COBie_Component", "SerialNumber",
                                       cardinality=Cardinality.OPTIONAL)

        # Type requirements
        self.add_property_requirement("COBIE_BASIC", "CB-TY-01", "Type Name",
                                       "IfcTypeObject", "COBie_Type", "Name")
        self.add_property_requirement("COBIE_BASIC", "CB-TY-02", "Manufacturer",
                                       "IfcTypeObject", "COBie_Type", "Manufacturer")
        self.add_property_requirement("COBIE_BASIC", "CB-TY-03", "Model Number",
                                       "IfcTypeObject", "COBie_Type", "ModelNumber")

        return "COBIE_BASIC"

    def create_standard_lod_spec(self, lod_level: int = 300) -> str:
        """Create standard LOD specification."""

        spec_id = f"LOD_{lod_level}"
        spec = self.create_specification(
            spec_id,
            f"LOD {lod_level} Requirements",
            "1.0",
            f"Level of Development {lod_level} requirements"
        )

        if lod_level >= 200:
            self.add_property_requirement(spec_id, f"LOD-{lod_level}-01",
                                           "Element must have type",
                                           "IfcElement", "Pset_ElementCommon", "Type")

        if lod_level >= 300:
            self.add_property_requirement(spec_id, f"LOD-{lod_level}-02",
                                           "Element must have dimensions",
                                           "IfcElement", "BaseQuantities", "Length")
            self.add_property_requirement(spec_id, f"LOD-{lod_level}-03",
                                           "Material assignment",
                                           "IfcElement", "Pset_MaterialCommon", "Material")

        if lod_level >= 350:
            self.add_property_requirement(spec_id, f"LOD-{lod_level}-04",
                                           "Fire rating",
                                           "IfcElement", "Pset_ElementCommon", "FireRating",
                                           cardinality=Cardinality.OPTIONAL)
            self.add_classification_requirement(spec_id, f"LOD-{lod_level}-05",
                                                 "Uniformat classification",
                                                 "IfcElement", "Uniformat")

        return spec_id

    def check_element(self, element: Dict[str, Any],
                      spec_id: str) -> List[ValidationResult]:
        """Check single element against specification."""

        results = []

        if spec_id not in self.specifications:
            return results

        spec = self.specifications[spec_id]

        for req in spec.requirements:
            # Check applicability
            if not self._matches_applicability(element, req.applicability):
                continue

            # Check requirements
            for req_def in req.requirements:
                result = self._check_requirement(element, req, req_def)
                results.append(result)

        return results

    def _matches_applicability(self, element: Dict[str, Any],
                                applicability: Dict[str, Any]) -> bool:
        """Check if element matches applicability criteria."""

        entity_filter = applicability.get('entity')
        if entity_filter:
            element_type = element.get('type', '')
            if entity_filter not in element_type:
                return False

        return True

    def _check_requirement(self, element: Dict[str, Any],
                           req: IDSRequirement,
                           req_def: Dict[str, Any]) -> ValidationResult:
        """Check single requirement."""

        req_type = req_def.get('type')

        if req_type == RequirementType.PROPERTY.value:
            return self._check_property_requirement(element, req, req_def)
        elif req_type == RequirementType.CLASSIFICATION.value:
            return self._check_classification_requirement(element, req, req_def)

        return ValidationResult(
            element_id=element.get('id', ''),
            element_type=element.get('type', ''),
            requirement_id=req.req_id,
            result=CheckResult.NOT_APPLICABLE,
            message="Unknown requirement type"
        )

    def _check_property_requirement(self, element: Dict[str, Any],
                                     req: IDSRequirement,
                                     req_def: Dict[str, Any]) -> ValidationResult:
        """Check property requirement."""

        pset_name = req_def.get('property_set')
        prop_name = req_def.get('property_name')
        value_pattern = req_def.get('value_pattern')

        # Get property value
        properties = element.get('properties', {})
        pset = properties.get(pset_name, {})
        value = pset.get(prop_name)

        result = ValidationResult(
            element_id=element.get('id', ''),
            element_type=element.get('type', ''),
            requirement_id=req.req_id,
            result=CheckResult.PASS,
            message="",
            details={'property_set': pset_name, 'property': prop_name, 'value': value}
        )

        # Check if property exists
        if value is None:
            if req.cardinality == Cardinality.REQUIRED:
                result.result = CheckResult.FAIL
                result.message = f"Missing required property: {pset_name}.{prop_name}"
            elif req.cardinality == Cardinality.PROHIBITED:
                result.result = CheckResult.PASS
                result.message = "Prohibited property correctly absent"
            else:
                result.result = CheckResult.WARNING
                result.message = f"Optional property missing: {pset_name}.{prop_name}"
            return result

        # Check if property should not exist
        if req.cardinality == Cardinality.PROHIBITED:
            result.result = CheckResult.FAIL
            result.message = f"Prohibited property exists: {pset_name}.{prop_name}"
            return result

        # Check value pattern
        if value_pattern:
            if not re.match(value_pattern, str(value)):
                result.result = CheckResult.FAIL
                result.message = f"Value '{value}' does not match pattern '{value_pattern}'"
                return result

        result.message = f"Property {prop_name} = {value}"
        return result

    def _check_classification_requirement(self, element: Dict[str, Any],
                                           req: IDSRequirement,
                                           req_def: Dict[str, Any]) -> ValidationResult:
        """Check classification requirement."""

        system = req_def.get('system')
        value_pattern = req_def.get('value_pattern')

        classifications = element.get('classifications', {})
        value = classifications.get(system)

        result = ValidationResult(
            element_id=element.get('id', ''),
            element_type=element.get('type', ''),
            requirement_id=req.req_id,
            result=CheckResult.PASS,
            message="",
            details={'system': system, 'value': value}
        )

        if value is None:
            if req.cardinality == Cardinality.REQUIRED:
                result.result = CheckResult.FAIL
                result.message = f"Missing classification: {system}"
            else:
                result.result = CheckResult.WARNING
                result.message = f"Optional classification missing: {system}"
            return result

        if value_pattern and not re.match(value_pattern, str(value)):
            result.result = CheckResult.FAIL
            result.message = f"Classification '{value}' does not match pattern"
            return result

        result.message = f"Classification {system} = {value}"
        return result

    def check_model(self, elements: List[Dict[str, Any]],
                    spec_id: str) -> Dict[str, Any]:
        """Check all elements against specification."""

        self.results = []

        for element in elements:
            element_results = self.check_element(element, spec_id)
            self.results.extend(element_results)

        # Summarize results
        pass_count = sum(1 for r in self.results if r.result == CheckResult.PASS)
        fail_count = sum(1 for r in self.results if r.result == CheckResult.FAIL)
        warning_count = sum(1 for r in self.results if r.result == CheckResult.WARNING)

        return {
            'specification': spec_id,
            'elements_checked': len(elements),
            'total_checks': len(self.results),
            'passed': pass_count,
            'failed': fail_count,
            'warnings': warning_count,
            'compliance_rate': round(pass_count / len(self.results) * 100, 1) if self.results else 0,
            'status': 'COMPLIANT' if fail_count == 0 else 'NON-COMPLIANT'
        }

    def get_failed_checks(self) -> List[Dict[str, Any]]:
        """Get list of failed checks."""

        return [
            {
                'element_id': r.element_id,
                'element_type': r.element_type,
                'requirement': r.requirement_id,
                'message': r.message,
                'details': r.details
            }
            for r in self.results if r.result == CheckResult.FAIL
        ]

    def export_to_excel(self, output_path: str) -> str:
        """Export validation results to Excel."""

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary
            summary = {
                'Total Checks': len(self.results),
                'Passed': sum(1 for r in self.results if r.result == CheckResult.PASS),
                'Failed': sum(1 for r in self.results if r.result == CheckResult.FAIL),
                'Warnings': sum(1 for r in self.results if r.result == CheckResult.WARNING)
            }
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # All results
            results_df = pd.DataFrame([{
                'Element ID': r.element_id,
                'Element Type': r.element_type,
                'Requirement': r.requirement_id,
                'Result': r.result.value,
                'Message': r.message
            } for r in self.results])
            results_df.to_excel(writer, sheet_name='All Results', index=False)

            # Failed only
            failed_df = pd.DataFrame(self.get_failed_checks())
            if not failed_df.empty:
                failed_df.to_excel(writer, sheet_name='Failed', index=False)

        return output_path
```

## Quick Start

```python
# Create IDS checker
checker = IDSChecker("Project BIM Validation")

# Create COBie specification
cobie_spec = checker.create_standard_cobie_spec()

# Sample BIM elements
elements = [
    {
        'id': 'Space_001',
        'type': 'IfcSpace',
        'properties': {
            'Pset_SpaceCommon': {'Name': 'Office 101'},
            'COBie_Space': {'SpaceNumber': 'SP-101', 'RoomTag': 'A101'}
        }
    },
    {
        'id': 'Door_001',
        'type': 'IfcDoor',
        'properties': {
            'COBie_Component': {'Name': 'Door 1', 'TypeName': 'Single Door'}
        }
    }
]

# Check model
results = checker.check_model(elements, cobie_spec)
print(f"Compliance: {results['compliance_rate']}%")
print(f"Status: {results['status']}")
```

## Common Use Cases

### 1. LOD Validation
```python
lod_spec = checker.create_standard_lod_spec(350)
results = checker.check_model(elements, lod_spec)
```

### 2. Custom Requirement
```python
checker.add_property_requirement(
    "COBIE_BASIC", "CB-CUSTOM-01", "Fire Rating Required",
    "IfcWall", "Pset_WallCommon", "FireRating",
    value_pattern=r"^\d+\s*hr$"
)
```

### 3. Get Failed Items
```python
failed = checker.get_failed_checks()
for item in failed:
    print(f"{item['element_id']}: {item['message']}")
```

## Resources
- **DDC Book**: Chapter 4.3 - Automated ETL Pipeline for Data Validation
- **buildingSMART IDS**: https://technical.buildingsmart.org/projects/information-delivery-specification-ids/
- **Website**: https://datadrivenconstruction.io
