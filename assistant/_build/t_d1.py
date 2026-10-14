import json, random, re, hashlib
from datetime import date, datetime, timedelta
from decimal import Decimal as D, ROUND_HALF_UP
from common import task, DIFF

J = lambda o: json.dumps(o, indent=2) + "\n"
for i in range(27, 39): pass

# =============================================================== 27 long meeting notes (A)
def t27():
    r = random.Random(127)
    P = {"dana": "Dana Whit", "lee": "Lee Park", "omar": "Omar Reyes", "priya": "Priya Shah", "marta": "Marta Voss", "ines": "Ines Calder",
         "joel": "Joel Ames", "kim": "Kim Lau", "ravi": "Ravi Sen", "sven": "Sven Holm", "tomas": "Tomas Berg"}
    ev = {  # date -> list of sentence variants (one picked per event)
        "2026-04-01": ["Kickoff roster: Platform is Dana Whit (lead), Lee Park, Omar Reyes. Data is Ines Calder (lead), Ravi Sen, Priya Shah. Web is Marta Voss (lead), Joel Ames, Kim Lau. "
                       "Platform standup is Tuesdays, Data standup is Mondays. Dana Whit holds the on-call pager. Staging runs on Nimbus. The team offsite is planned for 2026-09-18. "
                       "Starting budgets: Platform 60000, Data 40000, Web 35000 (USD)."],
        "2026-05-05": ["Sven Holm joins the Web team today.", "Welcome Sven Holm, who starts on Web this week.", "Web gains a new engineer: Sven Holm."],
        "2026-05-12": ["The Tuesday sync for Platform moves to Thursdays.", "Platform standup day: Thu (was Tue).", "From next week Platform meets on Thursdays rather than Tuesdays."],
        "2026-05-20": ["Decision: staging moves from Nimbus to Cirrus effective 2026-06-01.", "We agreed to leave Nimbus; staging will live on Cirrus from 1 June.",
                       "Staging hosting switches over to Cirrus on 2026-06-01, Nimbus is being retired."],
        "2026-06-02": ["Dana Whit hands the on-call pager to Lee Park.", "Lee Park takes over on-call from Dana Whit as of today.", "On-call owner is now Lee Park (previously Dana Whit)."],
        "2026-06-10": ["The offsite is moved to 2026-10-09.", "New offsite date: Friday 9 October 2026.", "We pushed the offsite from September to 2026-10-09."],
        "2026-06-15": ["Ines Calder has left the company. Marta Voss moves over from Web to take the Data lead role.", "Data lead Ines Calder departs; Marta Voss becomes Data lead and joins that team, leaving Web.",
                       "Marta Voss now leads Data (she moves off Web); Ines Calder's last day was Friday."],
        "2026-07-03": ["Data's budget is raised by 12000.", "We approved a 12k increase for the Data budget.", "Data gets 12000 more this year."],
        "2026-07-08": ["Joel Ames transfers from Web to Platform.", "Joel Ames moves to the Platform team starting today.", "Platform picks up Joel Ames from Web."],
        "2026-07-14": ["We are evaluating Dovetail for staging; nothing decided yet.", "Dovetail came up as a possible staging host. No decision."],
        "2026-07-21": ["Platform will now stand up on Wednesdays.", "Standup day for Platform: Wed.", "We settled on Wednesday mornings for the Platform sync."],
        "2026-07-30": ["Platform's budget goes up by 10000.", "Platform receives an extra 10k.", "Add 10000 to the Platform budget."],
        "2026-08-10": ["Lee Park is out 2026-08-11 through 2026-08-17; Omar Reyes covers on-call that week.", "Omar Reyes takes the pager from 2026-08-11 to 2026-08-17 while Lee Park is away."],
        "2026-08-14": ["The offsite gets pushed back one week.", "Offsite slips by a week."],
        "2026-08-20": ["Data's budget is cut by 5000.", "We trimmed 5k from the Data budget."],
        "2026-08-25": ["Decision: staging moves to Dovetail effective 2026-09-15; the Cirrus contract is not renewed.", "Staging goes to Dovetail starting 15 September; Cirrus is out."],
        "2026-08-30": ["Someone floated Mondays for the Platform standup; no decision, parked until Q4.", "Idea: try Mondays for Platform standup. Not decided."],
        "2026-09-02": ["Tomas Berg joins the Web team.", "Web welcomes Tomas Berg today."],
        "2026-09-05": ["Lee Park hands on-call to Priya Shah.", "On-call owner is now Priya Shah, taking over from Lee Park.", "Priya Shah takes the pager from Lee Park."],
        "2026-09-10": ["The Dovetail migration slipped; staging stays on Cirrus until 2026-10-15.", "Dovetail migration delayed. Cirrus keeps hosting staging through 2026-10-14."],
        "2026-09-12": ["Web's budget is cut by 10 percent.", "We reduce the Web budget by 10%."],
        "2026-09-18": ["Kim Lau is on parental leave through December and stays on the Web roster."],
        "2026-09-20": ["The offsite shifts from Friday to Thursday of that week.", "Offsite day changes: Thursday instead of Friday."],
        "2026-09-25": ["Priya Shah swaps on-call with Omar Reyes for 2026-09-28 through 2026-10-04.", "Omar Reyes covers on-call from 2026-09-28 to 2026-10-04 (swap with Priya Shah)."],
    }
    # extra distractors (Data standup, contractors)
    ev["2026-06-24"] = ["Data standup day is now Fridays instead of Mondays."]
    ev["2026-08-01"] = ["Two contractors start on Web today. Contractors are not part of headcount."]
    filler = ["We reviewed the backlog and closed {n} items.", "The nightly run took {n} minutes, same as last week.", "Snack budget remains a running joke.",
              "The on-call phone battery needs replacing, someone please order one.", "Staging felt slow after lunch but nothing changed on the host.",
              "Offsite catering menu will be discussed later.", "Standup ran long again, we should timebox it.", "{p} demoed the new dashboard widget.",
              "Parking validation for visitors is still unresolved.", "{p} asked for feedback on the draft runbook.", "The coffee machine on the second floor is fixed.",
              "Release notes for the minor update went out; {n} fixes in total.", "We talked about hiring plans without naming anyone.", "{p} will look into the flaky test.",
              "Reminder: timesheets are due Friday.", "The wiki search is slow; ticket filed.", "We celebrated {p}'s work anniversary.", "Budget for conference travel is a Q4 topic.",
              "Support queue is at {n} open tickets.", "The office plants got watered.", "Someone asked if the offsite includes a hike; unclear.", "The vendor invoice was approved without changes."]
    names = list(P.values())
    dates = [date(2026, 4, 1) + timedelta(days=i) for i in range(183) if (date(2026, 4, 1) + timedelta(days=i)).weekday() < 5]
    notes = []
    for d, vs in ev.items():
        notes.append((d, r.choice(vs)))
    while len(notes) < 400:
        notes.append((r.choice(dates).isoformat(), None))
    r.shuffle(notes)
    ws = {}
    for i, (d, s) in enumerate(notes):
        paras = []
        for _ in range(r.randint(3, 4)):
            paras.append(" ".join(r.choice(filler).format(n=r.randint(3, 90), p=r.choice(names)) for _ in range(r.randint(3, 5))))
        if s: paras.insert(r.randint(0, len(paras)), s)
        ws[f"notes/n{i + 1:04d}.md"] = f"---\ndate: {d}\ntitle: Team sync\n---\n\n" + "\n\n".join(paras) + "\n"
    exp = {"q1": "Wednesday", "q2": "Omar Reyes", "q3": 47000, "q4": "Cirrus", "q5": 3, "q6": "2026-10-15", "q7": 148500, "q8": "Platform"}
    naive = {"q1": "Tuesday", "q2": "Dana Whit", "q3": 35000, "q4": "Nimbus", "q5": 3, "q6": "2026-09-18", "q7": 135000, "q8": "Web"}
    md = """
    # Answer eight questions about the team's current state

    `/workspace/notes/` holds 400 meeting notes from 2026-04-01 to 2026-09-30, one per file. The file names carry no date order: each note's date is its `date:` line.
    Answer as of **2026-09-30**.

    How to read the notes:
    - A later-dated note overrides an earlier one on the same fact. Relative changes ("raised by 12000", "pushed back one week") apply to the value in force on that date.
    - Only decisions count. Ideas, evaluations and "no decision" remarks change nothing.
    - A change with an end date stops applying after it; a change with a future effective date does not apply yet.
    - Contractors are not headcount. Everyone else on a team roster counts, including people on leave.

    Write `/workspace/answers.json` with these keys:

    - `q1`: Platform standup weekday, full English name (e.g. `Monday`).
    - `q2`: full name of the person holding on-call on 2026-09-30.
    - `q3`: current budget in USD (integer) of the team that Marta Voss leads.
    - `q4`: which staging host is in use on 2026-09-30, as a single word.
    - `q5`: number of people on the Web team (integer).
    - `q6`: date of the team offsite, `YYYY-MM-DD`.
    - `q7`: sum of the current budgets of Platform, Data and Web, integer USD.
    - `q8`: the team (`Platform`, `Data` or `Web`) Joel Ames is on.
    """
    chk = """
    a = jl("answers.json")
    chk("answers-parses", isinstance(a, dict))
    a = a if isinstance(a, dict) else {}
    for k, v in E["a"].items():
        chk(k, a.get(k) == v and type(a.get(k)) is type(v), a.get(k))
    """
    spec = [("answers-parses", "Write `/workspace/answers.json` with these keys:"),
            ("q1", "`q1`: Platform standup weekday, full English name (e.g. `Monday`)."), ("q2", "`q2`: full name of the person holding on-call on 2026-09-30."),
            ("q3", "`q3`: current budget in USD (integer) of the team that Marta Voss leads."), ("q4", "`q4`: which staging host is in use on 2026-09-30, as a single word."),
            ("q5", "`q5`: number of people on the Web team (integer)."), ("q6", "`q6`: date of the team offsite, `YYYY-MM-DD`."),
            ("q7", "`q7`: sum of the current budgets of Platform, Data and Web, integer USD."), ("q8", "`q8`: the team (`Platform`, `Data` or `Web`) Joel Ames is on.")]
    note = ("Grep for a keyword (standup, on-call, budget, staging, offsite) hits stale values first and filler lines that mention the same words; files are not in date order. "
            "Naive = the value from the first/kickoff mention: gets q1,q2,q3,q4,q6,q7,q8 wrong (q5 coincides). Traps: temporary on-call swap still active on the as-of date, "
            "a slipped migration (Cirrus, not Dovetail), relative budget changes, a roster change that moves Marta between teams.")
    task("27-notes-current-state", "novel", "long-input", 40, "Current state from 400 dated notes", md, ws, chk, {"answers.json": J(exp)}, dict(a=exp), note,
         axis="A", spec=spec, naive={"answers.json": J(naive)})

