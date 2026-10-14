import itertools, json, random, re
from datetime import datetime, timedelta, timezone, date
from common import task, DIFF

J = lambda o: json.dumps(o, indent=2) + "\n"

# ---------------------------------------------------------------- 07 reply to a forum thread
def t07():
    thread = """# Thread: slow decode on two cards

**@sam-k** wrote:

Thanks for posting the rig numbers. A few questions before I try this myself:

- A1: What decode speed did `tp2-fp8` reach?
- A2: What was the peak VRAM per card for `single-q4`?
- A3: What is the largest context length that ran for `tp2-awq`?
- A4: Which exact command did you use to launch `tp2-fp8`?
"""
    csvt = ("config,decode_tps,prefill_tps,vram_gib,max_ctx_ok,launch\n"
            "tp2-fp8,88.2,6120,29.7,98304,`bash launch.sh --slug glm53 --tp 2 --quant fp8`\n"
            "tp2-awq,84.9,5840,27.3,65536,`bash launch.sh --slug glm53 --tp 2 --quant awq`\n"
            "single-q4,51.6,3310,31.4,32768,`bash launch.sh --slug glm53 --tp 1 --quant q4`\n")
    style = """# Reply style

- Start the reply with `@sam-k` and nothing before it.
- At most 150 words.
- No em dashes or en dashes. No exclamation marks.
- Never use these phrases (any case): "great question", "I hope this helps", "happy to help", "delve", "leverage", "game-changer", "certainly".
- Answer each ask (A1 to A4) with the value from `results.csv`, copied as written there. Put the launch command in backticks.
"""
    reply = ("@sam-k here are the answers.\n\nA1: `tp2-fp8` reached 88.2 tok/s decode.\n\nA2: `single-q4` peaked at 31.4 GiB per card.\n\n"
             "A3: `tp2-awq` ran up to a context of 65536.\n\nA4: I launched `tp2-fp8` with `bash launch.sh --slug glm53 --tp 2 --quant fp8`.\n")
    md = """
    # Draft the forum reply

    `/workspace/thread.md` holds a forum post with four questions (A1 to A4). The data is in `/workspace/results.csv`; the house rules for replies are in `/workspace/style.md`.

    Write the reply to `/workspace/reply.md`. It must follow every rule in `style.md` and answer all four questions with the exact values from the CSV. Quote only the values that answer A1 to A4: do not mention numbers from any other row of the CSV.
    """
    chk = """
    s = rd("reply.md") or ""
    chk("reply-exists", bool(s.strip()))
    chk("starts-with-mention", s.startswith("@sam-k"))
    chk("max-150-words", 0 < len(s.split()) <= 150, len(s.split()))
    chk("no-dashes", not re.search("[\\u2013\\u2014]", s))
    chk("no-exclamation", "!" not in s)
    low = s.lower()
    chk("no-banned-phrases", not [b for b in E["ban"] if b in low], [b for b in E["ban"] if b in low])
    chk("A1-decode-88.2", "88.2" in s)
    chk("A2-vram-31.4", "31.4" in s)
    chk("A3-context-65536", "65536" in s)
    chk("A4-command-in-backticks", "`" + E["cmd"] + "`" in s)
    chk("no-wrong-values", not re.search(r"\\b(84\\.9|51\\.6|98304|32768|29\\.7|27\\.3)\\b", s), "value from a different row")
    """
    task("07-forum-reply-style", "session-derived", "writing", 10, "Reply under style rules", md,
         {"thread.md": thread, "results.csv": csvt, "style.md": style}, chk, {"reply.md": reply},
         dict(ban=["great question", "i hope this helps", "happy to help", "delve", "leverage", "game-changer", "certainly"],
              cmd="bash launch.sh --slug glm53 --tp 2 --quant fp8"), "Shape from sessions drafting maintainer/forum replies against the stop-slop style rules.")
DIFF["07-forum-reply-style"] = "medium"

