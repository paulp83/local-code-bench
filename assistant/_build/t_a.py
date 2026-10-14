import hashlib, json, random
from datetime import datetime, timedelta, timezone
from common import task, DIFF

J = lambda o: json.dumps(o, indent=2) + "\n"

# ---------------------------------------------------------------- 01 issue bucketing
def t01():
    r = random.Random(101)
    labs = ["bug", "docs", "enhancement", "design", "good first issue", "question"]
    topics = ["launcher flag ignored", "preflight misreports free VRAM", "README typo in quickstart", "registry row missing quant",
              "bench script crashes on empty file", "TUI log pane stalls", "setup.sh hangs behind proxy", "slug table out of date",
              "kv cache size message unclear", "add --dry-run to bench", "support second GPU index", "docs: explain tok/s columns",
              "compose healthcheck too strict", "quality gate flaky", "env var name inconsistent", "model download resumes badly",
              "dashboard port clash", "log rotation missing"]
    issues, exp, ws = [], {}, {}
    for i, t in enumerate(topics):
        o = dict(number=300 + i * 7, title=t, labels=sorted(r.sample(labs, r.randint(1, 3))), files_touched=r.randint(1, 7),
                 has_repro=r.random() < 0.55, needs_gpu=r.random() < 0.35)
        s = (2 if o["files_touched"] > 3 else 0) + (0 if o["has_repro"] else 1) + (2 if o["needs_gpu"] else 0) \
            + (2 if "design" in o["labels"] else 0) - (2 if "good first issue" in o["labels"] else 0)
        o["_s"] = s
        exp[str(o["number"])] = "small" if s <= 0 else "medium" if s <= 2 else "large"
        ws[f"issues/{o['number']}.json"] = J({k: v for k, v in o.items() if k != "_s"})
    jun = sorted(int(n) for n, b in exp.items() if b == "small" and not [x for x in [json.loads(ws[f"issues/{n}.json"])] if x["needs_gpu"]])
    ref = {"buckets.json": J(exp), "junior.json": J(jun)}
    md = """
    # Bucket the open issues by effort

    `/workspace/issues/` holds one JSON file per open issue: `number`, `title`, `labels`, `files_touched` (estimated),
    `has_repro` (bool), `needs_gpu` (bool).

    Give every issue an effort score:

    - +2 if `files_touched` is greater than 3
    - +1 if `has_repro` is false
    - +2 if `needs_gpu` is true
    - +2 if the labels include `design`
    - -2 if the labels include `good first issue`

    Bucket: score <= 0 is `small`, 1 to 2 is `medium`, 3 or more is `large`.

    Deliverables:

    1. `/workspace/buckets.json`: a JSON object mapping each issue number (as a string key) to its bucket string.
    2. `/workspace/junior.json`: a JSON array of the issue numbers (integers, ascending) that are `small` and do not need a GPU.
    """
    chk = """
    b = jl("buckets.json"); j = jl("junior.json")
    chk("buckets-is-object", isinstance(b, dict))
    if isinstance(b, dict):
        chk("buckets-keys-complete", set(b) == set(E["b"]), "missing/extra keys")
        bad = [k for k in E["b"] if b.get(k) != E["b"][k]]
        chk("buckets-all-correct", not bad, "wrong: " + ",".join(bad[:6]))
        chk("buckets-at-least-14-correct", sum(b.get(k) == v for k, v in E["b"].items()) >= 14)
    chk("junior-exact", j == E["j"], j)
    """
    task("01-issue-effort-buckets", "session-derived", "triage", 10, "Bucket issues by effort", md, ws, chk, ref,
         dict(b=exp, j=jun), "Shape from omp sessions in the club-3090 repo and a private notes project: review open issues, bucket by level of effort for a part-time contributor.")

