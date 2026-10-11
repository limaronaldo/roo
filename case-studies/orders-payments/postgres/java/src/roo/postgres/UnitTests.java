package roo.postgres;

import java.util.HashMap;
import java.util.Map;
import static roo.postgres.Domain.*;

/** Pure boundary tests: no JDBC connection, fixture execution, or reliance on -ea. */
public final class UnitTests {
    private UnitTests() { }
    private static int checks;
    private static void check(boolean condition, String label) {
        checks++;
        if (!condition) throw new AssertionError(label);
    }
    private static void rejects(Runnable work, String label) {
        boolean rejected = false;
        try { work.run(); } catch (IllegalArgumentException | ArithmeticException expected) { rejected = true; }
        check(rejected, label);
    }
    public static void main(String[] args) {
        rejects(() -> new PaymentId("p_1"), "ASCII identity restriction");
        rejects(() -> new RefundId(""), "empty identity");
        rejects(() -> new OrderId("é"), "non-ASCII identity");
        rejects(() -> new Money(0, "USD"), "positive money");
        rejects(() -> new Money(1, "EUR"), "fixed currency");
        rejects(() -> candidate(0, Long.MAX_VALUE, 2), "checked multiplication");
        rejects(() -> candidate(Long.MAX_VALUE, 1, 1), "checked sum");
        rejects(() -> candidate(100, -1, 1), "negative line rejected");
        check(candidate(100, 50, 3) == 250, "minor unit arithmetic");
        Order draft = new Order(new OrderId("O1"), State.Draft, 100, null, null);
        rejects(() -> candidate(draft.total(), Long.MAX_VALUE, 2), "rejected candidate");
        check(draft.total() == 100 && draft.state() == State.Draft && draft.payment() == null, "rejected immutable candidate unchanged");
        check(Store.integer("9223372036854775808") == null, "positive text overflow");
        check(Store.integer("-9223372036854775809") == null, "negative text overflow");
        check(Store.integer("-9223372036854775808") == Long.MIN_VALUE, "signed minimum");
        rejects(() -> Store.integer("1e2"), "malformed integer differs from overflow");
        for (String input : new String[] {"add:1", "add:1:x", "pay:p:bogus:none", "refund:r:decline:none", "reconcile:ok:prepare", "relay:bogus", "pay:p_1:approve:none", "pay:p:approve:none:extra", ""}) {
            rejects(() -> Action.parse(input), "structural action rejection");
        }
        Action pay = Action.parse("pay:p1:approve:none");
        Prepared prepared = prepare(draft, pay);
        check(prepared.rejection() == null && prepared.request().amount().minor() == 100, "payment immutable request");
        check(prepared.request().identity() instanceof PaymentId, "payment identity retained as typed fact");
        rejects(() -> new Request("refund", new PaymentId("p1"), new OrderId("O1"), new Money(100, "USD"), new PaymentId("p1")), "request rejects mismatched identity type");
        check(draft.state() == State.Draft, "preparation decision does not mutate snapshot");
        check(prepare(new Order(new OrderId("O1"), State.Draft, 0, null, null), pay).rejection() == Result.InvalidOrder, "empty order rejected");
        PaymentId payment = new PaymentId("p1"); RefundId refund = new RefundId("r1");
        Order pending = new Order(new OrderId("O1"), State.Pending, 100, payment, null);
        check(prepare(pending, Action.parse("pay:p2:approve:none")).rejection() == Result.IntentConflict, "competing payment identity");
        check(prepare(pending, pay).request().equals(prepared.request()), "same key immutable retry");
        Order paid = new Order(new OrderId("O1"), State.Paid, 100, payment, null);
        check(prepare(paid, pay).rejection() == Result.AlreadyApplied, "terminal no-op");
        check(prepare(paid, Action.parse("reconcile:ok:none")).rejection() == Result.InvalidState, "cross-state reconciliation");
        Order declined = new Order(new OrderId("O1"), State.Declined, 100, payment, null);
        check(prepare(declined, pay).rejection() == Result.AlreadyDeclined, "stable decline");
        check(prepare(declined, Action.parse("refund:r1:approve:none")).rejection() == Result.InvalidState, "refund requires approved charge");
        Request rr = prepare(paid, Action.parse("refund:r1:approve:none")).request();
        check(rr.identity() instanceof RefundId, "refund identity retained as typed fact");
        Order refunding = new Order(new OrderId("O1"), State.Refunding, 100, payment, refund);
        check(prepare(refunding, Action.parse("refund:r2:approve:none")).rejection() == Result.IntentConflict, "competing refund identity");
        check(prepare(refunding, pay).rejection() == Result.AlreadyApplied, "payment no-op after refund preparation");
        check(replay(refunding, prepared.request()) == Result.AlreadyApplied, "concurrent payment finalizer cannot regress refund");
        Order refunded = new Order(new OrderId("O1"), State.Refunded, 100, payment, refund);
        check(replay(refunded, rr) == Result.AlreadyApplied, "concurrent refund terminal no-op");
        check(replay(pending, new Request("payment", "p1", new OrderId("O2"), new Money(100, "USD"), payment)) == Result.IntentConflict, "full order fingerprint");
        check(replay(pending, new Request("payment", "p1", new OrderId("O1"), new Money(101, "USD"), payment)) == Result.IntentConflict, "full amount fingerprint");
        Event event = terminal(prepared.request(), Result.Approved);
        check(event.equals(terminal(prepared.request(), Result.Approved)), "stable event facts");
        check(!event.equals(terminal(prepared.request(), Result.Declined)), "event fingerprint includes terminal kind");
        check(terminal(rr, Result.Approved).refund().equals(refund), "refund copied identity");
        rejects(() -> terminal(rr, Result.Declined), "refund cannot decline");
        check(Result.NotFound != Result.Unknown, "absence distinct from uncertainty");
        Map<String, String> env = new HashMap<>(Map.of("ROO_PG_HOST", "127.0.0.1", "ROO_PG_PORT", "5432", "ROO_PG_DATABASE", "roo_test", "ROO_PG_USER", "roo_test"));
        new Database(env);
        env.put("ROO_PG_HOST", "localhost"); rejects(() -> new Database(env), "literal loopback only");
        env.put("ROO_PG_HOST", "127.0.0.1"); env.put("ROO_PG_PORT", "65536"); rejects(() -> new Database(env), "port bounds");
        env.put("ROO_PG_PORT", "5432"); env.put("ROO_GATE_POINT", "after_effect"); rejects(() -> new Database(env), "gate requires key");
        env.put("ROO_GATE_LOCK", "0"); rejects(() -> new Database(env), "positive gate key");
        env.put("ROO_GATE_LOCK", "10"); env.put("ROO_WORKER_ID", "x".repeat(33)); rejects(() -> new Database(env), "bounded worker token");
        System.out.println("Java PostgreSQL pure checks: " + checks);
    }
}