# ---------------------------------------------------------------- 08 models folder -> slug index
def t08():
    reg = [dict(slug="glm53-flash-q4", repo="zai/GLM-5.3-Flash", quant="UD-Q4_K_XL"), dict(slug="glm53-flash-q6", repo="zai/GLM-5.3-Flash", quant="Q6_K"),
           dict(slug="qfn-fp8", repo="qwen/Qwen3.8-Flash-Next", quant="fp8"), dict(slug="qfn-awq", repo="qwen/Qwen3.8-Flash-Next", quant="awq"),
           dict(slug="qwen-27b-q4", repo="qwen/Qwen3.8-27B", quant="Q4_K_M"), dict(slug="llama-8b-q8", repo="meta/Llama-4-8B", quant="Q8_0")]
    folders = {"GLM-5.3-Flash-UD-Q4_K_XL": [("config.json", 400), ("model-00001.gguf", 5000), ("model-00002.gguf", 3000), (".cache/tmp", 999)],
               "glm5.3-flash_Q6_K": [("config.json", 400), ("model.gguf", 7000)],
               "Qwen3.8-Flash-Next-fp8": [("config.json", 350), ("w1.safetensors", 4100), ("w2.safetensors", 4200), ("tok/tokenizer.json", 80)],
               "qwen3.8-flash-next_FP8_old": [("config.json", 350), ("w.safetensors", 1000)],
               "Qwen3.8-27B-Q4_K_M": [("config.json", 300), ("model.gguf", 6500)],
               "misc-notes": [("readme.txt", 50)]}
    ws = {"registry.json": J(reg)}
    for f, fs in folders.items():
        for n, s in fs: ws[f"models/{f}/{n}"] = "x" * s
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    key = {norm(r["repo"].split("/")[-1] + r["quant"]): r["slug"] for r in reg}
    rows = []
    for f in sorted(folders):
        size = sum(s for n, s in folders[f] if not any(part.startswith(".") for part in n.split("/")))
        nfiles = sum(1 for n, s in folders[f] if not any(part.startswith(".") for part in n.split("/")))
        rows.append((f, key.get(norm(f), ""), size, nfiles))
    used = {r[1] for r in rows if r[1]}
    missing = sorted(r["slug"] for r in reg if r["slug"] not in used)
    csv_ = "folder,slug,size_bytes,files\n" + "".join(f"{a},{b},{c},{d}\n" for a, b, c, d in rows)
    md = """
    # Index the models folder against the slug registry

    `/workspace/models/` holds one folder per downloaded model. `/workspace/registry.json` lists slugs, each with a `repo` and a `quant`.

    A folder belongs to a slug when the folder name and the string `<last path part of repo><quant>` are equal after lowercasing and deleting every
    character that is not a letter or digit. Folders with no matching slug get an empty slug.

    Write:

    1. `/workspace/index.csv` with the header `folder,slug,size_bytes,files`, one row per folder, sorted by folder name (plain byte order).
       `size_bytes` is the sum of the file sizes under the folder, `files` is the count of files. Skip any file or directory whose name starts with `.` (and everything below it).
    2. `/workspace/missing.json`: a JSON array, sorted, of registry slugs that have no folder.
    """
    chk = """
    r = rows("index.csv")
    chk("index-parses", bool(r))
    if r:
        chk("header-exact", (rd("index.csv") or "").splitlines()[0].strip() == "folder,slug,size_bytes,files")
        chk("sorted-folders", [x["folder"] for x in r] == [e[0] for e in E["r"]], [x["folder"] for x in r])
        got = {x["folder"]: (x["slug"], x["size_bytes"], x["files"]) for x in r}
        for f, s, z, n in E["r"]:
            chk("row-" + f, got.get(f) == (s, str(z), str(n)), got.get(f))
    chk("missing-exact", jl("missing.json") == E["m"], jl("missing.json"))
    """
    task("08-models-slug-index", "session-derived", "filing", 12, "Index model folders to slugs", md, ws, chk,
         {"index.csv": csv_, "missing.json": J(missing)}, dict(r=rows, m=missing),
         "Shape from a session that indexed model storage folders against club-3090 slugs in a spreadsheet.")
DIFF["08-models-slug-index"] = "medium"

