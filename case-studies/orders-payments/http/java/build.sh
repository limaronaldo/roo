#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build/classes
jdbc=../../postgres/.deps/postgresql-42.7.14.jar
json=../.deps/jackson-core-2.22.3.jar
javac --release 21 --add-modules jdk.httpserver -Xlint:all -Werror \
    -cp "$jdbc:$json" -d build/classes ../../postgres/java/src/roo/postgres/*.java src/roo/postgres/*.java
java --add-modules jdk.httpserver -cp "build/classes:$jdbc:$json" roo.postgres.HttpUnitTests
