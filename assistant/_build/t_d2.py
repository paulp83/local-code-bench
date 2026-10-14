import json, random, re, hashlib, csv, io
from datetime import date, datetime, timedelta
from decimal import Decimal as D, ROUND_HALF_UP
from common import task, DIFF

J = lambda o: json.dumps(o, indent=2) + "\n"
def tocsv(head, rows):
    o = io.StringIO(); w = csv.writer(o, lineterminator="\n"); w.writerow(head); w.writerows(rows); return o.getvalue()

# =============================================================== 31 merge three vendor price lists (C)
def t31():
    r = random.Random(131)
    nm = ["Cable", "Bracket", "Fan", "Rail", "Clip", "Panel", "Sleeve", "Adapter", "Bolt", "Strap"]
    skus = []
    for i in range(60):
        skus.append(dict(sku=f"{r.choice('ABCD')}{r.choice('XYZ')}-{100 + i * 7}", desc=f"{r.choice(nm)} {r.choice(['small', 'large', 'black', 'steel'])}", unit=D(r.randrange(150, 9000)) / 100))
    vend = {"Alder": {}, "Birch": {}, "Cobalt": {}}
    case = {"Birch": 12, "Cobalt": 1, "Alder": 1}
    true_conf, notes = [], []
    for s in skus:
        who = [v for v in vend if r.random() < 0.7] or ["Alder"]
        if len(who) == 1 and r.random() < .5: who.append(r.choice([v for v in vend if v != who[0]]))
        for v in who: vend[v][s["sku"]] = [s["unit"], s["desc"]]
    keys = list(vend["Alder"].keys() & vend["Birch"].keys() & vend["Cobalt"].keys()) or list(skus)
    shared = [s["sku"] for s in skus if sum(s["sku"] in vend[v] for v in vend) >= 2]
    r.shuffle(shared)
    conflict = set(shared[:7])
    for sk in sorted(conflict):
        v = [x for x in vend if sk in vend[x]]; w = r.choice(v)
        vend[w][sk][0] = vend[w][sk][0] + D(r.choice([1, 2, 5, 10])) / 100 * r.choice([1, -1]) if vend[w][sk][0] > 1 else vend[w][sk][0] + D("0.25")
    # Birch lists per-case price (12): agree after conversion for non-conflicts. Cobalt/Alder per unit. One SKU where raw numbers match but Birch's is per case -> real conflict.
    birch_raw = {}
    trap_same_raw = [s for s in shared[7:] if s not in conflict and "Birch" in [x for x in vend if s in vend[x]] and len([x for x in vend if s in vend[x]]) >= 2][:1]
    for sk in trap_same_raw:
        u = [vend[x][sk][0] for x in vend if x != "Birch" and sk in vend[x]]
        if u: conflict.add(sk); birch_raw[sk] = u[0]  # Birch's raw case price equals the other vendor's unit price; per unit it differs
    # within-vendor duplicate with different prices
    dupsku = next(s for s in shared if s not in conflict and "Alder" in [x for x in vend if s in vend[x]])
    conflict.add(dupsku)
    files = {}
    def norm(s): return re.sub(r"[^A-Z0-9]", "", s.upper())
    rows_a = [[k.lower() if i % 3 == 0 else k, v[1], f"{v[0]:.2f}", "USD"] for i, (k, v) in enumerate(vend["Alder"].items())]
    rows_a.append([dupsku, vend["Alder"][dupsku][1], f"{vend['Alder'][dupsku][0] + D('0.40'):.2f}", "USD"])
    files["vendors/alder.csv"] = tocsv(["item_code", "name", "unit_price", "currency"], rows_a)
    rows_b = [[k.replace("-", ""), v[1], f"{(birch_raw.get(k, v[0] * 12)):.2f}", "12"] for k, v in vend["Birch"].items()]
    files["vendors/birch.csv"] = tocsv(["SKU", "description", "case_price", "case_size"], rows_b)
    files["vendors/cobalt.csv"] = tocsv(["sku", "desc", "price_usd"], [[k, v[1], f"{v[0]:.2f}"] for k, v in vend["Cobalt"].items()])
    # compute truth with the stated rules
    price = {}
    for vname, lst in (("Alder", rows_a), ("Birch", rows_b), ("Cobalt", [[k, v[1], f"{v[0]:.2f}"] for k, v in vend["Cobalt"].items()])):
        for row in lst:
            if vname == "Alder": sk, desc, up = norm(row[0]), row[1], D(row[2])
            elif vname == "Birch": sk, desc, up = norm(row[0]), row[1], (D(row[2]) / D(row[3])).quantize(D("0.01"), ROUND_HALF_UP)
            else: sk, desc, up = norm(row[0]), row[1], D(row[2])
            price.setdefault(sk, {}).setdefault(vname, set()).add(up); price[sk].setdefault("_desc", {}).setdefault(vname, desc)
    merged, conflicts = [], {}
    for sk in sorted(price):
        pv = {v: sorted(ps) for v, ps in price[sk].items() if v != "_desc"}
        allp = {p for ps in pv.values() for p in ps}
        desc = next(price[sk]["_desc"][v] for v in ("Alder", "Birch", "Cobalt") if v in price[sk]["_desc"])
        if len(allp) > 1: conflicts[sk] = {v: [f"{p:.2f}" for p in ps] for v, ps in sorted(pv.items())}; merged.append([sk, desc, "", ";".join(sorted(pv))])
        else: merged.append([sk, desc, f"{next(iter(allp)):.2f}", ";".join(sorted(pv))])
    # naive: concat, take first listed raw price per normalised sku, conflicts by raw mismatch
    raw = {}
    for vname, lst in (("Alder", rows_a), ("Birch", rows_b), ("Cobalt", [[k, v[1], f"{v[0]:.2f}"] for k, v in vend["Cobalt"].items()])):
        for row in lst: raw.setdefault(norm(row[0]), []).append((vname, row[2]))
    nmerged = [[sk, "", ps[0][1], ";".join(sorted({v for v, _ in ps}))] for sk, ps in sorted(raw.items())]
    nconf = {sk: {v: [p] for v, p in ps} for sk, ps in raw.items() if len({p for _, p in ps}) > 1}
    md = """
    # Merge three vendor price lists

    `/workspace/vendors/` has `alder.csv`, `birch.csv` and `cobalt.csv`. They use different column names and units.

    - Alder: `item_code`, `name`, `unit_price` (USD per unit), `currency` (always USD).
    - Birch: `SKU`, `description`, `case_price` (USD for a whole case), `case_size` (units per case). Unit price = `case_price / case_size`, rounded half up to 2 decimals.
    - Cobalt: `sku`, `desc`, `price_usd` (USD per unit).

    A SKU is identified by its code uppercased with every non-alphanumeric character removed (`ax-107`, `AX-107` and `AX107` are the same SKU). Descriptions may differ between vendors; that is **not** a conflict.

    A SKU is **in conflict** when the unit prices it has across the lists (all rows, all vendors) are not all equal. That includes one vendor listing the same SKU twice with different prices.

    Write:
    1. `/workspace/merged.csv` with header `sku,description,unit_price,vendors`: one row per SKU sorted by SKU; `description` from the first vendor in the order Alder, Birch, Cobalt that lists it;
       `unit_price` with 2 decimals, or empty if the SKU is in conflict; `vendors` the vendors that list it, sorted, joined by `;`.
    2. `/workspace/conflicts.json`: an object mapping each conflicting SKU to an object `{vendor: [unit prices as 2-decimal strings, ascending, no repeats]}` for the vendors that list it. Report **exactly** the conflicting SKUs, no others.
    """
    chk = """
    m = rows("merged.csv"); c = jl("conflicts.json")
    chk("merged-header", (rd("merged.csv") or "").splitlines()[:1] == ["sku,description,unit_price,vendors"])
    got = {x["sku"]: x for x in (m or [])}
    chk("merged-skus-exact", sorted(got) == sorted(E["m"]), "%d vs %d" % (len(got), len(E["m"])))
    chk("merged-sorted", [x["sku"] for x in (m or [])] == sorted(E["m"]))
    bad = [k for k, v in E["m"].items() if got.get(k) is None or [got[k]["unit_price"], got[k]["vendors"]] != v[1:]]
    chk("merged-prices-and-vendors", not bad, bad[:4])
    chk("merged-descriptions", all(got.get(k) and got[k]["description"] == v[0] for k, v in E["m"].items()))
    chk("conflicts-parses", isinstance(c, dict))
    c = c if isinstance(c, dict) else {}
    chk("conflicts-skus-exact", sorted(c) == sorted(E["c"]), "missing %s extra %s" % (sorted(set(E["c"]) - set(c))[:3], sorted(set(c) - set(E["c"]))[:3]))
    chk("conflicts-no-false-positives", not (set(c) - set(E["c"])), sorted(set(c) - set(E["c"]))[:4])
    chk("conflicts-no-misses", not (set(E["c"]) - set(c)), sorted(set(E["c"]) - set(c))[:4])
    chk("conflicts-detail", all(c.get(k) == v for k, v in E["c"].items()))
    chk("conflict-rows-blank-price", all(got.get(k) and got[k]["unit_price"] == "" for k in E["c"]))
    """
    spec = [("merged-header", "`/workspace/merged.csv` with header `sku,description,unit_price,vendors`"), ("merged-skus", "one row per SKU sorted by SKU"), ("merged-sorted", "one row per SKU sorted by SKU"),
            ("merged-prices", "`unit_price` with 2 decimals, or empty if the SKU is in conflict"), ("merged-descriptions", "`description` from the first vendor in the order Alder, Birch, Cobalt that lists it"),
            ("conflicts-parses", "`/workspace/conflicts.json`: an object mapping each conflicting SKU"), ("conflicts-skus", "Report **exactly** the conflicting SKUs, no others."),
            ("conflicts-no-false", "Report **exactly** the conflicting SKUs, no others."), ("conflicts-no-misses", "Report **exactly** the conflicting SKUs, no others."),
            ("conflicts-detail", "`{vendor: [unit prices as 2-decimal strings, ascending, no repeats]}` for the vendors that list it"),
            ("conflict-rows-blank", "`unit_price` with 2 decimals, or empty if the SKU is in conflict")]
    em = {k: [d, p, v] for k, d, p, v in merged}
    note = ("A naive concat-and-compare treats `ax-107` and `AX107` as different SKUs, compares Birch's case price against unit prices, and misses the SKU whose raw numbers match while Birch's is per case. "
            "Fails: merged-prices-and-vendors, conflicts-skus-exact, conflicts-no-false-positives/misses.")
    task("31-vendor-price-merge", "novel", "conflicting-sources", 35, "Merge price lists and report conflicts", md, files, chk,
         {"merged.csv": tocsv(["sku", "description", "unit_price", "vendors"], merged), "conflicts.json": J(conflicts)},
         dict(m=em, c=conflicts), note, axis="C", spec=spec,
         naive={"merged.csv": tocsv(["sku", "description", "unit_price", "vendors"], nmerged), "conflicts.json": J(nconf)})

