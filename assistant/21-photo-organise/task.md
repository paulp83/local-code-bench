# Organise photos by capture date

`/workspace/photos/` has `IMG_xxxx.jpg` files, each with a sidecar `IMG_xxxx.json` (`taken`: local ISO timestamp, `camera`).

Move every photo into `/workspace/organised/<YYYY>/<MM>/` and rename it `<YYYYMMDD>_<HHMMSS>_<camera lowercased>.jpg` from its sidecar. If two photos get the same name,
the one with the lower original number keeps the plain name and the next ones get `-2`, `-3` before the extension. Move each sidecar next to its photo with the same new stem and `.json`.
Nothing may be left in `photos/`. Write `/workspace/manifest.csv` with header `old,new` (paths relative to `/workspace`, `.jpg` files only, sorted by `old`).