# ---------------------------------------------------------------- 09 handoff doc
def t09():
    tasks = [dict(id="T1", title="fetch weights", status="done"), dict(id="T2", title="write quant recipe", status="done"),
             dict(id="T3", title="run quality gate", status="blocked"), dict(id="T4", title="bench two configs", status="in_progress", detail="tp2-fp8 finished, tp2-awq not started"),
             dict(id="T5", title="write results doc", status="todo"), dict(id="T6", title="reply on thread", status="todo")]
    prog = """# Progress notes (newest last)

- 10-05 fetched weights, 41 GB, checksums ok (T1).
- 10-05 quant recipe in `recipes/quant-fp8.md` reviewed, good (T2).
- 10-06 quality gate failed to start: preflight says port 8000 busy. Tried a second port, same result. Gave up for now.
- 10-06 bench: `tp2-fp8` run complete, results in `out/bench-fp8.json`. Did not start `tp2-awq` yet because the GPUs were needed elsewhere.
- 10-07 idea: skip T6 until results doc exists.
"""
    last = """$ bash scripts/run_quality.sh --slug glm53 --port 8000
preflight: checking port 8000
preflight: ERROR port 8000 already in use by pid 4411
exit status 3
"""
    tree = "scripts/run_quality.sh\nscripts/run_bench.sh\nscripts/make_results_doc.sh\nrecipes/quant-fp8.md\nout/bench-fp8.json\n"
    ref = """# Handoff

## Done
- T1 fetch weights
- T2 write quant recipe

## In progress
- T4 bench two configs: tp2-fp8 finished (out/bench-fp8.json), tp2-awq not started.

## Blockers
- T3 run quality gate: `bash scripts/run_quality.sh --slug glm53 --port 8000` exits 3, port 8000 already in use by pid 4411.

## Next
- Free port 8000, then rerun the quality gate.
- Run `scripts/run_bench.sh` for tp2-awq.
- T5 and T6 wait on the above.
"""
    md = """
    # Write a handoff for the next session

    `/workspace/tasks.json`, `/workspace/progress.md`, `/workspace/last-run.log` and `/workspace/tree.txt` describe where a multi-step job stands.
    Write `/workspace/HANDOFF.md` for someone who starts cold. Use exactly these four `##` headings, in this order: `Done`, `In progress`, `Blockers`, `Next`.

    - Every task goes under the heading that matches its status (`done` -> Done, `in_progress` -> In progress, `blocked` -> Blockers; `todo` tasks are mentioned only under Next). Refer to tasks by id (`T1`).
    - Blockers must quote the exact failing command from the log in backticks and the exit status number.
    - In progress must say which config finished and which has not started.
    - Next must name the script path to run for the unfinished bench.
    - At most 250 words in total.
    """
    chk = """
    s = rd("HANDOFF.md") or ""
    parts = re.split(r"(?m)^## +", s)
    secs = {}
    for part in parts[1:]:
        head, _, body = part.partition("\\n"); secs[head.strip()] = body
    chk("headings-exact-order", [h.strip() for h in re.findall(r"(?m)^## +(.*)$", s)] == ["Done", "In progress", "Blockers", "Next"], list(secs))
    ids = lambda t: set(re.findall(r"\\bT\\d\\b", t or ""))
    chk("done-has-T1-T2-only", ids(secs.get("Done")) == {"T1", "T2"}, ids(secs.get("Done")))
    chk("inprogress-T4-only", ids(secs.get("In progress")) == {"T4"}, ids(secs.get("In progress")))
    chk("blockers-T3-only", ids(secs.get("Blockers")) == {"T3"}, ids(secs.get("Blockers")))
    chk("blockers-exact-command", "`" + E["cmd"] + "`" in (secs.get("Blockers") or ""))
    chk("blockers-exit-status-3", re.search(r"\\b3\\b", secs.get("Blockers") or "") is not None)
    ip = (secs.get("In progress") or "")
    chk("inprogress-configs", "tp2-fp8" in ip and "tp2-awq" in ip)
    chk("next-script-path", "scripts/run_bench.sh" in (secs.get("Next") or ""))
    chk("todo-not-in-done-or-blockers", not ids(secs.get("Done")) & {"T5", "T6"} and not ids(secs.get("Blockers")) & {"T5", "T6"})
    chk("max-250-words", 0 < len(s.split()) <= 250, len(s.split()))
    """
    task("09-handoff-doc", "session-derived", "writing", 10, "Write a cold-start handoff", md,
         {"tasks.json": J(tasks), "progress.md": prog, "last-run.log": last, "tree.txt": tree}, chk, {"HANDOFF.md": ref},
         dict(cmd="bash scripts/run_quality.sh --slug glm53 --port 8000"), "Shape from the many handoff-doc sessions in a private notes project and the club-tasks project.")
DIFF["09-handoff-doc"] = "medium"