# ---------------------------------------------------------------- 02 thread asks
def t02():
    C = [
     (1, "nina-t", "Reproduced on 2x5090 with the stock compose. Logs attached."),
     (2, "owlmaint", "Thanks @nina-t, this is useful. Could you rerun with `--ctx 32768` and post the preflight output? Also please attach the compose file you used."),
     (3, "owlmaint", "@dev-ravi I merged the registry fix. Please rebase your branch when you can."),
     (4, "nina-t", "Rerun done. Please see the attached log, the preflight line is on page 2."),
     (5, "dev-ravi", "@nina-t does this also happen with the 4B slug?"),
     (6, "owlmaint", "> Please check the VRAM split\n> Can you confirm the driver version\nQuoting the template there, not a request. @nina-t the log shows 31.2 GiB used on GPU 1. Can you confirm that GPU 0 stays under 20 GiB?"),
     (7, "owlmaint", "General reminder for everyone: please keep logs under 1 MB."),
     (8, "nina-t", "GPU 0 stays at 18.4 GiB."),
     (9, "owlmaint", "Great. @nina-t Could you open a PR with the one-line fix? Please link this issue in the description. We can then cut a release."),
     (10, "owlmaint", "cc @nina-t no action needed on the docs side."),
     (11, "owlmaint", "@nina-t please add a regression test. Can you also run `bash scripts/preflight.sh` before pushing?"),
    ]
    th = dict(repo="example/club-demo", issue=77, maintainer="owlmaint", comments=[
        dict(id=i, author=a, created_at=f"2026-10-0{1 + i // 5}T1{i % 10}:00:00Z", body=b) for i, a, b in C])
    exp = {"2": 2, "6": 1, "9": 2, "11": 2}
    exp_s = {"2": ["Could you rerun with `--ctx 32768` and post the preflight output", "Also please attach the compose file you used"],
             "6": ["Can you confirm that GPU 0 stays under 20 GiB"],
             "9": ["Could you open a PR with the one-line fix", "Please link this issue in the description"],
             "11": ["please add a regression test", "Can you also run `bash scripts/preflight.sh` before pushing"]}
    ref = {"asks.json": J([dict(comment_id=int(k), requests=[s + "." for s in v]) for k, v in exp_s.items()])}
    md = """
    # List what the maintainer asked of @nina-t

    `/workspace/thread.json` is an export of a GitHub issue thread (`comments`: id, author, created_at, body).
    The maintainer's login is `owlmaint`.

    Find every request the maintainer made to `nina-t`:

    - Only comments authored by `owlmaint` that mention `@nina-t` count.
    - Ignore any line that starts with `>` (a quote).
    - A request is a sentence containing `please` (any case) or starting with `Can you` or `Could you`. Sentences end at `.`, `?`, `!` or a newline.
    - An `@mention` at the start of a sentence is not part of it: drop it (and the space after it) before applying the rule above and before writing the sentence.
    - A comment can hold several requests.

    Write `/workspace/asks.json`: a JSON array, ordered by comment id, of objects
    `{"comment_id": <int>, "requests": [<sentence text>, ...]}`, one object per qualifying comment, with each request sentence exactly as written
    in the comment (a trailing `.`, `?` or `!` is optional; case is ignored when checked).
    """
    chk = """
    a = jl("asks.json")
    chk("asks-is-list", isinstance(a, list))
    if isinstance(a, list):
        got = {}
        for o in a:
            if isinstance(o, dict): got[str(o.get("comment_id"))] = [re.sub(r"[.?!\\s]+$", "", s).strip().lower() for s in o.get("requests", []) if isinstance(s, str)]
        chk("ids-exact", set(got) == set(E["s"]), sorted(got))
        chk("ordered-by-id", [o.get("comment_id") for o in a if isinstance(o, dict)] == sorted(int(k) for k in E["s"]))
        for k, v in E["s"].items():
            want = sorted(re.sub(r"[.?!\\s]+$", "", s).strip().lower() for s in v)
            chk("comment-" + k, sorted(got.get(k, [])) == want, got.get(k))
    """
    task("02-thread-asks", "session-derived", "reading", 8, "List maintainer asks", md, {"thread.json": J(th)}, chk, ref,
         dict(s=exp_s), "Shape from sessions where the maintainer replied on a GitHub thread and the user asked what was requested of them.")

