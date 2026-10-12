#!/usr/bin/env bash
# Qualify each compiler and the private database serially.
set -euo pipefail
CASE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PG="$CASE/../postgres"
python3 "$PG/fetch_jdbc.py"
python3 "$CASE/fetch_json.py"
cargo fetch --manifest-path "$CASE/rust/Cargo.toml" --locked
bash "$CASE/java/build.sh"
cargo fmt --manifest-path "$CASE/rust/Cargo.toml" -- --check
cargo test --manifest-path "$CASE/rust/Cargo.toml" --locked --offline
cargo clippy --manifest-path "$CASE/rust/Cargo.toml" --locked --offline --all-targets -- -D warnings
cargo build --manifest-path "$CASE/rust/Cargo.toml" --locked --offline
cargo doc --manifest-path "$CASE/rust/Cargo.toml" --locked --offline --no-deps
# Never stop another cluster: the reused helper checks its private ownership marker.
trap 'python3 "$PG/cluster.py" stop' EXIT
python3 "$PG/cluster.py" start
python3 "$PG/cluster.py" schema
python3 "$CASE/verify.py"
python3 "$CASE/verify_authorization.py"
