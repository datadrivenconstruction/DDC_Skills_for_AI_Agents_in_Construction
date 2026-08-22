---
name: "material-passports-circular"
description: "Material passports and circular construction: generate per-element material inventories from BOQ/BIM, mark reuse potential and recycled content, and prepare deconstruction data. Use for circular-economy and EU Taxonomy-aligned projects."
---

# Material Passports & Circular Construction (2026)

## Why it matters

The EU Taxonomy and CSRD push construction toward circularity: buildings must be designed for disassembly, materials traceable for reuse. A **material passport** is a digital record of what is in a building, where, and how it can be reused at end of life.

## What a passport contains

Per element (or per BOQ line):

| Field | Source |
|---|---|
| material & volume/mass | BOQ components[] (`resource_name`, `resource_quantity`, `resource_unit`) |
| location in the building | BIM element link |
| manufacturer / EPD | procurement records |
| recycled content % | supplier declaration / EPD |
| reuse potential at EOL | disassembly class (reusable / recyclable / downcyclable / landfill) |
| embodied carbon (A1–A3) | `embodied-carbon-esg` skill |

## Building the passport from DDC data

```python
# per BOQ line: material inventory from CWICR components
for line in boq:
    for comp in line["components"]:
        if comp["type"] == "material":
            passport.append({
                "element": line["description"],
                "material": comp["name"],
                "quantity": line_quantity * comp["quantity"],
                "unit": comp["unit"],
                "recycled_content": epd_lookup(comp["name"]),   # from EPD library
                "reuse_class": disassembly_class(comp["name"]),  # rule-based
            })
```

## Design-for-disassembly rules to encode

1. Prefer mechanical fixings over wet trades (plaster/glue) at interfaces.
2. Mark structural vs non-structural layers — non-structural is the reuse pool.
3. One material per composite where possible (separate insulation from structure).
4. Record as-built changes — the passport must match the building, not the drawing.

## Reporting

- Total mass per material family (concrete, steel, timber, glass, insulation…).
- % recyclable/reusable by mass (EU Taxonomy circularity KPI).
- Hazardous content register (asbestos-free declaration, formaldehyde, VOC).

## Resources

- EU Level(s) framework: https://environment.ec.europa.eu/topics/circular-economy/levels_en
- Madaster (material passport platform): https://madaster.com
- EPD libraries: https://www.eco-platform.org
