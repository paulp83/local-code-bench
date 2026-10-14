# Move a run directory to cold storage

Move `/workspace/hot/runs-2026-08` to `/workspace/cold/runs-2026-08` and verify the move.

- `*.tmp` files are scratch: delete them, do not move them.
- Symbolic links must stay symbolic links with the same link text (do not follow or copy them).
- After the move `/workspace/hot/runs-2026-08` must not exist.
- Write `/workspace/cold/runs-2026-08.sha256` in `sha256sum` format (`<hash>  <path>`, two spaces) for every regular file in the moved tree,
  paths relative to `cold/runs-2026-08`, sorted by path (plain byte order). Symlinks are not listed there.
- Write `/workspace/cold/runs-2026-08.links.txt` with one line `<relative path> -> <link text>` per symlink, sorted by path.
