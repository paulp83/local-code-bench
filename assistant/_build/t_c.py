import json, random, re, hashlib, csv, io
from decimal import Decimal as D, ROUND_HALF_UP
from datetime import datetime, timedelta, timezone, date
from common import task, DIFF

J = lambda o: json.dumps(o, indent=2) + "\n"
q2 = lambda x: D(x).quantize(D("0.01"), ROUND_HALF_UP)
def tocsv(head, rows):
    o = io.StringIO(); w = csv.writer(o, lineterminator="\n"); w.writerow(head); w.writerows(rows); return o.getvalue()

# ---------------------------------------------------------------- 15 expense report (hard)
def t15():
    r = random.Random(115)
    fx = {"EUR": D("1.08"), "GBP": D("1.27"), "JPY": D("0.0068")}
    days = [date(2026, 9, 14) + timedelta(days=i) for i in range(12)]
    rate = {}
    for d in days:
        if d.weekday() < 5:
            for c, b in fx.items(): rate[(d, c)] = (b + D(r.randrange(-30, 30)) / D(1000) * (D("0.0063") if c == "JPY" else 1) * (D("0.01") if c != "JPY" else D(1))).quantize(D("0.0001"))
    def rt(d, c):
        while (d, c) not in rate: d -= timedelta(days=1)
        return rate[(d, c)]
    cats = ["meals", "transport", "lodging", "supplies"]
    vendors = ["Cafe Nord", "Rail Co", "Hotel Aurora", "Print Shop", "Taxi Uno", "Bistro Sud"]
    rec = []
    for i in range(22):
        c = r.choice(["USD", "EUR", "GBP", "JPY"]); d = r.choice(days)
        amt = D(r.randrange(800, 90000)) if c == "JPY" else D(r.randrange(900, 20000)) / 100
        rec.append((f"R{i+1:02d}", d.isoformat(), r.choice(vendors), str(amt), c, r.choice(cats)))
    rec.insert(7, ("R23",) + rec[3][1:]); rec.insert(15, ("R24",) + rec[10][1:])
    seen, rows_, dup, over = set(), [], [], []
    cap = D("60.00")
    agg = {c: [D(0), D(0)] for c in cats}
    for rid, d, v, a, c, cat in rec:
        k = (d, v, a, c)
        if k in seen: dup.append(rid); continue
        seen.add(k)
        dd = date.fromisoformat(d)
        usd = q2(D(a) * (1 if c == "USD" else rt(dd, c)))
        ok = usd if not (cat == "meals" and usd > cap) else D(0)
        if cat == "meals" and usd > cap: over.append(rid)
        agg[cat][0] += usd; agg[cat][1] += ok
    out = dict(categories={c: dict(claimed=float(a), reimbursable=float(b)) for c, (a, b) in agg.items()},
               total_reimbursable=float(sum(b for a, b in agg.values())), duplicates_dropped=sorted(dup), over_cap=sorted(over))
    fxrows = sorted((d.isoformat(), c, str(v)) for (d, c), v in rate.items())
    md = """
    # Expense report in USD

    `/workspace/receipts.csv` (id, date, vendor, amount, currency, category) and `/workspace/fx.csv` (date, currency, usd_per_unit) are the inputs. Write `/workspace/report.json`.

    Rules:
    1. **Duplicates**: receipts with the same date, vendor, amount and currency are one receipt. Keep the first in file order, list the dropped ids in `duplicates_dropped`.
    2. **Conversion** to USD: multiply by the `usd_per_unit` of the receipt's date and currency. If `fx.csv` has no rate for that exact date (weekends), use the latest earlier date's rate. USD receipts need no rate.
       Round **each receipt** to 2 decimals (half up) before summing.
    3. **Cap**: a `meals` receipt above 60.00 USD (after conversion and rounding) is not reimbursable at all (it counts in `claimed`, adds 0 to `reimbursable`); list its id in `over_cap`.
    4. Output JSON: `{"categories": {"<cat>": {"claimed": <number>, "reimbursable": <number>}, ...}, "total_reimbursable": <number>, "duplicates_dropped": [ids], "over_cap": [ids]}`
       with all four categories (`meals`, `transport`, `lodging`, `supplies`) present, ids sorted ascending, money as JSON numbers with at most 2 decimals.
    """
    chk = """
    o = jl("report.json")
    chk("report-parses", isinstance(o, dict))
    if isinstance(o, dict):
        cats = o.get("categories", {}) if isinstance(o.get("categories"), dict) else {}
        chk("four-categories", set(cats) == set(E["c"]), sorted(cats))
        near = lambda a, b: isinstance(a, (int, float)) and abs(a - b) < 0.005
        for c, v in E["c"].items():
            g = cats.get(c, {}) if isinstance(cats.get(c), dict) else {}
            chk("claimed-" + c, near(g.get("claimed"), v["claimed"]), (g.get("claimed"), v["claimed"]))
            chk("reimbursable-" + c, near(g.get("reimbursable"), v["reimbursable"]), (g.get("reimbursable"), v["reimbursable"]))
        chk("total-reimbursable", near(o.get("total_reimbursable"), E["t"]), (o.get("total_reimbursable"), E["t"]))
        chk("duplicates-dropped", o.get("duplicates_dropped") == E["d"], o.get("duplicates_dropped"))
        chk("over-cap", o.get("over_cap") == E["o"], o.get("over_cap"))
    """
    task("15-expense-report", "novel", "finance", 20, "Multi-currency expense report", md,
         {"receipts.csv": tocsv(["id", "date", "vendor", "amount", "currency", "category"], rec), "fx.csv": tocsv(["date", "currency", "usd_per_unit"], fxrows)},
         chk, {"report.json": J(out)}, dict(c=out["categories"], t=out["total_reimbursable"], d=out["duplicates_dropped"], o=out["over_cap"]),
         "Novel: duplicate removal, weekend FX fallback, per-receipt rounding, cap rule.")