# ---------------------------------------------------------------- 10 pair rig reports with quality results (hard)
def t10():
    alias = {"glm53f-q4": "glm53-flash-q4", "qfn8": "qfn-fp8"}
    rig = [("2026-10-01", "glm53-flash-q4", 1), ("2026-10-01", "glm53-flash-q4", 2), ("2026-10-02", "qfn-fp8", 1),
           ("2026-10-03", "qfn-awq", 1), ("2026-10-05", "llama-8b-q8", 1), ("2026-10-05", "qwen-27b-q4", 1), ("2026-10-05", "qwen-27b-q4", 2),
           ("2026-10-05", "qwen-27b-q4", 3)]
    qual = [("2026-10-01", "glm53f-q4"), ("2026-10-02", "qfn8"), ("2026-10-04", "qfn-awq"), ("2026-10-05", "qwen-27b-q4"), ("2026-10-06", "llama-8b-q8")]
    ws = {"aliases.json": J(alias)}
    for d, s, n in rig: ws[f"rig/{d}_{s}_run{n}.json"] = J(dict(date=d, slug=s, run=n))
    for d, s in qual: ws[f"quality/q-{d}-{s}.json"] = J(dict(date=d, slug_in_file=s))
    canon = lambda s: alias.get(s, s)
    latest = {}
    for d, s, n in rig:
        k = (d, s)
        if k not in latest or n > latest[k]: latest[k] = n
    pairs, used_r, used_q = [], set(), set()
    for d, s in sorted(qual):
        k = (d, canon(s))
        if k in latest:
            rf = f"{d}_{k[1]}_run{latest[k]}.json"; qf = f"q-{d}-{s}.json"
            pairs.append((k[1], d, rf, qf)); used_r.add(k); used_q.add(qf)
    pairs.sort()
    rig_names = {(d, s, n): f"{d}_{s}_run{n}.json" for d, s, n in rig}
    superseded = sorted(v for (d, s, n), v in rig_names.items() if latest[(d, s)] != n)
    paired_r = {p[2] for p in pairs}
    unp_r = sorted(v for v in rig_names.values() if v not in paired_r and v not in superseded)
    unp_q = sorted(f"q-{d}-{s}.json" for d, s in qual if f"q-{d}-{s}.json" not in used_q)
    csv_ = "slug,date,rig_file,quality_file\n" + "".join(",".join(p) + "\n" for p in pairs)
    lines = lambda l: "".join(x + "\n" for x in l)
    md = """
    # Pair rig reports with quality results

    `/workspace/rig/` has rig reports named `<date>_<slug>_run<N>.json`. `/workspace/quality/` has quality results named `q-<date>-<slug-as-written>.json`;
    their slug may be a short alias, and `/workspace/aliases.json` maps aliases to the canonical slug (a slug with no alias entry is already canonical).

    A quality result pairs with the rig report that has the same date and canonical slug. If several runs share a date and slug, only the highest run number counts;
    the lower runs are *superseded*.

    Write, all in `/workspace`:

    1. `pairs.csv` with header `slug,date,rig_file,quality_file` (file names without directory), one row per pair, sorted by slug then date. `slug` is canonical.
    2. `superseded.txt`: file names of superseded rig reports, one per line, sorted.
    3. `unpaired_rig.txt`: rig report file names that are neither paired nor superseded, one per line, sorted.
    4. `unpaired_quality.txt`: quality file names with no pair, one per line, sorted.

    Empty lists mean an empty file. Date must match exactly (no nearest-date matching).
    """
    chk = """
    r = rows("pairs.csv")
    chk("pairs-header", (rd("pairs.csv") or "").splitlines()[:1] == ["slug,date,rig_file,quality_file"])
    got = [tuple(x[k] for k in ("slug", "date", "rig_file", "quality_file")) for x in (r or [])]
    chk("pairs-exact", got == [tuple(x) for x in E["p"]], got)
    lst = lambda n: None if rd(n) is None else [l for l in rd(n).splitlines() if l.strip()]
    chk("superseded-exact", lst("superseded.txt") == E["s"], lst("superseded.txt"))
    chk("unpaired-rig-exact", lst("unpaired_rig.txt") == E["ur"], lst("unpaired_rig.txt"))
    chk("unpaired-quality-exact", lst("unpaired_quality.txt") == E["uq"], lst("unpaired_quality.txt"))
    chk("no-nearest-date-pairing", not any(x[1] == "2026-10-04" for x in got))
    """
    task("10-pair-rig-quality", "session-derived", "reconciliation", 15, "Pair rig and quality results", md, ws, chk,
         {"pairs.csv": csv_, "superseded.txt": lines(superseded), "unpaired_rig.txt": lines(unp_r), "unpaired_quality.txt": lines(unp_q)},
         dict(p=pairs, s=superseded, ur=unp_r, uq=unp_q), "Shape from a session pairing rig reports with quality results to draft an issue.")
DIFF["10-pair-rig-quality"] = "hard"

# ---------------------------------------------------------------- 11 job scheduling (hard)
def _best(jobs, cap=2):
    names = list(jobs)
    best = [10**9, None]
    def sgs(order):
        start = {}; usage = []  # list of (s,e,g)
        for n in order:
            j = jobs[n]
            t = max([j.get("ready", 0)] + [start[d] + jobs[d]["dur"] for d in j["deps"]])
            cands = sorted({t} | {s + jobs[m]["dur"] for m, s in start.items() if s + jobs[m]["dur"] > t})
            for c in cands:
                pts = {c} | {s for m, s in start.items() if c < s < c + j["dur"]}
                if all(sum(jobs[m]["gpus"] for m, s in start.items() if s <= x < s + jobs[m]["dur"]) + j["gpus"] <= cap for x in pts):
                    start[n] = c; break
        return start
    for perm in itertools.permutations(names):
        pos = {n: i for i, n in enumerate(perm)}
        if any(pos[d] > pos[n] for n in names for d in jobs[n]["deps"]): continue
        s = sgs(perm); mk = max(s[n] + jobs[n]["dur"] for n in names)
        if mk < best[0]: best = [mk, s]
    return best

