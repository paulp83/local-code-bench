#!/usr/bin/env python3
"""check.py for 22-form-fill: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{}')
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

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
