# REVIEW_2026 — 10-wave review results

Systematic 10-wave review of this collection (August 2026). Each wave checks one aspect;
findings were fixed in the same pass (commit history) and re-verified.

## Wave 1 — Repository structure & consistency
PASS. Six categories present and consistent (`1_DDC_Toolkit` … `6_OpenConstructionERP`),
every skill folder contains a `SKILL.md`, README mirrors the real folder list.

## Wave 2 — SKILL.md format validity
PASS. Frontmatter (`name`, `description`, optional `metadata`) present in sampled skills;
consistent YAML structure across categories.

## Wave 3 — Data accuracy (outdated facts)
**FOUND & FIXED.** 55 outdated references in 35 files:
- "55,719 work items / 9 languages" → **8 national bases (78,228 positions) + 30 markets, 26 languages**.
- `text-embedding-3-large` (3072d) → **BAAI/bge-m3** (1024d).
- `ddc_cwicr_en` → **`cwicr_<lang>_v3`** collections.
- CWICR release links `v0.1.0` → **v0.4.0**.
- Outdated parquet names in code samples (`ddc_cwicr_en.parquet` → national-base parquet).

## Wave 4 — License compliance
**FOUND & FIXED.**
- README claimed "CWICR Database: CC BY 4.0" — the real license is **CC BY-NC 4.0 + separate
  DDC commercial license**. Corrected in README and `1_DDC_Toolkit/README.md`.
- Added [NOTICE.md](NOTICE.md) documenting every license tier.

## Wave 5 — Trademark usage
**FOUND & FIXED.** ~480 mentions of third-party products (Revit, Autodesk, Procore,
Primavera/Oracle, Microsoft, Bluebeam, Navisworks, Trimble, Bentley, CSI…). Nominative use is
fine, but [NOTICE.md](NOTICE.md) now carries the required disclaimers and owner attribution.

## Wave 6 — Standards references (DIN 276, NRM, MasterFormat, GAEB, ISO 19650)
PASS after NOTICE.md. Only codes and short factual titles are referenced; NOTICE states that
no copyrighted standard text is reproduced and points to the official publishers.

## Wave 7 — External links validity
PASS. Key links (data repo, releases, platform repo, docs sites) resolve; the data repo is
live at v0.4.0.

## Wave 8 — Content quality & business value
PASS + additions. Every skill states business case → implementation → usage → best practices.
Added in this pass: OpenConstructionERP skills (`6_OpenConstructionERP`, 12 skills), MCP
integration, field ops, tendering, validation, geo/coordination, property development;
2026-trend skills (AI agents, embodied carbon/ESG, EU AI Act, material passports, generative design).

## Wave 9 — Legal documentation completeness
**FOUND & FIXED.** No NOTICE/attribution file existed. Added [NOTICE.md](NOTICE.md):
repository licenses, book copyright, trademark disclaimers, standards disclaimers, curated-skill
attribution with source links, and a health/safety/compliance disclaimer.

## Wave 10 — Final coherence
PASS. Badges, structure table and mindmap updated to **238 skills / 6 categories**;
all CWICR-facing numbers now describe the 2026 dataset (8 national bases, 30 markets,
26 languages, 95-column schema).

## Remaining honest notes
- The "31 languages" figures refer to the **book** (correct) — do not confuse with the
  CWICR database (26 languages).
- Curated skills remain subject to their source repositories' licenses (see NOTICE §4).
