# Triage the inbox

`/workspace/inbox/` has 30 emails (`.eml`). Write `/workspace/triage.csv` with header `id,priority,owner,due`, one row per email, `id` = file name without `.eml`, sorted by id.

**priority** (first rule that matches wins):
1. `P1` if the sender domain is `acme-hosting.example` or `gpu-vendor.example`, or the subject contains `outage` or `urgent` (any case).
2. `P3` if the message has a `Precedence: bulk` header, or the subject starts with `[newsletter]` (any case).
3. otherwise `P2`.

**owner**: the first row of this table whose keyword appears in the subject (any case), top to bottom; `unassigned` if none:
`invoice` -> finance, `billing` -> finance, `driver` -> hardware, `gpu` -> hardware, `token` -> security, `security` -> security, `preflight` -> tooling, `docs` -> docs.

**due**: the date in the email's `Date` header plus N business days (Monday to Friday; weekends are skipped when counting), as `YYYY-MM-DD`. N is 0 for P1, 2 for P2, 5 for P3.
