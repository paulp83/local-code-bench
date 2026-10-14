# Plan an event and report what does not add up

    The inputs for a client dinner are in `/workspace`: `request.md`, `venue.json`, `rsvp.csv`, `catering.csv`, `quotes.csv`, `budget.md`, `schedule.md`, `invitation.md`, `holidays.txt`.

    Some of them contradict each other. You report an issue **only** for these checks, one entry per code that occurs (do not invent other issues, and do not report a code whose condition does not hold):

    - `CAPACITY`: the venue's maximum seated capacity is below the number of confirmed (`yes`) RSVP guests (count `guests` of each `yes` row, plus 1 for the guest themself).
- `TIME_MISMATCH`: a file (or two files) states the same event time in two forms that are not the same instant (all offsets are fixed: CET = UTC+1).
- `CATERING_SHORT`: the `mains` count in `catering.csv` is below the confirmed guest count.
- `OVER_BUDGET`: the sum of the quotes in `quotes.csv` is above the budget in `budget.md`.
- `WEEKDAY_MISMATCH`: a file names a weekday that does not match the ISO date next to it.
- `DUPLICATE_RSVP`: the same email address appears on more than one `yes` row in `rsvp.csv` (case-insensitive).
- `HOLIDAY_CLASH`: the event date is in `holidays.txt`.
- `NO_ACCESSIBLE_ENTRY`: `venue.json` has `step_free_entry` false while at least one confirmed guest has `needs_step_free` true.

    Write:
    1. `/workspace/issues.json`: a JSON array of objects `{"code": <one of the codes above>, "files": [<names of the input files that disagree, sorted>]}`, sorted by code. A code that does not occur is left out.
       For a rule that compares two files, list both files; a rule that is only about one file lists that file.
    2. `/workspace/plan.md` with exactly these lines (plus anything else you like): `Date: <YYYY-MM-DD>`, `Venue: <venue name>`, `Confirmed guests: <number>`, `Open issues: <number of entries in issues.json>`.
       Confirmed guests counts each `yes` row's guest plus its `guests` extras.
