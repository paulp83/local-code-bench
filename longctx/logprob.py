#!/usr/bin/env python3
"""Teacher-forced log-probs at long prefixes. For each filler doc and prefix length L, send the first L tokens and
score the last --window tokens (log-prob of the token that actually came next, plus the server's top-1 token).
Run it against two servers that differ in one setting, then compare with logprob_report.py.

  python3 logprob.py --arm bf16 --out logprob_bf16.json --base-url http://localhost:8173
Needs SGLang's native /generate (input_ids, return_logprob, logprob_start_len) and /flush_cache."""
import argparse, json, time
from common import post, flush_cache, load_docs

ap = argparse.ArgumentParser()
ap.add_argument("--arm", required=True, help="label stored in the output")
ap.add_argument("--out", required=True)
ap.add_argument("--base-url", default="http://localhost:8173")
ap.add_argument("--corpus", default="corpus")
ap.add_argument("--docs", default="ABCDEFGH")
ap.add_argument("--lengths", default="8192,32768,131072,250000")
ap.add_argument("--window", type=int, default=256, help="tokens scored per prompt. 2048 ran a 0.95-mem-fraction slug out of memory")
a = ap.parse_args()
docs = load_docs(a.corpus, a.docs)
res = []
for d in a.docs:
    for L in map(int, a.lengths.split(",")):
        flush_cache(a.base_url)
        t0 = time.time()
        o = post(a.base_url, "/generate", {"input_ids": docs[d][:L], "sampling_params": {"max_new_tokens": 1, "temperature": 0},
                                           "return_logprob": True, "logprob_start_len": L - a.window, "top_logprobs_num": 1})
        mi = o["meta_info"]
        pairs = [x for x in mi["input_token_logprobs"] if x[0] is not None]
        res.append({"arm": a.arm, "doc": d, "L": L, "lp": [x[0] for x in pairs], "ids": [x[1] for x in pairs],
                    "top1": [t[0][1] for t in mi["input_top_logprobs"] if t], "cached": mi.get("cached_tokens")})
        print(f"{a.arm} doc{d} L={L}: n={len(pairs)} meanNLL={-sum(x[0] for x in pairs) / len(pairs):.4f} {time.time() - t0:.0f}s", flush=True)
        json.dump(res, open(a.out, "w"))