DIFF["15-expense-report"] = "hard"

# ---------------------------------------------------------------- 16 travel itinerary (hard)
def t16():
    legs = [("QA101", "Seattle", "-07:00", "2026-11-03 21:40", "Reykjavik", "+00:00", "2026-11-04 06:15"),
            ("QA202", "Reykjavik", "+00:00", "2026-11-04 08:05", "Frankfurt", "+01:00", "2026-11-04 12:50"),
            ("QA303", "Frankfurt", "+01:00", "2026-11-04 19:20", "Mumbai", "+05:30", "2026-11-05 07:45"),
            ("QA404", "Mumbai", "+05:30", "2026-11-05 22:10", "Tokyo", "+09:00", "2026-11-06 09:35")]
    def utc(t, o):
        s = 1 if o[0] == "+" else -1; h, m = int(o[1:3]), int(o[4:])
        return datetime.strptime(t, "%Y-%m-%d %H:%M") - s * timedelta(hours=h, minutes=m)
    fmt = lambda td: f"{int(td.total_seconds() // 3600)}h {int(td.total_seconds() % 3600 // 60):02d}m"
    ws, rows = {}, []
    for i, (f, a, ao, at, b, bo, bt) in enumerate(legs):
        ws[f"bookings/{i+1:02d}-{f}.json"] = J(dict(flight=f, from_city=a, depart_local=at, depart_utc_offset=ao, to_city=b, arrive_local=bt, arrive_utc_offset=bo))
    for i, (f, a, ao, at, b, bo, bt) in enumerate(legs):
        dur = utc(bt, bo) - utc(at, ao)
        lay = "-" if i == len(legs) - 1 else fmt(utc(legs[i + 1][3], legs[i + 1][2]) - utc(bt, bo))
        rows.append(f"| {i+1} | {f} | {a} {at} | {b} {bt} | {fmt(dur)} | {lay} |")
    total = fmt(utc(legs[-1][6], legs[-1][5]) - utc(legs[0][3], legs[0][2]))
    md_ref = "# Itinerary\n\n| leg | flight | depart (local) | arrive (local) | duration | layover |\n|---|---|---|---|---|---|\n" + "\n".join(rows) + f"\n\nTotal travel time: {total}\n"
    md = """
    # Build an itinerary from bookings

    `/workspace/bookings/` has one JSON file per flight leg with local departure/arrival times and each city's UTC offset. Legs are in file-name order.

    Write `/workspace/itinerary.md` containing a markdown table with exactly this header: `| leg | flight | depart (local) | arrive (local) | duration | layover |`, then one row per leg:

    - `leg`: 1, 2, ...
    - `depart (local)` / `arrive (local)`: `<city> <YYYY-MM-DD HH:MM>` in that city's local time, as booked.
    - `duration`: flight time computed from the UTC instants, formatted `<H>h <MM>m` (minutes always two digits, e.g. `7h 05m`).
    - `layover`: time from this leg's arrival to the next leg's departure (UTC instants), same format; `-` on the last leg.

    After the table add one line `Total travel time: <H>h <MM>m` from the first departure to the last arrival.
    """
    chk = """
    s = rd("itinerary.md") or ""
    tb = [[c.strip() for c in l.strip().strip("|").split("|")] for l in s.splitlines() if l.strip().startswith("|")]
    chk("header-exact", bool(tb) and tb[0] == ["leg", "flight", "depart (local)", "arrive (local)", "duration", "layover"], tb[:1])
    body = tb[2:] if len(tb) > 2 else []
    chk("four-rows", len(body) == 4)
    for i, e in enumerate(E["r"]):
        chk("row-%d" % (i + 1), i < len(body) and body[i] == e, body[i] if i < len(body) else None)
    chk("total-line", ("Total travel time: " + E["t"]) in s, E["t"])
    """
    erows = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
    task("16-travel-itinerary", "novel", "planning", 15, "Itinerary across time zones", md, ws, chk, {"itinerary.md": md_ref}, dict(r=erows, t=total),
         "Novel: time zone arithmetic incl. a half-hour offset and overnight legs.")
DIFF["16-travel-itinerary"] = "hard"

