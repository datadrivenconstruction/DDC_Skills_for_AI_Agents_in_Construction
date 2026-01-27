---
name: clash-resolution-analyzer
description: "Analyze BIM clash detection results and suggest resolutions. Prioritize clashes, identify patterns, assign responsibility, and track resolution status."
---

# Clash Resolution Analyzer for Construction

## Overview

Analyze clash detection results from BIM coordination. Prioritize clashes by impact, identify patterns, suggest resolutions, assign responsibility, and track resolution progress.

## Business Case

Clash resolution analysis enables:
- **Efficient Coordination**: Focus on critical clashes first
- **Pattern Recognition**: Fix root causes, not symptoms
- **Clear Accountability**: Assign responsibility by trade
- **Progress Tracking**: Monitor resolution status

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
from collections import defaultdict

class ClashPriority(Enum):
    CRITICAL = 1  # Must resolve before construction
    HIGH = 2      # Resolve in next coordination cycle
    MEDIUM = 3    # Resolve before trade starts
    LOW = 4       # Minor, can resolve in field

class ClashStatus(Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    APPROVED = "approved"
    VOID = "void"  # Not a real clash

class ResolutionType(Enum):
    ROUTE_AROUND = "Route around obstruction"
    RAISE_LOWER = "Raise or lower element"
    RESIZE = "Resize element"
    RELOCATE = "Relocate element"
    STRUCTURAL_MOD = "Structural modification required"
    DESIGN_CHANGE = "Design change required"
    NO_CLASH = "Not a real clash (tolerance)"
    SEQUENCE = "Resolve by construction sequence"

@dataclass
class ClashElement:
    id: str
    name: str
    category: str
    discipline: str
    level: str
    system: str

@dataclass
class Clash:
    id: str
    name: str
    element1: ClashElement
    element2: ClashElement
    location: Tuple[float, float, float]
    distance: float  # Negative = hard clash, positive = clearance violation
    clash_type: str  # hard, clearance, duplicate
    priority: ClashPriority = ClashPriority.MEDIUM
    status: ClashStatus = ClashStatus.NEW
    assigned_to: str = ""
    resolution_type: Optional[ResolutionType] = None
    resolution_notes: str = ""
    created_date: datetime = field(default_factory=datetime.now)
    resolved_date: Optional[datetime] = None

@dataclass
class ClashPattern:
    pattern_type: str
    disciplines: Tuple[str, str]
    systems: Tuple[str, str]
    clash_count: int
    example_clashes: List[str]
    suggested_resolution: str
    root_cause: str

@dataclass
class ClashReport:
    report_name: str
    total_clashes: int
    new_clashes: int
    resolved_clashes: int
    clashes_by_priority: Dict[str, int]
    clashes_by_discipline: Dict[str, int]
    clashes_by_status: Dict[str, int]
    patterns: List[ClashPattern]
    resolution_rate: float

class ClashResolutionAnalyzer:
    """Analyze and manage BIM clash detection results."""

    # Discipline priority for resolution responsibility
    DISCIPLINE_PRIORITY = {
        'Structural': 1,
        'Architectural': 2,
        'Mechanical': 3,
        'Plumbing': 4,
        'Electrical': 5,
        'Fire Protection': 6,
    }

    # Common resolution strategies by clash type
    RESOLUTION_STRATEGIES = {
        ('Mechanical', 'Structural'): {
            'strategy': ResolutionType.ROUTE_AROUND,
            'responsible': 'Mechanical',
            'notes': 'MEP typically routes around structure'
        },
        ('Plumbing', 'Structural'): {
            'strategy': ResolutionType.ROUTE_AROUND,
            'responsible': 'Plumbing',
            'notes': 'Coordinate sleeves/penetrations with SE'
        },
        ('Electrical', 'Mechanical'): {
            'strategy': ResolutionType.RAISE_LOWER,
            'responsible': 'Electrical',
            'notes': 'Conduit typically more flexible than ductwork'
        },
        ('Mechanical', 'Mechanical'): {
            'strategy': ResolutionType.RESIZE,
            'responsible': 'Mechanical',
            'notes': 'Review duct sizing and routing options'
        },
        ('Fire Protection', 'Mechanical'): {
            'strategy': ResolutionType.ROUTE_AROUND,
            'responsible': 'Fire Protection',
            'notes': 'Sprinkler typically routes around major duct'
        },
    }

    def __init__(self):
        self.clashes: Dict[str, Clash] = {}
        self.patterns: List[ClashPattern] = []
        self.history: List[Dict] = []

    def import_clashes(self, clash_data: List[Dict]) -> int:
        """Import clashes from Navisworks or other clash detection software."""
        count = 0

        for data in clash_data:
            clash = Clash(
                id=data.get('id', f'CLH-{count}'),
                name=data.get('name', ''),
                element1=ClashElement(
                    id=data.get('element1_id', ''),
                    name=data.get('element1_name', ''),
                    category=data.get('element1_category', ''),
                    discipline=data.get('element1_discipline', ''),
                    level=data.get('element1_level', ''),
                    system=data.get('element1_system', '')
                ),
                element2=ClashElement(
                    id=data.get('element2_id', ''),
                    name=data.get('element2_name', ''),
                    category=data.get('element2_category', ''),
                    discipline=data.get('element2_discipline', ''),
                    level=data.get('element2_level', ''),
                    system=data.get('element2_system', '')
                ),
                location=(
                    data.get('x', 0),
                    data.get('y', 0),
                    data.get('z', 0)
                ),
                distance=data.get('distance', 0),
                clash_type=data.get('clash_type', 'hard')
            )

            # Auto-prioritize
            clash.priority = self._auto_prioritize(clash)

            # Auto-assign
            clash.assigned_to = self._auto_assign(clash)

            self.clashes[clash.id] = clash
            count += 1

        return count

    def _auto_prioritize(self, clash: Clash) -> ClashPriority:
        """Automatically prioritize clash based on characteristics."""
        # Hard clashes with structure are critical
        if clash.element1.discipline == 'Structural' or clash.element2.discipline == 'Structural':
            if clash.clash_type == 'hard':
                return ClashPriority.CRITICAL

        # Large penetration clashes
        if abs(clash.distance) > 0.1:  # More than 100mm overlap
            return ClashPriority.HIGH

        # MEP-MEP clashes
        mep_disciplines = ['Mechanical', 'Electrical', 'Plumbing', 'Fire Protection']
        if clash.element1.discipline in mep_disciplines and clash.element2.discipline in mep_disciplines:
            return ClashPriority.MEDIUM

        # Clearance violations
        if clash.clash_type == 'clearance':
            return ClashPriority.LOW

        return ClashPriority.MEDIUM

    def _auto_assign(self, clash: Clash) -> str:
        """Automatically assign responsibility based on discipline priority."""
        d1 = clash.element1.discipline
        d2 = clash.element2.discipline

        # Check for known resolution strategy
        key = (d1, d2) if (d1, d2) in self.RESOLUTION_STRATEGIES else (d2, d1)
        if key in self.RESOLUTION_STRATEGIES:
            return self.RESOLUTION_STRATEGIES[key]['responsible']

        # Default to lower priority discipline (typically more flexible)
        p1 = self.DISCIPLINE_PRIORITY.get(d1, 10)
        p2 = self.DISCIPLINE_PRIORITY.get(d2, 10)

        return d2 if p2 > p1 else d1

    def analyze_patterns(self) -> List[ClashPattern]:
        """Identify patterns in clashes."""
        patterns = []

        # Group by discipline pair
        discipline_pairs = defaultdict(list)
        for clash in self.clashes.values():
            pair = tuple(sorted([clash.element1.discipline, clash.element2.discipline]))
            discipline_pairs[pair].append(clash)

        for (d1, d2), clashes in discipline_pairs.items():
            if len(clashes) >= 3:  # Pattern threshold
                # Further group by system
                system_pairs = defaultdict(list)
                for clash in clashes:
                    sys_pair = tuple(sorted([clash.element1.system, clash.element2.system]))
                    system_pairs[sys_pair].append(clash)

                for (s1, s2), sys_clashes in system_pairs.items():
                    if len(sys_clashes) >= 2:
                        # Get resolution strategy
                        key = (d1, d2) if (d1, d2) in self.RESOLUTION_STRATEGIES else (d2, d1)
                        strategy = self.RESOLUTION_STRATEGIES.get(key, {})

                        patterns.append(ClashPattern(
                            pattern_type=f"{d1} vs {d2}",
                            disciplines=(d1, d2),
                            systems=(s1, s2),
                            clash_count=len(sys_clashes),
                            example_clashes=[c.id for c in sys_clashes[:3]],
                            suggested_resolution=strategy.get('strategy', ResolutionType.ROUTE_AROUND).value,
                            root_cause=f"Coordination needed between {s1} and {s2} systems"
                        ))

        self.patterns = sorted(patterns, key=lambda p: -p.clash_count)
        return self.patterns

    def suggest_resolution(self, clash_id: str) -> Dict:
        """Suggest resolution for a specific clash."""
        if clash_id not in self.clashes:
            return {'error': 'Clash not found'}

        clash = self.clashes[clash_id]
        d1, d2 = clash.element1.discipline, clash.element2.discipline

        # Get strategy
        key = (d1, d2) if (d1, d2) in self.RESOLUTION_STRATEGIES else (d2, d1)
        strategy = self.RESOLUTION_STRATEGIES.get(key, {})

        suggestion = {
            'clash_id': clash_id,
            'resolution_type': strategy.get('strategy', ResolutionType.ROUTE_AROUND),
            'responsible_discipline': strategy.get('responsible', self._auto_assign(clash)),
            'notes': strategy.get('notes', 'Review and coordinate'),
            'similar_clashes': [],
        }

        # Find similar clashes
        for pattern in self.patterns:
            if d1 in pattern.disciplines and d2 in pattern.disciplines:
                suggestion['similar_clashes'] = pattern.example_clashes
                suggestion['pattern_root_cause'] = pattern.root_cause
                break

        return suggestion

    def update_clash_status(self, clash_id: str, status: ClashStatus,
                            resolution_type: ResolutionType = None,
                            notes: str = "") -> bool:
        """Update clash status."""
        if clash_id not in self.clashes:
            return False

        clash = self.clashes[clash_id]
        old_status = clash.status

        clash.status = status
        if resolution_type:
            clash.resolution_type = resolution_type
        if notes:
            clash.resolution_notes = notes
        if status in [ClashStatus.RESOLVED, ClashStatus.APPROVED]:
            clash.resolved_date = datetime.now()

        # Track history
        self.history.append({
            'clash_id': clash_id,
            'timestamp': datetime.now(),
            'old_status': old_status.value,
            'new_status': status.value,
            'notes': notes
        })

        return True

    def get_clashes_by_discipline(self, discipline: str) -> List[Clash]:
        """Get all clashes assigned to a discipline."""
        return [c for c in self.clashes.values() if c.assigned_to == discipline]

    def get_clashes_by_level(self, level: str) -> List[Clash]:
        """Get all clashes on a specific level."""
        return [c for c in self.clashes.values()
                if c.element1.level == level or c.element2.level == level]

    def generate_coordination_matrix(self) -> Dict[str, Dict[str, int]]:
        """Generate matrix showing clashes between disciplines."""
        matrix = defaultdict(lambda: defaultdict(int))

        for clash in self.clashes.values():
            d1 = clash.element1.discipline
            d2 = clash.element2.discipline
            matrix[d1][d2] += 1
            if d1 != d2:
                matrix[d2][d1] += 1

        return dict(matrix)

    def generate_report(self) -> ConsistencyReport:
        """Generate comprehensive clash analysis report."""
        clashes_by_priority = defaultdict(int)
        clashes_by_discipline = defaultdict(int)
        clashes_by_status = defaultdict(int)

        for clash in self.clashes.values():
            clashes_by_priority[clash.priority.name] += 1
            clashes_by_discipline[clash.assigned_to] += 1
            clashes_by_status[clash.status.value] += 1

        resolved = clashes_by_status.get('resolved', 0) + clashes_by_status.get('approved', 0)
        resolution_rate = resolved / len(self.clashes) * 100 if self.clashes else 0

        return ClashReport(
            report_name=f"Clash Report {datetime.now().strftime('%Y-%m-%d')}",
            total_clashes=len(self.clashes),
            new_clashes=clashes_by_status.get('new', 0),
            resolved_clashes=resolved,
            clashes_by_priority=dict(clashes_by_priority),
            clashes_by_discipline=dict(clashes_by_discipline),
            clashes_by_status=dict(clashes_by_status),
            patterns=self.patterns,
            resolution_rate=resolution_rate
        )

    def generate_report_markdown(self) -> str:
        """Generate markdown report."""
        report = self.generate_report()

        lines = ["# Clash Resolution Report", ""]
        lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
        lines.append(f"**Total Clashes:** {report.total_clashes}")
        lines.append(f"**Resolution Rate:** {report.resolution_rate:.1f}%")
        lines.append("")

        # By status
        lines.append("## Status Summary")
        for status, count in report.clashes_by_status.items():
            lines.append(f"- {status}: {count}")
        lines.append("")

        # By priority
        lines.append("## Priority Breakdown")
        for priority, count in sorted(report.clashes_by_priority.items()):
            lines.append(f"- {priority}: {count}")
        lines.append("")

        # By discipline
        lines.append("## By Responsible Discipline")
        for disc, count in sorted(report.clashes_by_discipline.items(), key=lambda x: -x[1]):
            lines.append(f"- {disc}: {count}")
        lines.append("")

        # Patterns
        if report.patterns:
            lines.append("## Clash Patterns Identified")
            for pattern in report.patterns[:5]:
                lines.append(f"\n### {pattern.pattern_type}")
                lines.append(f"- **Count:** {pattern.clash_count} clashes")
                lines.append(f"- **Systems:** {pattern.systems[0]} vs {pattern.systems[1]}")
                lines.append(f"- **Root Cause:** {pattern.root_cause}")
                lines.append(f"- **Suggested Resolution:** {pattern.suggested_resolution}")

        # Critical clashes
        critical = [c for c in self.clashes.values() if c.priority == ClashPriority.CRITICAL and c.status == ClashStatus.NEW]
        if critical:
            lines.append("\n## Critical Unresolved Clashes")
            for clash in critical[:10]:
                lines.append(f"- **{clash.id}**: {clash.element1.name} vs {clash.element2.name}")
                lines.append(f"  - Location: Level {clash.element1.level}")
                lines.append(f"  - Assigned: {clash.assigned_to}")

        return "\n".join(lines)
```

## Quick Start

```python
# Initialize analyzer
analyzer = ClashResolutionAnalyzer()

# Import clashes (from Navisworks export)
clash_data = [
    {
        'id': 'CLH-001',
        'name': 'Duct vs Beam',
        'element1_discipline': 'Mechanical',
        'element1_system': 'Supply Air',
        'element1_level': 'Level 2',
        'element2_discipline': 'Structural',
        'element2_system': 'Steel Frame',
        'element2_level': 'Level 2',
        'distance': -0.15,
        'clash_type': 'hard'
    }
]

count = analyzer.import_clashes(clash_data)
print(f"Imported {count} clashes")

# Analyze patterns
patterns = analyzer.analyze_patterns()
for pattern in patterns:
    print(f"Pattern: {pattern.pattern_type} - {pattern.clash_count} clashes")

# Get resolution suggestion
suggestion = analyzer.suggest_resolution('CLH-001')
print(f"Suggested resolution: {suggestion['resolution_type'].value}")
print(f"Responsible: {suggestion['responsible_discipline']}")

# Update status
analyzer.update_clash_status(
    'CLH-001',
    ClashStatus.RESOLVED,
    ResolutionType.ROUTE_AROUND,
    'Duct rerouted below beam'
)

# Generate report
print(analyzer.generate_report_markdown())
```

## Dependencies

```bash
pip install (no external dependencies)
```