# ---------------------------------------------------------------- 03 rig report table
def t03():
    r = random.Random(103)
    cfgs = ["tp2-fp8", "tp2-awq", "single-q4", "pp2-q6", "offload-q8"]
    data, secs, final = {}, [], {}
    for i, c in enumerate(cfgs):
        d = round(r.uniform(40, 110), 1); pf = r.randint(2100, 9800); v = r.randint(18000, 32000)
        data[c] = (d, pf, v)
    oom = "offload-q8"
    for c in cfgs:
        d, pf, v = data[c]
        if c == oom:
            secs.append(f"## Config `{c}`\n\nLoaded fine, then died on the first long prompt: CUDA out of memory. No numbers.\n")
        elif c == "pp2-q6":
            secs.append(f"## Config `{c}`\n\nDecode ran at {d} tok/s (median of 5). Prefill was {pf:,} tok/s. Peak VRAM {v/1024:.1f} GiB per card.\n")
        else:
            secs.append(f"## Config `{c}`\n\nMeasured: decode {d} tok/s, prefill {pf:,} tok/s. Peak VRAM was {v:,} MiB per card.\n")
    corr_d = round(data["tp2-awq"][0] - 4.3, 1)
    secs.append(f"## Corrections\n\nThe first `tp2-awq` decode run overlapped with a log rotation job. Re-run result: decode {corr_d} tok/s. Use this and drop the earlier figure. Prefill and VRAM from the first run stand.\n")
    rep = "# Rig report 2026-10-03\n\nHardware: 2x consumer 32 GB cards. Same prompt set for every config.\n\n" + "\n".join(secs)
    rows = []
    for c in cfgs:
        d, pf, v = data[c]
        if c == oom: rows.append(f"| {c} | n/a | n/a | n/a |")
        else:
            if c == "tp2-awq": d = corr_d
            rows.append(f"| {c} | {d:.1f} | {pf} | {v/1024:.1f} |")
    tbl = "| config | decode_tps | prefill_tps | peak_vram_gib |\n|---|---|---|---|\n" + "\n".join(rows) + "\n"
    exp = [[x.strip() for x in row.strip("|").split("|")] for row in rows]
    md = """
    # Summarise the rig report as a table

    `/workspace/rig-report.md` has one section per config plus a corrections section.

    Write `/workspace/summary.md` containing a markdown table with exactly this header row:

    `| config | decode_tps | prefill_tps | peak_vram_gib |`

    One row per config, in the order the report lists them, config names without backticks. Rules:

    - Use the corrected value where the report corrects one.
    - `decode_tps`: one decimal place. `prefill_tps`: integer, no thousands separators.
    - `peak_vram_gib`: GiB with one decimal place (1 GiB = 1024 MiB; round half up on the exact value).
    - A config with no numbers gets `n/a` in all three value columns.
    """
    chk = """
    s = rd("summary.md")
    chk("summary-exists", s is not None)
    tb = [l for l in (s or "").splitlines() if l.strip().startswith("|")]
    chk("header-exact", bool(tb) and re.sub(r"\\s+", " ", tb[0].strip()) == "| config | decode_tps | prefill_tps | peak_vram_gib |", tb[:1])
    body = [[c.strip() for c in l.strip().strip("|").split("|")] for l in tb[2:]] if len(tb) > 2 else []
    chk("row-order", [b[0] for b in body] == [x[0] for x in E["c"]], [b[0] for b in body])
    got = {b[0]: b[1:] for b in body if len(b) == 4}
    for k, *v in E["c"]:
        chk("row-" + k, got.get(k) == v, got.get(k))
    """
    task("03-rig-report-table", "session-derived", "summarising", 10, "Rig report to table", md, {"rig-report.md": rep}, chk,
         {"summary.md": "# Summary\n\n" + tbl}, dict(c=exp), "Shape from sessions summarising rig/bench reports into fixed tables (units, one superseded figure).")

