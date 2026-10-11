#!/usr/bin/env bash
# Run serially: one compiler or database qualification phase at a time.
set -euo pipefail
CASE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$CASE/fetch_jdbc.py"
cargo fetch --manifest-path "$CASE/rust/Cargo.toml" --locked
bash "$CASE/java/build.sh"
cargo fmt --manifest-path "$CASE/rust/Cargo.toml" -- --check
cargo test --manifest-path "$CASE/rust/Cargo.toml" --locked --offline
cargo clippy --manifest-path "$CASE/rust/Cargo.toml" --locked --offline --all-targets -- -D warnings
cargo build --manifest-path "$CASE/rust/Cargo.toml" --locked --offline
cargo doc --manifest-path "$CASE/rust/Cargo.toml" --locked --offline --no-deps
python3 "$CASE/verify_rust_negative.py"
# Even on a failed qualification, stop only the marked private cluster.
trap 'python3 "$CASE/cluster.py" stop' EXIT
python3 "$CASE/cluster.py" start
python3 "$CASE/cluster.py" schema
python3 "$CASE/verify.py"
