#!/usr/bin/env python3
"""Export the task lists and per-task results as CSVs for the discussion post (glm53/posts/11-attachments/).

Coding: runs/<config>/draw<N>/<pr>/result.json (+ draw1-v1 = the 8 tasks on their original text, before the Interface
sections). Assistant: assistant/runs/<config>/<harness>/draw1/<task>/result.json. Smoke runs are skipped.
"""
import csv, glob, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "results/2026-10-2x5090"
REPO = "https://github.com/noonghunna/club-3090/pull/"

# config tag -> (model, quant/serving, harness, effort)
CODING = {
    "thinkingcap-dualfast": ("ThinkingCap-Qwen3.8-27B", "sgl dual-fast", "mini-swe-agent", "low"),
    "thinkingcap-dualfast-xhigh": ("ThinkingCap-Qwen3.8-27B", "sgl dual-fast", "mini-swe-agent", "xhigh"),
    "thinkingcap-dualfast-omp": ("ThinkingCap-Qwen3.8-27B", "sgl dual-fast", "omp", "low"),
    "thinkingcap-dualfast-omp-xhigh": ("ThinkingCap-Qwen3.8-27B", "sgl dual-fast", "omp", "xhigh"),
    "strata-iq4xs": ("Qwen3.8-Flash-Next", "UD-IQ4_XS, Strata", "mini-swe-agent", "low"),
    "strata-iq4xs-xhigh": ("Qwen3.8-Flash-Next", "UD-IQ4_XS, Strata", "mini-swe-agent", "xhigh"),
    "strata-iq4xs-omp": ("Qwen3.8-Flash-Next", "UD-IQ4_XS, Strata", "omp", "low"),
    "strata-iq4xs-omp-xhigh": ("Qwen3.8-Flash-Next", "UD-IQ4_XS, Strata", "omp", "xhigh"),
    "strata-q4kxl": ("Qwen3.8-Flash-Next", "UD-Q4_K_XL, Strata", "mini-swe-agent", "low"),
    "glm-avar6": ("GLM-5.3-Flash", "avar6 Q2_K-Q3_K, llama.cpp moe-cache", "mini-swe-agent", "low"),
    "glm-avar6-xhigh": ("GLM-5.3-Flash", "avar6 Q2_K-Q3_K, llama.cpp moe-cache", "mini-swe-agent", "max"),
    "glm-avar6-omp": ("GLM-5.3-Flash", "avar6 Q2_K-Q3_K, llama.cpp moe-cache", "omp", "low"),
    "glm-avar6-omp-xhigh": ("GLM-5.3-Flash", "avar6 Q2_K-Q3_K, llama.cpp moe-cache", "omp", "max"),
    "glm-iq4xs": ("GLM-5.3-Flash", "UD-IQ4_XS, llama.cpp moe-cache", "mini-swe-agent", "low"),
}
ASSIST = {"thinkingcap-dualfast": ("ThinkingCap-Qwen3.8-27B", "sgl dual-fast"),
          "strata-iq4xs": ("Qwen3.8-Flash-Next", "UD-IQ4_XS, Strata")}


def write(name, header, rows):
    with open(OUT / name, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    titles = {str(p["number"]): p["title"] for p in json.load(open(HERE / "prs-raw.json"))}
    iface = set(json.load(open(HERE / "interfaces.json")))
    tasks = json.load(open(HERE / "tasks.json"))
    write("coding-tasks.csv", ["pr", "title", "merged", "area", "source", "tests", "has_interface_section", "url"],
          [[t["n"], titles.get(str(t["n"]), ""), t["merged"], t["area"], t["source"],
            " ".join(t["tests"] if isinstance(t["tests"], list) else [t["tests"]]), "yes" if str(t["n"]) in iface else "no", REPO + str(t["n"])] for t in tasks])

    rows = []
    for c, (model, serving, harness, effort) in CODING.items():
        for d in sorted((HERE / "runs" / c).glob("draw*")):
            text = "original (before Interface section)" if d.name == "draw1-v1" else "final"
            draw = 1 if d.name == "draw1-v1" else int(d.name[4:])
            for f in sorted(d.glob("*/result.json")):
                r = json.load(open(f))
                rows.append([r["n"], model, serving, harness, effort, draw, text, int(bool(r.get("passed"))),
                             r.get("partial"), r.get("localization"), len(r.get("regressions") or []),
                             round((r.get("agent_s") or 0) / 60, 1), r.get("steps"), r.get("exit_status"), c])
    rows.sort(key=lambda x: (x[0], x[1], x[2], x[3], x[4], x[6], x[5]))
    write("coding-results.csv", ["pr", "model", "serving", "harness", "effort", "draw", "task_text", "solved",
                                 "partial", "right_files", "regressions", "minutes", "steps", "exit_status",
                                 "config_tag"], rows)

    adirs = sorted(d for d in (HERE / "assistant").iterdir() if (d / "meta.json").exists())
    arows = []
    for d in adirs:
        m = json.load(open(d / "meta.json"))
        title = (d / "task.md").read_text().splitlines()[0].lstrip("# ").strip()
        arows.append([m["id"], title, m.get("set", "base"), m.get("axis", ""), m.get("category"), m.get("difficulty"),
                      m.get("source"), m.get("est_minutes")])
    write("assistant-tasks.csv", ["task", "title", "set", "axis", "category", "difficulty", "source", "est_minutes"], arows)

    sets = {r[0]: (r[2], r[3]) for r in arows}
    rows = []
    for c, (model, serving) in ASSIST.items():
        for h in ("hermes", "omp"):
            for f in sorted(glob.glob(str(HERE / "assistant" / "runs" / c / h / "draw1" / "*" / "result.json"))):
                r = json.load(open(f))
                t = r["task"]
                rows.append([t, sets[t][0], sets[t][1], model, serving, h, "low", int(bool(r.get("passed"))),
                             r.get("checks_passed"), r.get("checks_total"), r.get("partial"),
                             round(r.get("agent_s") or 0), r.get("tool_calls"), r.get("exit_status")])
    write("assistant-results.csv", ["task", "set", "axis", "model", "serving", "harness", "effort", "solved",
                                    "checks_passed", "checks_total", "partial", "seconds", "tool_calls",
                                    "exit_status"], rows)


if __name__ == "__main__":
    main()