def t11():
    jobs = {"fetch": dict(dur=30, gpus=0, deps=[], ready=0), "quant-a": dict(dur=50, gpus=2, deps=["fetch"]), "quant-b": dict(dur=40, gpus=1, deps=["fetch"]),
            "bench-a": dict(dur=35, gpus=2, deps=["quant-a"]), "bench-b": dict(dur=25, gpus=1, deps=["quant-b"]), "quality-b": dict(dur=45, gpus=1, deps=["quant-b"]),
            "docs": dict(dur=20, gpus=0, deps=[], ready=60), "report": dict(dur=15, gpus=0, deps=["bench-a", "bench-b", "quality-b", "docs"])}
    for j in jobs.values(): j.setdefault("ready", 0)
    mk, sched = _best(jobs)
    inp = [dict(name=n, duration_min=j["dur"], gpus=j["gpus"], after=j["deps"], not_before_min=j["ready"]) for n, j in jobs.items()]
    md = """
    # Schedule a chain of jobs on two GPUs

    `/workspace/jobs.json` lists jobs with `duration_min`, `gpus` (0, 1 or 2 of the 2 GPUs the job holds while it runs), `after` (jobs that must have **finished** before it starts)
    and `not_before_min` (it may not start earlier than this minute). Time starts at minute 0. Jobs cannot be interrupted. Several jobs may run at once as long as their `gpus` sum to at most 2 at every moment.

    Write `/workspace/schedule.json`: a JSON object mapping every job name to its integer start minute. The schedule must be valid and its makespan
    (latest finish minus 0) must be the **smallest possible**.
    """
    chk = """
    jobs = {j["name"]: j for j in jl("jobs.json") or []}
    s = jl("schedule.json")
    ok = isinstance(s, dict) and set(s) == set(jobs) and all(isinstance(v, int) and not isinstance(v, bool) for v in s.values())
    chk("schedule-complete-ints", ok, s)
    if ok:
        end = lambda n: s[n] + jobs[n]["duration_min"]
        chk("not-before-respected", all(s[n] >= jobs[n]["not_before_min"] for n in jobs))
        chk("dependencies-respected", all(s[n] >= end(d) for n in jobs for d in jobs[n]["after"]))
        pts = sorted(set(s.values()))
        chk("gpu-capacity-never-exceeded", all(sum(jobs[n]["gpus"] for n in jobs if s[n] <= t < end(n)) <= 2 for t in pts))
        mk = max(end(n) for n in jobs)
        chk("makespan-optimal", mk == E["mk"], "makespan %d, optimum %d" % (mk, E["mk"]))
        chk("makespan-within-10-percent", mk <= E["mk"] * 1.10, mk)
    """
    task("11-gpu-job-schedule", "session-derived", "planning", 20, "Optimal two-GPU job schedule", md, {"jobs.json": J(inp)}, chk,
         {"schedule.json": J(sched)}, dict(mk=mk), "Shape from sessions scheduling chains of eval/quant/bench jobs around two GPUs (chain-*.sh), rebuilt as a pure scheduling problem.")
DIFF["11-gpu-job-schedule"] = "hard"

