---
name: bim-visual-programming-automation
description: "Automate BIM workflows using visual programming and Python. Create parametric schedules, export data, batch modify elements, and integrate with external data sources."
---

# BIM Visual Programming Automation

## Overview

This skill provides visual programming scripts and Python nodes for automating BIM workflows. Extract data, modify elements in batch, generate schedules, and integrate with external systems.

> **Note:** Examples use Autodesk® Revit® and Dynamo™ APIs. Autodesk, Revit, and Dynamo are registered trademarks of Autodesk, Inc.

**Key Capabilities:**
- Batch element modification
- Data export/import
- Schedule generation
- Parameter management
- External data integration
- Automated QTO

## Quick Start (Dynamo Python)

```python
# Dynamo Python Script - Export all walls to Excel
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory

doc = DocumentManager.Instance.CurrentDBDocument

# Get all walls
collector = FilteredElementCollector(doc)
walls = collector.OfCategory(BuiltInCategory.OST_Walls).WhereElementIsNotElementType().ToElements()

# Extract data
wall_data = []
for wall in walls:
    wall_data.append({
        'id': wall.Id.IntegerValue,
        'name': wall.Name,
        'length': wall.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble() * 0.3048,
        'area': wall.get_Parameter(BuiltInParameter.HOST_AREA_COMPUTED).AsDouble() * 0.0929
    })

OUT = wall_data
```

## Element Data Extraction

### Comprehensive Element Extractor

```python
# Dynamo Python Node - Extract all element data
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
clr.AddReference('RevitNodes')

from RevitServices.Persistence import DocumentManager
from Autodesk.Revit.DB import *
import Revit
clr.ImportExtensions(Revit.Elements)

doc = DocumentManager.Instance.CurrentDBDocument

def get_element_data(element):
    """Extract data from Revit element"""
    data = {
        'id': element.Id.IntegerValue,
        'category': element.Category.Name if element.Category else None,
        'name': element.Name,
        'level': None,
        'parameters': {}
    }

    # Get level
    level_param = element.get_Parameter(BuiltInParameter.SCHEDULE_LEVEL_PARAM)
    if level_param:
        level_id = level_param.AsElementId()
        if level_id.IntegerValue > 0:
            level = doc.GetElement(level_id)
            data['level'] = level.Name if level else None

    # Get all parameters
    for param in element.Parameters:
        try:
            if param.HasValue:
                if param.StorageType == StorageType.Double:
                    data['parameters'][param.Definition.Name] = param.AsDouble()
                elif param.StorageType == StorageType.Integer:
                    data['parameters'][param.Definition.Name] = param.AsInteger()
                elif param.StorageType == StorageType.String:
                    data['parameters'][param.Definition.Name] = param.AsString()
        except:
            pass

    return data

def extract_category(category_enum):
    """Extract all elements of a category"""
    collector = FilteredElementCollector(doc)
    elements = collector.OfCategory(category_enum).WhereElementIsNotElementType().ToElements()
    return [get_element_data(e) for e in elements]

# Extract structural elements
categories = [
    BuiltInCategory.OST_Walls,
    BuiltInCategory.OST_Floors,
    BuiltInCategory.OST_StructuralColumns,
    BuiltInCategory.OST_StructuralFraming,
    BuiltInCategory.OST_Doors,
    BuiltInCategory.OST_Windows
]

all_data = {}
for cat in categories:
    cat_name = cat.ToString().replace('OST_', '')
    all_data[cat_name] = extract_category(cat)

OUT = all_data
```

### Quantity Take-Off Script

