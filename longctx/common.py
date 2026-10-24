"""Shared helpers for the long-context state probes (SGLang native API)."""
import json, time, urllib.request


def post(base, path, body, timeout=3600):
    req = urllib.request.Request(base + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def flush_cache(base, tries=30):
    """Empty the prefix cache so each prompt is prefilled from scratch. The server answers 400 while a request is
    still draining, so retry."""
    for _ in range(tries):
        try:
            urllib.request.urlopen(urllib.request.Request(base + "/flush_cache", method="POST"), timeout=60).read()
            return
        except Exception:
            time.sleep(5)
    raise SystemExit("flush_cache never succeeded")


def load_docs(corpus_dir, names):
    return {n: json.load(open(f"{corpus_dir}/doc{n}.json")) for n in names}