# =============================================================== 28 ledger + amendment emails (A)
def t28():
    r = random.Random(128)
    accs = [f"ACC-{i:02d}" for i in range(1, 13)]
    memos = ["fuel", "rent", "tools", "hosting", "refund", "salary", "license", "travel", "snacks", "cloud", "audit", "repair"]
    led = {}
    for i in range(1, 3001):
        led[f"T-{i:05d}"] = dict(date=(date(2026, 1, 1) + timedelta(days=r.randrange(0, 181))).isoformat(), acc=r.choice(accs),
                                 amt=r.choice([-1, -1, 1]) * r.randrange(500, 400000), memo=r.choice(memos))
    approved = ["rina@example.net", "sol@example.net", "tess@example.net"]
    outsiders = ["vendor-help@example.net", "pat.unknown@example.net"]
    ids = list(led)
    r.shuffle(ids)
    pool = iter(ids)
    nx = lambda: next(pool)
    ops = []  # (when, sender, kind, params)
    t0 = datetime(2026, 7, 1, 8, 0)
    clock = [0]
    def at():
        clock[0] += r.randrange(35, 900)
        return t0 + timedelta(minutes=clock[0])
    def fmt(c): return f"${abs(c) / 100:,.2f}"
    for _ in range(8): ops.append((at(), r.choice(approved), "reverse", dict(t=nx())))
    for _ in range(6): ops.append((at(), r.choice(approved), "set", dict(t=nx(), amt=r.choice([-1, 1]) * r.randrange(1000, 90000))))
    for _ in range(4): ops.append((at(), r.choice(approved), "move", dict(t=nx(), acc=r.choice(accs))))
    for _ in range(6): ops.append((at(), r.choice(approved), "flip", dict(t=nx())))
    for _ in range(4):  # chain set then move on same txn (different emails, later wins per field)
        t = nx(); s = r.choice(approved)
        ops.append((at(), s, "set", dict(t=t, amt=r.choice([-1, 1]) * r.randrange(1000, 90000)))); ops.append((at(), s, "move", dict(t=t, acc=r.choice(accs))))
    for _ in range(5):  # double set, later wins
        t = nx()
        ops.append((at(), r.choice(approved), "set", dict(t=t, amt=r.choice([-1, 1]) * r.randrange(1000, 90000))))
        ops.append((at(), r.choice(approved), "set", dict(t=t, amt=r.choice([-1, 1]) * r.randrange(1000, 90000))))
    for _ in range(4):
        a, b = nx(), nx(); ops.append((at(), r.choice(approved), "dup", dict(a=a, b=b)))
    for _ in range(5): ops.append((at(), r.choice(approved), "split", dict(t=nx(), a=r.choice(accs), b=r.choice(accs), pct=r.choice([30, 40, 60, 65, 70, 25]))))
    for _ in range(8): ops.append((at(), r.choice(outsiders), r.choice(["reverse", "set", "move"]), dict(t=nx(), amt=r.randrange(1000, 90000), acc=r.choice(accs))))
    for _ in range(2): ops.append((at(), r.choice(approved), "reverse", dict(t=f"T-{3001 + r.randrange(0, 90):05d}")))  # not in ledger
    ops.sort(key=lambda o: o[0])
    # retractions: retract 3 earlier approved single-email ops (set/move/flip), chosen by index
    cands = [i for i, o in enumerate(ops) if o[2] in ("flip", "move", "set") and o[1] in approved and o[3]["t"] in led]
    retracted = set()
    for i in r.sample(cands, 4):
        retracted.add(i)
    extra = []
    for i in sorted(retracted):
        o = ops[i]
        extra.append((o[0] + timedelta(minutes=r.randrange(3, 30)), o[1], "retract", dict(of=i)))
    allops = [(o, i) for i, o in enumerate(ops)] 
    # assign message numbers by shuffled file names
    items = [dict(when=o[0], sender=o[1], kind=o[2], p=o[3], idx=i) for i, o in enumerate(ops)]
    for e in extra: items.append(dict(when=e[0], sender=e[1], kind="retract", p=e[3], idx=None))
    items.sort(key=lambda x: x["when"])
    order = list(range(len(items))); r.shuffle(order)
    stamp = lambda x: x.strftime("%Y-%m-%dT%H:%M:00Z")
    for n, it in zip(order, items): it["file"] = f"emails/msg-{n + 1:03d}.txt"
    byidx = {it["idx"]: it for it in items if it["idx"] is not None}
    # render
    V = {
     "reverse": ["Please reverse {t}. It was posted by mistake.", "{t} should not be on the books; take it out entirely.", "Void {t} please, it never happened."],
     "set": ["The amount on {t} should have been {a}, not what is in the ledger.", "Please correct {t}: the right figure is {a}.", "{t} was keyed wrong, set it to {a}."],
     "move": ["{t} belongs to {acc}, not the account it is under.", "Please re-book {t} to {acc}.", "Move {t} over to {acc}, wrong account was used."],
     "flip": ["{t} was entered with the wrong sign; the debit and credit are swapped.", "Please flip the sign of {t}.", "On {t} the direction is backwards, reverse the sign."],
     "dup": ["{a} and {b} are the same payment entered twice. Keep the earlier-dated one and remove the other.", "Duplicate alert: {a} / {b}. Drop whichever is dated later.",
             "We think {b} duplicates {a}. Keep the one with the earlier date."],
     "split": ["Please split {t}: {pct}% to {a}, the rest to {b}.", "{t} should be shared between {a} ({pct}%) and {b} (remainder).", "Divide {t} so that {a} carries {pct}% and {b} the remaining part."],
    }
    ws = {}
    sign = lambda c: ("-" if c < 0 else "") + fmt(c)
    for it in items:
        k = it["kind"]; p = it["p"]
        if k == "retract":
            tgt = byidx[p["of"]]
            body = r.choice(["Please disregard my email dated {w} about {t}.", "Ignore my earlier message ({w}) regarding {t}; no change is needed.", "Scratch the request I sent at {w} on {t}."]).format(w=stamp(tgt["when"]), t=tgt["p"]["t"])
        else:
            body = r.choice(V[k]).format(t=p.get("t", ""), a=(sign(p["amt"]) if k == "set" else p.get("a", "")), b=p.get("b", ""), acc=p.get("acc", ""), pct=p.get("pct", ""))
        ws[it["file"]] = f"From: {it['sender']}\nDate: {stamp(it['when'])}\nSubject: ledger amendment\n\n{body}\n\nThanks,\n{it['sender'].split('@')[0]}\n"
    ws["approvers.txt"] = "\n".join(approved) + "\n"
    ws["ledger.csv"] = "txn_id,date,account,amount_cents,memo\n" + "".join(f"{k},{v['date']},{v['acc']},{v['amt']},{v['memo']}\n" for k, v in led.items())
    # apply
    state = {k: dict(acc=v["acc"], amt=v["amt"], gone=False, parts=None) for k, v in led.items()}
    ignored, cancelled = set(), set()
    for it in items:
        if it["kind"] == "retract": cancelled.add(byidx[it["p"]["of"]]["file"])
    rhu = lambda x: int((D(abs(x)) / 1).quantize(D(1), ROUND_HALF_UP))
    for it in items:
        k, p = it["kind"], it["p"]
        if k == "retract": continue
        if it["sender"] not in approved or it["file"] in cancelled: ignored.add(it["file"]); continue
        ts = [p[x] for x in ("t", "a", "b") if x in p and str(p[x]).startswith("T-")]
        if any(t not in led for t in ts): ignored.add(it["file"]); continue
        if k == "reverse": state[p["t"]]["gone"] = True
        elif k == "set": state[p["t"]]["amt"] = p["amt"]
        elif k == "move": state[p["t"]]["acc"] = p["acc"]
        elif k == "flip": state[p["t"]]["amt"] = -state[p["t"]]["amt"]
        elif k == "dup":
            x, y = sorted([p["a"], p["b"]], key=lambda t: (led[t]["date"], t)); state[y]["gone"] = True
        elif k == "split":
            s = state[p["t"]]; a = D(abs(s["amt"])) * p["pct"] / 100; pa = int(a.quantize(D(1), ROUND_HALF_UP)) * (1 if s["amt"] > 0 else -1)
            s["parts"] = [(p["a"], pa), (p["b"], s["amt"] - pa)]
    bal = {a: 0 for a in accs}
    for k, s in state.items():
        if s["gone"]: continue
        if s["parts"]:
            for a, c in s["parts"]: bal[a] += c
        else: bal[s["acc"]] += s["amt"]
    ign = sorted(ignored)
    naive = {a: 0 for a in accs}
    for k, v in led.items(): naive[v["acc"]] += v["amt"]
    md = f"""
    # Correct the ledger from amendment emails

    `/workspace/ledger.csv` (txn_id, date, account, amount_cents, memo) is a ledger export; negative amounts are debits. `/workspace/emails/` holds {len(items)} amendment emails
    (`From:`, `Date:`, then the request in plain words), `/workspace/approvers.txt` lists the senders whose requests may be applied.

    Rules:
    1. Ignore every email from a sender not in `approvers.txt`.
    2. Apply the remaining emails in ascending `Date:` order (all dates are distinct). Several emails can touch the same transaction; each works on the result of the earlier ones.
    3. A request to disregard an earlier email ("disregard my email dated <timestamp>") cancels the email from that sender with exactly that `Date:`. The disregard email itself is not an amendment.
    4. Kinds of amendment: *reverse/void* removes the transaction entirely; *set the amount* replaces its amount (signed, in dollars in the email, convert to cents); *move* changes its account;
       *flip the sign* multiplies the amount by -1; *duplicate pair* "keep the earlier-dated one": remove the transaction with the later ledger `date` (tie: the higher id).
       *split* "p% to A, the rest to B": the transaction becomes two parts; A's part is round-half-up of |amount| x p / 100 cents with the transaction's sign, B's part is the remainder (so the parts add up to the amount).
    5. An email that names a transaction that is not in the ledger has no effect.

    Write:
    - `/workspace/balances.json`: an object mapping all 12 account ids to the corrected balance in integer cents (the sum of the account's amounts after all amendments).
    - `/workspace/ignored_emails.json`: sorted array of the email paths (e.g. `emails/msg-007.txt`) that had no effect: from unapproved senders, cancelled by a disregard email, or naming a transaction not in the ledger.
      Disregard emails themselves are not listed.
    """
    chk = """
    b = jl("balances.json"); ig = jl("ignored_emails.json")
    chk("balances-parses", isinstance(b, dict))
    b = b if isinstance(b, dict) else {}
    chk("balances-all-12-accounts", set(b) == set(E["b"]), sorted(b))
    good = [a for a in E["b"] if b.get(a) == E["b"][a] and type(b.get(a)) is int]
    for a in sorted(E["b"]):
        chk("balance-" + a, a in good, b.get(a))
    chk("ignored-emails-exact", ig == E["i"], None if not isinstance(ig, list) else "got %d expected %d" % (len(ig), len(E["i"])))
    chk("ignored-emails-sorted", isinstance(ig, list) and ig == sorted(ig))
    """
    spec = [("balances-parses", "`/workspace/balances.json`: an object mapping all 12 account ids to the corrected balance in integer cents"),
            ("balances-all", "`/workspace/balances.json`: an object mapping all 12 account ids to the corrected balance in integer cents"),
            ("balance-", "the corrected balance in integer cents (the sum of the account's amounts after all amendments)"),
            ("ignored-emails-exact", "sorted array of the email paths (e.g. `emails/msg-007.txt`) that had no effect"),
            ("ignored-emails-sorted", "sorted array of the email paths (e.g. `emails/msg-007.txt`) that had no effect")]
    note = ("A single groupby on ledger.csv gives the unamended balances: every account whose transactions were amended is wrong, and ignored_emails.json is missing. "
            "Applying emails in file-name order instead of Date: order, or applying unapproved/disregarded emails, breaks the chained set+move and double-set cases.")
    task("28-ledger-amendments", "novel", "long-input", 45, "Corrected balances from 3000 rows and amendment emails", md, ws, chk,
         {"balances.json": J(bal), "ignored_emails.json": J(ign)}, dict(b=bal, i=ign), note, axis="A", spec=spec, naive={"balances.json": J(naive)})

