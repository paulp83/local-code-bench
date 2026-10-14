#!/usr/bin/env bash
# usage: ./fetch.sh <id>   prints the item JSON on stdout. Reads the offline mirror in .remote/.
set -u
here="$(cd "$(dirname "$0")" && pwd)"
id="${1:?usage: fetch.sh <id>}"
mkdir -p "$here/.remote/.state"
echo "$id" >> "$here/.remote/.state/calls.log"
n=$(grep -cx "$id" "$here/.remote/.state/calls.log")
f="$here/.remote/items/$id.json"
[ -f "$f" ] || { echo "error: 404 no such item $id" >&2; exit 4; }
case "$id" in
  i04|i11|i17) if [ "$n" -le 1 ]; then echo "error: 503 service unavailable (transient), please retry" >&2; exit 75; fi ;;
  i09) if [ "$n" -le 1 ]; then head -c $(( $(wc -c < "$f") / 2 )) "$f"; exit 0; fi ;;
esac
cat "$f"