# ---------------------------------------------------------------- 12 plan revision (hard)
def t12():
    steps = [("prep", "Prepare the rig", ["Stop the dev server.", "Confirm both GPUs are idle.", "(see Step @cleanup) for the stop procedure."]),
             ("fetch", "Fetch weights", ["Download the checkpoint.", "Verify checksums."]),
             ("legacy", "Convert legacy format", ["Run the converter.", "Keep the original files."]),
             ("quant", "Quantize", ["Run the fp8 recipe.", "Needs the output of Step @fetch."]),
             ("bench", "Bench", ["Run the 5-run bench.", "Record median decode tok/s."]),
             ("verify", "Verify quality", ["Run the quality gate.", "Compare against the Step @bench numbers."]),
             ("doc", "Write results", ["Fill the results template.", "Cite the Step @bench numbers and the Step @verify score."]),
             ("cleanup", "Cleanup", ["Remove temp files.", "Restart the dev server."])]
    def render(sts):
        key = {k: i + 1 for i, (k, t, b) in enumerate(sts)}
        out = ["# Plan", "", "Contents:"] + [f"{i+1}. {t}" for i, (k, t, b) in enumerate(sts)] + [""]
        for i, (k, t, b) in enumerate(sts):
            out.append(f"### Step {i+1}: {t}")
            n = 0
            for line in b:
                if line.startswith("@AC "):
                    n += 1; out.append(f"- AC-{i+1}.{n}: {line[4:]}")
                else:
                    out.append("- " + re.sub(r"@(\w+)", lambda m: str(key[m.group(1)]) if m.group(1) in key else "??", line))
            out.append("")
        return "\n".join(out)
    acs = lambda *x: ["@AC " + a for a in x]
    steps[1][2][:] = ["Download the checkpoint."] + acs("checksums match the manifest")
    steps[3][2][:] = ["Run the fp8 recipe.", "Needs the output of Step @fetch."] + acs("fp8 files exist")
    steps[4][2][:] = ["Run the 5-run bench."] + acs("median decode recorded in out/bench.json")
    steps[5][2][:] = ["Run the quality gate.", "Compare against the Step @bench numbers."] + acs("score within 1 point of baseline")
    steps[2][2][:] = ["Run the converter."] + acs("converted files load") + ["Skipped when @quant uses the new format."]
    plan = render(steps)
    # revised: delete legacy; insert warmup after fetch; merge bench+verify into "Bench and verify"; rename cleanup -> Teardown; refs to deleted steps are removed
    new = [s for s in steps if s[0] != "legacy"]
    bv = ("bench", "Bench and verify", ["Run the 5-run bench.", "Run the quality gate."] + acs("median decode recorded in out/bench.json", "score within 1 point of baseline"))
    new = [bv if s[0] == "bench" else s for s in new if s[0] != "verify"]
    i = [s[0] for s in new].index("fetch")
    new.insert(i + 1, ("warmup", "Warm-up run", ["Run one throwaway request.", "Discard its timing."] + acs("server answers 200 on /health")))
    new = [(k, "Teardown" if k == "cleanup" else t, b) for k, t, b in new]
    new = [(k, t, [re.sub(r"@verify", "@bench", x) for x in b]) for k, t, b in new]
    def fix(b): return [x for x in b if "Skipped when" not in x]
    new = [(k, t, ["Compare against the Step @bench numbers." if False else x for x in b]) for k, t, b in new]
    # step "doc": cite Step bench and Step verify -> both now the merged step
    new = [(k, t, [x for x in b]) for k, t, b in new]
    new = [(k, t, [x for x in b if not x.startswith("Compare against")]) for k, t, b in new]
    ref = render(new)
    exp_titles = [t for k, t, b in new]
    sect = {}
    for blk in re.split(r"(?m)^(?=### Step )", ref)[1:]:
        h = blk.splitlines()[0]; sect[h] = [l for l in blk.splitlines()[1:] if l.strip()]
    changes = """# Requested changes

1. Delete the step "Convert legacy format" entirely. Remove any line in another step that only refers to it.
2. Insert a new step "Warm-up run" right after "Fetch weights", with exactly these lines:
   - Run one throwaway request.
   - Discard its timing.
   - AC-<step>.1: server answers 200 on /health
3. Merge "Bench" and "Verify quality" into one step titled "Bench and verify": its lines are the instruction lines of Bench, then the instruction lines of Verify quality
   (drop the "Compare against ..." line, it no longer applies), then all acceptance criteria in their original order, renumbered.
4. Rename "Cleanup" to "Teardown".
5. Renumber every step, the Contents list, every `AC-<step>.<n>` id, and every "Step <number>" reference so everything is consistent. A reference to a merged step points at the merged step.
"""
    md = """
    # Revise a plan document

    `/workspace/plan.md` is a plan. `/workspace/changes.md` lists the edits to make. Apply all of them and write the result to `/workspace/plan-v2.md`
    (leave `plan.md` untouched). Keep the format: a `Contents:` numbered list, then `### Step N: Title` sections with `- ` bullet lines, acceptance criteria as `- AC-N.m: text`.
    """
    chk = """
    s = rd("plan-v2.md") or ""
    chk("plan-v1-untouched", hashlib.sha256((rd("plan.md") or "").encode()).hexdigest() == E["h"])
    toc = re.findall(r"(?m)^(\\d+)\\. (.+)$", s)
    chk("contents-matches", [(int(a), b.strip()) for a, b in toc] == [(i + 1, t) for i, t in enumerate(E["t"])], toc)
    heads = re.findall(r"(?m)^### Step (\\d+): (.+)$", s)
    chk("headings-match", [(int(a), b.strip()) for a, b in heads] == [(i + 1, t) for i, t in enumerate(E["t"])], heads)
    secs = {}
    for blk in re.split(r"(?m)^(?=### Step )", s)[1:]:
        ls = [l.rstrip() for l in blk.splitlines() if l.strip()]; secs[ls[0]] = ls[1:]
    for h, body in E["s"].items():
        chk("section-" + h.split(":")[1].strip().lower().replace(" ", "-"), secs.get(h) == body, secs.get(h))
    chk("no-stale-refs", "legacy" not in s.lower() and "??" not in s)
    """
    task("12-plan-revision", "session-derived", "writing", 18, "Revise a plan with renumbering", md,
         {"plan.md": plan, "changes.md": changes}, chk, {"plan-v2.md": ref},
         dict(h=__import__("hashlib").sha256(plan.encode()).hexdigest(), t=exp_titles, s=sect), "Shape from sessions revising plan docs (claude-model-router plan, kv-offload plan) where steps move and references must follow.")
