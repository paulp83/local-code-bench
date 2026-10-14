# Fetch 20 items from a flaky source

`/workspace/ids.txt` lists 20 item ids. `/workspace/fetch.sh <id>` fetches one item from the (offline) source and prints its JSON on stdout. It is the only sanctioned way to get items:
do not read `/workspace/.remote/` directly. The source is flaky, and **retrying a failed fetch is allowed**.
`/workspace/manifest.csv` has the expected `sha256` and byte size of each item's full JSON.

Deliver:
1. `/workspace/data/<id>.json` for all 20 items, each byte-identical to the item the source holds (it must match `manifest.csv`). A fetch that exits 0 can still return damaged data; check it against the manifest.
2. `/workspace/summary.json`: `{"count": 20, "total_amount_cents": <sum of the `amount_cents` field over all 20 items>, "retried": [<ids that needed more than one fetch call, sorted>]}`.
