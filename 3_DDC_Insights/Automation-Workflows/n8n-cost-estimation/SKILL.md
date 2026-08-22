---
name: "n8n-cost-estimation"
description: "Build n8n pipeline for automated cost estimation from Revit/IFC using DDC CWICR database and LLM classification."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🔧", "os": ["win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"env": ["QDRANT_URL"]}, "primaryEnv": "QDRANT_URL"}}
---
# Automated Cost Estimation Pipeline

## Business Case

### Problem Statement
Traditional cost estimation requires:
- Manual work item lookup in price databases
- Time-consuming element classification
- Expert knowledge of pricing standards
- Repetitive data entry

### Solution
Free open-source n8n pipeline that converts CAD (Revit 2015-2026) files into full cost and time estimates using AI (LLM) and vector database with 55,000+ work items.

### Business Value

| Traditional Role | Automated Alternative |
|-----------------|----------------------|
| BIM Manager manually exports data | Pipeline auto-classifies elements |
| Junior Estimator searches databases | Vector search finds matches in ms |
| Senior Estimator maps assemblies | LLM identifies quantity parameters |
| Foreman calculates labor hours | DDC CWICR contains documented norms |
| Project Manager aggregates costs | Pipeline outputs phased breakdown |

**Processing speed**: 3-10 seconds per element group

## Technical Implementation

### Pipeline Architecture
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Revit/IFC   │───>│ CAD2DATA    │───>│ Structured  │
│ File        │    │ Converter   │    │ Excel/CSV   │
└─────────────┘    └─────────────┘    └─────────────┘
                                             │
                                             ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Cost Report │<───│ Price Match │<───│ LLM Class.  │
│ HTML/Excel  │    │ DDC CWICR   │    │ + QTO       │
└─────────────┘    └─────────────┘    └─────────────┘
```

### n8n Pipeline Steps

#### 1. File Conversion Node
```javascript
// Execute CAD converter
const filePath = $input.first().json.file_path;
const outputDir = filePath.replace(/\.[^.]+$/, '');

const command = `RvtExporter.exe "${filePath}" complete bbox`;

// Returns: { xlsx_path, dae_path }
```

#### 2. Load Elements
```javascript
// Read converted Excel into n8n
const xlsx = $node["Read Binary Files"].json;
const elements = xlsx.sheets["Elements"];

// Group by category for processing
const grouped = elements.reduce((acc, el) => {
  const cat = el.Category;
  if (!acc[cat]) acc[cat] = [];
  acc[cat].push(el);
  return acc;
}, {});

return Object.entries(grouped).map(([category, items]) => ({
  json: {category, items, count: items.length}
}));
```

#### 3. LLM Classification
```javascript
// Prompt for Claude/GPT classification
const prompt = `
You are a construction estimator. Given these BIM elements:
Category: ${$input.first().json.category}
Sample elements: ${JSON.stringify($input.first().json.items.slice(0,5))}

1. Identify the construction work type
2. List relevant quantity parameters (Volume, Area, Length, Count)
3. Suggest standard work items from construction norms

Return as JSON:
{
  "work_type": "...",
  "quantity_params": ["Volume", "Area"],
  "suggested_items": ["Concrete foundation", "Formwork"]
}
`;
```

#### 4. Vector Search in CWICR
```javascript
// Search DDC CWICR database for matching work items
const qdrantClient = require('@qdrant/js-client-rest');

const searchResults = await qdrantClient.search('cwicr_en_v3', {
  vector: await getEmbedding($input.first().json.work_description),
  limit: 10,
  score_threshold: 0.7
});

return searchResults.map(r => ({
  json: {
    work_code: r.payload.work_item_code,
    description: r.payload.description,
    unit: r.payload.unit,
    unit_price: r.payload.unit_price,
    similarity: r.score
  }
}));
```

#### 5. Calculate Costs
```javascript
// Match quantities to prices
const elements = $node["Load Elements"].json;
const prices = $node["Vector Search"].json;

let totalCost = 0;
const breakdown = [];

for (const el of elements.items) {
  const matchedPrice = prices.find(p => p.similarity > 0.8);
  if (matchedPrice) {
    const quantity = el.Volume || el.Area || 1;
    const cost = quantity * matchedPrice.unit_price;
    totalCost += cost;

    breakdown.push({
      element: el.Name,
      quantity: quantity,
      unit: matchedPrice.unit,
      unit_price: matchedPrice.unit_price,
      total: cost
    });
  }
}

return [{json: {totalCost, breakdown}}];
```

#### 6. Generate Report
```javascript
// Create HTML report
const data = $input.first().json;

const html = `
<!DOCTYPE html>
<html>
<head>
  <title>Cost Estimate Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #4CAF50; color: white; }
    .total { font-size: 1.5em; font-weight: bold; }
  </style>
</head>
<body>
  <h1>Cost Estimate Report</h1>
  <p class="total">Total: $${data.totalCost.toLocaleString()}</p>
  <table>
    <tr><th>Element</th><th>Quantity</th><th>Unit</th><th>Price</th><th>Total</th></tr>
    ${data.breakdown.map(row => `
      <tr>
        <td>${row.element}</td>
        <td>${row.quantity.toFixed(2)}</td>
        <td>${row.unit}</td>
        <td>$${row.unit_price.toFixed(2)}</td>
        <td>$${row.total.toFixed(2)}</td>
      </tr>
    `).join('')}
  </table>
</body>
</html>
`;

return [{json: {html, filename: 'estimate_report.html'}}];
```

## Real-World Results

Example project (rac_basic_sample.rvt):
- Processing time: ~30 minutes with ChatGPT
- Elements analyzed: 500+
- Automatic classification: 95% accuracy
- Manual review needed: 5% edge cases

## Key Insight from Community

> "My subjective take: professionals who ignore workflow automation and AI-agents today have roughly 5 years before the construction industry moves past them. The tools are free and open. The data is open. The only question is who learns to use them first."

## Prerequisites

- n8n (local or hosted)
- DDC CAD converters
- DDC CWICR database
- OpenAI/Anthropic API key
- Qdrant vector database

## Resources

- **GitHub**: cad2data Pipeline repository
- **Database**: OpenConstructionEstimate-DDC-CWICR
- **Community**: n8n Workflows for Construction (Telegram)
