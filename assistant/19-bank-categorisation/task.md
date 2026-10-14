# Monthly totals per category

`/workspace/transactions.csv` (date, description, amount; negative = money out) and `/workspace/rules.csv` (pattern, category; **ordered**) are the inputs.

Write `/workspace/budget.csv` with header `month,category,total`, one row per (month, category) that has at least one transaction, sorted by month then category (byte order).
`month` is `YYYY-MM`; `total` is the **signed** sum of amounts, 2 decimals.

Rules:
1. **Transfers**: descriptions starting with `TRANSFER ` are moves between own accounts; ignore them entirely.
2. **Splits**: a description starting with `SPLIT:` ends with `groceries=<x>;household=<y>`. Do not use `rules.csv` for it; add `-x` to category `groceries` and `-y` to `household` (the row's amount is just their negated sum).
3. **Everything else**: the category of the **first** rule (top to bottom) whose pattern is contained in the description (case-insensitive); `uncategorised` if none.
