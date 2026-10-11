#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
variant=${1:-composition}
case "$variant" in
    composition) entry=roo.postgres.HttpCompositionServer ;;
    template) entry=roo.postgres.HttpTemplateServer ;;
    *) echo 'Expected composition or template' >&2; exit 1 ;;
esac
exec java --add-modules jdk.httpserver \
    -cp 'build/classes:../../postgres/.deps/postgresql-42.7.14.jar:../.deps/jackson-core-2.22.3.jar' "$entry"