# ---------------------------------------------------------------- 04 archive filing
def t04():
    contract = """# Archive naming contract

Result docs live in `archive/results/`. File name: `<YYYY-MM-DD>_<slug>_<kind>.md`.

- `<YYYY-MM-DD>`: the doc's `date` front-matter field.
- `<slug>`: the `model` field and the `quant` field joined with `-`, lowercased, every `.` and `_` and space replaced with `-`.
- `<kind>`: the `type` field (`rig`, `quality` or `bench`).

`archive/INDEX.md` has one `## YYYY-MM` section per month, newest month last. Each section holds a table
`| date | slug | kind | file | verdict |`. Rows are sorted by date ascending (ties: keep existing order, new row after).
The `verdict` cell is the text after `Verdict:` on the doc's Verdict line.
"""
    idx = """# Archive index

## 2026-09

| date | slug | kind | file | verdict |
|---|---|---|---|---|
| 2026-09-02 | glm-5-3-flash-q4 | rig | 2026-09-02_glm-5-3-flash-q4_rig.md | fits on 2 cards, 62 tok/s |
| 2026-09-20 | qwen-flash-next-fp8 | bench | 2026-09-20_qwen-flash-next-fp8_bench.md | fastest decode so far |

## 2026-10

| date | slug | kind | file | verdict |
|---|---|---|---|---|
| 2026-10-01 | glm-5-3-flash-q6 | quality | 2026-10-01_glm-5-3-flash-q6_quality.md | no quality loss vs fp16 |
| 2026-10-07 | qwen-flash-next-fp8 | rig | 2026-10-07_qwen-flash-next-fp8_rig.md | OOM above 64k context |
"""
    doc = """---
title: Draft result
date: 2026-10-04
model: Qwen3.8_Flash Next
quant: UD-Q4_K_XL
type: bench
---

# Bench run

Eight runs, median decode 71.3 tok/s.

Verdict: stable at 71 tok/s, no stalls over 2 h
"""
    ws = {"archive/NAMING.md": contract, "archive/INDEX.md": idx, "inbox/result-draft.md": doc}
    for n, d in [("2026-09-02_glm-5-3-flash-q4_rig.md", "a"), ("2026-09-20_qwen-flash-next-fp8_bench.md", "b"),
                 ("2026-10-01_glm-5-3-flash-q6_quality.md", "c"), ("2026-10-07_qwen-flash-next-fp8_rig.md", "d")]:
        ws["archive/results/" + n] = f"# {n}\n\nplaceholder {d}\n"
    newname = "2026-10-04_qwen3-8-flash-next-ud-q4-k-xl_bench.md"
    nidx = idx.replace("| 2026-10-07 |", f"| 2026-10-04 | qwen3-8-flash-next-ud-q4-k-xl | bench | {newname} | stable at 71 tok/s, no stalls over 2 h |\n| 2026-10-07 |")
    ref = {"archive/results/" + newname: doc, "archive/INDEX.md": nidx, "_delete.txt": "inbox/result-draft.md\n"}
    md = """
    # File a result doc into the archive

    `/workspace/inbox/result-draft.md` is a finished result doc. File it following `/workspace/archive/NAMING.md`:

    1. Move it into `archive/results/` under the name the contract gives (content unchanged).
    2. Add its row to `archive/INDEX.md` in the correct month section and position.
    3. Leave every other file and index row exactly as it is. The inbox must no longer contain the draft.
    """
    chk = """
    t = "archive/results/" + E["name"]
    chk("file-named-correctly", rd(t) == E["doc"], "expected " + E["name"])
    chk("draft-removed-from-inbox", not os.path.exists(p("inbox/result-draft.md")))
    chk("no-stray-files-in-results", sorted(os.listdir(p("archive/results"))) == sorted(E["names"]), sorted(os.listdir(p("archive/results"))))
    s = rd("archive/INDEX.md") or ""
    chk("index-matches-expected", s.strip() == E["idx"].strip(), "index differs from expected text")
    chk("index-row-present", E["row"] in s)
    chk("old-rows-kept", all(l in s for l in E["old"]))
    chk("section-order", s.find("## 2026-09") < s.find("## 2026-10") and s.count("## ") == 2)
    """
    old = [l for l in idx.splitlines() if l.startswith("| 2026")]
    names = sorted([k.split("/")[-1] for k in ws if k.startswith("archive/results/")] + [newname])
    task("04-archive-filing", "session-derived", "filing", 8, "File result into archive", md, ws, chk, ref,
         dict(name=newname, doc=doc, idx=nidx, row=f"| 2026-10-04 | qwen3-8-flash-next-ud-q4-k-xl | bench | {newname} | stable at 71 tok/s, no stalls over 2 h |", old=old, names=names),
         "Shape from sessions filing results into the notes archive with a naming contract and an INDEX row.")

