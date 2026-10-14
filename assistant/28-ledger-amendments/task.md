# Correct the ledger from amendment emails

`/workspace/ledger.csv` (txn_id, date, account, amount_cents, memo) is a ledger export; negative amounts are debits. `/workspace/emails/` holds 65 amendment emails
(`From:`, `Date:`, then the request in plain words), `/workspace/approvers.txt` lists the senders whose requests may be applied.

Rules:
1. Ignore every email from a sender not in `approvers.txt`.
2. Apply the remaining emails in ascending `Date:` order (all dates are distinct). Several emails can touch the same transaction; each works on the result of the earlier ones.
3. A request to disregard an earlier email ("disregard my email dated <timestamp>") cancels the email from that sender with exactly that `Date:`. The disregard email itself is not an amendment.
4. Kinds of amendment: *reverse/void* removes the transaction entirely; *set the amount* replaces its amount (signed, in dollars in the email, convert to cents); *move* changes its account;
   *flip the sign* multiplies the amount by -1; *duplicate pair* "keep the earlier-dated one": remove the transaction with the later ledger `date` (tie: the higher id).
   *split* "p% to A, the rest to B": the transaction becomes two parts; A's part is round-half-up of |amount| x p / 100 cents with the transaction's sign, B's part is the remainder (so the parts add up to the amount).
5. An email that names a transaction that is not in the ledger has no effect.

Write:
- `/workspace/balances.json`: an object mapping all 12 account ids to the corrected balance in integer cents (the sum of the account's amounts after all amendments).
- `/workspace/ignored_emails.json`: sorted array of the email paths (e.g. `emails/msg-007.txt`) that had no effect: from unapproved senders, cancelled by a disregard email, or naming a transaction not in the ledger.
  Disregard emails themselves are not listed.