DIFF["12-plan-revision"] = "hard"

# ---------------------------------------------------------------- 13 inbox triage
def _bd(d, n):
    while n:
        d += timedelta(days=1)
        if d.weekday() < 5: n -= 1
    return d

def t13():
    r = random.Random(113)
    vip = ["acme-hosting.example", "gpu-vendor.example"]
    subj = [("Weekly newsletter: tips for tuning", "bulk"), ("URGENT: billing failure on invoice 44", ""), ("Question about the preflight script", ""),
            ("Outage in the eu-west region", ""), ("[newsletter] October roundup", ""), ("Re: docs typo", ""), ("Invoice 88 attached", ""),
            ("Driver update for the 5090", ""), ("Lunch on Friday?", ""), ("Security notice: rotate your token", ""), ("Re: GPU quota request", "")]
    owners = [("invoice", "finance"), ("billing", "finance"), ("driver", "hardware"), ("gpu", "hardware"), ("token", "security"), ("security", "security"), ("preflight", "tooling"), ("docs", "docs")]
    senders = ["ana@acme-hosting.example", "bo@gpu-vendor.example", "cy@friends.example", "di@list.example", "ed@club.example", "fa@club.example"]
    ws, rows = {}, []
    for i in range(30):
        s, bulk = subj[i % len(subj)]
        s = s + ("" if i < 11 else f" #{i}")
        sender = senders[r.randrange(len(senders))]
        day = date(2026, 10, 5) + timedelta(days=r.randrange(0, 9))
        low = s.lower()
        if sender.split("@")[1] in vip or "outage" in low or "urgent" in low: pr = "P1"
        elif bulk or low.startswith("[newsletter]"): pr = "P3"
        else: pr = "P2"
        owner = next((o for k, o in owners if k in low), "unassigned")
        due = _bd(day, {"P1": 0, "P2": 2, "P3": 5}[pr])
        hdr = f"From: {sender}\nTo: me@club.example\nSubject: {s}\nDate: {day.strftime('%a, %d %b %Y')} 09:{i:02d}:00 +0000\n" + ("Precedence: bulk\n" if bulk else "") + "\nbody text\n"
        ws[f"inbox/m{i:02d}.eml"] = hdr
        rows.append((f"m{i:02d}", pr, owner, due.isoformat()))
    csv_ = "id,priority,owner,due\n" + "".join(",".join(x) + "\n" for x in rows)
    md = """
    # Triage the inbox

    `/workspace/inbox/` has 30 emails (`.eml`). Write `/workspace/triage.csv` with header `id,priority,owner,due`, one row per email, `id` = file name without `.eml`, sorted by id.

    **priority** (first rule that matches wins):
    1. `P1` if the sender domain is `acme-hosting.example` or `gpu-vendor.example`, or the subject contains `outage` or `urgent` (any case).
    2. `P3` if the message has a `Precedence: bulk` header, or the subject starts with `[newsletter]` (any case).
    3. otherwise `P2`.

    **owner**: the first row of this table whose keyword appears in the subject (any case), top to bottom; `unassigned` if none:
    `invoice` -> finance, `billing` -> finance, `driver` -> hardware, `gpu` -> hardware, `token` -> security, `security` -> security, `preflight` -> tooling, `docs` -> docs.

    **due**: the date in the email's `Date` header plus N business days (Monday to Friday; weekends are skipped when counting), as `YYYY-MM-DD`. N is 0 for P1, 2 for P2, 5 for P3.
    """
    chk = """
    r = rows("triage.csv")
    chk("csv-parses", bool(r))
    if r:
        chk("header-exact", (rd("triage.csv") or "").splitlines()[0].strip() == "id,priority,owner,due")
        chk("ids-complete-sorted", [x["id"] for x in r] == [e[0] for e in E["r"]])
        got = {x["id"]: x for x in r}
        for col, idx in (("priority", 1), ("owner", 2), ("due", 3)):
            good = sum(1 for e in E["r"] if got.get(e[0], {}).get(col) == e[idx])
            chk("column-%s-all-correct" % col, good == len(E["r"]), "%d/%d" % (good, len(E["r"])))
            chk("column-%s-at-least-27" % col, good >= 27)
    """
    task("13-inbox-triage", "novel", "triage", 12, "Triage 30 emails", md, ws, chk, {"triage.csv": csv_}, dict(r=rows),
         "Novel: rubric-driven inbox triage with business-day due dates.")
DIFF["13-inbox-triage"] = "easy"