# =============================================================== 32 event plan with contradictions (C)
def t32():
    codes = {"CAPACITY": "the venue's maximum seated capacity is below the number of confirmed (`yes`) RSVP guests (count `guests` of each `yes` row, plus 1 for the guest themself)",
             "TIME_MISMATCH": "a file (or two files) states the same event time in two forms that are not the same instant (all offsets are fixed: CET = UTC+1)",
             "CATERING_SHORT": "the `mains` count in `catering.csv` is below the confirmed guest count",
             "OVER_BUDGET": "the sum of the quotes in `quotes.csv` is above the budget in `budget.md`",
             "WEEKDAY_MISMATCH": "a file names a weekday that does not match the ISO date next to it",
             "DUPLICATE_RSVP": "the same email address appears on more than one `yes` row in `rsvp.csv` (case-insensitive)",
             "HOLIDAY_CLASH": "the event date is in `holidays.txt`",
             "NO_ACCESSIBLE_ENTRY": "`venue.json` has `step_free_entry` false while at least one confirmed guest has `needs_step_free` true"}
    ven = dict(name="Harbor Hall", seated_capacity=110, standing_capacity=160, step_free_entry=True)
    rsvp = [["Ana Ruiz", "ana@example.net", "yes", "1", "no"], ["Bo Lind", "bo@example.net", "yes", "2", "no"], ["Cy Zhao", "cy@example.net", "maybe", "3", "no"],
            ["Di Sato", "di@example.net", "no", "0", "no"], ["Ed Moss", "ED@example.net", "yes", "0", "yes"]]
    # make 5 true issues: CAPACITY, TIME_MISMATCH, CATERING_SHORT, OVER_BUDGET, WEEKDAY_MISMATCH
    rr = random.Random(132)
    for i in range(40): rsvp.append([f"Guest {i}", f"g{i}@example.net", "yes", str(rr.choice([0, 1, 1, 2])), "no"])
    for i in range(10): rsvp.append([f"Maybe {i}", f"m{i}@example.net", "maybe", "1", "no"])
    yes_total = sum(1 + int(x[3]) for x in rsvp if x[2] == "yes")
    ven["seated_capacity"] = yes_total - 7
    meals = yes_total - 12
    quotes = [["catering", "2400.00"], ["venue", "2100.00"], ["av", "900.00"], ["flowers", "380.00"]]
    budget = 5500
    sched = ("# Schedule\n\nDate: Friday 2026-11-14\n\n| item | start |\n|---|---|\n| doors | 17:30 CET |\n| welcome | 18:00 CET (17:00 UTC) |\n"
             "| keynote | 19:00 CET (17:30 UTC) |\n| dinner | 20:15 CET (19:15 UTC) |\n")
    inv = ("# Invitation text\n\nJoin us on Saturday 2026-11-14. Doors 17:30 CET, welcome at 18:00 CET.\n")
    md_budget = f"# Budget\n\nTotal budget: {budget:.2f} USD\n"
    holidays = "2026-12-24\n2026-12-25\n2027-01-01\n"
    expected = [dict(code="CAPACITY", files=["rsvp.csv", "venue.json"]), dict(code="TIME_MISMATCH", files=["schedule.md"]),
                dict(code="CATERING_SHORT", files=["catering.csv", "rsvp.csv"]), dict(code="OVER_BUDGET", files=["budget.md", "quotes.csv"]),
                dict(code="WEEKDAY_MISMATCH", files=["schedule.md"])]
    expected.sort(key=lambda o: o["code"])
    # sanity of the "no" codes: step-free fine, no duplicates (ED vs ed? only one), no holiday
    ws = {"venue.json": J(ven), "rsvp.csv": tocsv(["name", "email", "status", "guests", "needs_step_free"], rsvp), "catering.csv": tocsv(["item", "meals"], [["mains", str(meals)], ["desserts", str(yes_total + 5)]]),
          "quotes.csv": tocsv(["vendor", "amount_usd"], quotes), "budget.md": md_budget, "schedule.md": sched, "invitation.md": inv, "holidays.txt": holidays,
          "request.md": "# Request\n\nPlan the November client dinner at Harbor Hall. All times in the files are stated with their offsets; the event is in Berlin (CET, UTC+1).\n"}
    codes_txt = "\n".join(f"- `{k}`: {v}." for k, v in codes.items())
    md = f"""
    # Plan an event and report what does not add up

    The inputs for a client dinner are in `/workspace`: `request.md`, `venue.json`, `rsvp.csv`, `catering.csv`, `quotes.csv`, `budget.md`, `schedule.md`, `invitation.md`, `holidays.txt`.

    Some of them contradict each other. You report an issue **only** for these checks, one entry per code that occurs (do not invent other issues, and do not report a code whose condition does not hold):

    {codes_txt}

    Write:
    1. `/workspace/issues.json`: a JSON array of objects `{{"code": <one of the codes above>, "files": [<names of the input files that disagree, sorted>]}}`, sorted by code. A code that does not occur is left out.
       For a rule that compares two files, list both files; a rule that is only about one file lists that file.
    2. `/workspace/plan.md` with exactly these lines (plus anything else you like): `Date: <YYYY-MM-DD>`, `Venue: <venue name>`, `Confirmed guests: <number>`, `Open issues: <number of entries in issues.json>`.
       Confirmed guests counts each `yes` row's guest plus its `guests` extras.
    """
    chk = """
    iss = jl("issues.json")
    chk("issues-parses", isinstance(iss, list))
    got = {o.get("code"): o.get("files") for o in iss if isinstance(o, dict)} if isinstance(iss, list) else {}
    exp = {o["code"]: o["files"] for o in E["i"]}
    chk("issues-sorted-by-code", isinstance(iss, list) and [o.get("code") for o in iss if isinstance(o, dict)] == sorted(exp))
    for c in sorted(set(exp) | set(got)):
        if c in exp: chk("issue-found-" + c, c in got and got[c] == exp[c], got.get(c))
    chk("no-invented-issues", set(got) <= set(exp), sorted(set(got) - set(exp)))
    chk("issue-count-exact", isinstance(iss, list) and len(iss) == len(exp))
    s = rd("plan.md") or ""
    chk("plan-date", re.search(r"(?m)^Date: 2026-11-14\\s*$", s) is not None)
    chk("plan-venue", re.search(r"(?m)^Venue: Harbor Hall\\s*$", s) is not None)
    chk("plan-confirmed-guests", re.search(r"(?m)^Confirmed guests: %d\\s*$" % E["g"], s) is not None, E["g"])
    chk("plan-open-issues", re.search(r"(?m)^Open issues: %d\\s*$" % len(exp), s) is not None)
    """
    spec = [("issues-parses", "`/workspace/issues.json`: a JSON array of objects"), ("issues-sorted", "sorted by code"), ("issue-found-", "list both files; a rule that is only about one file lists that file."),
            ("no-invented", "do not invent other issues, and do not report a code whose condition does not hold"), ("issue-count", "A code that does not occur is left out."),
            ("plan-date", "`Date: <YYYY-MM-DD>`"), ("plan-venue", "`Venue: <venue name>`"), ("plan-confirmed", "`Confirmed guests: <number>`"), ("plan-open", "`Open issues: <number of entries in issues.json>`")]
    # naive: reports everything it sees (schedule's UTC/CET pairs, 'maybe' guests, standing capacity) and misses CATERING_SHORT
    naive_iss = [dict(code="CAPACITY", files=["rsvp.csv", "venue.json"]), dict(code="DUPLICATE_RSVP", files=["rsvp.csv"]), dict(code="OVER_BUDGET", files=["budget.md", "quotes.csv"]),
                 dict(code="TIME_MISMATCH", files=["invitation.md", "schedule.md"])]
    naive = {"issues.json": J(sorted(naive_iss, key=lambda o: o["code"])), "plan.md": f"Date: 2026-11-14\nVenue: Harbor Hall\nConfirmed guests: {yes_total}\nOpen issues: 4\n"}
    note = ("A pass that flags everything that looks odd reports DUPLICATE_RSVP (ED@ vs ed@ only differ in case but appear once), the UTC/CET pairs that agree, and misses the quiet CATERING_SHORT and WEEKDAY_MISMATCH. "
            "Check names list the exact codes; a decoy per rule (standing capacity, 'maybe' RSVPs, matching UTC pairs, holiday list) must stay unreported.")
    task("32-event-plan-issues", "novel", "conflicting-sources", 30, "Event plan with contradictory inputs", md, ws, chk,
         {"issues.json": J(expected), "plan.md": f"# Plan\n\nDate: 2026-11-14\nVenue: Harbor Hall\nConfirmed guests: {yes_total}\nOpen issues: 5\n"},
         dict(i=expected, g=yes_total), note, axis="C", spec=spec, naive=naive)

