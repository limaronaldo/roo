#!/usr/bin/env bash
set -euo pipefail
TRACK="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
if [[ "${1:-}" == "--help" ]]; then
    echo "Usage: verify.sh"
    echo "Build serially, require all independent starter RED groups, then qualify the full solution."
    exit 0
fi
if [[ "$#" -ne 0 ]]; then echo "Usage: verify.sh" >&2; exit 2; fi
bash "$TRACK/build.sh"
python3 "$TRACK/verify.py" --source starter --expect-incomplete
# Preserve both current receipts without touching historical research evidence.
cp "$TRACK/.runtime/last-run.json" "$TRACK/.runtime/starter-last-run.json"
python3 "$TRACK/verify.py" --source solution
cp "$TRACK/.runtime/last-run.json" "$TRACK/.runtime/solution-last-run.json"
python3 "$TRACK/check_independence.py"
