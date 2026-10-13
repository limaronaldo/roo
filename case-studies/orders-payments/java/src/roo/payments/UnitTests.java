package roo.payments;

import static roo.payments.Domain.*;
import static roo.payments.Adapters.*;

/** Explicit assertions execute with or without the VM's -ea option. */
public final class UnitTests {
    private UnitTests() { }
    private static int checks;
    private static void equal(Object actual, Object expected) {
        checks++;
        if (!java.util.Objects.equals(actual, expected)) throw new AssertionError("Expected " + expected + ", got " + actual);
    }
    private static void yes(boolean value) { equal(value, true); }
    private static Application app(boolean template, Store store, ProviderPort provider) {
        return template ? new InMemoryTemplateApplication(store, provider) : new CompositionApplication(store, provider);
    }
    private static final PaymentId P1 = new PaymentId("p1");
    private static final RefundId R1 = new RefundId("r1");
    public static void main(String[] args) {
        for (boolean template : new boolean[] { false, true }) {
            additions(template); paymentRecovery(template); refunds(template); declined(template);
            refundDecline(template); persistedBeforeRemote(template);
        }
        providerContract();
        System.out.println("Java unit checks: " + checks);
    }
    private static void additions(boolean template) {
        Store s = new Store(); Provider p = new Provider(); Application a = app(template, s, p);
        equal(a.pay(P1, Mode.approve, Failure.none), Result.InvalidOrder);
        equal(s.load().payment(), null); equal(p.requests(), 0);
        equal(a.refund(R1, Mode.approve, Failure.none), Result.InvalidState);
        equal(a.reconcile(false, Failure.none), Result.InvalidState);
        equal(a.add(100, 2), Result.Added); Order before = s.load();
        equal(a.add(0, 1), Result.InvalidLine); equal(a.add(1, -1), Result.InvalidLine);
        equal(a.add(Long.MAX_VALUE, 2), Result.Overflow);
        equal(s.load().lines(), before.lines()); equal(s.load().total(), before.total());
        equal(FixtureRunner.numericAdd(a, "9223372036854775808", "1"), Result.Overflow);
        equal(FixtureRunner.numericAdd(a, "1", "-9223372036854775809"), Result.Overflow);
        equal(s.load().total(), 200L);
        try { before.lines().clear(); throw new AssertionError("Mutable lines"); }
        catch (UnsupportedOperationException expected) { checks++; }
        Order detached = s.load(); Domain.add(detached, 10, 1);
        equal(s.load().total(), 200L);
        Store sum = new Store(); Application sumApp = app(template, sum, new Provider());
        equal(sumApp.add(Long.MAX_VALUE, 1), Result.Added);
        equal(sumApp.add(1, 1), Result.Overflow); equal(sum.load().total(), Long.MAX_VALUE);
        equal(sum.load().lines().size(), 1);
    }
    private static void paymentRecovery(boolean template) {
        Store s = new Store(); Provider p = new Provider(); Application a = app(template, s, p);
        a.add(250, 1);
        equal(a.pay(P1, Mode.approve, Failure.prepare), Result.LocalPrepareFailed);
        equal(s.load().state(), State.Draft); equal(s.load().payment(), null); equal(p.requests(), 0); equal(s.events().size(), 0);
        equal(a.pay(P1, Mode.timeout_before, Failure.commit), Result.Unknown);
        equal(s.load().state(), State.Pending); equal(p.chargeCount(), 0);
        equal(a.reconcile(false, Failure.commit), Result.NotFound);
        equal(a.reconcile(true, Failure.commit), Result.Unknown);
        equal(s.events().size(), 0);
        equal(a.pay(new PaymentId("p2"), Mode.approve, Failure.none), Result.IntentConflict); equal(p.requests(), 1);
        equal(a.add(1, 1), Result.InvalidState);
        equal(a.pay(P1, Mode.approve, Failure.commit), Result.LocalCommitFailed);
        equal(s.load().state(), State.Pending); equal(s.events().size(), 0); equal(p.chargeCount(), 1);
        equal(a.reconcile(false, Failure.commit), Result.LocalCommitFailed);
        equal(s.load().state(), State.Pending); equal(s.events().size(), 0);
        equal(a.pay(P1, Mode.decline, Failure.none), Result.Approved);
        equal(s.load().state(), State.Paid); equal(p.chargeCount(), 1); equal(s.events().size(), 1);
        Event fact = s.events().get(0);
        equal(fact.id(), new EventId("payment:p1")); equal(fact.payment(), P1); equal(fact.order(), new OrderId("O1"));
        equal(fact.amount(), new Money(250, "USD")); equal(fact.kind(), "PaymentApproved");
        equal(a.pay(P1, Mode.approve, Failure.commit), Result.AlreadyApplied);
        equal(s.events().get(0), fact); equal(s.events().size(), 1);
        Consumer consumer = new Consumer();
        equal(s.relay(consumer, Relay.send_fail), Result.RelaySendFailed); equal(consumer.count(), 0); equal(s.pending(), 1);
        equal(s.relay(consumer, Relay.ack_fail), Result.RelayAckFailed); equal(consumer.count(), 1); equal(s.pending(), 1);
        equal(s.relay(consumer, Relay.ok), Result.RelayOk); equal(consumer.count(), 1); equal(s.pending(), 0);
        equal(s.relay(consumer, Relay.send_fail), Result.RelayOk);
        Store t = new Store(); Provider q = new Provider(); Application b = app(template, t, q); b.add(1, 1);
        equal(b.pay(P1, Mode.timeout_after, Failure.none), Result.Unknown);
        equal(t.load().state(), State.Pending); equal(q.chargeCount(), 1); equal(t.events().size(), 0);
        equal(b.reconcile(true, Failure.none), Result.Unknown);
        equal(b.reconcile(false, Failure.none), Result.Approved); equal(q.chargeCount(), 1);
    }
    private static void refunds(boolean template) {
        Store s = new Store(); Provider p = new Provider(); Application a = app(template, s, p);
        a.add(250, 1); a.pay(P1, Mode.approve, Failure.none);
        equal(a.refund(R1, Mode.approve, Failure.prepare), Result.LocalPrepareFailed);
        equal(s.load().state(), State.Paid); equal(s.load().refund(), null); equal(p.refundCount(), 0); equal(s.events().size(), 1);
        equal(a.refund(R1, Mode.timeout_before, Failure.none), Result.Unknown);
        equal(s.load().state(), State.Refunding); equal(p.refundCount(), 0);
        equal(a.reconcile(false, Failure.none), Result.NotFound);
        equal(a.refund(new RefundId("r2"), Mode.approve, Failure.none), Result.IntentConflict);
        equal(a.pay(P1, Mode.approve, Failure.none), Result.AlreadyApplied);
        equal(a.pay(new PaymentId("p2"), Mode.approve, Failure.none), Result.IntentConflict);
        equal(a.refund(R1, Mode.timeout_after, Failure.commit), Result.Unknown);
        equal(p.refundCount(), 1); equal(s.load().state(), State.Refunding); equal(s.events().size(), 1);
        equal(a.reconcile(false, Failure.commit), Result.LocalCommitFailed);
        equal(s.load().state(), State.Refunding); equal(s.events().size(), 1);
        equal(a.refund(R1, Mode.approve, Failure.none), Result.Approved);
        equal(s.load().state(), State.Refunded); equal(p.refundCount(), 1); equal(s.events().size(), 2);
        Event refund = s.events().get(1);
        equal(refund.id(), new EventId("refund:r1")); equal(refund.refund(), R1); equal(refund.payment(), P1);
        equal(refund.amount(), new Money(250, "USD")); equal(refund.kind(), "RefundApproved");
        equal(a.refund(R1, Mode.approve, Failure.commit), Result.AlreadyApplied);
        equal(a.refund(new RefundId("r2"), Mode.approve, Failure.none), Result.IntentConflict);
        equal(a.reconcile(false, Failure.none), Result.InvalidState);
        Consumer c = new Consumer(); equal(s.relay(c, Relay.ack_fail), Result.RelayAckFailed);
        equal(c.count(), 1); equal(s.pending(), 2);
        equal(s.relay(c, Relay.ok), Result.RelayOk); equal(c.count(), 2); equal(s.pending(), 0);
        Store t = new Store(); Provider q = new Provider(); Application b = app(template, t, q);
        b.add(1, 1); b.pay(P1, Mode.approve, Failure.none);
        equal(b.refund(R1, Mode.approve, Failure.commit), Result.LocalCommitFailed);
        equal(t.load().state(), State.Refunding); equal(q.refundCount(), 1); equal(t.events().size(), 1);
        equal(b.reconcile(false, Failure.none), Result.Approved); equal(t.events().size(), 2);
    }
    private static void declined(boolean template) {
        Store s = new Store(); Provider p = new Provider(); Application a = app(template, s, p);
        a.add(1, 1); equal(a.pay(P1, Mode.decline, Failure.none), Result.Declined);
        equal(s.load().state(), State.Declined); equal(p.chargeCount(), 0); equal(s.events().size(), 1);
        equal(a.pay(P1, Mode.approve, Failure.commit), Result.AlreadyDeclined);
        equal(a.refund(R1, Mode.approve, Failure.none), Result.InvalidState);
        equal(a.reconcile(false, Failure.none), Result.InvalidState); equal(p.requests(), 1);
    }
    private static void refundDecline(boolean template) {
        Store s = new Store(); Provider p = new Provider(); Application a = app(template, s, p);
        equal(a.add(250, 1), Result.Added);
        equal(a.pay(P1, Mode.approve, Failure.none), Result.Approved);
        int requests = p.requests();
        equal(a.refund(R1, Mode.decline, Failure.none), Result.InvalidState);
        equal(s.load().state(), State.Paid); equal(s.load().refund(), null);
        equal(s.events().size(), 1); equal(p.requests(), requests); equal(p.refundCount(), 0);
    }
    private static void persistedBeforeRemote(boolean template) {
        Store store = new Store(); Provider delegate = new Provider();
        ProviderPort checking = new ProviderPort() {
            @Override public Result charge(PaymentRequest request, Mode mode) {
                equal(store.load().state(), State.Pending); equal(store.load().payment(), request);
                return delegate.charge(request, mode);
            }
            @Override public Result refund(RefundRequest request, Mode mode) {
                equal(store.load().state(), State.Refunding); equal(store.load().refund(), request);
                return delegate.refund(request, mode);
            }
            @Override public Result paymentStatus(PaymentRequest request, boolean unavailable) { return delegate.paymentStatus(request, unavailable); }
            @Override public Result refundStatus(RefundRequest request, boolean unavailable) { return delegate.refundStatus(request, unavailable); }
        };
        Application a = app(template, store, checking); a.add(10, 1);
        equal(a.pay(P1, Mode.approve, Failure.none), Result.Approved);
        equal(a.refund(R1, Mode.approve, Failure.none), Result.Approved);
    }
    private static void providerContract() {
        Provider p = new Provider(); OrderId order = new OrderId("O1"); Money money = new Money(250, "USD");
        PaymentRequest request = new PaymentRequest(P1, order, money);
        equal(p.charge(request, Mode.timeout_after), Result.Unknown);
        equal(p.charge(request, Mode.decline), Result.Approved);
        for (PaymentRequest mismatch : new PaymentRequest[] {
            new PaymentRequest(P1, new OrderId("O2"), money),
            new PaymentRequest(P1, order, new Money(250, "EUR")),
            new PaymentRequest(P1, order, new Money(251, "USD")) }) {
            equal(p.charge(mismatch, Mode.approve), Result.KeyConflict);
            equal(p.paymentStatus(mismatch, false), Result.KeyConflict);
        }
        equal(p.chargeCount(), 1); equal(p.recorded(P1), request);
        equal(FixtureRunner.conflict(p, P1, "9223372036854775808"), Result.Overflow);
        equal(FixtureRunner.conflict(p, P1, "-9223372036854775809"), Result.Overflow);
        equal(p.chargeCount(), 1); equal(p.recorded(P1), request);
        RefundRequest refund = new RefundRequest(R1, P1, order, money);
        equal(p.refund(new RefundRequest(R1, P1, order, new Money(251, "USD")), Mode.approve), Result.KeyConflict);
        equal(p.refund(refund, Mode.timeout_after), Result.Unknown);
        equal(p.refund(refund, Mode.approve), Result.Approved);
        for (RefundRequest mismatch : new RefundRequest[] {
            new RefundRequest(R1, new PaymentId("p2"), order, money),
            new RefundRequest(R1, P1, new OrderId("O2"), money),
            new RefundRequest(R1, P1, order, new Money(250, "EUR")),
            new RefundRequest(R1, P1, order, new Money(249, "USD")) }) equal(p.refund(mismatch, Mode.approve), Result.KeyConflict);
        equal(p.refund(new RefundRequest(new RefundId("r2"), P1, order, money), Mode.approve), Result.KeyConflict);
        equal(p.refundCount(), 1); yes(!P1.equals(order));
        Provider separate = new Provider();
        PaymentId sameToken = new PaymentId("same"); RefundId sameRefund = new RefundId("same");
        equal(separate.charge(new PaymentRequest(sameToken, order, money), Mode.approve), Result.Approved);
        equal(separate.refund(new RefundRequest(sameRefund, sameToken, order, money), Mode.approve), Result.Approved);
    }
}
