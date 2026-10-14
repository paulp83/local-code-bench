# Reconcile payments against invoices

`/workspace/invoices.csv` (inv_id, customer, amount, due) and `/workspace/payments.csv` (pay_id, date, payer, amount, reference) are the inputs. Today is **2026-10-10**.

Apply payments in file order. A payment's `reference` lists zero or more invoice ids (separated by commas or spaces). Allocate the payment amount to the listed invoices **in the order listed**, each up to its remaining balance.
Whatever is left over (including a whole payment with no valid reference) becomes a credit on that payment.

Write:
1. `/workspace/reconcile.csv`, header `inv_id,status,paid,outstanding`, one row per invoice in file order, money with 2 decimals. Status: `paid` if outstanding is 0; otherwise `overdue` if the due date is before today; otherwise `partial` if something was paid; otherwise `unpaid`.
2. `/workspace/credits.csv`, header `pay_id,credit`, one row per payment with a non-zero credit, in payment order.
