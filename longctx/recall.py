#!/usr/bin/env python3
"""Planted-fact recall, teacher-forced. Per (filler doc, prefix length L) one prompt holds 4 'plant' facts (a name, placed
at 2-10% depth) and 4 'update' facts (a name at 2-10% depth, then a correction at 45-55%). Eight queries follow, each
ending "Currently the X team on-call is"; the script scores the first answer token's log-prob for the correct name versus
an alternative: the stale name for updates, a name that never appears for plants. margin = lp(correct) - lp(alt).
Prompts are fully seeded, so two servers see byte-identical token ids.

  python3 recall.py --arm bf16 --out recall_bf16.json --tokenizer /path/to/tokenizer.json
Re-running with the same --out resumes: it skips finished (doc, L) groups. Needs SGLang's /generate with
token_ids_logprob, and /flush_cache."""
import argparse, hashlib, json, os, random, time
from tokenizers import Tokenizer
from common import post, flush_cache, load_docs

ap = argparse.ArgumentParser()
ap.add_argument("--arm", required=True, help="label stored in the output")
ap.add_argument("--out", required=True)
ap.add_argument("--tokenizer", required=True, help="tokenizer.json of the served model")
ap.add_argument("--base-url", default="http://localhost:8173")
ap.add_argument("--corpus", default="corpus")
ap.add_argument("--docs", default="ABCDEFGH")
ap.add_argument("--lengths", default="8192,32768,131072,250000")
args = ap.parse_args()
ARM, OUT, BASE, DOCS = args.arm, args.out, args.base_url, args.docs
LENS = [int(x) for x in args.lengths.split(",")]
tok = Tokenizer.from_file(args.tokenizer)
enc = lambda s: tok.encode(s).ids
FIRST = ["Priya","Dana","Marcus","Elena","Tomas","Ingrid","Kenji","Amara","Lucas","Noor","Felix","Sofia","Hugo","Mei","Oscar","Zara","Anton","Leila","Bruno","Chloe","Dmitri","Esme","Farid","Greta"]
LAST = ["Shah","Cole","Reyes","Novak","Okafor","Lindqvist","Tanaka","Haddad","Moreau","Petrov","Quinn","Varga","Weiss","Yilmaz","Abara","Brandt","Costa","Dubois","Ekström","Fontaine","Grimaldi","Holm","Iyer","Jansen"]
TEAMS = ["Alder","Birch","Cedar","Dune","Ember","Fjord","Glade","Heath","Isle","Juniper","Knoll","Larch","Moor","Nook","Oak","Pine"]
def name_first_tok(n): return enc(" " + n)[0]
def build(doc, L, filler):
    rng = random.Random(f"{doc}-{L}")
    # 12 distinct names whose first tokens differ, so one token decides the answer
    while True:
        names = [f"{rng.choice(FIRST)} {rng.choice(LAST)}" for _ in range(12)]
        ft = [name_first_tok(n) for n in names]
        if len(set(ft)) == 12 and len({n.split()[0] for n in names}) == 12: break
    teams = rng.sample(TEAMS, 8)
    items, inserts = [], []
    for i, t in enumerate(teams):
        if i < 4:  # plant-only: correct = names[i]; the alt is replaced below by a name that never appears
            inserts.append((rng.uniform(.02, .10), f"\n\n[Ops note] The on-call engineer for the {t} team is {names[i]}.\n\n"))
            items.append(dict(team=t, kind="plant", correct=names[i], alt=names[8 + i]))
        else:      # update: stale = names[i] (planted early), correct = names[i + 4] (the later correction)
            a, b = names[i], names[i + 4]
            inserts.append((rng.uniform(.02, .10), f"\n\n[Ops note] The on-call engineer for the {t} team is {a}.\n\n"))
            inserts.append((rng.uniform(.45, .55), f"\n\n[Ops note, later] Correction: the {t} team on-call has changed, and {b} now holds it.\n\n"))
            items.append(dict(team=t, kind="update", correct=b, alt=a))
    # names[8..11] are the corrections, so they appear in the prompt: draw fresh alts that appear nowhere in it
    for k, it in enumerate([x for x in items if x["kind"] == "plant"]):
        while True:
            alt = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
            if alt not in names and name_first_tok(alt) not in set(ft): break
        it["alt"] = alt
    ins = sorted(((int(f * L), enc(s)) for f, s in inserts), key=lambda x: x[0])
    qlen = max(len(enc(f"\n\nQuestion: Who currently holds on-call for the {t} team?\nAnswer: Currently the {t} team on-call is")) for t in teams)
    body_len = L - sum(len(s) for _, s in ins) - qlen - 2
    base = filler[:body_len]; out, prev = [], 0
    for pos, s in ins:
        out += base[prev:pos] + s; prev = pos
    out += base[prev:]
    return out, items
FILLER = load_docs(args.corpus, DOCS)


def run():
    res = json.load(open(OUT)) if os.path.exists(OUT) else []
    done = {(r["doc"], r["L"]) for r in res}
    # drop partial (doc,L) groups: a complete group has 8 items
    done = {k for k in done if sum((r["doc"], r["L"]) == k for r in res) == 8}
    res = [r for r in res if (r["doc"], r["L"]) in done]
    for doc in DOCS:
        filler = FILLER[doc]
        for L in LENS:
            if (doc, L) in done: continue
            flush_cache(BASE)
            ctx, items = build(doc, L, filler)
            for it in items:
                q = enc(f"\n\nQuestion: Who currently holds on-call for the {it['team']} team?\nAnswer: Currently the {it['team']} team on-call is")
                ids = ctx + q
                c, a = name_first_tok(it["correct"]), name_first_tok(it["alt"])
                t0 = time.time()
                o = post(BASE, "/generate", {"input_ids": ids, "sampling_params": {"max_new_tokens": 1, "temperature": 0},
                                       "return_logprob": True, "logprob_start_len": len(ids) - 1, "token_ids_logprob": [c, a]})
                mi = o["meta_info"]
                lc, la = [x[0] for x in mi["output_token_ids_logprobs"][0]][:2]
                res.append(dict(arm=ARM, doc=doc, L=L, kind=it["kind"], team=it["team"], correct=it["correct"], alt=it["alt"],
                                lc=lc, la=la, margin=lc - la, plen=len(ids), phash=hashlib.md5(json.dumps(ids).encode()).hexdigest(),
                                cached=mi.get("cached_tokens"), text=o["text"]))
                print(f"{ARM} {doc} L={L} {it['kind']:6} margin={lc-la:+.2f} lc={lc:.2f} cached={mi.get('cached_tokens')} {time.time()-t0:.0f}s", flush=True)
            json.dump(res, open(OUT, "w"))
run()
