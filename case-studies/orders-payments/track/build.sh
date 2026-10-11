#!/usr/bin/env bash
# Serial compilation; cached dependency helpers verify pinned artifacts.
set -euo pipefail
TRACK="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CASE="$TRACK/.."
if [[ "${1:-}" == "--help" ]]; then
    echo "Usage: build.sh [starter|solution|all] (default: all)"
    echo "Build track executables and existing PostgreSQL/HTTP boundary runners serially."
    exit 0
fi
source_set="${1:-all}"
if [[ "$#" -gt 1 || ! "$source_set" =~ ^(starter|solution|all)$ ]]; then
    echo "Usage: build.sh [starter|solution|all]" >&2
    exit 2
fi
sources=(starter solution)
if [[ "$source_set" != all ]]; then sources=("$source_set"); fi
for source in "${sources[@]}"; do
    classes="$TRACK/java/build/$source/classes"
    mkdir -p "$classes"
    files=()
    while IFS= read -r file; do files+=("$file"); done < <(
        find "$CASE/java/src" "$TRACK/java/common" "$TRACK/java/$source" -name '*.java' -type f -print | sort
    )
    javac --release 21 -Xlint:all -Werror -d "$classes" "${files[@]}"
    cargo build --manifest-path "$TRACK/rust/$source/Cargo.toml" --offline
 done
python3 "$CASE/postgres/fetch_jdbc.py"
python3 "$CASE/http/fetch_json.py"
bash "$CASE/postgres/java/build.sh"
cargo build --manifest-path "$CASE/postgres/rust/Cargo.toml" --locked --offline
bash "$CASE/http/java/build.sh"
cargo build --manifest-path "$CASE/http/rust/Cargo.toml" --locked --offline
echo "PASS serial track and boundary builds"
