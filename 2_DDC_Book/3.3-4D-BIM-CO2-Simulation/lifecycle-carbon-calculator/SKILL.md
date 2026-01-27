---
name: lifecycle-carbon-calculator
description: "Calculate embodied carbon and lifecycle emissions for construction materials and projects. Support sustainable design decisions with carbon data."
---

# Lifecycle Carbon Calculator for Construction

## Overview

Calculate embodied carbon (EC) and lifecycle carbon emissions for construction materials, assemblies, and projects. Support sustainable design decisions and carbon reduction targets.

## Business Case

Carbon calculation supports:
- **Regulatory Compliance**: Meet carbon reporting requirements
- **Green Certifications**: LEED, BREEAM, Living Building Challenge
- **Design Optimization**: Choose lower-carbon alternatives
- **Sustainability Goals**: Track progress toward net-zero

## Technical Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import pandas as pd

class LifecycleStage(Enum):
    A1_A3 = "Product Stage (A1-A3)"  # Raw materials, transport, manufacturing
    A4 = "Transport to Site (A4)"
    A5 = "Construction (A5)"
    B1_B7 = "Use Stage (B1-B7)"  # Maintenance, repair, replacement
    C1_C4 = "End of Life (C1-C4)"  # Demolition, transport, disposal
    D = "Beyond Lifecycle (D)"  # Reuse, recycling potential

@dataclass
class MaterialCarbon:
    material_id: str
    name: str
    category: str
    unit: str
    carbon_a1_a3: float  # kgCO2e per unit
    carbon_a4: float
    carbon_a5: float
    carbon_b: float
    carbon_c: float
    carbon_d: float  # Usually negative (credit)
    density: float  # kg/m³ if applicable
    source: str
    epd_url: str = ""

@dataclass
class AssemblyCarbon:
    assembly_id: str
    name: str
    materials: List[Dict[str, Any]]
    total_carbon: float
    carbon_by_stage: Dict[str, float]

@dataclass
class ProjectCarbon:
    project_id: str
    name: str
    gross_area: float
    assemblies: List[AssemblyCarbon]
    total_embodied_carbon: float
    carbon_per_area: float
    carbon_by_stage: Dict[str, float]
    carbon_by_category: Dict[str, float]
    benchmark_comparison: Dict[str, Any]

