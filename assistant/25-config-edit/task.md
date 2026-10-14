# Edit a settings file

Edit `/workspace/node.ini` in place:

1. `[server] port` becomes `8090`.
2. `[logging] level` becomes `debug`, and the `rotate` key is removed.
3. `[gpu] mem_fraction` becomes `0.85`.
4. Add a new section `[metrics]` with `enabled = true` and `port = 9100`.

Everything else (other keys, values, comments, section order) must stay exactly as it is.
