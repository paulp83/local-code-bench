# Merge three vendor price lists

`/workspace/vendors/` has `alder.csv`, `birch.csv` and `cobalt.csv`. They use different column names and units.

- Alder: `item_code`, `name`, `unit_price` (USD per unit), `currency` (always USD).
- Birch: `SKU`, `description`, `case_price` (USD for a whole case), `case_size` (units per case). Unit price = `case_price / case_size`, rounded half up to 2 decimals.
- Cobalt: `sku`, `desc`, `price_usd` (USD per unit).

A SKU is identified by its code uppercased with every non-alphanumeric character removed (`ax-107`, `AX-107` and `AX107` are the same SKU). Descriptions may differ between vendors; that is **not** a conflict.

A SKU is **in conflict** when the unit prices it has across the lists (all rows, all vendors) are not all equal. That includes one vendor listing the same SKU twice with different prices.

Write:
1. `/workspace/merged.csv` with header `sku,description,unit_price,vendors`: one row per SKU sorted by SKU; `description` from the first vendor in the order Alder, Birch, Cobalt that lists it;
   `unit_price` with 2 decimals, or empty if the SKU is in conflict; `vendors` the vendors that list it, sorted, joined by `;`.
2. `/workspace/conflicts.json`: an object mapping each conflicting SKU to an object `{vendor: [unit prices as 2-decimal strings, ascending, no repeats]}` for the vendors that list it. Report **exactly** the conflicting SKUs, no others.
