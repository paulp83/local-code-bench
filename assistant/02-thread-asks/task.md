# List what the maintainer asked of @nina-t

`/workspace/thread.json` is an export of a GitHub issue thread (`comments`: id, author, created_at, body).
The maintainer's login is `owlmaint`.

Find every request the maintainer made to `nina-t`:

- Only comments authored by `owlmaint` that mention `@nina-t` count.
- Ignore any line that starts with `>` (a quote).
- A request is a sentence containing `please` (any case) or starting with `Can you` or `Could you`. Sentences end at `.`, `?`, `!` or a newline.
- An `@mention` at the start of a sentence is not part of it: drop it (and the space after it) before applying the rule above and before writing the sentence.
- A comment can hold several requests.

Write `/workspace/asks.json`: a JSON array, ordered by comment id, of objects
`{"comment_id": <int>, "requests": [<sentence text>, ...]}`, one object per qualifying comment, with each request sentence exactly as written
in the comment (a trailing `.`, `?` or `!` is optional; case is ignored when checked).
