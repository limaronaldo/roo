package roo.postgres;

import java.util.Objects;

/** Immutable typed facts and pure transition decisions. SQL never owns these rules. */
public final class Domain {
    private Domain() { }
    static String token(String s) {
        if (s == null || !s.matches("[A-Za-z0-9]+")) throw new IllegalArgumentException("Invalid identity");
        return s;
    }
    static String scope(String s) {
        if (s == null || !s.matches("[A-Za-z0-9_]+")) throw new IllegalArgumentException("Invalid scope");
        return s;
    }
    public record OrderId(String value) { public OrderId { token(value); } }
    public sealed interface OperationId permits PaymentId, RefundId { String value(); }
    public record PaymentId(String value) implements OperationId { public PaymentId { token(value); } }
    public record RefundId(String value) implements OperationId { public RefundId { token(value); } }
    public record EventId(String value) {
        public EventId {
            if (value == null || !value.matches("(payment|refund):[A-Za-z0-9]+")) throw new IllegalArgumentException("Invalid event identity");
        }
    }
    public record Money(long minor, String currency) {
        public Money { if (minor <= 0 || !"USD".equals(currency)) throw new IllegalArgumentException("Invalid money"); }
    }
    public enum State { Draft, Pending, Paid, Declined, Refunding, Refunded }
    public enum Result { Added, InvalidLine, Overflow, InvalidOrder, InvalidState, IntentConflict,
        Approved, Declined, Unknown, NotFound, AlreadyApplied, AlreadyDeclined,
        LocalPrepareFailed, LocalCommitFailed, KeyConflict, RelayOk, RelaySendFailed, RelayAckFailed }
    public enum Mode { approve, decline, timeout_before, timeout_after }
    public enum Failure { none, prepare, commit }
    public enum Relay { ok, send_fail, ack_fail }
    /** A provider fingerprint owns every field, including the parent payment. */
    record Request(String kind, OperationId identity, OrderId order, Money amount, PaymentId payment) {
        Request {
            Objects.requireNonNull(identity); Objects.requireNonNull(order); Objects.requireNonNull(amount); Objects.requireNonNull(payment);
            if (!kind.equals("payment") && !kind.equals("refund")) throw new IllegalArgumentException("Invalid operation kind");
            if (kind.equals("payment") != (identity instanceof PaymentId)) throw new IllegalArgumentException("Mismatched operation identity type");
            if (kind.equals("payment") && !identity.equals(payment)) throw new IllegalArgumentException("Invalid payment fingerprint");
        }
        // Persistence-boundary reconstruction chooses and validates the typed identity.
        Request(String kind, String operation, OrderId order, Money amount, PaymentId payment) {
            this(kind, kind.equals("payment") ? new PaymentId(operation) : new RefundId(operation), order, amount, payment);
        }
        String operation() { return identity.value(); }
    }
    record Event(EventId id, String kind, OrderId order, Money amount, PaymentId payment, RefundId refund) {
        Event { Objects.requireNonNull(id); Objects.requireNonNull(kind); Objects.requireNonNull(order);
            Objects.requireNonNull(amount); Objects.requireNonNull(payment);
            boolean isRefund = kind.equals("RefundApproved");
            if (!isRefund && !kind.equals("PaymentApproved") && !kind.equals("PaymentDeclined")) throw new IllegalArgumentException("Invalid event kind");
            if (isRefund != (refund != null) || !id.value().equals(isRefund ? "refund:" + refund.value() : "payment:" + payment.value())) throw new IllegalArgumentException("Invalid event fingerprint");
        }
    }
    /** Private final state; observers can read but cannot install transitions. */
    static final class Order {
        private final OrderId id;
        private final State state;
        private final long total;
        private final PaymentId payment;
        private final RefundId refund;
        Order(OrderId id, State state, long total, PaymentId payment, RefundId refund) {
            this.id = Objects.requireNonNull(id); this.state = Objects.requireNonNull(state);
            this.total = total; this.payment = payment; this.refund = refund;
            if (total < 0 || (state == State.Draft) != (payment == null)
                || (state == State.Refunding || state == State.Refunded) != (refund != null)
                || (state != State.Draft && total == 0)) throw new IllegalArgumentException("Invalid persisted order");
        }
        OrderId id() { return id; } State state() { return state; } long total() { return total; }
        PaymentId payment() { return payment; } RefundId refund() { return refund; }
        Request request(boolean isRefund) {
            return new Request(isRefund ? "refund" : "payment", isRefund ? refund : payment, id, new Money(total, "USD"), payment);
        }
    }
    record Prepared(Result rejection, Request request) { }
    static Prepared prepare(Order o, Action a) {
        if (a.op().equals("reconcile")) {
            if (o.state() != State.Pending && o.state() != State.Refunding) return new Prepared(Result.InvalidState, null);
            return new Prepared(null, o.request(o.state() == State.Refunding));
        }
        boolean refund = a.op().equals("refund");
        if (!refund) {
            PaymentId id = new PaymentId(a.field(1));
            if (o.state() != State.Draft) {
                if (!o.payment().equals(id)) return new Prepared(Result.IntentConflict, null);
                if (o.state() == State.Declined) return new Prepared(Result.AlreadyDeclined, null);
                if (o.state() != State.Pending) return new Prepared(Result.AlreadyApplied, null);
                return new Prepared(null, o.request(false));
            }
            if (o.total() == 0) return new Prepared(Result.InvalidOrder, null);
            return new Prepared(null, new Request("payment", id, o.id(), new Money(o.total(), "USD"), id));
        }
        if (o.state() != State.Paid && o.state() != State.Refunding && o.state() != State.Refunded) return new Prepared(Result.InvalidState, null);
        RefundId id = new RefundId(a.field(1));
        if (o.refund() != null) {
            if (!o.refund().equals(id)) return new Prepared(Result.IntentConflict, null);
            if (o.state() == State.Refunded) return new Prepared(Result.AlreadyApplied, null);
            return new Prepared(null, o.request(true));
        }
        return new Prepared(null, new Request("refund", id, o.id(), new Money(o.total(), "USD"), o.payment()));
    }
    static Result replay(Order o, Request r) {
        if (!o.id().equals(r.order()) || o.total() != r.amount().minor() || !Objects.equals(o.payment(), r.payment())) return Result.IntentConflict;
        if (r.kind().equals("payment")) {
            if (o.state() == State.Pending) return null;
            return o.state() == State.Declined ? Result.AlreadyDeclined : Result.AlreadyApplied;
        }
        if (o.refund() == null || !o.refund().value().equals(r.operation())) return Result.IntentConflict;
        return o.state() == State.Refunding ? null : Result.AlreadyApplied;
    }
    static Event terminal(Request r, Result result) {
        boolean refund = r.kind().equals("refund");
        if (result != Result.Approved && (refund || result != Result.Declined)) throw new IllegalArgumentException("Invalid terminal result");
        return new Event(new EventId(r.kind() + ":" + r.operation()), refund ? "RefundApproved" : "Payment" + result,
            r.order(), r.amount(), r.payment(), refund ? new RefundId(r.operation()) : null);
    }
    static long candidate(long total, long unit, long quantity) {
        if (unit <= 0 || quantity <= 0) throw new IllegalArgumentException("Invalid line");
        return Math.addExact(total, Math.multiplyExact(unit, quantity));
    }
}
