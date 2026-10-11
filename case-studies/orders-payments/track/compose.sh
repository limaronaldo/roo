#!/usr/bin/env bash
# Rebuild edited sources; copy allowlisted evidence out of one disposable container.
set -euo pipefail
TRACK="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$TRACK/../../.." && pwd)"
mode="${1:-qualify}"
exercise="${2:-all}"
variant="${3:-all}"
usage='Usage: compose.sh [qualify | starter|solution [e1..e6|all] [java-composition|java-inheritance|rust|all]]'
if [[ "${1:-}" == --help ]]; then echo "$usage"; exit 0; fi
if [[ $# -gt 3 || ! "$mode" =~ ^(qualify|starter|solution)$ || ! "$exercise" =~ ^(e[1-6]|all)$ || ! "$variant" =~ ^(java-composition|java-inheritance|rust|all)$ || ( "$mode" == qualify && $# -gt 1 ) ]]; then
    echo "$usage" >&2; exit 2
fi
run_id="$(date -u +%Y%m%dt%H%M%Sz)-$$-${RANDOM}"
project="roo-track-$run_id"
container="$project-runner"
evidence="$ROOT/artifacts/roo-track/$run_id"
mkdir -p "$evidence"
export ROO_TRACK_IMAGE="roo-track:$run_id"
compose=(docker compose --project-name "$project" --project-directory "$ROOT" -f "$ROOT/compose.yaml")
owned=false
exported=false
cleanup() {
    status=$?
    trap - EXIT INT TERM
    set +e
    if [[ "$owned" == true ]]; then
        docker stop --time 45 "$container" >/dev/null 2>&1
        if [[ "$exported" != true ]]; then
            docker logs "$container" > "$evidence/run.log" 2>&1
            docker cp "$container:/workspace/evidence/." "$evidence/" 2> "$evidence/export.log"
            copy_status=$?
            if [[ $copy_status -ne 0 && $status -eq 0 ]]; then status=$copy_status; fi
        fi
        docker rm -v "$container" > "$evidence/cleanup.log" 2>&1
        cleanup_status=$?
        printf '%s\n' "$cleanup_status" > "$evidence/cleanup-exit-code.txt"
        if [[ $cleanup_status -ne 0 && $status -eq 0 ]]; then status=$cleanup_status; fi
    fi
    printf '%s\n' "$status" > "$evidence/wrapper-exit-code.txt"
    printf 'Evidence: %s\n' "$evidence"
    exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
printf '%q ' bash case-studies/orders-payments/track/compose.sh "$@" > "$evidence/host-command.txt"
printf '\n' >> "$evidence/host-command.txt"
# Portable content checksums preserve the edited source identity even if build fails.
# SHA-256 for the baked source is additionally recorded inside successful images.
(
    cd "$ROOT"
    find case-studies/orders-payments -type d \( -name target -o -name build -o -name .runtime -o -name .deps -o -name __pycache__ -o -name .git -o -name research -o -name artifacts -o -name .ssh -o -name .aws -o -name .config \) -prune -o \
        -type f ! -name '.env*' ! -name '*credentials*' ! -name '*secret*' ! -name '*.pem' ! -name '*.key' ! -name '*.pyc' -exec cksum '{}' \;
) > "$evidence/host-source-checksums.txt"
docker version > "$evidence/docker-version.txt" 2>&1
docker compose version >> "$evidence/docker-version.txt" 2>&1
set +e
"${compose[@]}" build --progress plain track 2>&1 | tee "$evidence/build.log"
build_status=${PIPESTATUS[0]}
set -e
printf '%s\n' "$build_status" > "$evidence/build-exit-code.txt"
if [[ $build_status -ne 0 ]]; then exit "$build_status"; fi
args=("$mode")
if [[ "$mode" != qualify ]]; then args+=("$exercise" "$variant"); fi
# Set ownership before creation so an interrupted create remains scoped for cleanup.
owned=true
"${compose[@]}" run --detach --no-deps --name "$container" track "${args[@]}" > "$evidence/container-id.txt"
docker inspect --format '{{.Image}}' "$container" > "$evidence/image-id.txt"
docker inspect --format '{"container_id":{{json .Id}},"image_id":{{json .Image}},"running":{{json .State.Running}},"user":{{json .Config.User}},"network_mode":{{json .HostConfig.NetworkMode}},"mounts":{{json .Mounts}},"port_bindings":{{json .HostConfig.PortBindings}},"ports":{{json .NetworkSettings.Ports}},"cap_drop":{{json .HostConfig.CapDrop}},"privileged":{{json .HostConfig.Privileged}},"security_opt":{{json .HostConfig.SecurityOpt}}}' "$container" > "$evidence/container-isolation.json"
isolation_ok="$(docker inspect --format '{{and (eq .Config.User "10001:10001") (eq .HostConfig.NetworkMode "none") (eq (len .Mounts) 0) (eq (len .HostConfig.PortBindings) 0) (not .HostConfig.Privileged) (eq (len .HostConfig.CapDrop) 1) (eq (index .HostConfig.CapDrop 0) "ALL") (eq (len .HostConfig.SecurityOpt) 1) (eq (index .HostConfig.SecurityOpt 0) "no-new-privileges:true")}}' "$container")"
if [[ "$isolation_ok" != true ]]; then
    printf '1\n' > "$evidence/isolation-check-exit-code.txt"
    echo 'Container isolation check failed; inspect the retained evidence.' >&2
    exit 1
fi
printf '0\n' > "$evidence/isolation-check-exit-code.txt"
docker image inspect "$(cat "$evidence/image-id.txt")" --format '{{.Os}}/{{.Architecture}}' > "$evidence/image-platform.txt"
if [[ "${ROO_REQUIRE_AMD64_IMAGE:-0}" == 1 && "$(cat "$evidence/image-platform.txt")" != linux/amd64 ]]; then
    echo 'Hosted qualification requires a Linux AMD64 image.' >&2
    exit 1
fi
docker wait "$container" > "$evidence/container-exit-code.txt"
docker logs "$container" 2>&1 | tee "$evidence/run.log"
set +e
docker cp "$container:/workspace/evidence/." "$evidence/" 2> "$evidence/export.log"
copy_status=$?
set -e
exported=true
printf '%s\n' "$copy_status" > "$evidence/export-exit-code.txt"
test_status="$(cat "$evidence/container-exit-code.txt")"
if [[ "$test_status" -ne 0 ]]; then exit "$test_status"; fi
exit "$copy_status"