# ---------------------------------------------------------------- 05 cold storage
def t05():
    r = random.Random(105)
    files = {}
    for i in range(14):
        d = ["logs", "logs/rig", "weights", "notes", "notes/old stuff"][i % 5]
        nm = ["a.log", "b run.json", "c.bin", "d.md", "e.txt"][i % 5] if i < 5 else f"f{i}.dat"
        files[f"{d}/{nm}"] = bytes(r.randrange(256) for _ in range(r.randint(20, 400)))
    files["logs/scratch1.tmp"] = b"junk"; files["notes/old stuff/draft.tmp"] = b"junk2"
    links = {"latest.log": "logs/a.log", "weights/current": "c.bin", "notes/toplevel": "../logs"}
    base = "hot/runs-2026-08/"
    ws = {base + k: v for k, v in files.items()} | {base + k: ("link", v) for k, v in links.items()}
    ref = {"_delete.txt": "hot/runs-2026-08\n"}
    kept = {k: v for k, v in files.items() if not k.endswith(".tmp")}
    ref |= {"cold/runs-2026-08/" + k: v for k, v in kept.items()} | {"cold/runs-2026-08/" + k: ("link", v) for k, v in links.items()}
    hashes = {k: hashlib.sha256(v).hexdigest() for k, v in kept.items()}
    man = "".join(f"{h}  {k}\n" for k, h in sorted(hashes.items()))
    ref["cold/runs-2026-08.sha256"] = man
    ref["cold/runs-2026-08.links.txt"] = "".join(f"{k} -> {v}\n" for k, v in sorted(links.items()))
    md = """
    # Move a run directory to cold storage

    Move `/workspace/hot/runs-2026-08` to `/workspace/cold/runs-2026-08` and verify the move.

    - `*.tmp` files are scratch: delete them, do not move them.
    - Symbolic links must stay symbolic links with the same link text (do not follow or copy them).
    - After the move `/workspace/hot/runs-2026-08` must not exist.
    - Write `/workspace/cold/runs-2026-08.sha256` in `sha256sum` format (`<hash>  <path>`, two spaces) for every regular file in the moved tree,
      paths relative to `cold/runs-2026-08`, sorted by path (plain byte order). Symlinks are not listed there.
    - Write `/workspace/cold/runs-2026-08.links.txt` with one line `<relative path> -> <link text>` per symlink, sorted by path.
    """
    chk = """
    root = p("cold", "runs-2026-08")
    chk("hot-dir-gone", not os.path.lexists(p("hot", "runs-2026-08")))
    got = {}
    links = {}
    for dp, dn, fn in os.walk(root):
        for f in fn + dn:
            full = os.path.join(dp, f); rel = os.path.relpath(full, root)
            if os.path.islink(full): links[rel] = os.readlink(full)
            elif os.path.isfile(full): got[rel] = hashlib.sha256(open(full, "rb").read()).hexdigest()
    chk("regular-files-intact", got == E["h"], "files differ: %d vs %d" % (len(got), len(E["h"])))
    chk("no-tmp-files", not [k for k in got if k.endswith(".tmp")])
    chk("symlinks-preserved", links == E["l"], links)
    chk("manifest-exact", rd("cold/runs-2026-08.sha256") == E["m"], "manifest differs")
    chk("links-file-exact", rd("cold/runs-2026-08.links.txt") == E["lt"], "links file differs")
    """
    task("05-cold-storage-move", "session-derived", "files", 10, "Cold-storage move with manifest", md, ws, chk, ref,
         dict(h=hashes, l=links, m=man, lt=ref["cold/runs-2026-08.links.txt"]),
         "Shape from sessions moving run trees to cold storage with a verified sha256 list and symlinks preserved.")