# ---------------------------------------------------------------- 17 policy diff (hard)
def t17():
    C = [("1.1", "Scope", "This policy covers all club members."), ("1.2", "Definitions", "A member is anyone with a registered account."),
         ("2.1", "Posting", "Posts must be on topic."), ("2.2", "Images", "Images may not exceed 2 MB."), ("2.3", "Links", "Links must be to public pages."),
         ("3.1", "Moderation", "Moderators may remove posts without notice."), ("3.2", "Appeals", "Appeals are answered within 14 days."),
         ("4.1", "Data", "We keep logs for 30 days."), ("4.2", "Contact", "Write to the admin address.")]
    v2 = [("1.1", "Scope", "This policy covers all club members."), ("1.2", "Definitions", "A member is anyone with a registered account."),
          ("2.1", "Posting", "Posts must be on topic and in English."),            # changed
          ("2.2", "Links", "Links must be to public pages."),                      # renumbered 2.3 -> 2.2
          ("2.3", "Attachments", "Attachments may not exceed 5 MB."),              # added (Images removed)
          ("3.1", "Moderation", "Moderators may remove posts without notice."),
          ("3.2", "Appeals", "Appeals are answered within 7 days."),               # changed
          ("4.1", "Data", "We keep logs for 30 days."), ("4.2", "Contact", "Write to the admin address."),
          ("4.3", "Retention", "Accounts idle for 2 years are deleted.")]          # added
    rend = lambda cl, t: f"# {t}\n\n" + "\n\n".join(f"### {i} {n}\n\n{b}" for i, n, b in cl) + "\n"
    exp = dict(added=["2.3", "4.3"], removed=["2.2"], changed=["2.1", "3.2"], renumbered=[dict(title="Links", **{"from": "2.3", "to": "2.2"})])
    md = """
    # Diff two versions of a policy

    `/workspace/policy-v1.md` and `/workspace/policy-v2.md` are two versions. Each clause is a `### <id> <Title>` heading followed by its text. A clause's identity is its **title** (titles are unique within a version).

    Write `/workspace/changes.json`:

    - `added`: ids (as in v2) of clauses whose title is only in v2.
    - `removed`: ids (as in v1) of clauses whose title is only in v1.
    - `changed`: ids (as in v2) of clauses with the same title in both versions whose text differs.
    - `renumbered`: objects `{"title": ..., "from": <v1 id>, "to": <v2 id>}` for clauses with the same title whose id differs. A clause may be both `changed` and `renumbered`.

    All four keys must be present; each list is sorted by the id (for `renumbered`, by `from`).
    """
    chk = """
    o = jl("changes.json")
    chk("parses-with-4-keys", isinstance(o, dict) and set(o) == {"added", "removed", "changed", "renumbered"}, o)
    if isinstance(o, dict):
        for k in ("added", "removed", "changed", "renumbered"):
            chk("key-" + k, o.get(k) == E[k], o.get(k))
    """
    task("17-policy-diff", "novel", "documents", 15, "Diff two policy versions", md,
         {"policy-v1.md": rend(C, "Club policy v1"), "policy-v2.md": rend(v2, "Club policy v2")}, chk, {"changes.json": J(exp)}, exp,
         "Novel: clause identity by title, so renumbered/changed/added/removed must be told apart.")
DIFF["17-policy-diff"] = "hard"

# ---------------------------------------------------------------- 18 contact cleanup (medium)
def t18():
    raw = [("Dana  Reyes", " Dana.Reyes@Example.com ", "(415) 555-0132", "Acme"), ("Lee Wu", "lee@example.org", "+44 20 7946 0958", ""),
           ("Dana Reyes", "dana.reyes@example.com", "", "Acme Inc"), ("M. Okafor", "mo@example.net", "0044 7700 900123", "Okafor Ltd"),
           ("Sam K", "", "415-555-0188", "Kite"), ("Samuel Kite", "", "(415) 555 0188", ""), ("Pat", "pat@example.com", "12345", ""),
           ("Lee Wu", "LEE@example.org", "+442079460958", "LW Co"), ("Ira", "ira@example.com", "555.0100.77", "")]
    def phone(p):
        d = re.sub(r"\D", "", p)
        if p.strip().startswith("+"): num = d
        elif d.startswith("00"): num = d[2:]
        elif len(d) == 10: num = "1" + d
        else: return ""
        return "+" + num if 8 <= len(num) <= 15 else ""
    groups = {}
    out = []
    invalid = 0
    for n, e, p, c in raw:
        e2 = e.strip().lower(); p2 = phone(p)
        if p.strip() and not p2: invalid += 1
        n2 = " ".join(n.split())
        key = ("e", e2) if e2 else ("p", p2) if p2 else ("n", n2)
        if key in groups:
            g = groups[key]
            for k, v in (("name", n2), ("email", e2), ("phone", p2), ("company", c.strip())):
                if not g[k] and v: g[k] = v
        else:
            groups[key] = dict(name=n2, email=e2, phone=p2, company=c.strip()); out.append(groups[key])
    out.sort(key=lambda g: (g["email"] == "", g["email"], g["name"]))
    csv_ = tocsv(["name", "email", "phone", "company"], [[g["name"], g["email"], g["phone"], g["company"]] for g in out])
    summ = dict(input_rows=len(raw), output_rows=len(out), invalid_phones=invalid)
    md = """
    # Clean up a contacts export

    `/workspace/contacts.csv` (name, email, phone, company) is messy. Write `/workspace/contacts_clean.csv` (same header) and `/workspace/summary.json`.

    Normalisation:
    - `name`: trim and collapse runs of spaces to one. `email`: trim, lowercase. `company`: trim.
    - `phone` to E.164 (`+` and digits only): a number starting with `+` keeps its digits; one starting with `00` has the `00` replaced by `+`; a 10-digit number is a US/Canada number, prefix `+1`.
      Anything else is invalid and becomes empty. A valid E.164 number has 8 to 15 digits after the `+`. Count every non-empty input phone that ends up empty as an invalid phone.

    Dedupe: rows are the same contact when their normalised emails are equal; a row with an empty email matches on normalised phone instead (if the phone is also empty it is its own contact).
    Merge duplicates into the **first** row in file order; fill that row's empty fields from later duplicates (never overwrite a non-empty field).

    Output order: contacts with an email first, sorted by email; then contacts without an email, in the order their first row appeared.

    `summary.json`: `{"input_rows": n, "output_rows": n, "invalid_phones": n}`.
    """
    chk = """
    r = rows("contacts_clean.csv")
    chk("header-exact", (rd("contacts_clean.csv") or "").splitlines()[:1] == ["name,email,phone,company"])
    got = [[x[k] for k in ("name", "email", "phone", "company")] for x in (r or [])]
    chk("row-count", len(got) == len(E["r"]), len(got))
    chk("rows-exact-in-order", got == E["r"], got)
    chk("all-emails-lowercase", all(g[1] == g[1].lower() for g in got))
    chk("all-phones-e164-or-empty", all(re.fullmatch(r"\\+\\d{8,15}", g[2]) or g[2] == "" for g in got))
    chk("summary-exact", jl("summary.json") == E["s"], jl("summary.json"))
    """
    task("18-contacts-cleanup", "novel", "data-cleaning", 15, "Dedupe and normalise contacts", md,
         {"contacts.csv": tocsv(["name", "email", "phone", "company"], raw)}, chk, {"contacts_clean.csv": csv_, "summary.json": J(summ)},
         dict(r=[[g["name"], g["email"], g["phone"], g["company"]] for g in out], s=summ), "Novel: normalisation plus merge rules with a fixed precedence.")
