#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build/classes build/negative
mapfile_compat=()
while IFS= read -r file; do mapfile_compat+=("$file"); done < <(find src -name '*.java' -print | sort)
javac --release 21 -Xlint:all -Werror -d build/classes "${mapfile_compat[@]}"
java -cp build/classes roo.payments.UnitTests
for sample in PrivateMutation OverrideAlgorithm; do
    if javac --release 21 -Xlint:all -Werror -cp build/classes -d build/negative "negative/$sample.java" >"build/negative/$sample.stdout" 2>"build/negative/$sample.stderr"; then
        echo "Negative sample unexpectedly compiled: $sample" >&2
        exit 1
    fi
    case "$sample" in
        PrivateMutation) grep -q 'private access' "build/negative/$sample.stderr" ;;
        OverrideAlgorithm) grep -q 'overridden method is final' "build/negative/$sample.stderr" ;;
    esac
done
echo "Java negative checks: private mutation and final algorithm rejected"
