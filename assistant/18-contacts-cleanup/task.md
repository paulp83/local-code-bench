# Clean up a contacts export

`/workspace/contacts.csv` (name, email, phone, company) is messy. Write `/workspace/contacts_clean.csv` (same header) and `/workspace/summary.json`.

Normalisation:
- `name`: trim and collapse runs of spaces to one. `email`: trim, lowercase. `company`: trim.
- `phone` to E.164 (`+` and digits only): a number starting with `+` keeps its digits; one starting with `00` has the `00` replaced by `+`; a 10-digit number is a US/Canada number, prefix `+1`.
  Anything else is invalid and becomes empty. A valid E.164 number has 8 to 15 digits after the `+`. Count every non-empty input phone that ends up empty as an invalid phone.

Dedupe: rows are the same contact when their normalised emails are equal; a row with an empty email matches on normalised phone instead (if the phone is also empty it is its own contact).
Merge duplicates into the **first** row in file order; fill that row's empty fields from later duplicates (never overwrite a non-empty field).

Output order: contacts with an email first, sorted by email; then contacts without an email, in the order their first row appeared.

`summary.json`: `{"input_rows": n, "output_rows": n, "invalid_phones": n}`.
