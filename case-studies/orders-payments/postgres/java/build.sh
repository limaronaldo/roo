#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build/classes build/negative
sources=(src/roo/postgres/*.java)
jar=../.deps/postgresql-42.7.14.jar
javac --release 21 -Xlint:all -Werror -cp "$jar" -d build/classes "${sources[@]}"
java -cp "build/classes:$jar" roo.postgres.UnitTests
for sample in PrivateMutation OverrideAlgorithm; do
    if javac -J-Duser.language=en --release 21 -Xlint:all -Werror -cp "build/classes:$jar" -d build/negative "negative/$sample.java" >"build/negative/$sample.stdout" 2>"build/negative/$sample.stderr"; then
        echo "Negative sample unexpectedly compiled: $sample" >&2
        exit 1
    fi
    case "$sample" in
        PrivateMutation) grep -q 'private access' "build/negative/$sample.stderr" ;;
        OverrideAlgorithm) grep -q 'overridden method is final' "build/negative/$sample.stderr" ;;
    esac
done
echo "Java PostgreSQL compiler negatives: private fields and final algorithm rejected"