DIFF["18-contacts-cleanup"] = "medium"

# ---------------------------------------------------------------- 19 bank categorisation (hard)
def t19():
    r = random.Random(119)
    rules = [("REFUND", "refunds"), ("PAYROLL", "income"), ("SHELL", "fuel"), ("SUPERMARKET", "groceries"), ("MARKET", "dining"),
             ("RAIL", "transport"), ("NETFLIX", "subscriptions"), ("RENT", "housing")]
    descs = ["SUPERMARKET OAK ST", "SHELL 4412", "RAIL CARD TOPUP", "NETFLIX.COM", "FARMERS MARKET", "CAFE LUNA", "HARDWARE DEPOT"]
    tx = []
    for i in range(120):
        d = date(2026, 7, 1) + timedelta(days=r.randrange(0, 92))
        k = r.random()
        if k < .06: tx.append((d, "PAYROLL ACME", D("2500.00")))
        elif k < .10: tx.append((d, "TRANSFER TO SAVINGS", D(-r.randrange(100, 400))))
        elif k < .14: tx.append((d, "REFUND SHELL 4412", D(r.randrange(500, 2500)) / 100))
        elif k < .18: tx.append((d, "SPLIT: SUPERMARKET OAK ST groceries=%s;household=%s" % (D(r.randrange(2000, 6000)) / 100, D(r.randrange(500, 2000)) / 100), None))
        elif k < .22: tx.append((d, "MONTHLY RENT", D(-900)))
        else: tx.append((d, r.choice(descs), -D(r.randrange(300, 9000)) / 100))
    tx.sort(key=lambda x: (x[0], x[1]))
    rows_ = []
    for d, ds, a in tx:
        if a is None:
            m = re.search(r"groceries=([\d.]+);household=([\d.]+)", ds)
            a = -(D(m.group(1)) + D(m.group(2)))
        rows_.append((d.isoformat(), ds, str(q2(a))))
    def cat(ds):
        for p, c in rules:
            if p in ds.upper(): return c
        return "uncategorised"
    tot = {}
    for d, ds, a in rows_:
        if ds.startswith("TRANSFER "): continue
        a = D(a)
        if ds.startswith("SPLIT:"):
            m = re.search(r"groceries=([\d.]+);household=([\d.]+)", ds)
            for c, v in (("groceries", D(m.group(1))), ("household", D(m.group(2)))): tot[(d[:7], c)] = tot.get((d[:7], c), D(0)) - v
        else: tot[(d[:7], cat(ds))] = tot.get((d[:7], cat(ds)), D(0)) + a
    out = sorted(tot.items())
    csv_ = tocsv(["month", "category", "total"], [[m, c, str(q2(v))] for (m, c), v in out])
    md = """
    # Monthly totals per category

    `/workspace/transactions.csv` (date, description, amount; negative = money out) and `/workspace/rules.csv` (pattern, category; **ordered**) are the inputs.

    Write `/workspace/budget.csv` with header `month,category,total`, one row per (month, category) that has at least one transaction, sorted by month then category (byte order).
    `month` is `YYYY-MM`; `total` is the **signed** sum of amounts, 2 decimals.

    Rules:
    1. **Transfers**: descriptions starting with `TRANSFER ` are moves between own accounts; ignore them entirely.
    2. **Splits**: a description starting with `SPLIT:` ends with `groceries=<x>;household=<y>`. Do not use `rules.csv` for it; add `-x` to category `groceries` and `-y` to `household` (the row's amount is just their negated sum).
    3. **Everything else**: the category of the **first** rule (top to bottom) whose pattern is contained in the description (case-insensitive); `uncategorised` if none.
    """
    chk = """
    r = rows("budget.csv")
    chk("header-exact", (rd("budget.csv") or "").splitlines()[:1] == ["month,category,total"])
    got = [(x["month"], x["category"], x["total"]) for x in (r or [])]
    chk("row-count", len(got) == len(E["r"]), len(got))
    chk("sorted", got == sorted(got))
    d = {(a, b): c for a, b, c in got}
    bad = [k for k, v in E["d"].items() if d.get(tuple(k.split("|"))) != v]
    chk("all-cells-correct", not bad and len(d) == len(E["d"]), bad[:4])
    chk("at-least-90pct-cells", sum(d.get(tuple(k.split("|"))) == v for k, v in E["d"].items()) >= 0.9 * len(E["d"]))
    chk("transfers-ignored", not any("TRANSFER" in c for c in d) and len(d) > 0)
    """
    task("19-bank-categorisation", "novel", "finance", 25, "Categorise 120 transactions", md,
         {"transactions.csv": tocsv(["date", "description", "amount"], rows_), "rules.csv": tocsv(["pattern", "category"], rules)}, chk,
         {"budget.csv": csv_}, dict(r=[list(x) for x in out], d={f"{m}|{c}": str(q2(v)) for (m, c), v in out}),
         "Novel: ordered rules (SUPERMARKET before MARKET), transfers excluded, split rows.")
