---
name: specification-extractor
description: "Extract structured data from construction specifications. Parse CSI sections, requirements, submittals, and product data from spec documents."
---

# Specification Extractor for Construction

## Overview

Extract structured data from construction specification documents. Parse CSI MasterFormat sections, identify requirements, submittals, product standards, and compile actionable data for estimating and procurement.

## Business Case

Automated spec extraction enables:
- **Faster Estimating**: Quickly identify scope and requirements
- **Procurement Accuracy**: Extract exact product specifications
- **Submittal Tracking**: Identify all required submittals
- **Compliance Checking**: Verify specs against standards

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re
import pdfplumber
from pathlib import Path

@dataclass
class SpecSection:
    number: str  # e.g., "03 30 00"
    title: str
    part1_general: Dict[str, Any]
    part2_products: Dict[str, Any]
    part3_execution: Dict[str, Any]
    raw_text: str

@dataclass
class ProductRequirement:
    section: str
    manufacturer: str
    product_name: str
    model: str
    standards: List[str]
    properties: Dict[str, str]

@dataclass
class SubmittalRequirement:
    section: str
    submittal_type: str  # shop drawings, samples, product data, etc.
    description: str
    timing: str
    copies: int

@dataclass
class SpecExtractionResult:
    document_name: str
    total_pages: int
    sections: List[SpecSection]
    products: List[ProductRequirement]
    submittals: List[SubmittalRequirement]
    standards_referenced: List[str]

