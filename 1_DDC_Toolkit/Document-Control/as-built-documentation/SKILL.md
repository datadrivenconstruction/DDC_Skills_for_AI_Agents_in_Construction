---
name: as-built-documentation
description: "Manage as-built documentation for project closeout. Track drawing markups, coordinate updates, and verify completeness."
---

# As-Built Documentation Manager

## Business Case

### Problem Statement
As-built documentation is often incomplete:
- Field changes not documented
- Drawings not updated consistently
- Missing documentation at closeout
- Difficult to verify completeness

### Solution
Systematic as-built documentation tracking with drawing markup management, completeness verification, and handover preparation.

## Technical Implementation

```python
import pandas as pd
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class DocumentType(Enum):
    DRAWING = "drawing"
    SPECIFICATION = "specification"
    SUBMITTAL = "submittal"
    MANUAL = "manual"
    WARRANTY = "warranty"
    CERTIFICATE = "certificate"


class MarkupStatus(Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    INCORPORATED = "incorporated"


class DocumentStatus(Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    FINAL = "final"


@dataclass
class Markup:
    markup_id: str
    description: str
    location: str
    marked_by: str
    marked_date: date
    status: MarkupStatus
    cloud_reference: str = ""
    notes: str = ""


@dataclass
class AsBuiltDocument:
    document_id: str
    document_number: str
    title: str
    document_type: DocumentType
    discipline: str
    revision: str
    status: DocumentStatus
    original_file: str
    as_built_file: str
    markups: List[Markup] = field(default_factory=list)
    last_updated: Optional[date] = None
    verified_by: str = ""
    verified_date: Optional[date] = None

    @property
    def is_complete(self) -> bool:
        return self.status == DocumentStatus.FINAL and all(
            m.status == MarkupStatus.INCORPORATED for m in self.markups
        )


class AsBuiltDocumentManager:
    """Manage as-built documentation."""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.documents: Dict[str, AsBuiltDocument] = {}
        self._markup_counter = 0

    def register_document(self, document_number: str, title: str,
                         document_type: DocumentType, discipline: str,
                         original_file: str, revision: str = "0") -> AsBuiltDocument:
        doc_id = f"DOC-{len(self.documents) + 1:04d}"

        doc = AsBuiltDocument(
            document_id=doc_id,
            document_number=document_number,
            title=title,
            document_type=document_type,
            discipline=discipline,
            revision=revision,
            status=DocumentStatus.DRAFT,
            original_file=original_file,
            as_built_file=""
        )
        self.documents[doc_id] = doc
        return doc

    def add_markup(self, doc_id: str, description: str, location: str,
                  marked_by: str, cloud_reference: str = "") -> Markup:
        if doc_id not in self.documents:
            raise ValueError(f"Document {doc_id} not found")

        self._markup_counter += 1
        markup = Markup(
            markup_id=f"MKP-{self._markup_counter:05d}",
            description=description,
            location=location,
            marked_by=marked_by,
            marked_date=date.today(),
            status=MarkupStatus.PENDING,
            cloud_reference=cloud_reference
        )
        self.documents[doc_id].markups.append(markup)
        return markup

    def update_markup_status(self, doc_id: str, markup_id: str, status: MarkupStatus):
        if doc_id in self.documents:
            for markup in self.documents[doc_id].markups:
                if markup.markup_id == markup_id:
                    markup.status = status
                    break

    def upload_as_built(self, doc_id: str, file_path: str, new_revision: str = None):
        if doc_id not in self.documents:
            return
        doc = self.documents[doc_id]
        doc.as_built_file = file_path
        doc.last_updated = date.today()
        if new_revision:
            doc.revision = new_revision
        doc.status = DocumentStatus.UNDER_REVIEW

    def verify_document(self, doc_id: str, verified_by: str):
        if doc_id not in self.documents:
            return
        doc = self.documents[doc_id]
        doc.verified_by = verified_by
        doc.verified_date = date.today()
        doc.status = DocumentStatus.FINAL

    def get_completeness_report(self) -> Dict[str, Any]:
        total = len(self.documents)
        complete = sum(1 for d in self.documents.values() if d.is_complete)
        pending_markups = sum(
            len([m for m in d.markups if m.status != MarkupStatus.INCORPORATED])
            for d in self.documents.values()
        )

        by_discipline = {}
        for doc in self.documents.values():
            if doc.discipline not in by_discipline:
                by_discipline[doc.discipline] = {'total': 0, 'complete': 0}
            by_discipline[doc.discipline]['total'] += 1
            if doc.is_complete:
                by_discipline[doc.discipline]['complete'] += 1

        return {
            'project': self.project_name,
            'total_documents': total,
            'complete': complete,
            'completion_percent': round(complete / total * 100, 1) if total > 0 else 0,
            'pending_markups': pending_markups,
            'by_discipline': by_discipline
        }

    def get_incomplete_documents(self) -> List[AsBuiltDocument]:
        return [d for d in self.documents.values() if not d.is_complete]

    def export_register(self, output_path: str):
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Document register
            doc_data = [{
                'ID': d.document_id,
                'Number': d.document_number,
                'Title': d.title,
                'Type': d.document_type.value,
                'Discipline': d.discipline,
                'Revision': d.revision,
                'Status': d.status.value,
                'Complete': d.is_complete,
                'Markups': len(d.markups),
                'Verified By': d.verified_by
            } for d in self.documents.values()]
            pd.DataFrame(doc_data).to_excel(writer, sheet_name='Register', index=False)

            # Markups
            markup_data = []
            for doc in self.documents.values():
                for m in doc.markups:
                    markup_data.append({
                        'Document': doc.document_number,
                        'Markup ID': m.markup_id,
                        'Description': m.description,
                        'Location': m.location,
                        'Marked By': m.marked_by,
                        'Status': m.status.value
                    })
            if markup_data:
                pd.DataFrame(markup_data).to_excel(writer, sheet_name='Markups', index=False)

        return output_path
```

## Quick Start

```python
manager = AsBuiltDocumentManager("Office Tower")

# Register document
doc = manager.register_document(
    document_number="A-101",
    title="Floor Plan Level 1",
    document_type=DocumentType.DRAWING,
    discipline="Architectural",
    original_file="drawings/A-101.pdf"
)

# Add field markup
markup = manager.add_markup(
    doc.document_id,
    description="Wall moved 6 inches south",
    location="Grid B-3",
    marked_by="Site Superintendent"
)

# Upload as-built
manager.upload_as_built(doc.document_id, "as-built/A-101-AB.pdf", "AB")

# Verify
manager.verify_document(doc.document_id, "Project Manager")

# Check completeness
report = manager.get_completeness_report()
print(f"Completion: {report['completion_percent']}%")
```

## Resources
- **DDC Book**: Chapter 5 - Project Closeout