```python
# Dynamo Python - QTO Export
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from Autodesk.Revit.DB import *

doc = DocumentManager.Instance.CurrentDBDocument

def get_qto_data():
    """Generate QTO data from model"""
    qto = {}

    # Walls
    walls = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Walls)\
        .WhereElementIsNotElementType().ToElements()

    wall_qto = {}
    for wall in walls:
        wall_type = doc.GetElement(wall.GetTypeId())
        type_name = wall_type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()

        if type_name not in wall_qto:
            wall_qto[type_name] = {'count': 0, 'area': 0, 'length': 0}

        wall_qto[type_name]['count'] += 1

        area_param = wall.get_Parameter(BuiltInParameter.HOST_AREA_COMPUTED)
        if area_param:
            wall_qto[type_name]['area'] += area_param.AsDouble() * 0.0929  # sqft to m2

        length_param = wall.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH)
        if length_param:
            wall_qto[type_name]['length'] += length_param.AsDouble() * 0.3048  # ft to m

    qto['Walls'] = wall_qto

    # Floors
    floors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Floors)\
        .WhereElementIsNotElementType().ToElements()

    floor_qto = {}
    for floor in floors:
        floor_type = doc.GetElement(floor.GetTypeId())
        type_name = floor_type.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()

        if type_name not in floor_qto:
            floor_qto[type_name] = {'count': 0, 'area': 0, 'volume': 0}

        floor_qto[type_name]['count'] += 1

        area_param = floor.get_Parameter(BuiltInParameter.HOST_AREA_COMPUTED)
        if area_param:
            floor_qto[type_name]['area'] += area_param.AsDouble() * 0.0929

        vol_param = floor.get_Parameter(BuiltInParameter.HOST_VOLUME_COMPUTED)
        if vol_param:
            floor_qto[type_name]['volume'] += vol_param.AsDouble() * 0.0283  # cuft to m3

    qto['Floors'] = floor_qto

    return qto

OUT = get_qto_data()
```

## Batch Modification

### Batch Parameter Update

```python
# Dynamo Python - Batch update parameters
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import *

doc = DocumentManager.Instance.CurrentDBDocument

def batch_update_parameter(elements, param_name, values):
    """Update parameter for multiple elements"""
    TransactionManager.Instance.EnsureInTransaction(doc)

    results = []
    for elem, value in zip(elements, values):
        try:
            param = elem.LookupParameter(param_name)
            if param and not param.IsReadOnly:
                if param.StorageType == StorageType.String:
                    param.Set(str(value))
                elif param.StorageType == StorageType.Double:
                    param.Set(float(value))
                elif param.StorageType == StorageType.Integer:
                    param.Set(int(value))
                results.append(True)
            else:
                results.append(False)
        except Exception as e:
            results.append(str(e))

    TransactionManager.Instance.TransactionTaskDone()
    return results

# Input from Dynamo nodes
elements = IN[0]  # List of elements
param_name = IN[1]  # Parameter name (string)
values = IN[2]  # List of values

OUT = batch_update_parameter(elements, param_name, values)
```

### Batch Copy Elements

```python
# Dynamo Python - Copy elements to levels
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import *
from System.Collections.Generic import List

doc = DocumentManager.Instance.CurrentDBDocument

def copy_to_levels(elements, target_levels):
    """Copy elements to multiple levels"""
    TransactionManager.Instance.EnsureInTransaction(doc)

    copied = []
    element_ids = List[ElementId]([e.Id for e in elements])

    for level in target_levels:
        # Calculate offset
        source_level = doc.GetElement(elements[0].LevelId)
        offset = XYZ(0, 0, level.Elevation - source_level.Elevation)

        # Copy
        new_ids = ElementTransformUtils.CopyElements(
            doc, element_ids, offset
        )

        copied.extend([doc.GetElement(id) for id in new_ids])

    TransactionManager.Instance.TransactionTaskDone()
    return copied

elements = IN[0]
target_levels = IN[1]

OUT = copy_to_levels(elements, target_levels)
```

## Schedule Generation

### Create Custom Schedule

