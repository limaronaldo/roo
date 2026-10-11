#!/usr/bin/env bash
set -euo pipefail
cd /workspace
TRACK=case-studies/orders-payments/track
mkdir -p evidence
mode="${1:-qualify}"
exercise="${2:-all}"
variant="${3:-all}"
if [[ $# -gt 3 || ! "$mode" =~ ^(qualify|starter|solution)$ || ! "$exercise" =~ ^(e[1-6]|all)$ || ! "$variant" =~ ^(java-composition|java-inheritance|rust|all)$ || ( "$mode" == qualify && $# -gt 1 ) ]]; then
    echo 'Usage: compose.sh [qualify | starter|solution [e1..e6|all] [java-composition|java-inheritance|rust|all]]' >&2
    exit 2
fi
finish() {
    status=$?
    trap - EXIT INT TERM
    set +e
    python3 "$TRACK/docker/evidence.py" collect
    export_status=$?
    printf '%s\n' "$status" > evidence/test-exit-code.txt
    printf '%s\n' "$export_status" > evidence/collection-exit-code.txt
    if [[ $status -eq 0 && $export_status -ne 0 ]]; then status=$export_status; fi
    exit "$status"
}
trap finish EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
printf '%q ' "$0" "$@" > evidence/command.txt
printf '\n' >> evidence/command.txt
python3 "$TRACK/docker/evidence.py" identity
{ java -version; javac -version; rustc --version; cargo --version; python3 --version; postgres --version; uname -m; } > evidence/tool-versions.txt 2>&1
dpkg-query -W -f='${Package}\t${Version}\n' > evidence/os-packages.tsv
if [[ "$mode" == qualify ]]; then
    bash "$TRACK/verify.sh"
else
    bash "$TRACK/build.sh" "$mode"
    python3 "$TRACK/verify.py" --source "$mode" --exercise "$exercise" --variant "$variant"
fi
