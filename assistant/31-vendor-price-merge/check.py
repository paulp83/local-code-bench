#!/usr/bin/env python3
"""check.py for 31-vendor-price-merge: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"c": {"AX135": {"Birch": ["72.77"], "Cobalt": ["72.87"]}, "BZ156": {"Alder": ["6.29", "6.69"], "Birch": ["6.29"]}, "BZ345": {"Alder": ["54.17"], "Birch": ["54.17"], "Cobalt": ["54.12"]}, "BZ359": {"Alder": ["35.37"], "Cobalt": ["35.35"]}, "BZ443": {"Alder": ["78.60"], "Cobalt": ["78.58"]}, "CX401": {"Alder": ["84.97"], "Birch": ["7.08"]}, "CZ478": {"Alder": ["4.37"], "Birch": ["4.37"], "Cobalt": ["4.39"]}, "CZ499": {"Birch": ["81.21"], "Cobalt": ["81.19"]}, "DX191": {"Alder": ["22.56"], "Birch": ["22.46"], "Cobalt": ["22.56"]}}, "m": {"AX135": ["Adapter black", "", "Birch;Cobalt"], "AX142": ["Bracket large", "16.58", "Birch;Cobalt"], "AX205": ["Panel steel", "24.01", "Alder"], "AX233": ["Sleeve large", "34.47", "Birch;Cobalt"], "AX338": ["Bracket steel", "78.47", "Birch;Cobalt"], "AY282": ["Bolt large", "10.65", "Birch;Cobalt"], "AY289": ["Cable large", "19.54", "Alder;Birch"], "AY331": ["Clip black", "49.72", "Alder;Cobalt"], "AY366": ["Bolt large", "19.04", "Alder;Birch;Cobalt"], "AY373": ["Clip large", "64.81", "Alder;Cobalt"], "AY471": ["Cable steel", "6.96", "Birch"], "AY506": ["Fan black", "5.92", "Birch;Cobalt"], "AZ114": ["Fan large", "73.87", "Birch;Cobalt"], "AZ303": ["Strap large", "64.79", "Alder"], "BX387": ["Sleeve small", "58.05", "Alder;Cobalt"], "BX485": ["Bolt large", "54.54", "Alder;Cobalt"], "BX492": ["Adapter black", "65.91", "Alder;Cobalt"], "BY128": ["Strap large", "72.55", "Birch;Cobalt"], "BY163": ["Clip small", "1.71", "Alder;Birch;Cobalt"], "BY177": ["Bracket steel", "12.51", "Alder;Birch"], "BY184": ["Bolt steel", "64.79", "Birch"], "BY275": ["Rail black", "16.65", "Birch;Cobalt"], "BY415": ["Rail steel", "74.54", "Alder;Birch"], "BZ156": ["Adapter black", "", "Alder;Birch"], "BZ219": ["Cable small", "86.50", "Alder;Birch;Cobalt"], "BZ261": ["Panel large", "15.40", "Alder;Cobalt"], "BZ268": ["Strap steel", "87.81", "Alder;Birch;Cobalt"], "BZ345": ["Bracket small", "", "Alder;Birch;Cobalt"], "BZ359": ["Fan large", "", "Alder;Cobalt"], "BZ443": ["Clip black", "", "Alder;Cobalt"], "CX107": ["Sleeve small", "58.53", "Alder"], "CX149": ["Bolt steel", "35.15", "Alder;Birch"], "CX198": ["Cable black", "7.76", "Alder;Birch"], "CX296": ["Rail black", "18.09", "Alder;Cobalt"], "CX401": ["Adapter large", "", "Alder;Birch"], "CX429": ["Adapter black", "50.41", "Alder;Cobalt"], "CY100": ["Bolt small", "65.87", "Cobalt"], "CY226": ["Adapter large", "39.32", "Birch;Cobalt"], "CY457": ["Clip black", "6.45", "Alder;Cobalt"], "CZ247": ["Bolt large", "53.73", "Alder;Birch"], "CZ352": ["Fan small", "4.70", "Alder;Birch;Cobalt"], "CZ478": ["Bolt steel", "", "Alder;Birch;Cobalt"], "CZ499": ["Adapter small", "", "Birch;Cobalt"], "DX170": ["Panel small", "75.93", "Alder;Birch;Cobalt"], "DX191": ["Clip black", "", "Alder;Birch;Cobalt"], "DX310": ["Panel small", "78.18", "Alder"], "DX317": ["Clip steel", "16.26", "Alder;Birch"], "DX324": ["Cable black", "14.25", "Alder;Birch"], "DX394": ["Strap small", "59.46", "Alder;Birch"], "DX422": ["Panel small", "12.65", "Alder;Birch"], "DX436": ["Fan large", "48.14", "Alder;Birch;Cobalt"], "DX513": ["Fan small", "41.65", "Cobalt"], "DY212": ["Fan steel", "83.95", "Alder;Birch;Cobalt"], "DY240": ["Bracket black", "80.00", "Alder"], "DY254": ["Rail small", "27.56", "Birch;Cobalt"], "DY380": ["Rail large", "85.23", "Birch;Cobalt"], "DY408": ["Rail black", "14.74", "Birch;Cobalt"], "DY464": ["Cable black", "35.08", "Birch"], "DZ121": ["Rail large", "9.83", "Alder;Birch;Cobalt"], "DZ450": ["Panel black", "20.22", "Birch;Cobalt"]}}')
R = []
def chk(name, ok, why=""):
    R.append((name, bool(ok), why))
def p(*a): return os.path.join(W, *a)
def rd(rel):
    try:
        with open(p(rel), encoding="utf-8") as f: return f.read()
    except Exception: return None
def jl(rel):
    s = rd(rel)
    if s is None: return None
    try: return json.loads(s)
    except Exception: return None
def rows(rel):
    s = rd(rel)
    if s is None: return None
    try: return list(csv.DictReader(io.StringIO(s)))
    except Exception: return None
def finish():
    for n, ok, why in R:
        print(("PASS " if ok else "FAIL ") + n + ("" if ok or not why else ": " + str(why)[:200]))
    f = sum(1 for r in R if not r[1])
    print("PASS: %d FAIL: %d" % (len(R) - f, f))
    sys.exit(0 if f == 0 and R else 1)
try:
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

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