# =============================================================== 33 fetch with transient failures (D)
def t33():
    r = random.Random(133)
    ids = [f"i{n:02d}" for n in range(1, 21)]
    items = {i: json.dumps(dict(id=i, name=f"item {i}", amount_cents=r.randrange(1000, 90000), tags=sorted(r.sample(["a", "b", "c", "d", "e"], 3)), note="x" * r.randrange(80, 200)), indent=1) + "\n" for i in ids}
    transient = ["i04", "i11", "i17"]; truncated = "i09"
    script = r'''#!/usr/bin/env bash
# usage: ./fetch.sh <id>   prints the item JSON on stdout. Reads the offline mirror in .remote/.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
id="${1:?usage: fetch.sh <id>}"
mkdir -p "$here/.remote/.state"
echo "$id" >> "$here/.remote/.state/calls.log"
n=$(grep -cx "$id" "$here/.remote/.state/calls.log")
f="$here/.remote/items/$id.json"
[ -f "$f" ] || { echo "error: 404 no such item $id" >&2; exit 4; }
case "$id" in
  i04|i11|i17) if [ "$n" -le 1 ]; then echo "error: 503 service unavailable (transient), please retry" >&2; exit 75; fi ;;
  i09) if [ "$n" -le 1 ]; then head -c $(( $(wc -c < "$f") / 2 )) "$f"; exit 0; fi ;;
esac
cat "$f"
'''
    ws = {"fetch.sh": ("exec", script), "ids.txt": "\n".join(ids) + "\n"}
    man = []
    for i in ids:
        ws[f".remote/items/{i}.json"] = items[i]; man.append([i, hashlib.sha256(items[i].encode()).hexdigest(), str(len(items[i].encode()))])
    ws["manifest.csv"] = tocsv(["id", "sha256", "bytes"], man)
    ref = {f"data/{i}.json": items[i] for i in ids}
    calls = []
    for i in ids:
        calls.append(i)
        if i in transient or i == truncated: calls.append(i)
    ref[".remote/.state/calls.log"] = "".join(c + "\n" for c in calls)
    total = sum(json.loads(items[i])["amount_cents"] for i in ids)
    retried = sorted(transient + [truncated])
    ref["summary.json"] = J(dict(count=20, total_amount_cents=total, retried=retried))
    md = """
    # Fetch 20 items from a flaky source

    `/workspace/ids.txt` lists 20 item ids. `/workspace/fetch.sh <id>` fetches one item from the (offline) source and prints its JSON on stdout. It is the only sanctioned way to get items:
    do not read `/workspace/.remote/` directly. The source is flaky, and **retrying a failed fetch is allowed**.
    `/workspace/manifest.csv` has the expected `sha256` and byte size of each item's full JSON.

    Deliver:
    1. `/workspace/data/<id>.json` for all 20 items, each byte-identical to the item the source holds (it must match `manifest.csv`). A fetch that exits 0 can still return damaged data; check it against the manifest.
    2. `/workspace/summary.json`: `{"count": 20, "total_amount_cents": <sum of the `amount_cents` field over all 20 items>, "retried": [<ids that needed more than one fetch call, sorted>]}`.
    """
    chk = """
    man = {x["id"]: x for x in (rows("manifest.csv") or [])}
    for i in sorted(man):
        f = p("data", i + ".json")
        ok = os.path.isfile(f) and hashlib.sha256(open(f, "rb").read()).hexdigest() == man[i]["sha256"]
        chk("item-" + i, ok)
    chk("all-20-items", sum(1 for i in man if os.path.isfile(p("data", i + ".json"))) == 20)
    s = jl("summary.json")
    chk("summary-count", isinstance(s, dict) and s.get("count") == 20)
    chk("summary-total", isinstance(s, dict) and s.get("total_amount_cents") == E["t"], s.get("total_amount_cents") if isinstance(s, dict) else None)
    chk("summary-retried", isinstance(s, dict) and s.get("retried") == E["r"], s.get("retried") if isinstance(s, dict) else None)
    log = (rd(".remote/.state/calls.log") or "").split()
    chk("fetched-via-script", all(i in log for i in man), "calls.log missing ids" )
    chk("retries-actually-made", all(log.count(i) >= 2 for i in E["r"]))
    """
    spec = [("item-", "each byte-identical to the item the source holds (it must match `manifest.csv`)"), ("all-20", "`/workspace/data/<id>.json` for all 20 items"),
            ("summary-count", "`{\"count\": 20,"), ("summary-total", "<sum of the `amount_cents` field over all 20 items>"), ("summary-retried", "<ids that needed more than one fetch call, sorted>"),
            ("fetched-via-script", "do not read `/workspace/.remote/` directly"), ("retries-actually-made", "**retrying a failed fetch is allowed**")]
    task("33-flaky-fetch", "novel", "error-recovery", 25, "Fetch 20 items from a flaky source", md, ws, chk, ref, dict(t=total, r=retried),
         "Three items fail loudly on the first call (exit 75), one returns a half body with exit 0 (only the manifest hash catches it). Skipping failures or trusting exit codes fails item-* checks.",
         axis="D", spec=spec)