DIFF["19-bank-categorisation"] = "hard"

# ---------------------------------------------------------------- 20 meeting notes -> actions (medium)
def t20():
    notes = """# Platform sync, Wed 2026-10-07

Attendees: Dana, Lee, Omar, Priya

- Decided to freeze the quant recipe until the quality gate lands.
- Dana to send the vendor quote by Friday.
- Lee will review the rig report next Tuesday.
- Omar mentioned the log rotation bug again (no owner yet).
- Priya to draft the results post in 2 weeks.
- Omar will book the test window by end of month.
- Dana to update the runbook tomorrow.
- FYI the dashboard port changed to 8090.
- Lee to rerun the bench on 2026-10-19.
- Priya will confirm the budget by Monday.
- Maybe we should look at the offload path someday.
"""
    exp = [("Dana", "send the vendor quote", "2026-10-09"), ("Lee", "review the rig report", "2026-10-13"), ("Priya", "draft the results post", "2026-10-21"),
           ("Omar", "book the test window", "2026-10-31"), ("Dana", "update the runbook", "2026-10-08"), ("Lee", "rerun the bench", "2026-10-19"),
           ("Priya", "confirm the budget", "2026-10-12")]
    out = [dict(owner=o, task=t, due=d) for o, t, d in exp]
    md = """
    # Turn meeting notes into actions

    `/workspace/notes.md` are notes from a meeting held on **Wednesday 2026-10-07** (that is "today"). Write `/workspace/actions.json`: a JSON array, in note order, of
    `{"owner": <first name>, "task": <text>, "due": "YYYY-MM-DD"}`, one per line that assigns a named person a task with a deadline (`<Name> to ...` or `<Name> will ...`).

    - `task` is the text between `to`/`will` and the deadline phrase, e.g. `send the vendor quote`.
    - Deadline phrases: `tomorrow` = 2026-10-08; `by <weekday>` = the next such weekday strictly after today; `next <weekday>` = that weekday in the **following** calendar week (weeks run Monday to Sunday);
      `in N weeks` = today + 7N days; `by end of month` = the last day of the month; `on <date>` = that date.
    - Ignore decisions, FYIs, ideas, and lines with no owner.
    """
    chk = """
    a = jl("actions.json")
    chk("is-list-of-expected-length", isinstance(a, list) and len(a) == len(E["a"]), None if not isinstance(a, list) else len(a))
    if isinstance(a, list):
        norm = lambda s: re.sub(r"[^a-z0-9 ]", "", str(s).lower()).strip()
        for i, e in enumerate(E["a"]):
            g = a[i] if i < len(a) and isinstance(a[i], dict) else {}
            chk("owner-%d-%s" % (i + 1, e["owner"]), g.get("owner") == e["owner"], g.get("owner"))
            chk("due-%d-%s" % (i + 1, e["owner"]), g.get("due") == e["due"], g.get("due"))
            chk("task-%d-%s" % (i + 1, e["owner"]), norm(g.get("task")) == norm(e["task"]), g.get("task"))
    """
    task("20-notes-to-actions", "novel", "extraction", 12, "Meeting notes to dated actions", md, {"notes.md": notes}, chk, {"actions.json": J(out)}, dict(a=out),
         "Novel: relative-date resolution against a stated today.")
DIFF["20-notes-to-actions"] = "medium"

# ---------------------------------------------------------------- 21 photo organisation (easy)
def t21():
    r = random.Random(121)
    shots = [("IMG_0001", "2026-08-14T17:22:09", "X100"), ("IMG_0002", "2026-08-14T17:22:09", "X100"), ("IMG_0003", "2026-08-14T17:22:09", "GR3"),
             ("IMG_0004", "2026-09-02T08:01:45", "GR3"), ("IMG_0005", "2025-12-31T23:59:59", "X100"), ("IMG_0006", "2026-09-02T08:01:46", "X100")]
    ws, mv, ref = {}, [], {}
    seen = {}
    for stem, t, cam in shots:
        body = bytes(r.randrange(256) for _ in range(64))
        ws[f"photos/{stem}.jpg"] = body; ws[f"photos/{stem}.json"] = J(dict(taken=t, camera=cam))
        dt = datetime.fromisoformat(t); base = f"{dt:%Y%m%d_%H%M%S}_{cam.lower()}"
        n = seen.get(base, 0) + 1; seen[base] = n
        name = base + ("" if n == 1 else f"-{n}")
        folder = f"organised/{dt:%Y}/{dt:%m}/"
        ref[folder + name + ".jpg"] = body; ref[folder + name + ".json"] = ws[f"photos/{stem}.json"]
        mv.append((f"photos/{stem}.jpg", folder + name + ".jpg"))
    ref["manifest.csv"] = tocsv(["old", "new"], sorted(mv)); ref["_delete.txt"] = "".join(f"photos/{s}.{e}\n" for s, _, _ in shots for e in ("jpg", "json"))
    hashes = {new: hashlib.sha256(ref[new]).hexdigest() for _, new in mv}
    md = """
    # Organise photos by capture date

    `/workspace/photos/` has `IMG_xxxx.jpg` files, each with a sidecar `IMG_xxxx.json` (`taken`: local ISO timestamp, `camera`).

    Move every photo into `/workspace/organised/<YYYY>/<MM>/` and rename it `<YYYYMMDD>_<HHMMSS>_<camera lowercased>.jpg` from its sidecar. If two photos get the same name,
    the one with the lower original number keeps the plain name and the next ones get `-2`, `-3` before the extension. Move each sidecar next to its photo with the same new stem and `.json`.
    Nothing may be left in `photos/`. Write `/workspace/manifest.csv` with header `old,new` (paths relative to `/workspace`, `.jpg` files only, sorted by `old`).
    """
    chk = """
    r = rows("manifest.csv")
    chk("manifest-exact", (rd("manifest.csv") or "") == E["m"], "manifest differs")
    chk("photos-dir-empty", not os.path.isdir(p("photos")) or not os.listdir(p("photos")), os.listdir(p("photos")) if os.path.isdir(p("photos")) else "")
    for new, h in E["h"].items():
        f = p(new)
        chk("photo-" + new.split("/")[-1], os.path.isfile(f) and hashlib.sha256(open(f, "rb").read()).hexdigest() == h)
    sc = sum(1 for new in E["h"] if os.path.isfile(p(new[:-4] + ".json")))
    chk("sidecars-moved", sc == len(E["h"]), sc)
    """
    task("21-photo-organise", "novel", "files", 8, "Organise photos by date", md, ws, chk, ref, dict(m=ref["manifest.csv"], h=hashes), "Novel: rename/move with collision suffix.")
