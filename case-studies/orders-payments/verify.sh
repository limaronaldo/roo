#!/usr/bin/env bash
# Compile and test serially; adapters remain local and in memory.
set -euo pipefail
case_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd -- "$case_dir/../.." && pwd)"
cd "$project_dir"
bash "$case_dir/java/build.sh"
cargo fmt --manifest-path "$case_dir/rust/Cargo.toml" --all -- --check
cargo test --offline --manifest-path "$case_dir/rust/Cargo.toml"
cargo clippy --offline --manifest-path "$case_dir/rust/Cargo.toml" --all-targets -- -D warnings
cargo build --offline --manifest-path "$case_dir/rust/Cargo.toml" --bin roo-payments
RUSTDOCFLAGS="-D warnings" cargo doc --offline --manifest-path "$case_dir/rust/Cargo.toml" --no-deps
python3 "$case_dir/verify_rust_negative.py"
python3 "$case_dir/verify.py"
cargo test --offline --manifest-path "$project_dir/Cargo.toml"
printf '%s\n' 'PASS orders/payments case and original ROO laboratory'
