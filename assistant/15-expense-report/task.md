# Expense report in USD

`/workspace/receipts.csv` (id, date, vendor, amount, currency, category) and `/workspace/fx.csv` (date, currency, usd_per_unit) are the inputs. Write `/workspace/report.json`.

Rules:
1. **Duplicates**: receipts with the same date, vendor, amount and currency are one receipt. Keep the first in file order, list the dropped ids in `duplicates_dropped`.
2. **Conversion** to USD: multiply by the `usd_per_unit` of the receipt's date and currency. If `fx.csv` has no rate for that exact date (weekends), use the latest earlier date's rate. USD receipts need no rate.
   Round **each receipt** to 2 decimals (half up) before summing.
3. **Cap**: a `meals` receipt above 60.00 USD (after conversion and rounding) is not reimbursable at all (it counts in `claimed`, adds 0 to `reimbursable`); list its id in `over_cap`.
4. Output JSON: `{"categories": {"<cat>": {"claimed": <number>, "reimbursable": <number>}, ...}, "total_reimbursable": <number>, "duplicates_dropped": [ids], "over_cap": [ids]}`
   with all four categories (`meals`, `transport`, `lodging`, `supplies`) present, ids sorted ascending, money as JSON numbers with at most 2 decimals.