DIFF["21-photo-organise"] = "easy"

# ---------------------------------------------------------------- 22 form fill (easy)
def t22():
    cv = """# Jordan Ellis
Email: jordan.ellis@example.com | Phone: +1 415 555 0177 | Location: Austin, TX, USA

## Experience
- 2023-2026 Senior support engineer, Northwind (remote)
- 2019-2023 Support engineer, Contoso

## Skills
Python, SQL, Linux, incident response

## Education
BSc Information Systems, State University, 2018
"""
    schema = {"type": "object", "required": ["full_name", "email", "country", "years_experience", "skills", "highest_degree", "available"], "additionalProperties": False,
              "properties": {"full_name": {"type": "string"}, "email": {"type": "string", "pattern": "^[^@\\s]+@[^@\\s]+\\.[a-z]+$"},
                             "country": {"type": "string", "enum": ["US", "CA", "GB", "DE"]}, "years_experience": {"type": "integer", "minimum": 0, "maximum": 60},
                             "skills": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 5}, "highest_degree": {"type": "string", "enum": ["BSc", "MSc", "PhD", "none"]},
                             "available": {"type": "boolean"}}}
    out = dict(full_name="Jordan Ellis", email="jordan.ellis@example.com", country="US", years_experience=7, skills=["Python", "SQL", "Linux", "incident response"], highest_degree="BSc", available=True)
    md = """
    # Fill in the application form

    `/workspace/cv.md` is a CV and `/workspace/schema.json` is the JSON Schema of an application form. Write `/workspace/application.json` that validates against the schema and answers truthfully from the CV.

    Notes: `country` uses the schema's enum codes; `years_experience` counts whole years of work from the earliest start year to 2026 (the CV's last job runs to 2026);
    `skills` lists the CV's skills in order; `available` is `true`.
    """
    chk = """
    sc = jl("schema.json"); a = jl("application.json")
    def val(v, s):
        t = s.get("type")
        if t == "object":
            if not isinstance(v, dict): return False
            if any(k not in v for k in s.get("required", [])): return False
            if s.get("additionalProperties") is False and set(v) - set(s.get("properties", {})): return False
            return all(val(v[k], s["properties"][k]) for k in v if k in s.get("properties", {}))
        if t == "array":
            return isinstance(v, list) and s.get("minItems", 0) <= len(v) <= s.get("maxItems", 10**9) and all(val(x, s["items"]) for x in v)
        if t == "string": ok = isinstance(v, str)
        elif t == "integer": ok = isinstance(v, int) and not isinstance(v, bool)
        elif t == "boolean": ok = isinstance(v, bool)
        else: ok = True
        if ok and "enum" in s: ok = v in s["enum"]
        if ok and "pattern" in s: ok = re.search(s["pattern"], v) is not None
        if ok and "minimum" in s: ok = v >= s["minimum"]
        if ok and "maximum" in s: ok = v <= s["maximum"]
        return ok
    chk("valid-against-schema", isinstance(a, dict) and isinstance(sc, dict) and val(a, sc))
    a = a if isinstance(a, dict) else {}
    chk("full_name", a.get("full_name") == "Jordan Ellis", a.get("full_name"))
    chk("email", a.get("email") == "jordan.ellis@example.com", a.get("email"))
    chk("country-US", a.get("country") == "US", a.get("country"))
    chk("years-7", a.get("years_experience") == 7, a.get("years_experience"))
    chk("skills-in-order", a.get("skills") == ["Python", "SQL", "Linux", "incident response"], a.get("skills"))
    chk("degree-BSc", a.get("highest_degree") == "BSc", a.get("highest_degree"))
    chk("available-true", a.get("available") is True)
    """
    task("22-form-fill", "novel", "forms", 6, "Fill a schema-validated form", md, {"cv.md": cv, "schema.json": J(schema)}, chk, {"application.json": J(out)}, {},
         "Novel: structured extraction under a JSON schema (enum, bounds, pattern).")
DIFF["22-form-fill"] = "easy"

