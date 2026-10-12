package roo.postgres;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Map;
import java.util.Properties;
import java.util.Set;

/** Structured loopback configuration and retry of known-aborted short transactions only. */
final class Database {
    private final String port;
    private final String worker;
    private final String gatePoint;
    private final Long gateLock;
    private final Authorization authorization;
    record Authorization(String scope, String principal, Operation operation) {
        Authorization {
            if (scope == null || !scope.matches("[A-Za-z0-9_]{1,96}")
                || principal == null || !principal.matches("[A-Za-z0-9_]{1,32}") || operation == null)
                throw new IllegalArgumentException("Invalid authorization context");
        }
    }
    static final class Forbidden extends RuntimeException {
        private static final long serialVersionUID = 1L;
        Forbidden() { super("Access forbidden"); }
    }
    Database(Map<String, String> env) {
        authorization = null;
        if (!"127.0.0.1".equals(env.get("ROO_PG_HOST")) || !"roo_test".equals(env.get("ROO_PG_DATABASE"))
            || !"roo_test".equals(env.get("ROO_PG_USER"))) throw new IllegalArgumentException("Invalid dedicated database configuration");
        port = env.get("ROO_PG_PORT");
        if (port == null || !port.matches("[0-9]{1,5}") || Integer.parseInt(port) < 1 || Integer.parseInt(port) > 65535) throw new IllegalArgumentException("Invalid database port");
        worker = env.getOrDefault("ROO_WORKER_ID", "java");
        if (!worker.matches("[A-Za-z0-9_]{1,32}")) throw new IllegalArgumentException("Invalid worker identity");
        gatePoint = env.get("ROO_GATE_POINT"); String key = env.get("ROO_GATE_LOCK");
        if ((gatePoint == null) != (key == null)) throw new IllegalArgumentException("Incomplete gate configuration");
        if (gatePoint != null && !Set.of("inside_prepare", "after_prepare", "after_effect", "after_finalize", "before_delivery", "after_delivery").contains(gatePoint)) throw new IllegalArgumentException("Invalid gate point");
        try { gateLock = key == null ? null : Long.valueOf(key); }
        catch (NumberFormatException bad) { throw new IllegalArgumentException("Invalid gate key"); }
        if (gateLock != null && (gateLock <= 0 || !key.matches("[0-9]+"))) throw new IllegalArgumentException("Invalid gate key");
    }
    private Database(Database source, Authorization authorization) {
        port = source.port; worker = source.worker; gatePoint = source.gatePoint; gateLock = source.gateLock;
        this.authorization = authorization;
    }
    Database authorized(String scope, String principal, Operation operation) {
        if (authorization != null) throw new IllegalStateException("Authorization context already bound");
        return new Database(this, new Authorization(scope, principal, operation));
    }
    Operation operation() { return authorization == null ? null : authorization.operation(); }
    void requireOperation(Operation expected) {
        if (authorization != null && (expected == null || authorization.operation() != expected)) throw new Forbidden();
    }
    Operation requireOneOf(Operation... allowed) {
        if (authorization == null) return allowed[0];
        for (Operation operation : allowed) if (authorization.operation() == operation) return operation;
        throw new Forbidden();
    }
    void requireUnbound() { if (authorization != null) throw new Forbidden(); }
    void checkScope(String scope) {
        if (authorization != null && !authorization.scope().equals(scope)) throw new Forbidden();
    }
    private void authorize(Connection c, String scope) throws SQLException {
        checkScope(scope);
        if (authorization == null) return;
        try (PreparedStatement p = c.prepareStatement("SELECT allowed FROM roo_authorization.operation_grants WHERE scope=? AND principal=? AND operation=? FOR SHARE")) {
            p.setString(1, scope); p.setString(2, authorization.principal()); p.setString(3, authorization.operation().token());
            try (ResultSet r = p.executeQuery()) { if (!r.next() || !r.getBoolean(1)) throw new Forbidden(); }
        }
    }
    // Detached advisory observation: no retained policy lock or authority for a later transaction.
    boolean observeAuthorization(String scope, String principal, Operation operation) throws SQLException {
        new Authorization(scope, principal, operation);
        checkScope(scope);
        if (operation == null) throw new IllegalArgumentException("Invalid authorization operation");
        if (authorization != null && (!authorization.principal().equals(principal) || authorization.operation() != operation)) throw new Forbidden();
        try (Connection c = open(false); PreparedStatement p = c.prepareStatement("SELECT allowed FROM roo_authorization.operation_grants WHERE scope=? AND principal=? AND operation=?")) {
            p.setString(1, scope); p.setString(2, principal); p.setString(3, operation.token());
            try (ResultSet r = p.executeQuery()) { return r.next() && r.getBoolean(1); }
        }
    }
    Connection open(boolean gate) throws SQLException {
        Properties props = new Properties();
        props.setProperty("user", "roo_test"); props.setProperty("connectTimeout", "5");
        props.setProperty("ApplicationName", "roo:" + worker);
        props.setProperty("options", gate ? "-c statement_timeout=30000 -c lock_timeout=30000" : "-c statement_timeout=10000 -c lock_timeout=5000");
        Connection c = DriverManager.getConnection("jdbc:postgresql://127.0.0.1:" + port + "/roo_test", props);
        try { c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED); return c; }
        catch (SQLException e) { c.close(); throw e; }
    }
    @FunctionalInterface interface Work<T> { Decision<T> run(Connection c) throws SQLException; }
    record Decision<T>(T value, boolean rollback) { }
    static <T> Decision<T> commit(T value) { return new Decision<>(value, false); }
    static <T> Decision<T> rollback(T value) { return new Decision<>(value, true); }
    <T> T transaction(Work<T> work) throws SQLException {
        if (authorization != null) throw new Forbidden();
        return transaction(null, null, work);
    }
    <T> T transaction(String scope, Work<T> work) throws SQLException {
        if (authorization != null) throw new Forbidden();
        return transaction(scope, null, work);
    }
    <T> T transaction(String scope, Operation expected, Work<T> work) throws SQLException {
        requireOperation(expected);
        checkScope(scope);
        for (int attempt = 1; ; attempt++) {
            try (Connection c = open(false)) {
                c.setAutoCommit(false);
                try {
                    authorize(c, scope);
                    Decision<T> d = work.run(c);
                    if (d.rollback()) c.rollback(); else c.commit();
                    return d.value();
                } catch (SQLException e) {
                    try { c.rollback(); } catch (SQLException ignored) { /* Preserve original failure classification. */ }
                    if (attempt < 3 && Set.of("40001", "40P01", "55P03").contains(e.getSQLState() == null ? "" : e.getSQLState())) continue;
                    throw e;
                } catch (RuntimeException e) {
                    try { c.rollback(); } catch (SQLException ignored) { /* Preserve original error. */ }
                    throw e;
                }
            }
        }
    }
    void gate(String point) throws SQLException {
        if (!point.equals(gatePoint)) return;
        try (Connection c = open(true)) {
            try (PreparedStatement p = c.prepareStatement("SELECT set_config('application_name', ?, false)")) {
                p.setString(1, "roo:" + worker + ":" + point); p.execute();
            }
            try (PreparedStatement p = c.prepareStatement("SELECT pg_advisory_lock(?)")) { p.setLong(1, gateLock); p.execute(); }
            try (PreparedStatement p = c.prepareStatement("SELECT pg_advisory_unlock(?)")) { p.setLong(1, gateLock); p.execute(); }
        } catch (SQLException failure) {
            // A gate timeout is instrumentation failure, never a retryable business abort.
            throw new SQLException("Diagnostic gate failed", "RG001", failure);
        }
    }
}