# ---------------------------------------------------------------- 14 meeting scheduling (hard)
def t14():
    r = random.Random(114)
    people = {"ana": dict(tz=-1), "bo": dict(tz=1), "chen": dict(tz=3)}
    base = datetime(2026, 10, 12, 0, 0, tzinfo=timezone.utc)
    busy = {p: [] for p in people}
    ws = {}
    for p, o in people.items():
        lines = ["BEGIN:VCALENDAR", "VERSION:2.0"]
        for k in range(12):
            st = base + timedelta(days=r.randrange(0, 3), minutes=15 * r.randrange(0, 96)) 
            en = st + timedelta(minutes=15 * r.randrange(2, 7))
            busy[p].append((st, en))
            lines += ["BEGIN:VEVENT", f"UID:{p}{k}@example", f"DTSTART:{st.strftime('%Y%m%dT%H%M%SZ')}", f"DTEND:{en.strftime('%Y%m%dT%H%M%SZ')}", f"SUMMARY:busy {k}", "END:VEVENT"]
        lines.append("END:VCALENDAR")
        ws[f"calendars/{p}.ics"] = "\r\n".join(lines) + "\r\n"
    def ok(st):
        en = st + timedelta(minutes=45)
        for p, o in people.items():
            tz = timezone(timedelta(hours=o["tz"]))
            ls, le = st.astimezone(tz), en.astimezone(tz)
            if ls.weekday() > 4 or le.date() != ls.date(): return False
            m0 = ls.hour * 60 + ls.minute; m1 = m0 + 45
            if m0 < 9 * 60 or m1 > 17 * 60 + 30: return False
            if m0 < 13 * 60 and m1 > 12 * 60: return False
            for a, b in busy[p]:
                if st < b + timedelta(minutes=15) and en > a - timedelta(minutes=15): return False
        return True
    first = None
    t = base
    while t < base + timedelta(days=3):
        if ok(t): first = t; break
        t += timedelta(minutes=15)
    assert first, "no slot"
    ics = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nBEGIN:VEVENT\r\nUID:sync@example\r\nDTSTART:%s\r\nDTEND:%s\r\nSUMMARY:Sync\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n" % (
        first.strftime("%Y%m%dT%H%M%SZ"), (first + timedelta(minutes=45)).strftime("%Y%m%dT%H%M%SZ"))
    md = """
    # Find a meeting slot for three people

    `/workspace/calendars/` has one `.ics` file per person (`ana`, `bo`, `chen`) listing busy events in UTC. Find the **earliest** 45-minute slot that works for all three and write it
    to `/workspace/meeting.ics` as one `VEVENT` with `DTSTART`, `DTEND` (both UTC, `YYYYMMDDTHHMMSSZ`) and `SUMMARY:Sync`.

    Rules:
    - Candidate starts are on a 15-minute grid in UTC, from 2026-10-12T00:00Z up to but not including 2026-10-15T00:00Z.
    - Fixed UTC offsets (no daylight saving): ana UTC-1, bo UTC+1, chen UTC+3.
    - Each person's local working hours are 09:00 to 17:30, Monday to Friday, judged on **their** local clock; the whole slot must fit inside.
    - Local lunch 12:00 to 13:00 is blocked: the slot must not overlap it.
    - The slot must leave a gap of at least 15 minutes before and after every busy event of every person (it may not overlap one either).
    """
    chk = """
    s = rd("meeting.ics") or ""
    chk("one-vevent", s.count("BEGIN:VEVENT") == 1 and s.count("END:VEVENT") == 1)
    ds = re.search(r"(?m)^DTSTART:(\\d{8}T\\d{6}Z)\\s*$", s); de = re.search(r"(?m)^DTEND:(\\d{8}T\\d{6}Z)\\s*$", s)
    chk("dtstart-dtend-utc-format", bool(ds and de))
    chk("summary-sync", re.search(r"(?m)^SUMMARY:Sync\\s*$", s) is not None)
    if ds and de:
        a = ds.group(1); b = de.group(1)
        from datetime import datetime as D
        pa = D.strptime(a, "%Y%m%dT%H%M%SZ"); pb = D.strptime(b, "%Y%m%dT%H%M%SZ")
        chk("duration-45-min", (pb - pa).total_seconds() == 45 * 60)
        chk("earliest-valid-slot", a == E["s"], "got %s expected %s" % (a, E["s"]))
    """
    task("14-meeting-slot", "novel", "scheduling", 20, "Earliest slot across 3 time zones", md, ws, chk, {"meeting.ics": ics},
         dict(s=first.strftime("%Y%m%dT%H%M%SZ")), "Novel: calendar intersection with local working hours, lunch, and buffers.")
DIFF["14-meeting-slot"] = "hard"

for f in (t07, t08, t09, t10, t11, t12, t13, t14): f()