# ---------------------------------------------------------------- 23 recipe scaling (easy)
def t23():
    rec = """# Oat pancakes (serves 4)

| ingredient | amount |
|---|---|
| rolled oats | 1.5 cup |
| milk | 1 cup |
| eggs | 2 |
| butter | 2 tbsp |
| baking powder | 2 tsp |
| flour | 6 oz |
| salt | 1 pinch |
"""
    # x2.5: oats 3.75 cup = 900 ml; milk 2.5 cup = 600 ml; eggs 5; butter 5 tbsp=75 ml; bp 5 tsp=25 ml; flour 15 oz=420 g -> 420; salt 1 pinch
    rows = [("rolled oats", "900 ml"), ("milk", "600 ml"), ("eggs", "5"), ("butter", "75 ml"), ("baking powder", "25 ml"), ("flour", "420 g"), ("salt", "1 pinch")]
    ref = "# Oat pancakes (serves 10)\n\n| ingredient | amount |\n|---|---|\n" + "".join(f"| {a} | {b} |\n" for a, b in rows)
    md = """
    # Scale a recipe from 4 to 10 servings, in metric

    Write `/workspace/recipe-10.md` from `/workspace/recipe.md`: scale every amount by 10/4, then convert units: 1 cup = 240 ml, 1 tbsp = 15 ml, 1 tsp = 5 ml, 1 oz = 28 g.
    Counts (eggs) are rounded to the nearest whole number (halves up); `pinch` amounts stay `1 pinch` (a pinch does not scale). Do not round the metric values.
    Keep the format: first line `# Oat pancakes (serves 10)`, the same two-column table, amounts written `<number> <unit>` (counts as a bare number, no trailing `.0`), same ingredient order.
    """
    chk = """
    s = rd("recipe-10.md") or ""
    chk("title-line", s.splitlines()[:1] == ["# Oat pancakes (serves 10)"] if s else False)
    tb = [[c.strip() for c in l.strip().strip("|").split("|")] for l in s.splitlines() if l.strip().startswith("|")]
    chk("header", tb[:1] == [["ingredient", "amount"]], tb[:1])
    got = dict((r[0], r[1]) for r in tb[2:] if len(r) == 2)
    chk("order", [r[0] for r in tb[2:]] == [e[0] for e in E["r"]])
    for k, v in E["r"]:
        chk("row-" + k.replace(" ", "-"), got.get(k) == v, got.get(k))
    """
    task("23-recipe-scaling", "novel", "documents", 6, "Scale a recipe to metric", md, {"recipe.md": rec}, chk, {"recipe-10.md": ref}, dict(r=rows), "Novel: unit conversion and scaling.")
DIFF["23-recipe-scaling"] = "easy"

# ---------------------------------------------------------------- 24 needle in notes (easy)
def t24():
    r = random.Random(124)
    words = "alpha river stone window garden copper lantern harbor meadow signal paper orchard".split()
    ws = {}
    for i in range(200):
        ws[f"notes/n{i:03d}.md"] = f"# Note {i}\n\n" + " ".join(r.choice(words) for _ in range(40)) + "\n"
    ws["notes/n047.md"] += "\nThe rental van plate is KV-4821-Q. The spare key is in the blue tin.\n"
    ws["notes/n113.md"] += "\nDentist appointment moved to 2026-11-18 at 14:30 (Dr. Halvorsen).\n"
    ws["notes/n181.md"] += "\nWifi password for the cabin: maple-otter-92.\n"
    ws["notes/n020.md"] += "\nOld van plate was KV-4812-Q, sold in March.\n"
    ws["notes/n150.md"] += "\nDentist appointment idea: ask about 2026-11-81.\n"
    ans = {"q1": "KV-4821-Q", "q2": "2026-11-18 14:30", "q3": "maple-otter-92"}
    md = """
    # Find three facts in 200 notes

    `/workspace/notes/` has 200 short notes. Answer in `/workspace/answers.json` as `{"q1": ..., "q2": ..., "q3": ...}` (strings):

    - q1: the plate of the **current** rental van (a note mentions an old, sold van too).
    - q2: the dentist appointment as `YYYY-MM-DD HH:MM` (24-hour clock).
    - q3: the wifi password of the cabin.
    """
    chk = """
    a = jl("answers.json")
    chk("answers-parses", isinstance(a, dict))
    a = a if isinstance(a, dict) else {}
    for k, v in E["a"].items(): chk(k, a.get(k) == v, a.get(k))
    """
    task("24-needle-in-notes", "novel", "retrieval", 6, "Three facts in 200 notes", md, ws, chk, {"answers.json": J(ans)}, dict(a=ans), "Novel: retrieval with a decoy.")
DIFF["24-needle-in-notes"] = "easy"

# ---------------------------------------------------------------- 25 config edit (easy)
def t25():
    ini = """# club node settings
[server]
host = 0.0.0.0
port = 8000   ; inline note stays
max_ctx = 32768

[logging]
# keep this comment
level = info
rotate = yes

[gpu]
devices = 0,1
mem_fraction = 0.90
"""
    new = ini.replace("port = 8000", "port = 8090").replace("level = info", "level = debug").replace("rotate = yes\n", "").replace("mem_fraction = 0.90", "mem_fraction = 0.85")
    new += "\n[metrics]\nenabled = true\nport = 9100\n"
    md = """
    # Edit a settings file

    Edit `/workspace/node.ini` in place:

    1. `[server] port` becomes `8090`.
    2. `[logging] level` becomes `debug`, and the `rotate` key is removed.
    3. `[gpu] mem_fraction` becomes `0.85`.
    4. Add a new section `[metrics]` with `enabled = true` and `port = 9100`.

    Everything else (other keys, values, comments, section order) must stay exactly as it is.
    """
    chk = """
    import configparser
    s = rd("node.ini") or ""
    cp = configparser.ConfigParser(inline_comment_prefixes=(";",)); 
    try: cp.read_string(s); ok = True
    except Exception: ok = False
    chk("parses", ok)
    g = lambda a, b: cp.get(a, b, fallback=None) if ok else None
    chk("server-port", g("server", "port") == "8090")
    chk("logging-level", g("logging", "level") == "debug")
    chk("rotate-removed", ok and not cp.has_option("logging", "rotate"))
    chk("gpu-mem-fraction", g("gpu", "mem_fraction") == "0.85")
    chk("metrics-section", g("metrics", "enabled") == "true" and g("metrics", "port") == "9100")
    chk("untouched-values", g("server", "host") == "0.0.0.0" and g("server", "max_ctx") == "32768" and g("gpu", "devices") == "0,1")
    chk("comments-kept", "# club node settings" in s and "# keep this comment" in s and "; inline note stays" in s)
    chk("only-expected-lines-changed", [l for l in s.splitlines() if l.strip()][:len(E["head"])] == E["head"], "head changed")
    """
    head = [l for l in new.splitlines() if l.strip()][:9]
    task("25-config-edit", "novel", "config", 5, "Targeted edits to an ini file", md, {"node.ini": ini}, chk, {"node.ini": new}, dict(head=head), "Novel: state change that must preserve comments.")