class LifecycleCarbonCalculator:
    """Calculate lifecycle carbon for construction."""

    # Sample material carbon data (kgCO2e per unit)
    DEFAULT_MATERIALS = {
        'concrete_30mpa': MaterialCarbon(
            material_id='C30', name='Concrete 30MPa', category='Concrete',
            unit='m³', carbon_a1_a3=300, carbon_a4=5, carbon_a5=2,
            carbon_b=0, carbon_c=10, carbon_d=-20, density=2400,
            source='EPD Database'
        ),
        'concrete_40mpa': MaterialCarbon(
            material_id='C40', name='Concrete 40MPa', category='Concrete',
            unit='m³', carbon_a1_a3=350, carbon_a4=5, carbon_a5=2,
            carbon_b=0, carbon_c=10, carbon_d=-20, density=2400,
            source='EPD Database'
        ),
        'steel_rebar': MaterialCarbon(
            material_id='REBAR', name='Steel Reinforcing Bar', category='Steel',
            unit='kg', carbon_a1_a3=1.99, carbon_a4=0.05, carbon_a5=0.02,
            carbon_b=0, carbon_c=0.05, carbon_d=-0.5, density=7850,
            source='WorldSteel EPD'
        ),
        'steel_structural': MaterialCarbon(
            material_id='STEEL', name='Structural Steel', category='Steel',
            unit='kg', carbon_a1_a3=1.55, carbon_a4=0.05, carbon_a5=0.03,
            carbon_b=0, carbon_c=0.05, carbon_d=-0.8, density=7850,
            source='AISC EPD'
        ),
        'timber_clt': MaterialCarbon(
            material_id='CLT', name='Cross-Laminated Timber', category='Timber',
            unit='m³', carbon_a1_a3=-500, carbon_a4=10, carbon_a5=5,
            carbon_b=0, carbon_c=50, carbon_d=-100, density=500,
            source='AWC EPD'
        ),
        'gypsum_board': MaterialCarbon(
            material_id='GYP', name='Gypsum Board 12.5mm', category='Finishes',
            unit='m²', carbon_a1_a3=3.2, carbon_a4=0.2, carbon_a5=0.1,
            carbon_b=0, carbon_c=0.3, carbon_d=-0.1, density=10,
            source='EUROGYPSUM EPD'
        ),
        'insulation_mineral': MaterialCarbon(
            material_id='INS_MW', name='Mineral Wool Insulation', category='Insulation',
            unit='m³', carbon_a1_a3=45, carbon_a4=2, carbon_a5=1,
            carbon_b=0, carbon_c=5, carbon_d=-2, density=40,
            source='EURIMA EPD'
        ),
        'glass_double': MaterialCarbon(
            material_id='GLASS', name='Double Glazed Unit', category='Glazing',
            unit='m²', carbon_a1_a3=35, carbon_a4=1, carbon_a5=0.5,
            carbon_b=0, carbon_c=2, carbon_d=-5, density=25,
            source='Glass for Europe EPD'
        ),
        'aluminum': MaterialCarbon(
            material_id='ALU', name='Aluminum Profile', category='Metals',
            unit='kg', carbon_a1_a3=8.0, carbon_a4=0.1, carbon_a5=0.05,
            carbon_b=0, carbon_c=0.1, carbon_d=-4.0, density=2700,
            source='EAA EPD'
        ),
    }

    # Building type benchmarks (kgCO2e/m²)
    BENCHMARKS = {
        'Office': {'typical': 500, 'good': 350, 'best': 200},
        'Residential': {'typical': 400, 'good': 280, 'best': 150},
        'Retail': {'typical': 450, 'good': 320, 'best': 180},
        'Industrial': {'typical': 350, 'good': 250, 'best': 150},
        'Healthcare': {'typical': 700, 'good': 500, 'best': 350},
    }

    def __init__(self):
        self.materials: Dict[str, MaterialCarbon] = dict(self.DEFAULT_MATERIALS)
        self.assemblies: Dict[str, AssemblyCarbon] = {}

    def add_material(self, material: MaterialCarbon):
        """Add or update a material."""
        self.materials[material.material_id] = material

    def calculate_material_carbon(self, material_id: str, quantity: float,
                                   stages: List[LifecycleStage] = None) -> Dict:
        """Calculate carbon for a material quantity."""
        if material_id not in self.materials:
            raise ValueError(f"Unknown material: {material_id}")

        material = self.materials[material_id]

        if stages is None:
            stages = list(LifecycleStage)

        carbon_by_stage = {}
        total = 0

        for stage in stages:
            if stage == LifecycleStage.A1_A3:
                carbon = material.carbon_a1_a3 * quantity
            elif stage == LifecycleStage.A4:
                carbon = material.carbon_a4 * quantity
            elif stage == LifecycleStage.A5:
                carbon = material.carbon_a5 * quantity
            elif stage == LifecycleStage.B1_B7:
                carbon = material.carbon_b * quantity
            elif stage == LifecycleStage.C1_C4:
                carbon = material.carbon_c * quantity
            elif stage == LifecycleStage.D:
                carbon = material.carbon_d * quantity
            else:
                carbon = 0

            carbon_by_stage[stage.value] = carbon
            total += carbon

        return {
            'material_id': material_id,
            'material_name': material.name,
            'quantity': quantity,
            'unit': material.unit,
            'total_carbon': total,
            'carbon_by_stage': carbon_by_stage
        }

    def create_assembly(self, assembly_id: str, name: str,
                        components: List[Dict]) -> AssemblyCarbon:
        """Create an assembly from multiple materials."""
        total_carbon = 0
        carbon_by_stage = {stage.value: 0 for stage in LifecycleStage}
        material_details = []

        for comp in components:
            material_id = comp['material_id']
            quantity = comp['quantity']

            result = self.calculate_material_carbon(material_id, quantity)
            total_carbon += result['total_carbon']

            for stage, carbon in result['carbon_by_stage'].items():
                carbon_by_stage[stage] += carbon

            material_details.append({
                'material': result['material_name'],
                'quantity': quantity,
                'unit': result['unit'],
                'carbon': result['total_carbon']
            })

        assembly = AssemblyCarbon(
            assembly_id=assembly_id,
            name=name,
            materials=material_details,
            total_carbon=total_carbon,
            carbon_by_stage=carbon_by_stage
        )

        self.assemblies[assembly_id] = assembly
        return assembly

    def calculate_project_carbon(self, project_id: str, project_name: str,
                                  gross_area: float, building_type: str,
                                  quantities: List[Dict]) -> ProjectCarbon:
        """Calculate total project carbon."""
        assemblies = []
        total_carbon = 0
        carbon_by_stage = {stage.value: 0 for stage in LifecycleStage}
        carbon_by_category = {}

        for qty in quantities:
            if 'assembly_id' in qty:
                # Use predefined assembly
                if qty['assembly_id'] in self.assemblies:
                    assembly = self.assemblies[qty['assembly_id']]
                    multiplier = qty.get('multiplier', 1)
                    scaled_carbon = assembly.total_carbon * multiplier

                    assemblies.append(AssemblyCarbon(
                        assembly_id=assembly.assembly_id,
                        name=assembly.name,
                        materials=assembly.materials,
                        total_carbon=scaled_carbon,
                        carbon_by_stage={k: v * multiplier for k, v in assembly.carbon_by_stage.items()}
                    ))
                    total_carbon += scaled_carbon

            elif 'material_id' in qty:
                # Direct material
                result = self.calculate_material_carbon(
                    qty['material_id'], qty['quantity']
                )
                total_carbon += result['total_carbon']

                for stage, carbon in result['carbon_by_stage'].items():
                    carbon_by_stage[stage] += carbon

                # Track by category
                material = self.materials[qty['material_id']]
                cat = material.category
                carbon_by_category[cat] = carbon_by_category.get(cat, 0) + result['total_carbon']

        # Calculate metrics
        carbon_per_area = total_carbon / gross_area if gross_area > 0 else 0

        # Compare to benchmarks
        benchmark = self.BENCHMARKS.get(building_type, self.BENCHMARKS['Office'])
        benchmark_comparison = {
            'carbon_per_area': carbon_per_area,
            'typical_benchmark': benchmark['typical'],
            'good_benchmark': benchmark['good'],
            'best_benchmark': benchmark['best'],
            'vs_typical': (carbon_per_area / benchmark['typical'] - 1) * 100,
            'rating': self._get_rating(carbon_per_area, benchmark)
        }

        return ProjectCarbon(
            project_id=project_id,
            name=project_name,
            gross_area=gross_area,
            assemblies=assemblies,
            total_embodied_carbon=total_carbon,
            carbon_per_area=carbon_per_area,
            carbon_by_stage=carbon_by_stage,
            carbon_by_category=carbon_by_category,
            benchmark_comparison=benchmark_comparison
        )

    def _get_rating(self, carbon: float, benchmark: Dict) -> str:
        """Get rating based on benchmark comparison."""
        if carbon <= benchmark['best']:
            return 'A (Best Practice)'
        elif carbon <= benchmark['good']:
            return 'B (Good Practice)'
        elif carbon <= benchmark['typical']:
            return 'C (Typical)'
        else:
            return 'D (Above Typical)'

    def compare_alternatives(self, base_project: ProjectCarbon,
                              alternatives: List[Dict]) -> pd.DataFrame:
        """Compare carbon of design alternatives."""
        comparisons = [{
            'Option': 'Base Design',
            'Total Carbon (tCO2e)': base_project.total_embodied_carbon / 1000,
            'Carbon/m² (kgCO2e)': base_project.carbon_per_area,
            'vs Base': '0%',
            'Rating': base_project.benchmark_comparison['rating']
        }]

        for alt in alternatives:
            project = self.calculate_project_carbon(
                alt['id'], alt['name'], alt['gross_area'],
                alt.get('building_type', 'Office'), alt['quantities']
            )

            change = (project.total_embodied_carbon - base_project.total_embodied_carbon) / base_project.total_embodied_carbon * 100

            comparisons.append({
                'Option': alt['name'],
                'Total Carbon (tCO2e)': project.total_embodied_carbon / 1000,
                'Carbon/m² (kgCO2e)': project.carbon_per_area,
                'vs Base': f'{change:+.1f}%',
                'Rating': project.benchmark_comparison['rating']
            })

        return pd.DataFrame(comparisons)

    def suggest_reductions(self, project: ProjectCarbon) -> List[Dict]:
        """Suggest carbon reduction opportunities."""
        suggestions = []

        # Analyze by category
        if 'Concrete' in project.carbon_by_category:
            concrete_carbon = project.carbon_by_category['Concrete']
            if concrete_carbon > project.total_embodied_carbon * 0.3:
                suggestions.append({
                    'category': 'Concrete',
                    'current_carbon': concrete_carbon,
                    'suggestion': 'Consider low-carbon concrete (GGBS/PFA replacement)',
                    'potential_reduction': '20-40%',
                    'impact': concrete_carbon * 0.3
                })

        if 'Steel' in project.carbon_by_category:
            steel_carbon = project.carbon_by_category['Steel']
            if steel_carbon > project.total_embodied_carbon * 0.2:
                suggestions.append({
                    'category': 'Steel',
                    'current_carbon': steel_carbon,
                    'suggestion': 'Specify high recycled content steel',
                    'potential_reduction': '10-25%',
                    'impact': steel_carbon * 0.2
                })

        # Benchmark-based suggestions
        if project.benchmark_comparison['vs_typical'] > 0:
            suggestions.append({
                'category': 'Overall',
                'current_carbon': project.total_embodied_carbon,
                'suggestion': 'Project exceeds typical benchmark - review high-carbon elements',
                'potential_reduction': f"{abs(project.benchmark_comparison['vs_typical']):.0f}%",
                'impact': project.total_embodied_carbon * abs(project.benchmark_comparison['vs_typical']) / 100
            })

        return sorted(suggestions, key=lambda x: -x['impact'])

    def generate_report(self, project: ProjectCarbon) -> str:
        """Generate carbon assessment report."""
        lines = ["# Embodied Carbon Assessment Report", ""]
        lines.append(f"**Project:** {project.name}")
        lines.append(f"**Gross Area:** {project.gross_area:,.0f} m²")
        lines.append(f"**Assessment Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}")
        lines.append("")

        # Summary
        lines.append("## Carbon Summary")
        lines.append(f"- **Total Embodied Carbon:** {project.total_embodied_carbon/1000:,.0f} tCO2e")
        lines.append(f"- **Carbon Intensity:** {project.carbon_per_area:,.0f} kgCO2e/m²")
        lines.append(f"- **Rating:** {project.benchmark_comparison['rating']}")
        lines.append("")

        # By lifecycle stage
        lines.append("## Carbon by Lifecycle Stage")
        for stage, carbon in project.carbon_by_stage.items():
            if carbon != 0:
                pct = carbon / project.total_embodied_carbon * 100
                lines.append(f"- {stage}: {carbon/1000:,.1f} tCO2e ({pct:.1f}%)")
        lines.append("")

        # By category
        lines.append("## Carbon by Material Category")
        for cat, carbon in sorted(project.carbon_by_category.items(), key=lambda x: -x[1]):
            pct = carbon / project.total_embodied_carbon * 100
            lines.append(f"- {cat}: {carbon/1000:,.1f} tCO2e ({pct:.1f}%)")
        lines.append("")

        # Benchmark
        lines.append("## Benchmark Comparison")
        bc = project.benchmark_comparison
        lines.append(f"- Project: {bc['carbon_per_area']:.0f} kgCO2e/m²")
        lines.append(f"- Typical: {bc['typical_benchmark']} kgCO2e/m²")
        lines.append(f"- Good Practice: {bc['good_benchmark']} kgCO2e/m²")
        lines.append(f"- Best Practice: {bc['best_benchmark']} kgCO2e/m²")
        lines.append("")

        # Reduction opportunities
        suggestions = self.suggest_reductions(project)
        if suggestions:
            lines.append("## Reduction Opportunities")
            for sug in suggestions[:5]:
                lines.append(f"\n### {sug['category']}")
                lines.append(f"- **Suggestion:** {sug['suggestion']}")
                lines.append(f"- **Potential Reduction:** {sug['potential_reduction']}")
                lines.append(f"- **Impact:** {sug['impact']/1000:,.1f} tCO2e")

        return "\n".join(lines)
```

## Quick Start

```python
# Initialize calculator
calc = LifecycleCarbonCalculator()

# Calculate project carbon
project = calc.calculate_project_carbon(
    project_id="PROJ-001",
    project_name="Office Building",
    gross_area=5000,
    building_type="Office",
    quantities=[
        {'material_id': 'concrete_40mpa', 'quantity': 1500},  # m³
        {'material_id': 'steel_rebar', 'quantity': 150000},   # kg
        {'material_id': 'steel_structural', 'quantity': 200000},
        {'material_id': 'gypsum_board', 'quantity': 8000},    # m²
        {'material_id': 'glass_double', 'quantity': 1200},    # m²
    ]
)

print(f"Total Carbon: {project.total_embodied_carbon/1000:,.0f} tCO2e")
print(f"Carbon Intensity: {project.carbon_per_area:,.0f} kgCO2e/m²")
print(f"Rating: {project.benchmark_comparison['rating']}")

# Get reduction suggestions
suggestions = calc.suggest_reductions(project)
for sug in suggestions:
    print(f"- {sug['category']}: {sug['suggestion']}")

# Generate full report
report = calc.generate_report(project)
print(report)
```

## Dependencies

```bash
pip install pandas
```
