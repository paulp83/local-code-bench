# Index the models folder against the slug registry

`/workspace/models/` holds one folder per downloaded model. `/workspace/registry.json` lists slugs, each with a `repo` and a `quant`.

A folder belongs to a slug when the folder name and the string `<last path part of repo><quant>` are equal after lowercasing and deleting every
character that is not a letter or digit. Folders with no matching slug get an empty slug.

Write:

1. `/workspace/index.csv` with the header `folder,slug,size_bytes,files`, one row per folder, sorted by folder name (plain byte order).
   `size_bytes` is the sum of the file sizes under the folder, `files` is the count of files. Skip any file or directory whose name starts with `.` (and everything below it).
2. `/workspace/missing.json`: a JSON array, sorted, of registry slugs that have no folder.
