---
name: "semantic-search-cwicr"
description: "Semantic search in the DDC CWICR construction cost database using vector embeddings (BGE-M3, 1024-dim, per-language Qdrant collections). Find similar work items and resources for cost estimation across 8 national bases and 30 markets in 26 languages."
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🗄️", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"], "env": ["QDRANT_URL"]}, "primaryEnv": "QDRANT_URL"}}
---

# Semantic Search in DDC CWICR Database

## Business Case

### Problem Statement
Construction cost estimation requires finding relevant work items from large databases. Traditional keyword search fails when:
- Users describe work in natural language
- Terminology varies across regions and languages
- Similar work items have different naming conventions

### Solution
DDC CWICR provides pre-computed embeddings (BAAI/bge-m3, 1024 dimensions) enabling multilingual semantic search across **8 national bases (78,228 positions)** plus the **30-market global base** in **26 languages**, with 48 PPP-repriced market catalogs per national base.

### Business Value
- **90% faster** work item lookup compared to manual search
- **Multi-language**: Arabic, Bulgarian, Chinese, Croatian, Czech, Danish, Dutch, English, Finnish, French, German, Hindi, Indonesian, Italian, Japanese, Korean, Mongolian, Norwegian, Polish, Portuguese, Romanian, Russian, Spanish, Swedish, Thai, Turkish, Vietnamese
- **Higher accuracy** by finding semantically similar items, not just keyword matches

## Data landscape (2026)

| National base | Region id | Positions |
|---|---|---|
| Turkey (Birim Fiyat) | `TR_NATIONAL` | 22,704 |
| China (Beijing Dinge + Bole) | `ZH_CHINA` | 11,312 |
| Brazil (SINAPI) | `BR_NATIONAL` | 9,723 |
| Spain (BCCA Andalucía) | `ES_ANDALUCIA` | 6,453 |
| Italy (Prezzario Toscana) | `IT_TOSCANA` | 5,836 |
| Vietnam (Dinh Muc) | `VN_NATIONAL` | 4,299 |
| Indonesia (AHSP) | `ID_NATIONAL` | 2,784 |
| Greece (GGDE) | `GR_NATIONAL` | 2,647 |

Each base ships the **95-column CWICR master schema** (`rate_code`, `rate_original_name`, `rate_final_name`, `rate_unit`, `total_cost_per_position`, classification hierarchy `collection/department/section/subsection/category`, `resource_*` component lines with `is_material/is_machine/is_labor` flags) plus 26 language editions and 48 `markets/*.csv` catalogs.

Latest data release: **v0.4.0** (see [releases](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR/releases)).

## Technical Implementation

### Prerequisites
```bash
pip install qdrant-client pandas sentence-transformers
```

### Collections (2026)

The vector store uses **BAAI/bge-m3** (1024-dim dense + sparse + colbert in one forward pass, MIT license, 100+ languages). Production collections are named `cwicr_{LANG}_v3` (e.g. `cwicr_tr_v3`, `cwicr_zh_v3`). An ONNX-int8 variant (`gpahal/bge-m3-onnx-int8`, ~700 MB) is used on VPS-sized hosts.

### Python Implementation

```python
import pandas as pd
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class CWICRSemanticSearch:
    def __init__(self, host="localhost", port=6333, lang="en"):
        self.client = QdrantClient(host=host, port=port)
        self.collection = f"cwicr_{lang}_v3"
        self.model = SentenceTransformer("BAAI/bge-m3")

    def search_work_items(self, query, limit=10):
        vec = self.model.encode(query).tolist()
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=vec,
            limit=limit,
        )
        return pd.DataFrame([{**h.payload, "score": h.score} for h in hits])

    def search_by_category(self, query, category, limit=10):
        vec = self.model.encode(query).tolist()
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=vec,
            query_filter={"must": [{"key": "category", "match": {"value": category}}]},
            limit=limit,
        )
        return pd.DataFrame([{**h.payload, "score": h.score} for h in hits])
```

### Inside OpenConstructionERP

The platform's `costs` module already exposes semantic matching:
- `POST /api/v1/costs/suggest-for-element` — rank cost items for a BIM element body.
- `/qdrant-search` — multilingual candidate retrieval for a query.
- The SQL fallback (`GET /api/v1/costs/?q=...`) works without Qdrant.

## Database Schema (95-column master)

Key fields the payload carries:

| Field | Type | Description |
|-------|------|-------------|
| `rate_code` | string | Unique work item code (e.g. `15.115.1008`) |
| `rate_original_name` | string | Source-language description |
| `rate_final_name` | string | Display/translated description |
| `rate_unit` | string | m², m³, m, kg, Ad, Sa… |
| `total_cost_per_position` | float | Total unit price |
| `total_resource_cost_per_position` | float | Resource sum (before markup) |
| `collection_name` / `department_name` / `section_name` / `subsection_name` | string | Classification hierarchy |
| `category_type` | string | Normalized category (e.g. `CONSTRUCTION WORK`) |
| `resource_name` / `resource_quantity` / `resource_price_per_unit_current` / `resource_cost` | mixed | Component lines |
| `is_material` / `is_machine` / `is_labor` | bool | Component nature flags |

## Usage Examples

### Basic Search
```python
search = CWICRSemanticSearch(lang="tr")

# Natural language query
results = search.search_work_items("tuğla duvar örülmesi")
print(results[["rate_code", "rate_original_name", "total_cost_per_position", "score"]])
```

### Cost Estimation
```python
# Find work items for foundation work
foundation = search.search_work_items("reinforced concrete foundation", limit=20)

# Estimate with quantities (BIM takeoff)
quantities = {"15.115.1008": 150.0}  # m³
total = sum(quantities[c] * row["total_cost_per_position"]
            for _, row in foundation.iterrows() if row["rate_code"] in quantities)
print(f"Estimated: {total:,.2f} TRY")
```

## Best Practices

1. **Use specific queries** - "reinforced concrete slab 200mm" beats "concrete"
2. **Filter by category** - Narrow results to relevant work types
3. **Check similarity scores** - Low scores need manual verification
4. **Combine with QTO** - Use BIM quantities for automated estimation
5. **Mind the coefficient bases** - Vietnam and Indonesia have no prices (rate 0); price them via a market resource sheet
6. **Trust the source column** - `rate_original_name` holds the source wording; translations live in `rate_final_name`

## Resources

- **GitHub**: [OpenConstructionEstimate-DDC-CWICR](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR)
- **Releases**: [v0.4.0](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR/releases)
- **Platform**: [OpenConstructionERP](https://github.com/datadrivenconstruction/OpenConstructionERP)
- **Qdrant Docs**: https://qdrant.tech/documentation/
