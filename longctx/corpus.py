#!/usr/bin/env python3
"""Build the filler corpus: N shuffled orderings of a repo's markdown docs, tokenized to TOKENS ids each.

  python3 corpus.py --repo ~/club-3090 --tokenizer /path/to/tokenizer.json --out corpus/

Writes corpus/docA.json ... (a JSON list of token ids each). Needs `pip install tokenizers`. Use the tokenizer of the
model you will serve: the probes send token ids, so both servers must tokenize identically."""
import argparse, glob, json, random
from pathlib import Path
from tokenizers import Tokenizer

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True, help="a clone of club-3090 (any repo with lots of markdown works)")
ap.add_argument("--tokenizer", required=True, help="tokenizer.json of the served model")
ap.add_argument("--out", default="corpus")
ap.add_argument("--docs", type=int, default=8)
ap.add_argument("--tokens", type=int, default=250000)
a = ap.parse_args()
repo = Path(a.repo).expanduser().resolve()
tok = Tokenizer.from_file(a.tokenizer)
files = sorted(glob.glob(f"{repo}/docs/**/*.md", recursive=True) + glob.glob(f"{repo}/models/**/*.md", recursive=True))
texts = [open(f, errors="ignore").read() for f in files]
Path(a.out).mkdir(exist_ok=True)
for k in range(a.docs):
    name, idx = "ABCDEFGHIJKLMNOP"[k], list(range(len(files)))
    random.Random(k + 1).shuffle(idx)
    ids = []
    for i in idx:
        ids += tok.encode(f"\n\n# FILE {Path(files[i]).relative_to(repo)}\n\n" + texts[i]).ids
        if len(ids) >= a.tokens:
            break
    json.dump(ids[:a.tokens], open(f"{a.out}/doc{name}.json", "w"))
    print(name, min(len(ids), a.tokens), "tokens from", len(files), "files")
