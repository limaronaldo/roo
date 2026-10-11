package roo.payments;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/** Typed immutable facts; only the aggregate can replace its commercial state. */
public final class Domain {
    private Domain() { }
    static String token(String value) {
        if (value == null || !value.matches("[A-Za-z0-9]+")) throw new IllegalArgumentException("Invalid identity");
        return value;
    }
    public record OrderId(String value) { public OrderId { token(value); } }
    public record PaymentId(String value) { public PaymentId { token(value); } }
    public record RefundId(String value) { public RefundId { token(value); } }
    public record EventId(String value) {
        public EventId {
            if (value == null || !value.matches("(payment|refund):[A-Za-z0-9]+")) throw new IllegalArgumentException("Invalid event identity");
        }
    }
    public record Money(long minor, String currency) {
        public Money {
            if (minor <= 0 || currency == null || !currency.matches("[A-Z]{3}")) throw new IllegalArgumentException("Invalid money");
        }
    }
    public record Line(Money unit, long quantity) {
        public Line {
            Objects.requireNonNull(unit);
            if (quantity <= 0) throw new IllegalArgumentException("Invalid quantity");
            Math.multiplyExact(unit.minor(), quantity);
        }
    }
    public record PaymentRequest(PaymentId id, OrderId order, Money amount) {
        public PaymentRequest { Objects.requireNonNull(id); Objects.requireNonNull(order); Objects.requireNonNull(amount); }
    }
    public record RefundRequest(RefundId id, PaymentId payment, OrderId order, Money amount) {
        public RefundRequest { Objects.requireNonNull(id); Objects.requireNonNull(payment); Objects.requireNonNull(order); Objects.requireNonNull(amount); }
    }
    public enum State { Draft, Pending, Paid, Declined, Refunding, Refunded }
    public enum Result { Added, InvalidLine, Overflow, InvalidOrder, InvalidState, IntentConflict,
        Approved, Declined, Unknown, NotFound, AlreadyApplied, AlreadyDeclined,
        LocalPrepareFailed, LocalCommitFailed, KeyConflict, RelayOk, RelaySendFailed, RelayAckFailed }
    public record Event(EventId id, String kind, OrderId order, PaymentId payment, RefundId refund, Money amount) { }
    public static final class Order {
        private final OrderId id;
        private List<Line> lines;
        private long total;
        private State state;
        private PaymentRequest payment;
        private RefundRequest refund;
        public Order(OrderId id) { this.id = Objects.requireNonNull(id); lines = List.of(); state = State.Draft; }
        private Order(Order other) {
            id = other.id; lines = List.copyOf(other.lines); total = other.total; state = other.state;
            payment = other.payment; refund = other.refund;
        }
        public Order snapshot() { return new Order(this); }
        public OrderId id() { return id; }
        public List<Line> lines() { return lines; }
        public long total() { return total; }
        public State state() { return state; }
        public PaymentRequest payment() { return payment; }
        public RefundRequest refund() { return refund; }
        private Result add(long unit, long quantity) {
            if (state != State.Draft) return Result.InvalidState;
            if (unit <= 0 || quantity <= 0) return Result.InvalidLine;
            final long candidate;
            try { candidate = Math.addExact(total, Math.multiplyExact(unit, quantity)); }
            catch (ArithmeticException failure) { return Result.Overflow; }
            var updated = new ArrayList<>(lines);
            updated.add(new Line(new Money(unit, "USD"), quantity));
            lines = List.copyOf(updated); total = candidate;
            return Result.Added;
        }
        private void preparePayment(PaymentId key) {
            if (state != State.Draft || total <= 0) throw new IllegalStateException("Payment preparation");
            payment = new PaymentRequest(key, id, new Money(total, "USD")); state = State.Pending;
        }
        private void prepareRefund(RefundId key) {
            if (state != State.Paid) throw new IllegalStateException("Refund preparation");
            refund = new RefundRequest(key, payment.id(), id, payment.amount()); state = State.Refunding;
        }
        private Event finish(Result terminal) {
            if (state == State.Pending && (terminal == Result.Approved || terminal == Result.Declined)) {
                state = terminal == Result.Approved ? State.Paid : State.Declined;
                return new Event(new EventId("payment:" + payment.id().value()), "Payment" + terminal,
                    id, payment.id(), null, payment.amount());
            }
            if (state == State.Refunding && terminal == Result.Approved) {
                state = State.Refunded;
                return new Event(new EventId("refund:" + refund.id().value()), "RefundApproved",
                    id, payment.id(), refund.id(), refund.amount());
            }
            throw new IllegalStateException("Invalid terminal transition");
        }
    }
    // Package-scoped commands keep adapters and public observers from arbitrary field mutation.
    static Result add(Order order, long unit, long quantity) { return order.add(unit, quantity); }
    static void preparePayment(Order order, PaymentId id) { order.preparePayment(id); }
    static void prepareRefund(Order order, RefundId id) { order.prepareRefund(id); }
    static Event finish(Order order, Result terminal) { return order.finish(terminal); }
}
