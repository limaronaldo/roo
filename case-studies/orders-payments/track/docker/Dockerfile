# Index pins cover amd64 and arm64. No PostgreSQL image VOLUME is inherited.
FROM postgres:18.6-bookworm@sha256:afc7e2d441324c0388fa80c3d24f733b4194a4eb7f47dd8ee2b08eb1a24a647c AS postgres
RUN mkdir /roo-pg-lib && find /usr/lib -name 'libpq.so*' -exec cp -L '{}' /roo-pg-lib/ \;
FROM eclipse-temurin:21-jdk-jammy@sha256:e0c60c487345d1dc9d0fc7b6f0496f3cc941e5132e09296cc17a6decc71b902b AS java
FROM rust:1.96.0-bookworm@sha256:5e2214abe154fe26e39f64488952e5c991eeed1d6d6da7cc8381ae83927f0cfc
# Debian packages deliberately follow bookworm security updates; see DOCKER.md.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 bash ca-certificates libicu72 libldap-2.5-0 liblz4-1 libpam0g \
    libssl3 libxml2 libxslt1.1 libzstd1 zlib1g libreadline8 \
    libgssapi-krb5-2 libkrb5-3 libsasl2-2 libnuma1 libatomic1 liburing2 \
    libselinux1 libsystemd0 libuuid1 tzdata \
    libfontconfig1 libfreetype6 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 roo && useradd --uid 10001 --gid roo --create-home roo
COPY --from=postgres /usr/lib/postgresql/18/ /usr/lib/postgresql/18/
COPY --from=postgres /usr/share/postgresql/18/ /usr/share/postgresql/18/
COPY --from=postgres /usr/share/postgresql/postgresql.conf.sample /usr/share/postgresql/postgresql.conf.sample
COPY --from=postgres /roo-pg-lib/ /usr/local/lib/
COPY --from=java /opt/java/openjdk/ /opt/java/openjdk/
ENV JAVA_HOME=/opt/java/openjdk \
    ROO_PG_BINDIR=/usr/lib/postgresql/18/bin \
    LD_LIBRARY_PATH=/usr/local/lib \
    PATH=/opt/java/openjdk/bin:/usr/lib/postgresql/18/bin:/usr/local/cargo/bin:/usr/local/bin:/usr/bin:/bin \
    CARGO_NET_OFFLINE=true \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /workspace
COPY --chown=roo:roo case-studies/orders-payments/ case-studies/orders-payments/
RUN /sbin/ldconfig && chown roo:roo /workspace /usr/local/cargo /usr/local/rustup \
    && chmod -R a+rX /usr/local/rustup
USER 10001:10001
# Check the copied PostgreSQL runtime closure before fetching dependencies.
RUN failures=0; for binary in postgres initdb pg_ctl psql createdb; do \
      printf 'Runtime dependencies: %s\n' "$binary"; \
      dependencies="$(ldd /usr/lib/postgresql/18/bin/"$binary" 2>&1)" || failures=1; \
      printf '%s\n' "$dependencies"; \
      if printf '%s\n' "$dependencies" | grep 'not found'; then failures=1; fi; \
      if printf '%s\n' "$dependencies" | grep -q 'libpq.so.5 =>'; then \
        if ! printf '%s\n' "$dependencies" | grep -q 'libpq.so.5 => /usr/local/lib/libpq.so.5 '; then failures=1; fi; \
      elif [ "$binary" = psql ]; then failures=1; fi; \
    done; exit "$failures"
RUN python3 -c "import ctypes; pq = ctypes.CDLL('libpq.so.5'); pq.PQlibVersion.restype = ctypes.c_int; version = pq.PQlibVersion(); assert version == 180006, version; getattr(pq, 'PQsendPipelineSync'); print('PASS pinned libpq runtime:', version)"
RUN LD_BIND_NOW=1 psql --version
# Fetch only locked graphs and SHA-verified JARs while networking is available.
RUN for manifest in \
      case-studies/orders-payments/rust/Cargo.toml \
      case-studies/orders-payments/postgres/rust/Cargo.toml \
      case-studies/orders-payments/http/rust/Cargo.toml \
      case-studies/orders-payments/track/rust/starter/Cargo.toml \
      case-studies/orders-payments/track/rust/solution/Cargo.toml; do \
      CARGO_NET_OFFLINE=false cargo fetch --locked --manifest-path "$manifest" || exit; \
    done \
    && python3 case-studies/orders-payments/postgres/fetch_jdbc.py \
    && python3 case-studies/orders-payments/http/fetch_json.py \
    && java -version && javac -version && rustc --version && cargo --version \
    && postgres --version && initdb --version && psql --version
ENTRYPOINT ["bash", "/workspace/case-studies/orders-payments/track/docker/entrypoint.sh"]
CMD ["qualify"]
