# Clean an order export and list what cannot be fixed

`/workspace/orders_raw.csv` is an export with problems. Parse it as RFC 4180 CSV (like Python's `csv` module with defaults) after removing a leading byte-order mark if present. A *record* is one CSV row; number records from 1 for the first data row after the header.

Fix, per record:
- `customer`: replace any run of whitespace (including line breaks) with one space and trim.
- `date`: accepted forms are `YYYY-MM-DD`, `DD/MM/YYYY` and `Mon D YYYY` (three-letter English month, no comma). Output ISO `YYYY-MM-DD`.
- `amount`: remove thousands commas; the result must be a plain decimal number; output with exactly 2 decimals.
- `currency`: must be `USD`, `EUR` or `GBP`.

A record that cannot be fixed by these rules is a **reject**. Give each reject the first reason that applies, in this order:
`BAD_COLUMNS` (not exactly 5 fields), `MISSING_ID` (empty `order_id`), `DUPLICATE_ID` (its `order_id` already appeared in an earlier record), `BAD_DATE`, `BAD_AMOUNT`, `BAD_CURRENCY`.

Write:
1. `/workspace/clean.csv` with header `order_id,customer,date,amount,currency`: every record that is not a reject, sorted by `order_id`.
2. `/workspace/rejects.csv` with header `record,reason`: the record number and reason of every reject, in record order.
Do not drop or repair rejects silently, and do not reject records the rules can fix.
