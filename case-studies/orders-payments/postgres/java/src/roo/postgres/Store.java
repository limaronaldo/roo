package roo.postgres;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import static roo.postgres.Domain.*;

/** Short local transactions; every mutation serializes on the order row. */
final class Store {
    private final Database db;
    Store(Database db) { this.db = db; }
    static Order load(Connection c, String scope, boolean lock) throws SQLException {
        try (PreparedStatement p = c.prepareStatement("SELECT order_id,state,total,payment_id,refund_id FROM roo_app.orders WHERE scope=?" + (lock ? " FOR UPDATE" : ""))) {
            p.setString(1, scope);
            try (ResultSet r = p.executeQuery()) {
                if (!r.next()) throw new IllegalArgumentException("Missing scope");
                String payment = r.getString(4), refund = r.getString(5);
                return new Order(new OrderId(r.getString(1)), State.valueOf(r.getString(2)), r.getLong(3),
                    payment == null ? null : new PaymentId(payment), refund == null ? null : new RefundId(refund));
            }
        }
    }
    void init(String scope) throws SQLException {
        db.transaction(scope, c -> {
            try (PreparedStatement p = c.prepareStatement("INSERT INTO roo_app.orders(scope) VALUES (?) ON CONFLICT DO NOTHING")) { p.setString(1, scope); p.executeUpdate(); }
            load(c, scope, false); return Database.commit(null);
        });
    }
    void fresh(List<String> scopes) throws SQLException {
        db.transaction(c -> {
            for (String scope : scopes) {
                try (PreparedStatement p = c.prepareStatement("INSERT INTO roo_app.orders(scope) VALUES (?)")) { p.setString(1, scope); p.executeUpdate(); }
            }
            return Database.commit(null);
        });
    }
    Result add(String scope, Action action) throws SQLException {
        // Parsing is complete before entering the transaction; overflow is a domain outcome.
        Long unit = integer(action.field(1)), quantity = integer(action.field(2));
        return db.transaction(scope, c -> {
            Order o = load(c, scope, true);
            if (unit == null || quantity == null) return Database.commit(Result.Overflow);
            if (o.state() != State.Draft) return Database.commit(Result.InvalidState);
            if (unit <= 0 || quantity <= 0) return Database.commit(Result.InvalidLine);
            final long total;
            try { total = candidate(o.total(), unit, quantity); }
            catch (ArithmeticException overflow) { return Database.commit(Result.Overflow); }
            try (PreparedStatement p = c.prepareStatement("INSERT INTO roo_app.lines(scope,line_no,unit_minor,quantity) SELECT ?,COALESCE(MAX(line_no),0)+1,?,? FROM roo_app.lines WHERE scope=?")) {
                p.setString(1, scope); p.setLong(2, unit); p.setLong(3, quantity); p.setString(4, scope); p.executeUpdate();
            }
            try (PreparedStatement p = c.prepareStatement("UPDATE roo_app.orders SET total=? WHERE scope=?")) { p.setLong(1, total); p.setString(2, scope); p.executeUpdate(); }
            db.gate("inside_prepare");
            return Database.commit(Result.Added);
        });
    }
    static Long integer(String text) {
        Action.number(text);
        try { return Long.valueOf(text); } catch (NumberFormatException overflow) { return null; }
    }
    Prepared prepare(String scope, Action action) throws SQLException {
        return db.transaction(scope, c -> {
            Order o = load(c, scope, true);
            Prepared decision = Domain.prepare(o, action);
            if (decision.rejection() != null) return Database.commit(decision);
            boolean changed = action.op().equals("pay") && o.state() == State.Draft
                || action.op().equals("refund") && o.state() == State.Paid;
            if (changed) {
                Request r = decision.request();
                boolean refund = r.kind().equals("refund");
                try (PreparedStatement p = c.prepareStatement(refund
                    ? "UPDATE roo_app.orders SET state='Refunding',refund_id=? WHERE scope=?"
                    : "UPDATE roo_app.orders SET state='Pending',payment_id=? WHERE scope=?")) {
                    p.setString(1, r.operation()); p.setString(2, scope); p.executeUpdate();
                }
                db.gate("inside_prepare");
                if (action.failure() == Failure.prepare) return Database.rollback(new Prepared(Result.LocalPrepareFailed, null));
            }
            return Database.commit(decision);
        });
    }
    record Finalized(Result result, boolean committed) { }
    Finalized finish(String scope, Request request, Result observed, Failure failure) throws SQLException {
        db.checkScope(scope);
        if (observed != Result.Approved && observed != Result.Declined) return new Finalized(observed, false);
        return db.transaction(scope, c -> {
            Order current = load(c, scope, true);
            Result replay = Domain.replay(current, request);
            if (replay != null) return Database.commit(new Finalized(replay, false));
            Event event = terminal(request, observed);
            State state = request.kind().equals("refund") ? State.Refunded : observed == Result.Approved ? State.Paid : State.Declined;
            try (PreparedStatement p = c.prepareStatement("UPDATE roo_app.orders SET state=? WHERE scope=?")) { p.setString(1, state.name()); p.setString(2, scope); p.executeUpdate(); }
            insertEvent(c, "roo_app.outbox", scope, event);
            if (failure == Failure.commit) return Database.rollback(new Finalized(Result.LocalCommitFailed, false));
            return Database.commit(new Finalized(observed, true));
        });
    }
    static void insertEvent(Connection c, String table, String scope, Event event) throws SQLException {
        // Table is a closed adapter constant, never an input identifier.
        if (!table.equals("roo_app.outbox") && !table.equals("roo_consumer.inbox")) throw new IllegalArgumentException("Invalid event table");
        try (PreparedStatement p = c.prepareStatement("INSERT INTO " + table + "(scope,event_id,event_kind,order_id,currency,payment_id,refund_id,amount) VALUES (?,?,?,?,?,?,?,?) ON CONFLICT DO NOTHING")) {
            bindEvent(p, scope, event); p.executeUpdate();
        }
        // A separate statement sees the winner even after a losing READ COMMITTED insert.
        try (PreparedStatement p = c.prepareStatement("SELECT event_id,event_kind,order_id,currency,payment_id,refund_id,amount FROM " + table + " WHERE scope=? AND event_id=?")) {
            p.setString(1, scope); p.setString(2, event.id().value());
            try (ResultSet r = p.executeQuery()) {
                if (!r.next() || !event.equals(event(r))) throw new IllegalStateException("Conflicting retained event");
            }
        }
    }
    private static void bindEvent(PreparedStatement p, String scope, Event e) throws SQLException {
        p.setString(1, scope); p.setString(2, e.id().value()); p.setString(3, e.kind()); p.setString(4, e.order().value());
        p.setString(5, e.amount().currency()); p.setString(6, e.payment().value()); p.setString(7, e.refund() == null ? null : e.refund().value()); p.setLong(8, e.amount().minor());
    }
    static Event event(ResultSet r) throws SQLException {
        String refund = r.getString(6);
        return new Event(new EventId(r.getString(1)), r.getString(2), new OrderId(r.getString(3)), new Money(r.getLong(7), r.getString(4)), new PaymentId(r.getString(5)), refund == null ? null : new RefundId(refund));
    }
    Result relay(String scope, Relay mode) throws SQLException {
        while (true) {
            Result result = db.transaction(scope, c -> {
                load(c, scope, true);
                Event event;
                try (PreparedStatement p = c.prepareStatement("SELECT event_id,event_kind,order_id,currency,payment_id,refund_id,amount FROM roo_app.outbox WHERE scope=? AND NOT delivered ORDER BY seq LIMIT 1")) {
                    p.setString(1, scope);
                    try (ResultSet r = p.executeQuery()) {
                        if (!r.next()) return Database.commit(Result.RelayOk);
                        event = event(r);
                    }
                }
                if (mode == Relay.send_fail) return Database.commit(Result.RelaySendFailed);
                // The outer transaction retains the policy and order locks through this effect.
                // Reacquiring the same policy on another connection can deadlock with a queued
                // revoker. Only this private nested effect inherits the outer authorization.
                db.gate("before_delivery");
                deliverInbox(event, scope);
                db.gate("after_delivery");
                try (PreparedStatement p = c.prepareStatement("UPDATE roo_app.outbox SET delivered=true WHERE scope=? AND event_id=?")) {
                    p.setString(1, scope); p.setString(2, event.id().value()); p.executeUpdate();
                }
                if (mode == Relay.ack_fail) return Database.rollback(Result.RelayAckFailed);
                // null means one acknowledgement committed and the scan should continue.
                return Database.<Result>commit(null);
            });
            if (result != null) return result;
        }
    }
    private void deliverInbox(Event event, String scope) throws SQLException {
        try (Connection inbox = db.open(false)) {
            inbox.setAutoCommit(false);
            try {
                insertEvent(inbox, "roo_consumer.inbox", scope, event);
                inbox.commit();
            } catch (SQLException | RuntimeException failure) {
                try { inbox.rollback(); } catch (SQLException ignored) { /* Preserve original failure. */ }
                throw failure;
            }
        }
    }
    String snapshot(String scope, String label, String result) throws SQLException {
        return db.transaction(scope, c -> {
            try (PreparedStatement p = c.prepareStatement("""
                SELECT state,total,
                  (SELECT count(*) FROM roo_provider.records WHERE scope=o.scope AND kind='payment' AND result='Approved'),
                  (SELECT count(*) FROM roo_provider.records WHERE scope=o.scope AND kind='refund' AND result='Approved'),
                  (SELECT count(*) FROM roo_app.outbox WHERE scope=o.scope),
                  (SELECT count(*) FROM roo_consumer.inbox WHERE scope=o.scope),
                  (SELECT count(*) FROM roo_app.outbox WHERE scope=o.scope AND NOT delivered),
                  payment_id,refund_id FROM roo_app.orders o WHERE scope=?
                """)) {
                p.setString(1, scope);
                try (ResultSet r = p.executeQuery()) {
                    if (!r.next()) throw new IllegalArgumentException("Missing scope");
                    StringBuilder out = new StringBuilder(label);
                    for (int i = 1; i <= 7; i++) out.append('\t').append(r.getString(i));
                    out.append('\t').append(result);
                    for (int i = 8; i <= 9; i++) { String v = r.getString(i); out.append('\t').append(v == null ? "-" : v); }
                    return Database.commit(out.append('\n').toString());
                }
            }
        });
    }
}
