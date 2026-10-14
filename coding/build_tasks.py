#!/usr/bin/env python3
"""Turn validated PR candidates into agent tasks: problem text only (no fix), spread across areas.

usage: build_tasks.py [--n 25]   -> tasks.json + tasks-review.md (for a human read before any run)
Problem text: the linked issue's title + body when the PR closes one; otherwise the PR title + only the body's
problem section(s) (## Why / ## What broke / ## Problem / ## Bug / ## Context), cut at the first solution heading.
"""
import argparse, json, re, subprocess
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
IFACE = {int(k): v for k, v in json.load(open(HERE / "interfaces.json")).items() if not k.startswith("_")} \
    if (HERE / "interfaces.json").exists() else {}
EXCLUDE = {1333, 1196, 1210, 1218, 1354, 1495, 1557, 1560, 1581, 1593, 1291, 1511, 1528, 1580}  # reviewed 2026-10-10: text describes only the test, or hidden tests need names the text never gives
PROBLEM = re.compile(r"^#{1,3}\s*(why|what broke|problem|the problem|bug|context|symptom|background|motivation)\b", re.I)
HEADING = re.compile(r"^#{1,3}\s+\S")
FOOTER = (
    "\n\nWork in /testbed (the club-3090 repository). Make the change in the source files. The repository's test "
    "suite for this behaviour will be checked after you submit; you may add or run tests, but your test edits are "
    "not graded.")


def problem_section(body: str) -> str:
    keep, on = [], False
    for line in (body or "").splitlines():
        if HEADING.match(line):
            on = bool(PROBLEM.match(line))
            continue
        if on:
            keep.append(line)
    return "\n".join(keep).strip()


def issue_text(n: int) -> str | None:
    p = subprocess.run(["gh", "issue", "view", str(n), "-R", "noonghunna/club-3090", "--json", "title,body"],
                       capture_output=True, text=True)
    if p.returncode:
        return None
    d = json.loads(p.stdout)
    return f"{d['title']}\n\n{d['body']}".strip()


def area(t: dict) -> str:
    src = [f for f in t["files"] if not f.startswith("scripts/tests/")]
    f = src[0] if src else t["files"][0]
    m = re.match(r"scripts/(lib/profiles|lib|[^/]+)", f)
    return m.group(1).removesuffix(".sh").removesuffix(".py") if m else f.split("/")[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=25)
    a = ap.parse_args()
    raw = {p["number"]: p for p in json.load(open(HERE / "prs-raw.json"))}
    val = [v for v in json.load(open(HERE / "validated.json")) if v["ok"]]
    tasks = []
    for v in val:
        text, src = None, None
        for i in v["issues"]:
            text = issue_text(i)
            if text:
                src = f"issue #{i}"
                break
        if not text:
            sec = problem_section(raw[v["n"]]["body"])
            if len(sec) < 120:  # no usable problem section -> skip rather than leak the fix
                continue
            text, src = f"{raw[v['n']]['title']}\n\n{sec}", "PR problem section"
        if len(text) > 8000 or v["n"] in EXCLUDE:  # rig-report dumps / text that only describes the test
            continue
        tasks.append(dict(n=v["n"], merged=v["merged"], base=v["base"], merge=v["merge"], tests=v["tests"],
                          files=v["files"], area=area(v), size=v["size"], source=src + (" + interface" if v["n"] in IFACE else ""),
                          problem=text + (f"\n\n## Interface (what the checks call and expect)\n\n{IFACE[v['n']]}"
                                          if v["n"] in IFACE else "") + FOOTER))
    # spread: round-robin across areas, oldest first within an area
    by = defaultdict(list)
    for t in sorted(tasks, key=lambda t: t["merged"]):
        by[t["area"]].append(t)
    pick = []
    while len(pick) < a.n and any(by.values()):
        for k in sorted(by, key=lambda k: -len(by[k])):
            if by[k] and len(pick) < a.n:
                pick.append(by[k].pop(0))
    pick.sort(key=lambda t: t["n"])
    json.dump(pick, open(HERE / "tasks.json", "w"), indent=1)
    with open(HERE / "tasks-review.md", "w") as f:
        f.write(f"# club-3090 agent tasks ({len(pick)} of {len(tasks)} usable, {len(val)} validated)\n\n")
        for t in pick:
            f.write(f"## #{t['n']} ({t['merged']}, area {t['area']}, {t['size']} lines, text from {t['source']})\n"
                    f"Hidden tests: {', '.join(t['tests'])}\n\n```\n{t['problem']}\n```\n\n")
    print(f"{len(val)} validated, {len(tasks)} with usable problem text, {len(pick)} picked across "
          f"{len({t['area'] for t in pick})} areas")


if __name__ == "__main__":
    main()
