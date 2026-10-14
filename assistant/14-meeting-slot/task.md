# Find a meeting slot for three people

`/workspace/calendars/` has one `.ics` file per person (`ana`, `bo`, `chen`) listing busy events in UTC. Find the **earliest** 45-minute slot that works for all three and write it
to `/workspace/meeting.ics` as one `VEVENT` with `DTSTART`, `DTEND` (both UTC, `YYYYMMDDTHHMMSSZ`) and `SUMMARY:Sync`.

Rules:
- Candidate starts are on a 15-minute grid in UTC, from 2026-10-12T00:00Z up to but not including 2026-10-15T00:00Z.
- Fixed UTC offsets (no daylight saving): ana UTC-1, bo UTC+1, chen UTC+3.
- Each person's local working hours are 09:00 to 17:30, Monday to Friday, judged on **their** local clock; the whole slot must fit inside.
- Local lunch 12:00 to 13:00 is blocked: the slot must not overlap it.
- The slot must leave a gap of at least 15 minutes before and after every busy event of every person (it may not overlap one either).
