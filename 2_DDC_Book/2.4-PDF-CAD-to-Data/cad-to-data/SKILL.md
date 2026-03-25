---
name: "cad-to-data"
description: "Convert CAD/BIM files (Revit, IFC, DWG, DGN) to structured JSON, CSV, or DataFrames. Extract element properties, quantities, materials, and relationships. Use when parsing .ifc, .rvt, .dwg, .dxf, or .dgn files, running quantity takeoffs from BIM models, or extracting building component schedules."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw":{"emoji":"🗂️","os":["darwin","linux","win32"],"homepage":"https://datadrivenconstruction.io","requires":{"bins":["python3"]}}}
---
# CAD To Data

Based on DDC methodology (Chapter 2.4), convert CAD and BIM files to structured data. Extracts element properties, quantities, materials, and relationships from Revit, IFC, DWG, DGN, and DXF files.

**Book Reference:** "Data Transformation to Structured Form"

## Workflow

1. **Detect format** from file extension (.ifc, .rvt, .dwg, .dxf, .dgn)
2. **Extract elements** using the appropriate parser (ifcopenshell for IFC, ezdxf for DWG/DXF)
3. **Validate extraction** — check element count > 0 and expected categories are present
4. **Transform** to structured output (JSON, CSV, or DataFrame)
5. **Export** quantities, schedules, or full element data

## Quick Start

```python
# IFC extraction using ifcopenshell
import ifcopenshell

ifc_file = ifcopenshell.open("building.ifc")

# Extract all walls
walls = ifc_file.by_type("IfcWall")
for wall in walls:
    psets = ifcopenshell.util.element.get_psets(wall)
    print(f"{wall.Name}: {psets}")

# Extract quantities
import ifcopenshell.util.element
for wall in walls:
    qtos = ifcopenshell.util.element.get_psets(wall, qtos_only=True)
    print(f"{wall.Name} quantities: {qtos}")
```

```python
# DWG/DXF extraction using ezdxf
import ezdxf

doc = ezdxf.readfile("drawing.dwg")
msp = doc.modelspace()

# Extract all entities by layer
for entity in msp:
    print(f"Type: {entity.dxftype()}, Layer: {entity.dxf.layer}")

# Filter by layer
walls = msp.query('LWPOLYLINE[layer=="Walls"]')
print(f"Wall polylines found: {len(list(walls))}")
```

## Common Use Cases

### Full BIM-to-JSON Conversion

```python
from cad_to_data import CADDataConverter

converter = CADDataConverter()
data = converter.convert("building.ifc", output_format="json")

# Validate extraction
assert data['total_elements'] > 0, "No elements extracted"
print(f"Total elements: {data['total_elements']}")
print(f"Categories: {data['categories']}")

for element in data['elements'][:5]:
    print(f"  {element['name']}: {element['type']}")
```

### Quantity Takeoff

```python
from cad_to_data import CADDataConverter, ElementCategory

converter = CADDataConverter()
quantities = converter.extract_quantities(
    "building.ifc",
    categories=[ElementCategory.WALL, ElementCategory.FLOOR]
)

print(f"Wall count: {quantities['quantities']['wall']['count']}")
print(f"Total wall area: {quantities['quantities']['wall']['totals']['Area']} m2")
```

### Door/Window Schedule

```python
door_schedule = converter.extract_schedule(
    "building.ifc",
    category=ElementCategory.DOOR,
    fields=["Width", "Height", "FireRating", "IsExternal"]
)

for door in door_schedule:
    print(f"{door['name']}: {door.get('Width')}x{door.get('Height')}")
```

### Generate Extraction Report

```python
from cad_to_data import IFCExtractor

extractor = IFCExtractor()
result = extractor.extract("building.ifc")
report = converter.generate_report(result)
print(report)
```

## Supported Formats

| Format | Extension | Parser Library | Element Types |
|--------|-----------|---------------|---------------|
| IFC | .ifc | ifcopenshell | Full BIM elements with properties, quantities, materials |
| Revit | .rvt | Revit API / pyrevit | Families, types, parameters |
| DWG | .dwg | ezdxf | Entities, layers, blocks |
| DXF | .dxf | ezdxf | Entities, layers, blocks |
| DGN | .dgn | Bentley SDK | Elements, levels, cells |
| NWD | .nwd | Navisworks API | Aggregated model data |

## IFC Type Mapping

| IFC Type | Category | Common Properties |
|----------|----------|-------------------|
| IfcWall | wall | IsExternal, FireRating, LoadBearing |
| IfcSlab | floor | IsExternal, LoadBearing |
| IfcDoor | door | FireRating, IsExternal, HandicapAccessible |
| IfcWindow | window | ThermalTransmittance, IsExternal |
| IfcColumn | column | LoadBearing, FireRating |
| IfcBeam | beam | LoadBearing, Span |
| IfcSpace | space | OccupancyType, NetFloorArea |
| IfcPipeSegment | pipe | NominalDiameter, SystemType |
| IfcDuctSegment | duct | NominalDiameter, SystemType |

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `CADDataConverter` | Main conversion engine (format detection + extraction) |
| `IFCExtractor` | IFC file extraction via ifcopenshell |
| `DWGExtractor` | DWG/DXF extraction via ezdxf |
| `convert()` | Full file-to-JSON/CSV conversion |
| `extract_quantities()` | Aggregated quantity takeoff by category |
| `extract_schedule()` | Element schedule with selected properties |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 2.4
- **ifcopenshell**: https://ifcopenshell.org — IFC parsing library
- **ezdxf**: https://ezdxf.mozman.at — DWG/DXF parsing library
- **Website**: https://datadrivenconstruction.io

## Next Steps

- Use [image-to-data](../image-to-data/SKILL.md) for image extraction
- Use [qto-report](../../3.2-QTO-Auto-Estimates/qto-report/SKILL.md) for quantity reports
- Use [bim-validation-pipeline](../../4.3-BIM-Validation-Pipeline/bim-validation-pipeline/SKILL.md) for validation