class SpecificationExtractor:
    """Extract structured data from construction specifications."""

    # CSI MasterFormat patterns
    CSI_SECTION_PATTERN = r'^(\d{2}\s?\d{2}\s?\d{2})\s*[-–]\s*(.+?)$'
    PART_PATTERN = r'^PART\s+(\d+)\s*[-–]\s*(.+?)$'
    ARTICLE_PATTERN = r'^(\d+\.\d+)\s+([A-Z][A-Z\s]+)$'

    # Submittal type keywords
    SUBMITTAL_TYPES = {
        'shop drawings': 'Shop Drawings',
        'product data': 'Product Data',
        'samples': 'Samples',
        'certificates': 'Certificates',
        'test reports': 'Test Reports',
        'manufacturer instructions': 'Manufacturer Instructions',
        'warranty': 'Warranty',
        'maintenance data': 'Maintenance Data',
        'mock-ups': 'Mock-ups',
    }

    # Common standard organizations
    STANDARD_PATTERNS = [
        r'ASTM\s+[A-Z]\d+',
        r'ANSI\s+[A-Z]?\d+',
        r'ACI\s+\d+',
        r'AISC\s+\d+',
        r'AWS\s+[A-Z]\d+',
        r'ASCE\s+\d+',
        r'UL\s+\d+',
        r'FM\s+\d+',
        r'NFPA\s+\d+',
        r'IBC\s+\d+',
    ]

    def __init__(self):
        self.sections: Dict[str, SpecSection] = {}

    def extract_from_pdf(self, pdf_path: str) -> SpecExtractionResult:
        """Extract specification data from PDF."""
        path = Path(pdf_path)

        all_text = ""
        page_count = 0

        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text() or ""
                all_text += text + "\n\n"

        # Parse sections
        sections = self._parse_sections(all_text)

        # Extract products
        products = self._extract_products(sections)

        # Extract submittals
        submittals = self._extract_submittals(sections)

        # Extract standards
        standards = self._extract_standards(all_text)

        return SpecExtractionResult(
            document_name=path.name,
            total_pages=page_count,
            sections=sections,
            products=products,
            submittals=submittals,
            standards_referenced=standards
        )

    def _parse_sections(self, text: str) -> List[SpecSection]:
        """Parse CSI sections from specification text."""
        sections = []
        lines = text.split('\n')

        current_section = None
        current_part = None
        current_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for section header
            section_match = re.match(self.CSI_SECTION_PATTERN, line, re.IGNORECASE)
            if section_match:
                # Save previous section
                if current_section:
                    sections.append(self._finalize_section(current_section, current_content))

                current_section = {
                    'number': section_match.group(1).replace(' ', ''),
                    'title': section_match.group(2).strip(),
                    'parts': {}
                }
                current_content = []
                current_part = None
                continue

            # Check for part header
            part_match = re.match(self.PART_PATTERN, line, re.IGNORECASE)
            if part_match and current_section:
                part_num = part_match.group(1)
                part_name = part_match.group(2).strip()
                current_part = f"part{part_num}"
                current_section['parts'][current_part] = {
                    'name': part_name,
                    'content': []
                }
                continue

            # Add content to current part
            if current_section and current_part:
                current_section['parts'][current_part]['content'].append(line)
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            sections.append(self._finalize_section(current_section, current_content))

        return sections

    def _finalize_section(self, section_data: Dict, general_content: List[str]) -> SpecSection:
        """Finalize a section with parsed parts."""
        parts = section_data.get('parts', {})

        part1 = self._parse_part_content(parts.get('part1', {}).get('content', []))
        part2 = self._parse_part_content(parts.get('part2', {}).get('content', []))
        part3 = self._parse_part_content(parts.get('part3', {}).get('content', []))

        return SpecSection(
            number=section_data['number'],
            title=section_data['title'],
            part1_general=part1,
            part2_products=part2,
            part3_execution=part3,
            raw_text='\n'.join(general_content)
        )

    def _parse_part_content(self, content: List[str]) -> Dict[str, Any]:
        """Parse part content into structured data."""
        result = {
            'articles': {},
            'items': []
        }

        current_article = None

        for line in content:
            # Check for article header
            article_match = re.match(self.ARTICLE_PATTERN, line)
            if article_match:
                current_article = article_match.group(1)
                result['articles'][current_article] = {
                    'title': article_match.group(2),
                    'items': []
                }
                continue

            # Add to current article or general items
            if current_article and current_article in result['articles']:
                result['articles'][current_article]['items'].append(line)
            else:
                result['items'].append(line)

        return result

    def _extract_products(self, sections: List[SpecSection]) -> List[ProductRequirement]:
        """Extract product requirements from Part 2."""
        products = []

        for section in sections:
            part2 = section.part2_products

            for article_num, article in part2.get('articles', {}).items():
                if 'MANUFACTURERS' in article['title'].upper():
                    for item in article['items']:
                        # Extract manufacturer names
                        if item.strip().startswith(('A.', 'B.', 'C.', '1.', '2.', '3.')):
                            mfr_name = re.sub(r'^[A-Z\d]+\.\s*', '', item).strip()
                            products.append(ProductRequirement(
                                section=section.number,
                                manufacturer=mfr_name,
                                product_name='',
                                model='',
                                standards=[],
                                properties={}
                            ))

                elif 'MATERIALS' in article['title'].upper() or 'PRODUCTS' in article['title'].upper():
                    for item in article['items']:
                        # Extract material requirements
                        standards = self._extract_standards(item)
                        if standards:
                            products.append(ProductRequirement(
                                section=section.number,
                                manufacturer='',
                                product_name=item[:100],
                                model='',
                                standards=standards,
                                properties={}
                            ))

        return products

    def _extract_submittals(self, sections: List[SpecSection]) -> List[SubmittalRequirement]:
        """Extract submittal requirements from Part 1."""
        submittals = []

        for section in sections:
            part1 = section.part1_general

            for article_num, article in part1.get('articles', {}).items():
                if 'SUBMITTAL' in article['title'].upper():
                    for item in article['items']:
                        item_lower = item.lower()

                        for keyword, submittal_type in self.SUBMITTAL_TYPES.items():
                            if keyword in item_lower:
                                submittals.append(SubmittalRequirement(
                                    section=section.number,
                                    submittal_type=submittal_type,
                                    description=item.strip(),
                                    timing='Prior to fabrication',
                                    copies=3
                                ))
                                break

        return submittals

    def _extract_standards(self, text: str) -> List[str]:
        """Extract referenced standards from text."""
        standards = []

        for pattern in self.STANDARD_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            standards.extend(matches)

        return list(set(standards))

    def generate_submittal_log(self, result: SpecExtractionResult) -> str:
        """Generate submittal log from extraction results."""
        lines = ["# Submittal Log", ""]
        lines.append(f"**Project Specs:** {result.document_name}")
        lines.append(f"**Total Submittals:** {len(result.submittals)}")
        lines.append("")

        lines.append("| # | Section | Type | Description | Status |")
        lines.append("|---|---------|------|-------------|--------|")

        for i, sub in enumerate(result.submittals, 1):
            desc = sub.description[:50] + "..." if len(sub.description) > 50 else sub.description
            lines.append(f"| {i} | {sub.section} | {sub.submittal_type} | {desc} | Pending |")

        return "\n".join(lines)

    def generate_product_schedule(self, result: SpecExtractionResult) -> str:
        """Generate product schedule from extraction results."""
        lines = ["# Product Schedule", ""]

        # Group by section
        by_section = {}
        for prod in result.products:
            if prod.section not in by_section:
                by_section[prod.section] = []
            by_section[prod.section].append(prod)

        for section, products in sorted(by_section.items()):
            lines.append(f"## Section {section}")
            lines.append("")

            for prod in products:
                if prod.manufacturer:
                    lines.append(f"- **Manufacturer:** {prod.manufacturer}")
                if prod.product_name:
                    lines.append(f"- **Product:** {prod.product_name}")
                if prod.standards:
                    lines.append(f"- **Standards:** {', '.join(prod.standards)}")
                lines.append("")

        return "\n".join(lines)

    def generate_report(self, result: SpecExtractionResult) -> str:
        """Generate comprehensive extraction report."""
        lines = ["# Specification Extraction Report", ""]
        lines.append(f"**Document:** {result.document_name}")
        lines.append(f"**Pages:** {result.total_pages}")
        lines.append(f"**Sections Found:** {len(result.sections)}")
        lines.append("")

        # Sections summary
        lines.append("## Sections Extracted")
        for section in result.sections:
            lines.append(f"- **{section.number}** - {section.title}")
        lines.append("")

        # Standards
        if result.standards_referenced:
            lines.append("## Standards Referenced")
            for std in sorted(set(result.standards_referenced)):
                lines.append(f"- {std}")
            lines.append("")

        # Submittals summary
        lines.append("## Submittals Required")
        lines.append(f"Total: {len(result.submittals)}")
        by_type = {}
        for sub in result.submittals:
            by_type[sub.submittal_type] = by_type.get(sub.submittal_type, 0) + 1
        for t, count in sorted(by_type.items()):
            lines.append(f"- {t}: {count}")
        lines.append("")

        # Products summary
        lines.append("## Products/Manufacturers")
        lines.append(f"Total: {len(result.products)}")

        return "\n".join(lines)
```

## Quick Start

```python
# Initialize extractor
extractor = SpecificationExtractor()

# Extract from PDF
result = extractor.extract_from_pdf("Project_Specifications.pdf")

print(f"Found {len(result.sections)} sections")
print(f"Found {len(result.submittals)} submittals")
print(f"Found {len(result.products)} product requirements")

# Generate submittal log
submittal_log = extractor.generate_submittal_log(result)
print(submittal_log)

# Generate product schedule
product_schedule = extractor.generate_product_schedule(result)
print(product_schedule)

# Full report
report = extractor.generate_report(result)
print(report)
```

## Dependencies

```bash
pip install pdfplumber
```
