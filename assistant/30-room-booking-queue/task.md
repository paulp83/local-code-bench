# Process a queue of room requests

`/workspace/state/rooms.json` (name -> capacity) and `/workspace/state/bookings.json` (list of `id`, `room`, `who`, `date`, `start`, `end`) are the booking state.
`/workspace/requests/R01.txt` ... `R25.txt` are requests in plain words. Process them **in order R01 to R25**; each request sees the state left by the earlier ones.

Rules:
- Rooms are bookable 08:00 to 18:00 (a booking must start at or after 08:00 and end at or before 18:00). Two bookings in the same room on the same date conflict if their time ranges overlap; touching at an endpoint is fine.
- New bookings get ids `BK-007`, `BK-008`, ... in order of success (a rejected request uses no id).
- "Book <room>": reject `BAD_ROOM` (no such room), then `OUTSIDE_HOURS`, then `CONFLICT`, in that order of precedence.
- "A room for N people": reject `OUTSIDE_HOURS` first; otherwise the free room with the smallest capacity that is at least N (ties: alphabetical); `NO_ROOM` if none.
- "Cancel booking BK-xxx": `NOT_FOUND` if it does not exist now. "Cancel the booking created for request Rxx": `REF_NOT_BOOKED` if request Rxx was rejected, else as above.
- "Cancel all of <person>'s bookings on <date>": removes all of them (`NOT_FOUND` if none).
- "Move <person>'s booking on <date> to <room>": the same time in the new room. `BAD_ROOM`, then `NOT_FOUND` (the person has none that day), then `AMBIGUOUS` (more than one), then `CONFLICT` with other bookings (not itself).
- "Extend the booking made for request Rxx by <time>": `REF_NOT_BOOKED` if Rxx was rejected, `NOT_FOUND` if that booking has since been cancelled, then `OUTSIDE_HOURS`, then `CONFLICT`.

Write:
1. `/workspace/state/bookings.json`: the final state as a JSON list of the same objects (`id`, `room`, `who`, `date`, `start`, `end`), sorted by date, start, room, id.
2. `/workspace/log.csv` with header `request,outcome,detail` and one row per request R01..R25: `outcome` is `ok` or `rejected`; `detail` is the affected booking id (several ids joined by `;`, sorted) when ok, or the reason code when rejected.