# =============================================================== 29 file 45 documents (B)
def t29():
    r = random.Random(129)
    areas = {"rig-report": "reports/rig", "quality-result": "reports/quality", "plan": "planning", "handoff": "handoffs", "minutes": "meetings"}
    slug_of = lambda t: re.sub(r"-+$", "", re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:40])
    authors = ["Dana Whit", "Lee Park", "Omar Reyes", "Priya Shah", "Marta Voss"]
    words = ["Quantization", "Kernel", "Offload", "Latency", "Budget", "Rollout", "Cache", "Scheduler", "Gateway", "Replay", "Context", "Staging", "Release", "Throughput", "Capacity"]
    def mk(title, typ, d, auth, ver):
        return f"---\ntitle: {title}\ntype: {typ}\ndate: {d}\nauthor: {auth}\nversion: {ver}\n---\n\n# {title}\n\nBody text for {title} ({typ}, v{ver}). {r.randrange(10**6)}\n"
    lib, existing = {}, []
    def addlib(title, typ, d, auth, ver):
        area = areas.get(typ, "misc"); yr = d[:4]; s = slug_of(title)
        path = f"library/{area}/{yr}/{s}.md"
        lib[path] = mk(title, typ, d, auth, ver)
        existing.append(dict(path=path, title=title, area=area, year=yr, slug=s, date=d, author=auth, ver=ver, typ=typ))
    for i in range(14):
        typ = r.choice(list(areas) + ["memo"])
        addlib(f"{r.choice(words)} {r.choice(words)} note {i}", typ, f"2026-{r.randrange(1, 7):02d}-{r.randrange(1, 28):02d}", r.choice(authors), 1)
    docs = []
    # 4 conflicts with existing: two where the new doc is newer, two where the existing is newer/equal-date lower version
    conf = r.sample(existing, 4)
    for j, e in enumerate(conf):
        if j < 2: d, ver = f"2026-{int(e['date'][5:7]) + 1:02d}-{e['date'][8:]}", 2
        elif j == 2: d, ver = e["date"], 1   # same date, lower... existing v1, new v1 -> tie on version: existing stays (rule below)
        else: d, ver = f"2026-{int(e['date'][5:7]) - 1:02d}-{e['date'][8:]}" if int(e["date"][5:7]) > 1 else "2025-12-31", 3
        docs.append(dict(title=e["title"], typ=e["typ"], date=d, author=r.choice(authors), ver=ver, conflict=e["path"]))
    # fix: j==2 same date and equal version -> existing stays; j==3 older date with higher version -> existing stays (date decides first)
    for i in range(41):
        typ = r.choice(list(areas) + ["memo", "faq"])
        docs.append(dict(title=f"{r.choice(words)} {r.choice(words)}: review {i}" if i % 3 else f"{r.choice(words)}  {r.choice(words)} (draft) {i}!", typ=typ,
                         date=f"2026-{r.randrange(7, 10):02d}-{r.randrange(1, 28):02d}", author=r.choice(authors), ver=1))
    # 2 intra-inbox collisions
    base = docs[10]; docs[11] = dict(title=base["title"], typ=base["typ"], date=base["date"][:8] + f"{min(28, int(base['date'][8:]) + 3):02d}", author=docs[11]["author"], ver=1)
    base = docs[20]; docs[21] = dict(title=base["title"].upper(), typ=base["typ"], date=base["date"][:8] + f"{max(1, int(base['date'][8:]) - 5):02d}", author=docs[21]["author"], ver=1)
    order = list(range(45)); r.shuffle(order)
    ws = {}
    for p, t in lib.items(): ws[p] = t
    for n, d in zip(order, docs):
        d["file"] = f"inbox/doc-{n + 1:02d}.md"; d["text"] = mk(d["title"], d["typ"], d["date"], d["author"], d["ver"]); ws[d["file"]] = d["text"]
    # resolve
    live = {e["path"]: dict(e, text=lib[e["path"]]) for e in existing}
    superseded = {}
    groups = {}
    for d in docs:
        area = areas.get(d["typ"], "misc"); d["area"] = area; d["year"] = d["date"][:4]; d["slug"] = slug_of(d["title"])
        groups.setdefault((area, d["year"], d["slug"]), []).append(d)
    place = {}
    for (area, yr, s), g in groups.items():
        g.sort(key=lambda d: (d["date"], d["file"]))
        for i, d in enumerate(g):
            d["slug2"] = d["slug"] if i == 0 else f"{d['slug']}-{i + 1}"
    final = {}  # path -> text (live) ; sup -> path
    expect_paths = {}
    for d in docs:
        path = f"library/{d['area']}/{d['year']}/{d['slug2']}.md"
        if path in live:
            e = live[path]
            newwins = (d["date"], d["ver"]) > (e["date"], e["ver"])
            if newwins:
                sp = f"library/_superseded/{e['area']}/{e['year']}/{e['slug']}--v{e['ver']}.md"
                expect_paths[sp] = e["text"]; live.pop(path)
                live[path] = dict(path=path, title=d["title"], area=d["area"], year=d["year"], slug=d["slug2"], date=d["date"], author=d["author"], ver=d["ver"], text=d["text"])
            else:
                sp = f"library/_superseded/{d['area']}/{d['year']}/{d['slug2']}--v{d['ver']}.md"
                expect_paths[sp] = d["text"]
        else:
            live[path] = dict(path=path, title=d["title"], area=d["area"], year=d["year"], slug=d["slug2"], date=d["date"], author=d["author"], ver=d["ver"], text=d["text"])
    for p, e in live.items(): expect_paths[p] = e["text"]
    rows = sorted(live.values(), key=lambda e: (e["date"], e["slug"]))
    def idx_area(rows_):
        out = "# Index by area\n"
        for a in sorted({e["area"] for e in rows_}):
            out += f"\n## {a}\n\n| date | slug | title |\n|---|---|---|\n" + "".join(f"| {e['date']} | {e['slug']} | {e['title']} |\n" for e in rows_ if e["area"] == a)
        return out
    def idx_date(rows_):
        return "# Index by date\n\n| date | area | slug |\n|---|---|---|\n" + "".join(f"| {e['date']} | {e['area']} | {e['slug']} |\n" for e in sorted(rows_, key=lambda e: (e["date"], e["slug"]), reverse=True)) 
    def idx_people(rows_):
        out = "# Index by author\n"
        for a in sorted({e["author"] for e in rows_}):
            out += f"\n## {a}\n\n" + "".join(f"- {e['date']} {e['area']}/{e['year']}/{e['slug']}\n" for e in rows_ if e["author"] == a)
        return out
    # existing indexes (before)
    ex = sorted([dict(e) for e in existing], key=lambda e: (e["date"], e["slug"]))
    ws["library/INDEX-by-area.md"] = idx_area(ex); ws["library/INDEX-by-date.md"] = idx_date(ex); ws["library/INDEX-by-author.md"] = idx_people(ex)
    idx_final = {"library/INDEX-by-area.md": idx_area(rows), "library/INDEX-by-date.md": idx_date(rows), "library/INDEX-by-author.md": idx_people(rows)}
    ref = dict(expect_paths) | idx_final
    ref = {k: v for k, v in ref.items() if k not in lib or v != lib[k] or True}
    ref["_delete.txt"] = "".join(d["file"] + "\n" for d in docs) + "".join(p + "\n" for p in (set(lib) - set(expect_paths)) if p in lib)
    # existing files that are superseded must be removed from their old location only if path no longer live (it is replaced by new doc, overlay replaces content) -> nothing to delete
    ref["_delete.txt"] = "".join(d["file"] + "\n" for d in docs)
    hashes = {p: hashlib.sha256(t.encode()).hexdigest() for p, t in expect_paths.items()}
    md = """
    # File 45 documents into the library

    `/workspace/inbox/` holds 45 documents, each with a front matter block (`title`, `type`, `date`, `author`, `version`). `/workspace/library/` is the archive, with three index files:
    `INDEX-by-area.md`, `INDEX-by-date.md`, `INDEX-by-author.md`. File every inbox document and bring the indexes up to date.

    **Path.** `library/<area>/<year>/<slug>.md`, content unchanged.
    - `area` from `type`: `rig-report` -> `reports/rig`, `quality-result` -> `reports/quality`, `plan` -> `planning`, `handoff` -> `handoffs`, `minutes` -> `meetings`, any other type -> `misc`.
    - `year`: the first four characters of `date`.
    - `slug` from `title`: lowercase, every run of characters other than `a-z0-9` becomes one `-`, strip leading and trailing `-`, cut to 40 characters, then strip a trailing `-` again.

    **Collisions inside the inbox.** If several inbox documents get the same `<area>/<year>/<slug>`, the one with the earliest `date` (ties: lower inbox file name) keeps the plain slug, and the next ones get `-2`, `-3`, ... appended to the slug, in date order.

    **Conflicts with the library.** If the final path already exists in `library/`, the document with the later `date` stays at that path; on equal dates the higher `version` stays; if both are equal the existing one stays.
    The loser is moved to `library/_superseded/<area>/<year>/<slug>--v<version>.md` (its own area, year, slug and version, content unchanged). Superseded documents are not in the indexes.

    **Indexes.** Rebuild all three so they list exactly the live documents, using exactly these formats (every file ends with a newline, no other text):
    - `INDEX-by-area.md`: `# Index by area`, then for each area in alphabetical order a blank line, `## <area>`, a blank line, the table header `| date | slug | title |`, `|---|---|---|`, and one row `| <date> | <slug> | <title> |` per document sorted by date then slug.
    - `INDEX-by-date.md`: `# Index by date`, a blank line, `| date | area | slug |`, `|---|---|---|`, and one row per document, sorted by date descending then slug descending.
    - `INDEX-by-author.md`: `# Index by author`, then for each author in alphabetical order a blank line, `## <author>`, a blank line, and one line `- <date> <area>/<year>/<slug>` per document sorted by date then slug.
    The `slug` in an index is the final slug (with any `-2` suffix). The inbox must end up empty.
    """
    chk = """
    for path, h in sorted(E["h"].items()):
        f = p(path)
        chk("filed-" + path, os.path.isfile(f) and hashlib.sha256(open(f, "rb").read()).hexdigest() == h)
    chk("inbox-empty", not os.path.isdir(p("inbox")) or not [x for x in os.listdir(p("inbox"))], os.listdir(p("inbox")) if os.path.isdir(p("inbox")) else "")
    live = sorted(os.path.relpath(os.path.join(dp, f), W) for dp, dn, fn in os.walk(p("library")) for f in fn if f.endswith(".md") and not f.startswith("INDEX"))
    chk("no-stray-library-files", live == sorted(E["h"]), "extra: %s" % sorted(set(live) - set(E["h"]))[:3])
    for n in ("INDEX-by-area.md", "INDEX-by-date.md", "INDEX-by-author.md"):
        chk("index-exact-" + n, rd("library/" + n) == E["i"][n], "differs")
    """
    spec = [("filed-", "**Path.** `library/<area>/<year>/<slug>.md`, content unchanged."), ("inbox-empty", "The inbox must end up empty."),
            ("no-stray", "Superseded documents are not in the indexes."), ("index-exact", "Rebuild all three so they list exactly the live documents, using exactly these formats")]
    task("29-library-filing", "session-derived", "long-job", 40, "File 45 documents with conflicts and indexes", md, ws, chk, ref,
         dict(h=hashes, i={k.split("/")[-1]: v for k, v in idx_final.items()}), "State accumulates: collisions inside the inbox and against the library must be resolved before the final indexes are right. Per-file checks give partial credit.",
         axis="B", spec=spec)