# =============================================================== 34 messy CSV with rejects (D)
def t34():
    r = random.Random(134)
    mon = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    recs, clean, rejects = [], [], []
    custs = ["Acme", "Birch & Co", "Cobalt", 'Dune "North"', "Elm Street", "Fjord"]
    n = 0
    def good(i, fmt):
        d = date(2026, 6, 1) + timedelta(days=r.randrange(0, 100)); amt = D(r.randrange(500, 900000)) / 100
        ds = {0: d.isoformat(), 1: f"{d.day:02d}/{d.month:02d}/{d.year}", 2: f"{mon[d.month - 1]} {d.day} {d.year}"}[fmt]
        a = f"{amt:,.2f}" if r.random() < .3 else f"{amt:.2f}"
        return [f"O{i:04d}", r.choice(custs), ds, a, r.choice(["USD", "EUR", "GBP"])], [f"O{i:04d}", None, d.isoformat(), f"{amt:.2f}", None]
    bad_at = {5: "MISSING_ID", 11: "BAD_DATE", 17: "BAD_AMOUNT", 23: "BAD_CURRENCY", 29: "BAD_COLUMNS", 34: "DUPLICATE_ID"}
    for k in range(1, 41):
        i = 1000 + k
        if k in bad_at:
            row, _ = good(i, 0); why = bad_at[k]
            if why == "MISSING_ID": row[0] = ""
            elif why == "BAD_DATE": row[2] = "sometime in sept"
            elif why == "BAD_AMOUNT": row[3] = "12.5O"
            elif why == "BAD_CURRENCY": row[4] = "XXX"
            elif why == "BAD_COLUMNS": row = row + ["extra"]
            elif why == "DUPLICATE_ID": row[0] = recs[3][0]; row[3] = "99.99"
            recs.append(row); rejects.append((k, why)); continue
        row, c = good(i, r.randrange(3)); recs.append(row); clean.append((row, c))
    # inject a customer with embedded newline into a good record
    ix = 8; recs[ix][1] = "Gamma\nIndustries"
    out = io.StringIO(); w = csv.writer(out, lineterminator="\r\n" if True else "\n"); w.writerow(["order_id", "customer", "date", "amount", "currency"])
    for i, row in enumerate(recs): w.writerow(row)
    raw = "﻿" + out.getvalue().replace("\r\n", "\n", 12)  # mixed line endings
    # recompute clean rows from recs
    cl = []
    seen = {}
    rej = []
    for k, row in enumerate(recs, 1):
        why = dict(rejects).get(k)
        if why: rej.append([str(k), why]); continue
        d = row[2]
        if re.fullmatch(r"\d{4}-\d\d-\d\d", d): iso = d
        elif re.fullmatch(r"\d\d/\d\d/\d{4}", d): iso = f"{d[6:]}-{d[3:5]}-{d[:2]}"
        else: m = re.fullmatch(r"([A-Za-z]{3}) (\d+) (\d{4})", d); iso = f"{m.group(3)}-{mon.index(m.group(1)) + 1:02d}-{int(m.group(2)):02d}"
        amt = f"{D(row[3].replace(',', '')):.2f}"
        cl.append([row[0], " ".join(row[1].split()), iso, amt, row[4]])
    cl.sort(key=lambda x: x[0])
    md = """
    # Clean an order export and list what cannot be fixed

    `/workspace/orders_raw.csv` is an export with problems. Parse it as RFC 4180 CSV (like Python's `csv` module with defaults) after removing a leading byte-order mark if present. A *record* is one CSV row; number records from 1 for the first data row after the header.

    Fix, per record:
    - `customer`: replace any run of whitespace (including line breaks) with one space and trim.
    - `date`: accepted forms are `YYYY-MM-DD`, `DD/MM/YYYY` and `Mon D YYYY` (three-letter English month, no comma). Output ISO `YYYY-MM-DD`.
    - `amount`: remove thousands commas; the result must be a plain decimal number; output with exactly 2 decimals.
    - `currency`: must be `USD`, `EUR` or `GBP`.

    A record that cannot be fixed by these rules is a **reject**. Give each reject the first reason that applies, in this order:
    `BAD_COLUMNS` (not exactly 5 fields), `MISSING_ID` (empty `order_id`), `DUPLICATE_ID` (its `order_id` already appeared in an earlier record), `BAD_DATE`, `BAD_AMOUNT`, `BAD_CURRENCY`.

    Write:
    1. `/workspace/clean.csv` with header `order_id,customer,date,amount,currency`: every record that is not a reject, sorted by `order_id`.
    2. `/workspace/rejects.csv` with header `record,reason`: the record number and reason of every reject, in record order.
    Do not drop or repair rejects silently, and do not reject records the rules can fix.
    """
    chk = """
    c = list(csv.DictReader(io.StringIO((rd("clean.csv") or "").lstrip("\\ufeff")))); rj = rows("rejects.csv")
    chk("clean-header", (rd("clean.csv") or "").lstrip("\\ufeff").splitlines()[:1] == ["order_id,customer,date,amount,currency"])
    chk("rejects-header", (rd("rejects.csv") or "").splitlines()[:1] == ["record,reason"])
    got = [[x[k] for k in ("order_id", "customer", "date", "amount", "currency")] for x in (c or [])]
    chk("clean-row-count", len(got) == len(E["c"]), len(got))
    chk("clean-sorted", [g[0] for g in got] == sorted(g[0] for g in got))
    chk("clean-exact", got == E["c"], "first diff at %s" % next((i for i, (a, b) in enumerate(zip(got, E["c"])) if a != b), "-"))
    chk("clean-multiline-customer-flattened", any(g[1] == "Gamma Industries" for g in got))
    chk("clean-dates-iso", all(re.fullmatch(r"\\d{4}-\\d\\d-\\d\\d", g[2]) for g in got) and bool(got))
    g2 = [[x["record"], x["reason"]] for x in (rj or [])]
    chk("rejects-exact", g2 == E["r"], g2)
    chk("rejects-none-silently-dropped", len(got) + len(g2) == 40, len(got) + len(g2))
    """
    spec = [("clean-header", "`/workspace/clean.csv` with header `order_id,customer,date,amount,currency`"), ("rejects-header", "`/workspace/rejects.csv` with header `record,reason`"),
            ("clean-row-count", "do not reject records the rules can fix"), ("clean-sorted", "every record that is not a reject, sorted by `order_id`"), ("clean-exact", "Output ISO `YYYY-MM-DD`."),
            ("clean-multiline", "replace any run of whitespace (including line breaks) with one space and trim"), ("clean-dates", "Output ISO `YYYY-MM-DD`."),
            ("rejects-exact", "the record number and reason of every reject, in record order"), ("rejects-none", "Do not drop or repair rejects silently")]
    task("34-messy-orders-rejects", "novel", "error-recovery", 25, "Clean a messy export, list rejects", md, {"orders_raw.csv": raw}, chk,
         {"clean.csv": tocsv(["order_id", "customer", "date", "amount", "currency"], cl), "rejects.csv": tocsv(["record", "reason"], rej)},
         dict(c=cl, r=rej), "BOM, mixed line endings, a quoted multi-line customer, three date forms, quoted thousands separators, six deliberate rejects. A script that skips bad rows silently fails the rejects checks.", axis="D", spec=spec)

for f in (t31, t32, t33, t34): f()
