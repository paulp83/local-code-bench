#!/usr/bin/env python3
"""check.py for 05-cold-storage-move: deterministic, stdlib only. Usage: check.py [workspace_dir]  (default /workspace)."""
import sys, os, re, json, csv, hashlib, io
W = sys.argv[1] if len(sys.argv) > 1 else "/workspace"
E = json.loads('{"h": {"logs/a.log": "226e8522d23598dd711452ec0e8d97359de227cd0e50a1cb1dade8ed7f1c376a", "logs/f10.dat": "adbe04b848d2f9704972d24fa51a75c7a3f9d69d47757b33a0ccd484d7a3919e", "logs/f5.dat": "70bfc696c2bd1c4ce986194643ace107a513ae1537a64545e807ac720bb7f6a5", "logs/rig/b run.json": "62709fa011b51be5778eafb0e4869f3ed875905e0e9e4c0fa36ed19caf7d2862", "logs/rig/f11.dat": "565931a287e2c487c5b90fe1df5777336293f148baeb5a16680af35483e59429", "logs/rig/f6.dat": "aabf6d8d5846cace7922345afe23ff8801b6a1f659ac0a2dbc13cf4dd90c6ecf", "notes/d.md": "10c1283f829d84b6c306062f50189e2a9fc99b4771b0718e033e4af9d31f94f1", "notes/f13.dat": "b7c34b24a38d043795d9d2d6c5468d0418e2cf5e8e6e5cd78e52f25ae32312e5", "notes/f8.dat": "1d9a56cd06e0cde01290c3d6041681025234c8b30db94168c8020bbd681a6e40", "notes/old stuff/e.txt": "f1c7e83a8dc770b4b33fef90e887a14a90bde77606ea8791a998c01cfd321655", "notes/old stuff/f9.dat": "850d7c237997ac6a1ba6b6c2640d535c6c8a47cb56ee2e329966151716c7028e", "weights/c.bin": "bb9249659f944a73d1af3954f4ae7860d518cab8c623324b819aa304103af735", "weights/f12.dat": "2d3d98c13eecf4bef1e50f925f8c8364efbc7e8da550eae3f6e285c5f7b70e16", "weights/f7.dat": "4f4c64f7a92048bb359610a14b00351d58c66d143612c1819ecce5b6831cde7a"}, "l": {"latest.log": "logs/a.log", "notes/toplevel": "../logs", "weights/current": "c.bin"}, "lt": "latest.log -> logs/a.log\\nnotes/toplevel -> ../logs\\nweights/current -> c.bin\\n", "m": "226e8522d23598dd711452ec0e8d97359de227cd0e50a1cb1dade8ed7f1c376a  logs/a.log\\nadbe04b848d2f9704972d24fa51a75c7a3f9d69d47757b33a0ccd484d7a3919e  logs/f10.dat\\n70bfc696c2bd1c4ce986194643ace107a513ae1537a64545e807ac720bb7f6a5  logs/f5.dat\\n62709fa011b51be5778eafb0e4869f3ed875905e0e9e4c0fa36ed19caf7d2862  logs/rig/b run.json\\n565931a287e2c487c5b90fe1df5777336293f148baeb5a16680af35483e59429  logs/rig/f11.dat\\naabf6d8d5846cace7922345afe23ff8801b6a1f659ac0a2dbc13cf4dd90c6ecf  logs/rig/f6.dat\\n10c1283f829d84b6c306062f50189e2a9fc99b4771b0718e033e4af9d31f94f1  notes/d.md\\nb7c34b24a38d043795d9d2d6c5468d0418e2cf5e8e6e5cd78e52f25ae32312e5  notes/f13.dat\\n1d9a56cd06e0cde01290c3d6041681025234c8b30db94168c8020bbd681a6e40  notes/f8.dat\\nf1c7e83a8dc770b4b33fef90e887a14a90bde77606ea8791a998c01cfd321655  notes/old stuff/e.txt\\n850d7c237997ac6a1ba6b6c2640d535c6c8a47cb56ee2e329966151716c7028e  notes/old stuff/f9.dat\\nbb9249659f944a73d1af3954f4ae7860d518cab8c623324b819aa304103af735  weights/c.bin\\n2d3d98c13eecf4bef1e50f925f8c8364efbc7e8da550eae3f6e285c5f7b70e16  weights/f12.dat\\n4f4c64f7a92048bb359610a14b00351d58c66d143612c1819ecce5b6831cde7a  weights/f7.dat\\n"}')
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

except Exception as ex:
    chk("check-crashed", False, repr(ex))
finish()
