package roo.payments;

import java.util.List;
import static roo.payments.Adapters.*;
import static roo.payments.Domain.*;

/** Native checks obtain facts directly from the unchanged applications and adapters. */
public final class TrackNative {
    private TrackNative() { }

    static final class BehaviorFailure extends RuntimeException {
        private static final long serialVersionUID = 1L;
        BehaviorFailure(String message) { super(message); }
    }

    private static final class World {
        final Store store = new Store();
        final Provider provider = new Provider();
        final Consumer consumer = new Consumer();
        final Application app;
        World(boolean inheritance) {
            app = inheritance ? new InMemoryTemplateApplication(store, provider)
                    : new CompositionApplication(store, provider);
        }
    }

    public static void run(String exercise, boolean inheritance) {
        switch (exercise) {
            case "e1" -> lines(inheritance);
            case "e2" -> recovery(inheritance);
            case "e3" -> retry(inheritance);
            case "e4" -> redelivery(inheritance);
            default -> throw new IllegalArgumentException("Unknown native exercise");
        }
    }

    private static World seeded(boolean inheritance, long unit, long quantity, long extra) {
        World world = new World(inheritance);
        require(world.app.add(unit, quantity) == Result.Added, "Could not seed first line");
        require(world.app.add(extra, 1) == Result.Added, "Could not seed second line");
        return world;
    }

    private static void lines(boolean inheritance) {
        World world = seeded(inheritance, 100, 2, 50);
        Order before = world.store.load();
        require(before.total() == 250 && before.lines().equals(List.of(
                new Line(new Money(100, "USD"), 2), new Line(new Money(50, "USD"), 1))),
                "Invalid line setup");
        long[][] invalid = { {13, 0}, {0, 7}, {Long.MAX_VALUE, 2}, {Long.MAX_VALUE, 1} };
        Result[] expected = {Result.InvalidLine, Result.InvalidLine, Result.Overflow, Result.Overflow};
        for (int index = 0; index < invalid.length; index++) {
            long unit = invalid[index][0];
            long quantity = invalid[index][1];
            TrackInput input = observe(world, "e1", "add", null, "-", unit, quantity, "ok");
            Result result = execute(world, action(input, "add:" + unit + ":" + quantity));
            check(result == expected[index], "Domain rejection was not observed for requested line");
            check(sameOrder(before, world.store.load()), "Rejected line changed exact order facts");
            check(world.provider.requests() == 0 && world.provider.chargeCount() == 0
                    && world.store.events().isEmpty(), "Rejected line produced an effect or event");
        }
        World varied = seeded(inheritance, 73, 3, 19);
        Order variedBefore = varied.store.load();
        TrackInput input = observe(varied, "e1", "add", Result.Added, "-", 41, 5, "ok");
        check(execute(varied, action(input, "add:" + input.unit() + ":" + input.quantity())) == Result.Added,
                "Valid requested line was not added");
        Order after = varied.store.load();
        check(after.id().equals(variedBefore.id()) && after.state() == State.Draft
                && after.total() == variedBefore.total() + input.unit() * input.quantity()
                && after.lines().size() == variedBefore.lines().size() + 1
                && after.lines().subList(0, variedBefore.lines().size()).equals(variedBefore.lines())
                && after.lines().getLast().equals(new Line(new Money(input.unit(), "USD"), input.quantity()))
                && after.payment() == null && after.refund() == null,
                "Valid addition did not preserve prior facts and append requested line");
        check(varied.provider.requests() == 0 && varied.store.events().isEmpty(),
                "Valid line addition produced a payment effect or event");
    }

    private static void recovery(boolean inheritance) {
        recoverOne(inheritance, "p1", 100, 2, 50);
        recoverOne(inheritance, "Recover27", 211, 3, 5);
        World unavailable = seeded(inheritance, 47, 7, 9);
        PaymentId id = new PaymentId("Lookup9");
        require(unavailable.app.pay(id, Mode.approve, Failure.commit) == Result.LocalCommitFailed,
                "Failed commit setup did not fail");
        assertPending(unavailable, id, false);
        Order before = unavailable.store.load();
        TrackInput input = observe(unavailable, "e2", "recover", Result.LocalCommitFailed, "-", 0, 0,
                "unavailable");
        check(execute(unavailable, action(input, "reconcile:" + input.lookup() + ":none")) == Result.Unknown,
                "Unavailable lookup was not observed");
        check(sameOrder(before, unavailable.store.load()) && unavailable.provider.chargeCount() == 1
                && unavailable.store.events().isEmpty(), "Unavailable lookup changed Pending facts");
    }

    private static void recoverOne(boolean inheritance, String identity, long unit, long quantity, long extra) {
        World world = seeded(inheritance, unit, quantity, extra);
        PaymentId id = new PaymentId(identity);
        require(world.app.pay(id, Mode.approve, Failure.commit) == Result.LocalCommitFailed,
                "Failed commit setup did not fail");
        assertPending(world, id, false);
        TrackInput input = observe(world, "e2", "recover", Result.LocalCommitFailed, "-", 0, 0, "ok");
        check(execute(world, action(input, "reconcile:" + input.lookup() + ":none")) == Result.Approved,
                "Recovery did not finalize approved payment");
        assertPaid(world, id);
    }

