package roo.postgres;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import static roo.postgres.Domain.*;

/** Independent provider commits with durable full-fingerprint idempotency. */
final class Provider {
    private final Database db;
    Provider(Database db) { this.db = db; }
    private record Record(Request request, Result result) { }
    private static Record read(Connection c, String scope, String kind, String operation) throws SQLException {
        try (PreparedStatement p = c.prepareStatement("SELECT order_id,currency,amount,payment_id,result FROM roo_provider.records WHERE scope=? AND kind=? AND operation_id=?")) {
            p.setString(1, scope); p.setString(2, kind); p.setString(3, operation);
            try (ResultSet r = p.executeQuery()) {
                if (!r.next()) return null;
                return new Record(new Request(kind, operation, new OrderId(r.getString(1)), new Money(r.getLong(3), r.getString(2)), new PaymentId(r.getString(4))), Result.valueOf(r.getString(5)));
            }
        }
    }
    private static void lock(Connection c, String scope) throws SQLException {
        try (PreparedStatement p = c.prepareStatement("SELECT pg_advisory_xact_lock(hashtextextended(?,0))")) { p.setString(1, scope); p.execute(); }
    }
    Result call(String scope, Request request, Mode mode) throws SQLException {
        return db.transaction(scope, c -> {
            lock(c, scope);
            Record old = read(c, scope, request.kind(), request.operation());
            if (old != null) return Database.commit(old.request().equals(request) ? old.result() : Result.KeyConflict);
            if (request.kind().equals("refund")) {
                Record parent = read(c, scope, "payment", request.payment().value());
                if (parent == null || parent.result() != Result.Approved || !parent.request().order().equals(request.order())
                    || !parent.request().amount().equals(request.amount()) || !parent.request().payment().equals(request.payment())) return Database.commit(Result.KeyConflict);
                try (PreparedStatement p = c.prepareStatement("SELECT 1 FROM roo_provider.records WHERE scope=? AND kind='refund' AND payment_id=?")) {
                    p.setString(1, scope); p.setString(2, request.payment().value());
                    try (ResultSet r = p.executeQuery()) { if (r.next()) return Database.commit(Result.KeyConflict); }
                }
                if (mode == Mode.decline) throw new IllegalArgumentException("Invalid refund mode");
            }
            if (mode == Mode.timeout_before) return Database.commit(Result.Unknown);
            Result terminal = mode == Mode.decline ? Result.Declined : Result.Approved;
            try (PreparedStatement p = c.prepareStatement("INSERT INTO roo_provider.records(scope,kind,operation_id,order_id,currency,amount,payment_id,result) VALUES (?,?,?,?,?,?,?,?)")) {
                p.setString(1, scope); p.setString(2, request.kind()); p.setString(3, request.operation()); p.setString(4, request.order().value());
                p.setString(5, request.amount().currency()); p.setLong(6, request.amount().minor()); p.setString(7, request.payment().value()); p.setString(8, terminal.name()); p.executeUpdate();
            }
            return Database.commit(mode == Mode.timeout_after ? Result.Unknown : terminal);
        });
    }
    Result lookup(String scope, Request request, boolean unavailable) throws SQLException {
        return db.transaction(scope, c -> {
            if (unavailable) return Database.commit(Result.Unknown);
            Record old = read(c, scope, request.kind(), request.operation());
            return Database.commit(old == null ? Result.NotFound : old.request().equals(request) ? old.result() : Result.KeyConflict);
        });
    }
    Result conflict(String scope, PaymentId id, String amountText) throws SQLException {
        Long amount = Store.integer(amountText);
        if (amount == null) {
            // Require the scope to exist even for numeric boundary outcomes.
            db.transaction(scope, c -> { Store.load(c, scope, false); return Database.commit(null); });
            return Result.Overflow;
        }
        Request changed = db.transaction(scope, c -> {
            Store.load(c, scope, false);
            Record old = read(c, scope, "payment", id.value());
            if (old == null || amount <= 0 || amount == old.request().amount().minor()) throw new IllegalArgumentException("Invalid conflict probe");
            return Database.commit(new Request("payment", id.value(), new OrderId("O1"), new Money(amount, "USD"), id));
        });
        return call(scope, changed, Mode.approve);
    }
}