```python
# Dynamo Python - Create view schedule
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import *

doc = DocumentManager.Instance.CurrentDBDocument

def create_wall_schedule(schedule_name):
    """Create a wall schedule with QTO fields"""
    TransactionManager.Instance.EnsureInTransaction(doc)

    # Create schedule
    schedule = ViewSchedule.CreateSchedule(
        doc,
        ElementId(BuiltInCategory.OST_Walls)
    )
    schedule.Name = schedule_name

    # Add fields
    definition = schedule.Definition
    schedulable = definition.GetSchedulableFields()

    # Find and add specific fields
    field_names = ['Type', 'Level', 'Length', 'Area', 'Volume']

    for sf in schedulable:
        if sf.GetName(doc) in field_names:
            definition.AddField(sf)

    # Add sorting/grouping
    type_field = None
    for field in definition.GetFieldOrder():
        if definition.GetField(field).GetName() == 'Type':
            type_field = field
            break

    if type_field:
        sorting = ScheduleSortGroupField(type_field, ScheduleSortOrder.Ascending)
        sorting.ShowHeader = True
        sorting.ShowFooter = True
        definition.AddSortGroupField(sorting)

    TransactionManager.Instance.TransactionTaskDone()
    return schedule

schedule_name = IN[0]
OUT = create_wall_schedule(schedule_name)
```

## External Data Integration

### Import Data from Excel

```python
# Dynamo Python - Import Excel and update Revit
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
from Autodesk.Revit.DB import *

# Requires Excel data as input from Dynamo Excel nodes
doc = DocumentManager.Instance.CurrentDBDocument

def update_from_excel(excel_data, id_column, param_columns):
    """Update Revit elements from Excel data"""
    TransactionManager.Instance.EnsureInTransaction(doc)

    results = []

    for row in excel_data:
        try:
            # Get element by ID
            elem_id = ElementId(int(row[id_column]))
            element = doc.GetElement(elem_id)

            if element:
                row_result = {'id': elem_id.IntegerValue, 'updates': {}}

                for col_name, col_index in param_columns.items():
                    param = element.LookupParameter(col_name)
                    if param and not param.IsReadOnly:
                        value = row[col_index]
                        if param.StorageType == StorageType.String:
                            param.Set(str(value))
                        elif param.StorageType == StorageType.Double:
                            param.Set(float(value))
                        row_result['updates'][col_name] = value

                results.append(row_result)
        except Exception as e:
            results.append({'error': str(e)})

    TransactionManager.Instance.TransactionTaskDone()
    return results

excel_data = IN[0]  # 2D list from Excel
id_column = IN[1]   # Column index for element ID
param_columns = IN[2]  # Dict: param_name -> column_index

OUT = update_from_excel(excel_data, id_column, param_columns)
```

## Dynamo Package Workflow

### Full QTO Pipeline (Dynamo Graph Nodes)

```
1. Categories (Input)
   |
2. All Elements of Category (Revit)
   |
3. Element.GetParameterValueByName (Multiple parameters)
   |
4. Python Script (Process and calculate)
   |
5. List.Transpose
   |
6. Data.ExportExcel
   |
7. File Path (Output)
```

## Quick Reference

| Task | Method | Performance |
|------|--------|-------------|
| Get Elements | FilteredElementCollector | Fast |
| Get Parameter | element.LookupParameter() | Fast |
| Set Parameter | TransactionManager required | Moderate |
| Copy Elements | ElementTransformUtils | Moderate |
| Create Views | ViewSchedule.CreateSchedule | Slow |
| Delete Elements | Document.Delete | Fast |

## Common Parameter Names

```python
# Built-in parameters for quantities
QUANTITY_PARAMS = {
    'Length': BuiltInParameter.CURVE_ELEM_LENGTH,
    'Area': BuiltInParameter.HOST_AREA_COMPUTED,
    'Volume': BuiltInParameter.HOST_VOLUME_COMPUTED,
    'Height': BuiltInParameter.WALL_USER_HEIGHT_PARAM,
    'Width': BuiltInParameter.DOOR_WIDTH,
    'Level': BuiltInParameter.SCHEDULE_LEVEL_PARAM
}

# Unit conversion (Imperial to Metric)
CONVERSIONS = {
    'feet_to_meters': 0.3048,
    'sqft_to_sqm': 0.0929,
    'cuft_to_cum': 0.0283
}
```

## Resources

- **Dynamo Primer**: https://primer.dynamobim.org
- **Revit API Docs**: https://www.revitapidocs.com
- **DDC Website**: https://datadrivenconstruction.io

## Next Steps

- See `ifc-data-extraction` for IFC export
- See `qto-report` for advanced quantity reports
- See `n8n-workflow-automation` for external integration