# =============================================================== 30 booking queue (B)
def t30():
    rooms = {"Aspen": 6, "Birch": 10, "Cedar": 20, "Dogwood": 4}
    init = [("BK-001", "Aspen", "Marta Voss", "2026-10-14", "09:00", "10:00"), ("BK-002", "Birch", "Dana Whit", "2026-10-14", "10:00", "12:00"),
            ("BK-003", "Cedar", "Priya Shah", "2026-10-14", "13:00", "15:00"), ("BK-004", "Dogwood", "Lee Park", "2026-10-14", "09:30", "10:30"),
            ("BK-005", "Aspen", "Omar Reyes", "2026-10-15", "11:00", "12:00"), ("BK-006", "Cedar", "Dana Whit", "2026-10-15", "09:00", "17:00")]
    st = [dict(id=a, room=b, who=c, date=d, start=e, end=f) for a, b, c, d, e, f in init]
    mins = lambda t: int(t[:2]) * 60 + int(t[3:])
    hhmm = lambda m: f"{m // 60:02d}:{m % 60:02d}"
    reqs = [("book", "Dana Whit", "Aspen", "2026-10-14", "10:00", "11:30"), ("any", "Lee Park", 8, "2026-10-14", "10:30", 60), ("extend", "R01", 30),
            ("book", "Lee Park", "Dogwood", "2026-10-14", "10:00", "11:00"), ("book", "Marta Voss", "Aspen", "2026-10-14", "11:45", "12:30"), ("cancel", "BK-002"),
            ("any", "Omar Reyes", 9, "2026-10-14", "11:00", 90), ("move", "Dana Whit", "2026-10-14", "Cedar"), ("extend", "R05", 30),
            ("book", "Lee Park", "Aspen", "2026-10-14", "07:30", "08:30"), ("book", "Ines Calder", "Elm", "2026-10-14", "10:00", "11:00"), ("cancel", "BK-002"),
            ("any", "Kim Lau", 5, "2026-10-15", "11:30", 30), ("cancelall", "Dana Whit", "2026-10-15"), ("move", "Priya Shah", "2026-10-14", "Aspen"),
            ("book", "Omar Reyes", "Cedar", "2026-10-15", "09:00", "12:00"), ("extend", "R16", 420), ("any", "Dana Whit", 25, "2026-10-15", "13:00", 60),
            ("book", "Lee Park", "Aspen", "2026-10-15", "11:30", "12:30"), ("book", "Lee Park", "Dogwood", "2026-10-15", "10:00", "11:00"), ("move", "Lee Park", "2026-10-15", "Birch"),
            ("move", "Dana Whit", "2026-10-14", "Birch"), ("book", "Marta Voss", "Cedar", "2026-10-14", "11:30", "12:00"), ("cancelref", "R02"), ("move", "Marta Voss", "2026-10-14", "Dogwood")]
    nxt = [7]; made = {}; log = []
    def overlap(room, d, s, e, skip=None):
        return [b for b in st if b["room"] == room and b["date"] == d and b["id"] != skip and mins(b["start"]) < e and s < mins(b["end"])]
    def hours(s, e): return s >= 480 and e <= 1080 and s < e
    txt = {}
    for i, q in enumerate(reqs, 1):
        rid = f"R{i:02d}"; k = q[0]; out = None
        if k == "book":
            _, who, room, d, s, e = q; s, e = mins(s), mins(e)
            if room not in rooms: out = ("rejected", "BAD_ROOM")
            elif not hours(s, e): out = ("rejected", "OUTSIDE_HOURS")
            elif overlap(room, d, s, e): out = ("rejected", "CONFLICT")
            else:
                bid = f"BK-{nxt[0]:03d}"; nxt[0] += 1; st.append(dict(id=bid, room=room, who=who, date=d, start=hhmm(s), end=hhmm(e))); made[rid] = bid; out = ("ok", bid)
            txt[rid] = r_ = [f"Hi, could {who} get {room} on {d} from {hhmm(s)} to {hhmm(e)}? Thanks.", f"{who} here: please book the room {room} for {d}, {hhmm(s)}-{hhmm(e)}."][i % 2]
        elif k == "any":
            _, who, n, d, s, dur = q; s = mins(s); e = s + dur
            if not hours(s, e): out = ("rejected", "OUTSIDE_HOURS")
            else:
                c = sorted([(c_, rn) for rn, c_ in rooms.items() if c_ >= n and not overlap(rn, d, s, e)])
                if not c: out = ("rejected", "NO_ROOM")
                else:
                    bid = f"BK-{nxt[0]:03d}"; nxt[0] += 1; st.append(dict(id=bid, room=c[0][1], who=who, date=d, start=hhmm(s), end=hhmm(e))); made[rid] = bid; out = ("ok", bid)
            txt[rid] = [f"{who} needs a room for {n} people on {d} at {hhmm(s)} for {dur} minutes. Any room that fits is fine.", f"Please find {who} a space for {n} on {d}, starting {hhmm(s)}, {dur} min."][i % 2]
        elif k == "cancel":
            b = [x for x in st if x["id"] == q[1]]
            if b: st.remove(b[0]); out = ("ok", q[1])
            else: out = ("rejected", "NOT_FOUND")
            txt[rid] = f"Please cancel booking {q[1]}."
        elif k == "cancelref":
            bid = made.get(q[1]); b = [x for x in st if x["id"] == bid]
            if not bid: out = ("rejected", "REF_NOT_BOOKED")
            elif b: st.remove(b[0]); out = ("ok", bid)
            else: out = ("rejected", "NOT_FOUND")
            txt[rid] = f"Cancel the booking that was created for request {q[1]}."
        elif k == "cancelall":
            bs = sorted([x for x in st if x["who"] == q[1] and x["date"] == q[2]], key=lambda x: x["id"])
            if not bs: out = ("rejected", "NOT_FOUND")
            else:
                for b in bs: st.remove(b)
                out = ("ok", ";".join(b["id"] for b in bs))
            txt[rid] = f"{q[1]} no longer needs anything on {q[2]}. Cancel all of their bookings that day."
        elif k == "move":
            _, who, d, room = q
            bs = [x for x in st if x["who"] == who and x["date"] == d]
            if room not in rooms: out = ("rejected", "BAD_ROOM")
            elif not bs: out = ("rejected", "NOT_FOUND")
            elif len(bs) > 1: out = ("rejected", "AMBIGUOUS")
            else:
                b = bs[0]
                if overlap(room, d, mins(b["start"]), mins(b["end"]), skip=b["id"]): out = ("rejected", "CONFLICT")
                else: b["room"] = room; out = ("ok", b["id"])
            txt[rid] = f"Move {who}'s booking on {d} to {room}, same time."
        elif k == "extend":
            ref, mn = q[1], q[2]; bid = made.get(ref)
            b = [x for x in st if x["id"] == bid]
            if not bid: out = ("rejected", "REF_NOT_BOOKED")
            elif not b: out = ("rejected", "NOT_FOUND")
            else:
                b = b[0]; e = mins(b["end"]) + mn
                if not hours(mins(b["start"]), e): out = ("rejected", "OUTSIDE_HOURS")
                elif overlap(b["room"], b["date"], mins(b["start"]), e, skip=b["id"]): out = ("rejected", "CONFLICT")
                else: b["end"] = hhmm(e); out = ("ok", b["id"])
            txt[rid] = f"Please extend the booking made for request {ref} by {mn // 60} hours." if mn % 60 == 0 else f"Please extend the booking made for request {ref} by {mn} minutes."
        log.append((rid, out[0], out[1]))
    final = sorted(st, key=lambda b: (b["date"], b["start"], b["room"], b["id"]))
    ws = {"state/rooms.json": J(rooms), "state/bookings.json": J(sorted([dict(id=a, room=b, who=c, date=d, start=e, end=f) for a, b, c, d, e, f in init], key=lambda b: b["id"]))}
    for rid, t in txt.items(): ws[f"requests/{rid}.txt"] = t + "\n"
    logcsv = "request,outcome,detail\n" + "".join(",".join(x) + "\n" for x in log)
    md = """
    # Process a queue of room requests

    `/workspace/state/rooms.json` (name -> capacity) and `/workspace/state/bookings.json` (list of `id`, `room`, `who`, `date`, `start`, `end`) are the booking state.
    `/workspace/requests/R01.txt` ... `R25.txt` are requests in plain words. Process them **in order R01 to R25**; each request sees the state left by the earlier ones.

    Rules:
    - Rooms are bookable 08:00 to 18:00 (a booking must start at or after 08:00 and end at or before 18:00). Two bookings in the same room on the same date conflict if their time ranges overlap; touching at an endpoint is fine.
    - New bookings get ids `BK-007`, `BK-008`, ... in order of success (a rejected request uses no id).
    - "Book <room>": reject `BAD_ROOM` (no such room), then `OUTSIDE_HOURS`, then `CONFLICT`, in that order of precedence.
    - "A room for N people": reject `OUTSIDE_HOURS` first; otherwise the free room with the smallest capacity that is at least N (ties: alphabetical); `NO_ROOM` if none.
    - "Cancel booking BK-xxx": `NOT_FOUND` if it does not exist now. "Cancel the booking created for request Rxx": `REF_NOT_BOOKED` if request Rxx was rejected, else as above.
    - "Cancel all of <person>'s bookings on <date>": removes all of them (`NOT_FOUND` if none).
    - "Move <person>'s booking on <date> to <room>": the same time in the new room. `BAD_ROOM`, then `NOT_FOUND` (the person has none that day), then `AMBIGUOUS` (more than one), then `CONFLICT` with other bookings (not itself).
    - "Extend the booking made for request Rxx by <time>": `REF_NOT_BOOKED` if Rxx was rejected, `NOT_FOUND` if that booking has since been cancelled, then `OUTSIDE_HOURS`, then `CONFLICT`.

    Write:
    1. `/workspace/state/bookings.json`: the final state as a JSON list of the same objects (`id`, `room`, `who`, `date`, `start`, `end`), sorted by date, start, room, id.
    2. `/workspace/log.csv` with header `request,outcome,detail` and one row per request R01..R25: `outcome` is `ok` or `rejected`; `detail` is the affected booking id (several ids joined by `;`, sorted) when ok, or the reason code when rejected.
    """
    chk = """
    fb = jl("state/bookings.json")
    chk("final-state-exact", fb == E["f"], "differs" if fb is not None else "missing")
    chk("final-state-count", isinstance(fb, list) and len(fb) == len(E["f"]), None if not isinstance(fb, list) else len(fb))
    r = rows("log.csv")
    chk("log-header", (rd("log.csv") or "").splitlines()[:1] == ["request,outcome,detail"])
    got = {x["request"]: (x["outcome"], x["detail"]) for x in (r or [])}
    for rid, o, d in E["l"]:
        chk("log-" + rid, got.get(rid) == (o, d), got.get(rid))
    """
    spec = [("final-state", "`/workspace/state/bookings.json`: the final state as a JSON list of the same objects"), ("log-header", "`/workspace/log.csv` with header `request,outcome,detail`"),
            ("log-", "`outcome` is `ok` or `rejected`; `detail` is the affected booking id")]
    task("30-room-booking-queue", "session-derived", "long-job", 35, "25 dependent booking requests", md, ws, chk, {"state/bookings.json": J(final), "log.csv": logcsv},
         dict(f=final, l=log), "Each request reads the state the earlier ones left, and later requests refer to earlier ones (R05, R16 extend; R02 cancel). One slip changes later outcomes.",
         axis="B", spec=spec)

for f in (t27, t28, t29, t30): f()
