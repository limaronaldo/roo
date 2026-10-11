#!/usr/bin/env python3
"""Own one private, loopback-only PostgreSQL cluster for synthetic ROO tests."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys

CASE = Path(__file__).resolve().parent
RUNTIME = CASE / ".runtime"
CONFIG = RUNTIME / "config.json"
MARKER = RUNTIME / "ROO_OWNED_CLUSTER"
MARKER_TEXT = "ROO local synthetic PostgreSQL cluster v1\n"


def utility_environment():
    """Prevent libpq variables from redirecting or configuring owned utilities."""
    env = {key: value for key, value in os.environ.items() if not key.upper().startswith("PG")}
    env.update(PGPASSFILE=os.devnull, PGSERVICEFILE=os.devnull, PGCONNECT_TIMEOUT="5")
    return env


def checked(command, **options):
    result = subprocess.run(command, env=utility_environment(), text=True,
                            capture_output=True, timeout=45, **options)
    if result.returncode:
        raise RuntimeError(f"{Path(command[0]).name} failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def binary_directory():
    configured = os.environ.get("ROO_PG_BINDIR")
    executable = shutil.which("pg_ctl")
    directory = Path(configured) if configured else Path(executable).resolve().parent if executable else None
    # Homebrew libpq supplies client tools, including pg_ctl, without postgres.
    if not configured and (directory is None or not (directory / "postgres").is_file()):
        directory = next((p for p in (
            Path("/opt/homebrew/opt/postgresql@18/bin"),
            Path("/usr/local/opt/postgresql@18/bin"),
        ) if (p / "postgres").is_file()), directory)
    if directory is None or any(not (directory / name).is_file() for name in (
        "postgres", "initdb", "pg_ctl", "psql", "createdb",
    )):
        raise RuntimeError("Install PostgreSQL separately or set ROO_PG_BINDIR to its bin directory")
    return directory.resolve()


def configuration(create=False):
    if CONFIG.exists():
        if not MARKER.exists() or MARKER.read_text() != MARKER_TEXT:
            raise RuntimeError("Refusing to operate on an unmarked cluster")
        config = json.loads(CONFIG.read_text())
        if Path(config["data"]).resolve() != (RUNTIME / "data").resolve():
            raise RuntimeError("Owned cluster path mismatch")
        if config["host"] != "127.0.0.1" or config["database"] != "roo_test" or config["user"] != "roo_test":
            raise RuntimeError("Owned cluster configuration mismatch")
        return config
    if not create:
        raise RuntimeError("Run cluster.py start first")
    directory = binary_directory()
    if RUNTIME.exists() and any(p != MARKER for p in RUNTIME.iterdir()):
        raise RuntimeError("Refusing to initialize a nonempty unconfigured runtime directory")
    if MARKER.exists() and MARKER.read_text() != MARKER_TEXT:
        raise RuntimeError("Refusing to initialize an unmarked runtime directory")
    RUNTIME.mkdir(mode=0o700, parents=True, exist_ok=True)
    RUNTIME.chmod(0o700)
    MARKER.write_text(MARKER_TEXT)
    with socket.socket() as candidate:
        candidate.bind(("127.0.0.1", 0))
        port = candidate.getsockname()[1]
    data = RUNTIME / "data"
    output = checked([
        str(directory / "initdb"), "-D", str(data), "--username=roo_test",
        "--auth=trust", "--encoding=UTF8", "--locale=C",
    ])
    (RUNTIME / "initdb.log").write_text(output)
    with (data / "postgresql.conf").open("a") as config_file:
        config_file.write(
            "\n# ROO synthetic test cluster; never bind a public interface.\n"
            "listen_addresses = '127.0.0.1'\n"
            f"port = {port}\n"
            "unix_socket_directories = ''\n"
            "max_connections = 40\nshared_buffers = '16MB'\n"
            "fsync = on\nsynchronous_commit = on\nfull_page_writes = on\n"
        )
    config = {"bindir": str(directory), "data": str(data), "host": "127.0.0.1",
              "port": port, "database": "roo_test", "user": "roo_test"}
    CONFIG.write_text(json.dumps(config, indent=2) + "\n")
    return config


def environment(config=None):
    config = configuration() if config is None else config
    return {"ROO_PG_HOST": config["host"], "ROO_PG_PORT": str(config["port"]),
            "ROO_PG_DATABASE": config["database"], "ROO_PG_USER": config["user"]}


def endpoint_guard(config=None):
    config = configuration() if config is None else config
    path = config["data"].replace("'", "''")
    return ("DO $roo_guard$ BEGIN IF current_setting('data_directory') <> '" + path
            + "' THEN RAISE EXCEPTION 'Refusing an endpoint outside the owned cluster'; "
              "END IF; END $roo_guard$;")


def sql(query, *, database=None):
    config = configuration()
    return checked([
        str(Path(config["bindir"]) / "psql"), "-XAtq", "-v", "ON_ERROR_STOP=1",
        "-h", config["host"], "-p", str(config["port"]), "-U", config["user"],
        "-d", database or config["database"], "-c", endpoint_guard(config) + query,
    ])


def running(config):
    result = subprocess.run([
        str(Path(config["bindir"]) / "pg_ctl"), "-D", config["data"], "status",
    ], env=utility_environment(), capture_output=True, timeout=10)
    return result.returncode == 0


def start():
    config = configuration(create=True)
    if not running(config):
        checked([str(Path(config["bindir"]) / "pg_ctl"), "-D", config["data"],
                 "-l", str(RUNTIME / "server.log"), "-w", "-t", "30", "start"])
    present = sql("SELECT 1 FROM pg_database WHERE datname='roo_test'", database="postgres").strip()
    if present != "1":
        checked([str(Path(config["bindir"]) / "createdb"), "-h", config["host"],
                 "-p", str(config["port"]), "-U", config["user"], "roo_test"])
    return config


def stop(mode="fast"):
    config = configuration()
    if running(config):
        checked([str(Path(config["bindir"]) / "pg_ctl"), "-D", config["data"],
                 "-w", "-t", "30", "-m", mode, "stop"])


def apply_schema():
    config = configuration()
    schema = CASE / "schema.sql"
    digest = hashlib.sha256(schema.read_bytes()).hexdigest()
    if "schema_sha256" in config:
        if config["schema_sha256"] != digest:
            raise RuntimeError("Installed schema differs; preserve this cluster and plan an explicit migration")
        return
    checked([str(Path(config["bindir"]) / "psql"), "-X", "-v", "ON_ERROR_STOP=1",
             "-h", config["host"], "-p", str(config["port"]), "-U", config["user"],
             "-d", config["database"], "-c", endpoint_guard(config), "-f", str(schema)])
    config["schema_sha256"] = digest
    CONFIG.write_text(json.dumps(config, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "stop", "crash-restart", "status", "env", "schema"))
    action = parser.parse_args().action
    if action == "start":
        start()
        print("Owned PostgreSQL cluster started on loopback")
    elif action == "stop":
        stop()
        print("Owned PostgreSQL cluster stopped; test data retained")
    elif action == "crash-restart":
        stop("immediate")
        start()
        print("Owned PostgreSQL cluster recovered after immediate shutdown")
    elif action == "schema":
        apply_schema()
        print("Shared schema applied to owned test database")
    elif action == "env":
        print(json.dumps(environment(), sort_keys=True))
    else:
        config = configuration()
        print(json.dumps({"running": running(config), "environment": environment(config)}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(f"Cluster failure: {error}", file=sys.stderr)
        sys.exit(1)
