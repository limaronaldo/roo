package roo.payments;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import static roo.payments.Domain.*;

/** Independent provider records and detached local transactions, for one thread only. */
public final class Adapters {
    private Adapters() { }
    public enum Mode { approve, decline, timeout_before, timeout_after }
    public enum Failure { none, prepare, commit }
    public enum Relay { ok, send_fail, ack_fail }
    public interface ProviderPort {
        Result charge(PaymentRequest request, Mode mode);
        Result refund(RefundRequest request, Mode mode);
        Result paymentStatus(PaymentRequest request, boolean unavailable);
        Result refundStatus(RefundRequest request, boolean unavailable);
    }
    public interface StorePort {
        Order load();
        boolean commit(Order candidate, Event event, boolean fail);
    }
    private record Charge(PaymentRequest request, Result result) { }
    public static final class Provider implements ProviderPort {
        private final Map<PaymentId, Charge> charges = new HashMap<>();
        private final Map<RefundId, RefundRequest> refunds = new HashMap<>();
        private final Set<PaymentId> refundedPayments = new HashSet<>();
        private int chargeCount;
        private int refundCount;
        private int requests;
        public int chargeCount() { return chargeCount; }
        public int refundCount() { return refundCount; }
        public int requests() { return requests; }
        public PaymentRequest recorded(PaymentId id) { var entry = charges.get(id); return entry == null ? null : entry.request(); }
        @Override public Result charge(PaymentRequest request, Mode mode) {
            requests++;
            var old = charges.get(request.id());
            if (old != null) return old.request().equals(request) ? old.result() : Result.KeyConflict;
            if (mode == Mode.timeout_before) return Result.Unknown;
            Result terminal = mode == Mode.decline ? Result.Declined : Result.Approved;
            charges.put(request.id(), new Charge(request, terminal));
            if (terminal == Result.Approved) chargeCount++;
            return mode == Mode.timeout_after ? Result.Unknown : terminal;
        }
        @Override public Result refund(RefundRequest request, Mode mode) {
            requests++;
            var old = refunds.get(request.id());
            if (old != null) return old.equals(request) ? Result.Approved : Result.KeyConflict;
            var paid = charges.get(request.payment());
            if (paid == null || paid.result() != Result.Approved || !paid.request().order().equals(request.order())
                || !paid.request().amount().equals(request.amount()) || refundedPayments.contains(request.payment())) return Result.KeyConflict;
            if (mode == Mode.decline) throw new IllegalArgumentException("Refund decline unsupported");
            if (mode == Mode.timeout_before) return Result.Unknown;
            refunds.put(request.id(), request); refundedPayments.add(request.payment()); refundCount++;
            return mode == Mode.timeout_after ? Result.Unknown : Result.Approved;
        }
        @Override public Result paymentStatus(PaymentRequest request, boolean unavailable) {
            if (unavailable) return Result.Unknown;
            var old = charges.get(request.id());
            return old == null ? Result.NotFound : old.request().equals(request) ? old.result() : Result.KeyConflict;
        }
        @Override public Result refundStatus(RefundRequest request, boolean unavailable) {
            if (unavailable) return Result.Unknown;
            var old = refunds.get(request.id());
            return old == null ? Result.NotFound : old.equals(request) ? Result.Approved : Result.KeyConflict;
        }
    }
    /** Package-private: only this package may construct a store or install committed state. */
    static final class Store implements StorePort {
        private Order committed = new Order(new OrderId("O1"));
        private final List<Event> events = new ArrayList<>();
        private final Set<EventId> acknowledged = new HashSet<>();
        @Override public Order load() { return committed.snapshot(); }
        public List<Event> events() { return List.copyOf(events); }
        public int pending() { return (int) events.stream().filter(event -> !acknowledged.contains(event.id())).count(); }
        @Override public boolean commit(Order candidate, Event event, boolean fail) {
            if (fail) return false;
            if (event != null && events.stream().anyMatch(old -> old.id().equals(event.id()))) throw new IllegalStateException("Duplicate committed event");
            Order installed = candidate.snapshot();
            if (event != null) events.add(event);
            committed = installed;
            return true;
        }
        public Result relay(Consumer consumer, Relay mode) {
            for (Event event : events) {
                if (acknowledged.contains(event.id())) continue;
                if (mode == Relay.send_fail) return Result.RelaySendFailed;
                consumer.accept(event);
                if (mode == Relay.ack_fail) return Result.RelayAckFailed;
                acknowledged.add(event.id());
            }
            return Result.RelayOk;
        }
    }
    public static final class Consumer {
        private final Map<EventId, Event> applied = new HashMap<>();
        public void accept(Event event) {
            Event old = applied.putIfAbsent(event.id(), event);
            if (old != null && !old.equals(event)) throw new IllegalStateException("Conflicting event fact");
        }
        public int count() { return applied.size(); }
    }
}
