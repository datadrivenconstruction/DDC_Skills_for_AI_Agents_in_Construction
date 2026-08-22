# -*- coding: utf-8 -*-
"""Report distinct outdated lines across the skills repo, then apply safe replacements."""
from __future__ import annotations
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = r"C:\Users\Artem Boiko\Desktop\CodeProjects\_skills_repo_work"
PAT = re.compile(r"55,719|9 languages|31 languages|3072|text-embedding-3-large|ddc_cwicr_en|v0\.1\.0|CC BY 4\.0")

# 1) collect distinct outdated lines
distinct = {}
for dirpath, _, files in os.walk(ROOT):
    if ".git" in dirpath:
        continue
    for fn in files:
        if not fn.endswith(".md"):
            continue
        p = os.path.join(dirpath, fn)
        with open(p, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if PAT.search(line):
                    key = line.strip()
                    distinct.setdefault(key, []).append((os.path.relpath(p, ROOT), i))

print(f"distinct outdated lines: {len(distinct)}\n")
for key, locs in sorted(distinct.items(), key=lambda kv: -len(kv[1])):
    print(f"[{len(locs)}x] {key[:130]}")
    for p, i in locs[:3]:
        print(f"       {p}:{i}")
print()
