#!/usr/bin/env python3
"""prs-raw.json (gh pr list export) -> candidates.json: merged PRs that touch scripts/tests/, <= 6 files, <= 400 lines."""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
c = []
for p in json.load(open(HERE / "prs-raw.json")):
    files = [f["path"] for f in p["files"]]
    tests = [f for f in files if f.startswith("scripts/tests/") and f.endswith((".sh", ".py"))]
    if not tests or len(files) > 6 or p["additions"] + p["deletions"] > 400:
        continue
    issues = sorted({int(x) for x in re.findall(r"(?i)(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", p["body"] or "")})
    c.append(dict(n=p["number"], merged=p["mergedAt"][:10], merge=p["mergeCommit"]["oid"], files=files, tests=tests,
                  title=p["title"], issues=issues, size=p["additions"] + p["deletions"]))
json.dump(c, open(HERE / "candidates.json", "w"), indent=1)
print(f"{len(c)} candidates")