# ---------------------------------------------------------------- 06 job chain log
def t06():
    L = []
    def ts(m, s): return (datetime(2026, 10, 4, 1, 0, 0, tzinfo=timezone.utc) + timedelta(minutes=m, seconds=s)).strftime("%Y-%m-%dT%H:%M:%SZ")
    L += [f"{ts(0,0)} [chain] boot: queue has 6 stages", f"{ts(0,3)} [chain] stage=fetch start", f"{ts(4,41)} [chain] stage=fetch done rc=0",
          f"{ts(4,45)} [chain] stage=quant start", f"{ts(4,50)} [gpu0] mem 1204MiB", f"{ts(9,12)} [chain] stage=quant FAILED rc=1 (disk full)",
          f"{ts(9,20)} [chain] stage=quant start (retry 1)", f"{ts(15,2)} [chain] stage=quant done rc=0",
          f"{ts(15,5)} [chain] stage=bench start", f"{ts(15,9)} [gpu1] mem 30114MiB", f"{ts(33,30)} [chain] stage=bench done rc=0",
          f"{ts(33,31)} [chain] stage=quality start", f"{ts(40,0)} [chain] stage=quality FAILED rc=137 (OOM)",
          f"{ts(40,2)} [chain] stage=report skipped (dependency quality failed)", f"{ts(40,3)} [chain] stage=publish skipped (dependency report not run)",
          f"{ts(40,4)} [chain] chain finished with failures"]
    log = "\n".join(L) + "\n"
    def sec(a, b):
        f = lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")
        return int((f(b) - f(a)).total_seconds())
    rows = [("fetch", 1, ts(0, 3), ts(4, 41), "ok"), ("quant", 2, ts(9, 20), ts(15, 2), "ok"), ("bench", 1, ts(15, 5), ts(33, 30), "ok"),
            ("quality", 1, ts(33, 31), ts(40, 0), "failed"), ("report", 0, "", "", "skipped"), ("publish", 0, "", "", "skipped")]
    csv_ = "stage,attempts,start,end,result,duration_s\n" + "".join(
        f"{s},{a},{b},{e},{r},{sec(b, e) if b else ''}\n" for s, a, b, e, r in rows)
    exp = [dict(stage=s, attempts=str(a), start=b, end=e, result=r, duration_s=str(sec(b, e)) if b else "") for s, a, b, e, r in rows]
    md = """
    # Turn a job-chain log into a status table

    `/workspace/chain.log` is the log of a chain of stages. Write `/workspace/status.csv` with the header
    `stage,attempts,start,end,result,duration_s` and one row per stage, ordered by the first log line that names the stage.

    - `attempts`: how many times the stage started (a retry counts); 0 if it never started.
    - `start`, `end`: timestamps exactly as logged, of the **last** attempt's `start` line and its `done` or `FAILED` line. Empty if the stage never started.
    - `result`: `ok` if the last attempt logged `done`, `failed` if it logged `FAILED`, `skipped` if the stage was skipped.
    - `duration_s`: whole seconds from `start` to `end`; empty for skipped stages.
    - Lines that are not stage events (for example GPU memory lines) are noise.
    """
    chk = """
    r = rows("status.csv")
    chk("csv-parses", r is not None and len(r) > 0)
    if r:
        chk("header-exact", (rd("status.csv") or "").splitlines()[0].strip() == "stage,attempts,start,end,result,duration_s")
        chk("stage-order", [x.get("stage") for x in r] == [e["stage"] for e in E["r"]], [x.get("stage") for x in r])
        got = {x.get("stage"): {k: (v or "").strip() for k, v in x.items()} for x in r}
        for e in E["r"]:
            chk("row-" + e["stage"], got.get(e["stage"]) == e, got.get(e["stage"]))
    """
    task("06-job-chain-status", "session-derived", "summarising", 8, "Chain log to status table", md, {"chain.log": log}, chk,
         {"status.csv": csv_}, dict(r=exp), "Shape from sessions that chained long eval/quant/bench jobs and had to report what ran, failed or was skipped.")

for f in (t01, t02, t03, t04, t05, t06): f()

DIFF.update({"01-issue-effort-buckets": "easy", "02-thread-asks": "medium", "03-rig-report-table": "easy", "04-archive-filing": "medium", "05-cold-storage-move": "medium", "06-job-chain-status": "medium"})
