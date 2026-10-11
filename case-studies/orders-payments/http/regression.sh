#!/usr/bin/env bash
# Requalify the unchanged baselines, preserving their historical evidence.
set -euo pipefail
CASE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PG="$CASE/../postgres"
bash "$CASE/../verify.sh"
python3 "$PG/fetch_jdbc.py"
cargo fetch --manifest-path "$PG/rust/Cargo.toml" --locked
bash "$PG/java/build.sh"
cargo fmt --manifest-path "$PG/rust/Cargo.toml" -- --check
cargo test --manifest-path "$PG/rust/Cargo.toml" --locked --offline
cargo clippy --manifest-path "$PG/rust/Cargo.toml" --locked --offline --all-targets -- -D warnings
cargo build --manifest-path "$PG/rust/Cargo.toml" --locked --offline
cargo doc --manifest-path "$PG/rust/Cargo.toml" --locked --offline --no-deps
python3 "$PG/verify_rust_negative.py"
trap 'python3 "$PG/cluster.py" stop' EXIT
python3 "$PG/cluster.py" start
python3 "$PG/cluster.py" schema
python3 "$CASE/regression.py"
