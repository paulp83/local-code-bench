# Build an itinerary from bookings

`/workspace/bookings/` has one JSON file per flight leg with local departure/arrival times and each city's UTC offset. Legs are in file-name order.

Write `/workspace/itinerary.md` containing a markdown table with exactly this header: `| leg | flight | depart (local) | arrive (local) | duration | layover |`, then one row per leg:

- `leg`: 1, 2, ...
- `depart (local)` / `arrive (local)`: `<city> <YYYY-MM-DD HH:MM>` in that city's local time, as booked.
- `duration`: flight time computed from the UTC instants, formatted `<H>h <MM>m` (minutes always two digits, e.g. `7h 05m`).
- `layover`: time from this leg's arrival to the next leg's departure (UTC instants), same format; `-` on the last leg.

After the table add one line `Total travel time: <H>h <MM>m` from the first departure to the last arrival.
