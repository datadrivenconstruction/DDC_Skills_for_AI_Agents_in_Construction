---
name: oce-load-cost-bases
description: "Load national and market cost bases into OpenConstructionERP: the 8 national bases (Turkey Birim Fiyat, China Dinge, Brazil SINAPI, Spain BCCA, Italy Prezzario Toscana, Greece GGDE, Vietnam Dinh Muc, Indonesia AHSP), the 30 global markets, and 48 PPP market catalogs per base. Use when importing a cost database, repricing into a market, or troubleshooting a load."
---

# Load Cost Bases into OpenConstructionERP

## The catalog of bases (2026)

National bases ship a 95-column parquet each plus 26 language editions and a `markets/` folder of 48 PPP-repriced resource catalogs.

| Region id | Base | Positions | Currency | Priced? |
|---|---|---|---|---|
| `TR_NATIONAL` | Turkey (Birim Fiyat, ÇŞB+10 institutions) | 22,704 | TRY | yes |
| `ZH_CHINA` | China (Beijing Dinge + Bole 2022) | 11,312 | CNY | yes |
| `BR_NATIONAL` | Brazil (SINAPI, CAIXA/IBGE) | 9,723 | BRL | yes |
| `ES_ANDALUCIA` | Spain (BCCA 2023, Andalucía) | 6,453 | EUR | yes |
| `IT_TOSCANA` | Italy (Prezzario Regione Toscana 2026) | 5,836 | EUR | yes |
| `VN_NATIONAL` | Vietnam (Dinh Muc, TT 12/2021) | 4,299 | VND | coefficient (rate 0) |
| `ID_NATIONAL` | Indonesia (AHSP, Permen PUPR) | 2,784 | IDR | coefficient (rate 0) |
| `GR_NATIONAL` | Greece (GGDE) | 2,647 | EUR | partly |

Plus the flagship global base: 30 markets under `CIS-Russia-GESN-FER-TER` (USA_USD, DE_BERLIN, RU_STPETERSBURG, …).

## Load a base (API)

```http
POST /api/v1/costs/load-cwicr/TR_NATIONAL
```

- Reads the parquet (local `WORLD_COST_BASES`, cache, bundled dir, then GitHub download fallback).
- Groups rows by `rate_code` (one row per work item, components[] inline).
- Idempotent on `(code, region)`: second call → `{"status": "already_loaded", ...}`.
- After load, the backend swaps the region's text to the base's home language parquet (`TR___DDC_CWICR/TR_tr_...`), so a Turkish user sees Turkish.

### Verify the load

```http
GET /api/v1/costs/regions/stats/      # item count per region
GET /api/v1/costs/?region=TR_NATIONAL&limit=5   # check currency and descriptions
GET /api/v1/costs/{id}                # components[] = labour/material/machine lines
GET /api/v1/costs/category-tree/?region=TR_NATIONAL
```

## Import the resource catalog

```http
POST /api/v1/catalog/import/TR_NATIONAL
```

Reads `DDC_CWICR_TR_Catalog.csv` (`resource_code, name, type, category, unit, price_avg, price_min, price_max, currency, usage_count` + `parent_*` classification preserved in `specifications`).

## Reprice a base into a market (PPP)

1. Pick a market card from `GET /api/v1/costs/base-catalog` (e.g. `TR_NATIONAL:DE_BERLIN_de`).
2. The platform downloads the market's `DDC_CWICR_DE_BERLIN_de_Catalog.csv` (resources already PPP-repriced to EUR and translated to German).
3. It re-prices the base region's resource price sheet in place — text follows the language, price follows the market.

## Troubleshooting

- **404 "not found"** → no local parquet and GitHub download failed; check `~/.openestimator/cache/{db_id}.parquet` and network.
- **Empty currency** → region missing from the currency map; add it to `cwicr_v3_catalogue.py` / `_REGION_CURRENCY`.
- **Coefficient base shows rate 0** → expected for VN/ID; seed prices via `ResourcePriceService.seed_region`.
- **Duplicate rows** → importer collapses by `(code, region)`; multiple price layers per code keep the first.