DIFF["25-config-edit"] = "easy"

# ---------------------------------------------------------------- 26 invoice reconciliation (hard)
def t26():
    inv = [("INV-1001", "Acme", "500.00", "2026-09-10"), ("INV-1002", "Acme", "250.00", "2026-09-20"), ("INV-1003", "Birch", "1200.00", "2026-10-05"),
           ("INV-1004", "Birch", "300.00", "2026-09-01"), ("INV-1005", "Cobalt", "75.50", "2026-10-20"), ("INV-1006", "Cobalt", "980.00", "2026-09-25"), ("INV-1007", "Dune", "410.00", "2026-10-15")]
    pay = [("P01", "2026-09-12", "Acme", "750.00", "INV-1001, INV-1002"), ("P02", "2026-09-28", "Birch", "800.00", "INV-1003"),
           ("P03", "2026-09-30", "Cobalt", "1100.00", "INV-1006 INV-1005"), ("P04", "2026-10-02", "Dune", "410.00", ""),
           ("P05", "2026-10-03", "Birch", "300.00", "INV-1004"), ("P06", "2026-10-04", "Birch", "100.00", "INV-1004")]
    amt = {i[0]: D(i[2]) for i in inv}; due = {i[0]: i[3] for i in inv}
    paid = {k: D(0) for k in amt}; credits = []
    for pid, d, who, a, ref in pay:
        ids = re.findall(r"INV-\d+", ref); a = D(a)
        for i in ids:
            take = min(a, amt[i] - paid[i]); paid[i] += take; a -= take
        if a > 0 and ids: credits.append((pid, str(q2(a))))
        elif a > 0 and not ids: credits.append((pid, str(q2(a))))
    today = "2026-10-10"
    rows_ = []
    for i, c, a, d in inv:
        out = amt[i] - paid[i]
        st = "paid" if out == 0 else ("overdue" if d < today else ("partial" if paid[i] > 0 else "unpaid"))
        rows_.append((i, st, str(q2(paid[i])), str(q2(out))))
    md = """
    # Reconcile payments against invoices

    `/workspace/invoices.csv` (inv_id, customer, amount, due) and `/workspace/payments.csv` (pay_id, date, payer, amount, reference) are the inputs. Today is **2026-10-10**.

    Apply payments in file order. A payment's `reference` lists zero or more invoice ids (separated by commas or spaces). Allocate the payment amount to the listed invoices **in the order listed**, each up to its remaining balance.
    Whatever is left over (including a whole payment with no valid reference) becomes a credit on that payment.

    Write:
    1. `/workspace/reconcile.csv`, header `inv_id,status,paid,outstanding`, one row per invoice in file order, money with 2 decimals. Status: `paid` if outstanding is 0; otherwise `overdue` if the due date is before today; otherwise `partial` if something was paid; otherwise `unpaid`.
    2. `/workspace/credits.csv`, header `pay_id,credit`, one row per payment with a non-zero credit, in payment order.
    """
    chk = """
    r = rows("reconcile.csv")
    chk("reconcile-header", (rd("reconcile.csv") or "").splitlines()[:1] == ["inv_id,status,paid,outstanding"])
    got = [(x["inv_id"], x["status"], x["paid"], x["outstanding"]) for x in (r or [])]
    chk("reconcile-order", [g[0] for g in got] == [e[0] for e in E["r"]])
    for e in E["r"]:
        g = [x for x in got if x[0] == e[0]]
        chk("invoice-" + e[0], g == [tuple(e)], g)
    c = rows("credits.csv")
    chk("credits-header", (rd("credits.csv") or "").splitlines()[:1] == ["pay_id,credit"])
    chk("credits-exact", [(x["pay_id"], x["credit"]) for x in (c or [])] == [tuple(x) for x in E["c"]], c)
    """
    task("26-invoice-reconciliation", "novel", "finance", 20, "Reconcile payments to invoices", md,
         {"invoices.csv": tocsv(["inv_id", "customer", "amount", "due"], inv), "payments.csv": tocsv(["pay_id", "date", "payer", "amount", "reference"], pay)}, chk,
         {"reconcile.csv": tocsv(["inv_id", "status", "paid", "outstanding"], rows_), "credits.csv": tocsv(["pay_id", "credit"], credits)},
         dict(r=rows_, c=credits), "Novel: multi-invoice allocation, partial and over-payments, overdue status.")
DIFF["26-invoice-reconciliation"] = "hard"

for f in (t15, t16, t17, t18, t19, t20, t21, t22, t23, t24, t25, t26): f()
