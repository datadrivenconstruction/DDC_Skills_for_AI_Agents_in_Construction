# -*- coding: utf-8 -*-
"""Apply exact-string replacements for outdated CWICR facts and license across all .md files."""
from __future__ import annotations
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = r"C:\Users\Artem Boiko\Desktop\CodeProjects\_skills_repo_work"
REPLACEMENTS = [
    ('cwicr = pd.read_parquet("ddc_cwicr_en.parquet")', 'cwicr = pd.read_parquet("TR_workitems_costs_resources_DDC_CWICR.parquet")'),
    ('cwicr = loader.load("ddc_cwicr_en.parquet")', 'cwicr = loader.load("TR_workitems_costs_resources_DDC_CWICR.parquet")'),
    ('df = loader.load("ddc_cwicr_en.parquet")', 'df = loader.load("TR_workitems_costs_resources_DDC_CWICR.parquet")'),
    ('collection_name="ddc_cwicr_en",', 'collection_name="cwicr_en_v3",'),
    ("qdrantClient.search('ddc_cwicr_en', {", "qdrantClient.search('cwicr_en_v3', {"),
    ('- ddc_cwicr_en  # English (Toronto prices)', '- cwicr_en_v3  # English (Toronto prices)'),
    ('CWICR Database — 55,719 standardized work items in 9 languages.',
     'CWICR Database — 8 national bases (78,228 positions) plus 30 markets in 26 languages.'),
    ('55,719 work items, 9 languages', '8 national bases + 30 markets, 26 languages'),
    ('Semantic search across 55,719 items in 31 languages',
     'Semantic search across 78,228 national + 55,719 global items in 26 languages'),
    ('← 55,719 work items database', '← 8 national bases + 30 markets database'),
    ('55,719 work items database in 31 languages', '8 national bases + 30 markets in 26 languages'),
    ('- **CWICR Database**: CC BY 4.0',
     '- **CWICR Database**: CC BY-NC 4.0 (non-commercial; separate DDC commercial license)'),
    ('Construction cost database with 55,719 work items',
     'Cost database: 8 national bases + 30 markets'),
    ('[DDC CWICR v0.1.0](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR/releases) - 55,719 work items, 9 languages',
     '[DDC CWICR v0.4.0](https://github.com/datadrivenconstruction/OpenConstructionEstimate-DDC-CWICR/releases) - 8 national bases + 30 markets, 26 languages'),
    ('│ 55,719      │', '│ 78,228      │'),
    ('│ 9 Languages │', '│ 26 Languages │'),
    ('- **Database**: CC BY 4.0 (free commercial use with attribution)',
     '- **Database**: CC BY-NC 4.0 (non-commercial) + separate DDC commercial license'),
    ('(55,719 work items across 9 languages)', '(8 national bases, 78,228 positions, 26 languages)'),
    ('55,719 work items, 27,672 resources, 85 fields per item',
     '8 national bases (78,228 positions) + 30 markets, 95-column schema'),
    ('text-embedding-3-large (3072 dimensions)', 'BAAI/bge-m3 (1024 dimensions)'),
    ('DDC CWICR database with 55,719 work items', 'DDC CWICR database (8 national bases, 78,228 positions)'),
    ('work_items: 55,719', 'work_items: 78228  # 8 national bases'),
    ('embedding_model: text-embedding-3-large (3072d)', 'embedding_model: BAAI/bge-m3 (1024d)'),
    ('model="text-embedding-3-large",', 'model="BAAI/bge-m3",'),
    ('dimensions=3072', 'dimensions=1024'),
    ('- 55,719 work items across all construction trades',
     '- 8 national bases (78,228 positions) across all construction trades'),
    ('- 9 languages: EN, DE, RU, ES, FR, AR, HI, PT, ZH',
     '- 26 languages (incl. EN, DE, RU, ES, FR, AR, HI, PT, ZH, TR, IT, PL and 15 more)'),
    ('Work with CWICR database across 9 languages.', 'Work with CWICR database across 26 languages.'),
    ('CWICR database supports 9 languages', 'CWICR database supports 26 languages'),
    ('- **CWICR Database**: 9 languages, 55,000+ items',
     '- **CWICR Database**: 26 languages, 8 national bases + 30 markets'),
]

total = 0
changed_files = []
for dirpath, _, files in os.walk(ROOT):
    if ".git" in dirpath:
        continue
    for fn in files:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(dirpath, fn)
        with open(p, encoding="utf-8") as f:
            text = f.read()
        new = text
        for old, rep in REPLACEMENTS:
            if old in new:
                new = new.replace(old, rep)
        if new != text:
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(new)
            n = sum(1 for old, _ in REPLACEMENTS if old in text)
            total += n
            changed_files.append((os.path.relpath(p, ROOT), n))
            print(f"  {os.path.relpath(p, ROOT)}: {n} replacements")

print(f"\nTOTAL: {total} replacements in {len(changed_files)} files")