    private static void retry(boolean inheritance) {
        World world = seeded(inheritance, 137, 2, 31);
        PaymentId id = new PaymentId("Retry42");
        require(world.app.pay(id, Mode.timeout_after, Failure.none) == Result.Unknown,
                "Timeout-after setup did not return Unknown");
        assertPending(world, id, false);
        Order before = world.store.load();
        TrackInput changed = observe(world, "e3", "retry", Result.Unknown, "Changed43", 0, 0, "ok");
        check(execute(world, action(changed, "pay:" + changed.requestedPaymentId() + ":approve:none"))
                == Result.IntentConflict, "Changed caller identity did not conflict");
        check(sameOrder(before, world.store.load()) && world.provider.chargeCount() == 1
                && world.store.events().isEmpty(), "Changed identity altered intent or effect");
        TrackInput same = observe(world, "e3", "retry", Result.IntentConflict, id.value(), 0, 0, "ok");
        check(execute(world, action(same, "pay:" + same.requestedPaymentId() + ":approve:none"))
                == Result.Approved, "Same identity retry did not finalize");
        assertPaid(world, id);
        PaymentRequest recorded = world.provider.recorded(id);
        check(FixtureRunner.conflict(world.provider, id, Long.toString(recorded.amount().minor() + 1))
                == Result.KeyConflict, "Changed fingerprint did not produce KeyConflict");
        check(world.provider.recorded(id).equals(recorded) && world.provider.chargeCount() == 1,
                "Fingerprint conflict changed provider effect");
        assertPaid(world, id);
    }

    private static void redelivery(boolean inheritance) {
        World world = seeded(inheritance, 83, 4, 17);
        PaymentId id = new PaymentId("Relay58");
        require(world.app.pay(id, Mode.approve, Failure.none) == Result.Approved,
                "Payment setup did not approve");
        require(world.store.relay(world.consumer, Relay.ack_fail) == Result.RelayAckFailed,
                "Acknowledgement failure setup did not fail");
        require(world.consumer.count() == 1 && world.store.pending() == 1,
                "Acknowledgement failure did not preserve pending event");
        Event before = world.store.events().getFirst();
        require(paymentEvent(world, id, before), "Invalid initial event facts");
        TrackInput input = observe(world, "e4", "redeliver", Result.RelayAckFailed, "-", 0, 0, "ok");
        check(execute(world, action(input, "relay:ok")) == Result.RelayOk, "Redelivery did not succeed");
        check(world.consumer.count() == 1 && world.store.pending() == 0
                && world.store.events().equals(List.of(before)) && paymentEvent(world, id, before),
                "Redelivery duplicated consumer fact or changed event identity/content");
        TrackInput empty = observe(world, "e4", "redeliver", Result.RelayOk, "-", 0, 0, "ok");
        action(empty, "stop");
        check(world.consumer.count() == 1 && world.store.pending() == 0,
                "Empty outbox decision changed delivery facts");
    }

    private static TrackInput observe(World world, String exercise, String phase, Result last,
            String requested, long unit, long quantity, String lookup) {
        Order order = world.store.load();
        return TrackInput.parse(new String[] {exercise, phase, order.state().name(), Long.toString(order.total()),
                order.payment() == null ? "-" : order.payment().id().value(), last == null ? "-" : last.name(),
                Integer.toString(world.store.pending()), requested, Long.toString(unit), Long.toString(quantity), lookup});
    }

    private static String action(TrackInput input, String required) {
        String actual = LearnerPolicy.decide(input);
        check(required.equals(actual), "Expected decision " + required + ", received " + actual);
        return actual;
    }

    private static Result execute(World world, String action) {
        String[] fields = action.split(":", -1);
        return switch (fields[0]) {
            case "add" -> world.app.add(TrackInput.integer(fields[1]), TrackInput.integer(fields[2]));
            case "pay" -> world.app.pay(new PaymentId(fields[1]), Mode.valueOf(fields[2]), Failure.valueOf(fields[3]));
            case "reconcile" -> world.app.reconcile(fields[1].equals("unavailable"), Failure.valueOf(fields[2]));
            case "relay" -> world.store.relay(world.consumer, Relay.valueOf(fields[1]));
            default -> throw new IllegalStateException("Decision does not execute a domain action");
        };
    }

    private static void assertPending(World world, PaymentId id, boolean behavioral) {
        Order order = world.store.load();
        boolean valid = order.state() == State.Pending && order.payment() != null
                && order.payment().id().equals(id) && order.payment().amount().minor() == order.total()
                && world.provider.chargeCount() == 1 && world.store.events().isEmpty()
                && world.provider.recorded(id).equals(order.payment());
        if (behavioral) check(valid, "Pending intent/effect facts changed");
        else require(valid, "Invalid Pending setup facts");
    }

    private static void assertPaid(World world, PaymentId id) {
        Order order = world.store.load();
        check(order.state() == State.Paid && order.payment() != null && order.payment().id().equals(id)
                && order.payment().amount().minor() == order.total() && world.provider.chargeCount() == 1
                && world.provider.recorded(id).equals(order.payment()) && world.store.events().size() == 1,
                "Final payment state, identity, amount, effect, or event count is wrong");
        check(paymentEvent(world, id, world.store.events().getFirst()), "Final event identity or content is wrong");
    }

    private static boolean paymentEvent(World world, PaymentId id, Event event) {
        Order order = world.store.load();
        return event.id().value().equals("payment:" + id.value()) && event.kind().equals("PaymentApproved")
                && event.order().equals(order.id()) && event.payment().equals(id) && event.refund() == null
                && event.amount().equals(order.payment().amount());
    }

    private static boolean sameOrder(Order left, Order right) {
        return left.id().equals(right.id()) && left.lines().equals(right.lines()) && left.total() == right.total()
                && left.state() == right.state() && java.util.Objects.equals(left.payment(), right.payment())
                && java.util.Objects.equals(left.refund(), right.refund());
    }

    private static void require(boolean valid, String message) {
        if (!valid) throw new IllegalStateException(message);
    }

    private static void check(boolean valid, String message) {
        if (!valid) throw new BehaviorFailure(message);
    }
}
