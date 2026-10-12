package roo.authorization;

import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.FutureTask;
import java.util.concurrent.TimeUnit;

import static roo.authorization.Coordinator.Outcome.*;
import static roo.authorization.Coordinator.Status.DRAFT;

public final class ConcurrencyTests {
    private ConcurrencyTests() {}

    private static void equal(Object actual, Object expected) {
        if (!expected.equals(actual)) {
            throw new AssertionError("Expected " + expected + ", got " + actual);
        }
    }

    private static Coordinator coordinator() {
        Coordinator coordinator = new Coordinator(List.of("order-1"));
        coordinator.grant("alice", "order-1");
        return coordinator;
    }

    private static void await(CountDownLatch gate) throws InterruptedException {
        if (!gate.await(5, TimeUnit.SECONDS)) {
            throw new AssertionError("Timed out waiting for the test schedule");
        }
    }

    private static <T> FutureTask<T> start(java.util.concurrent.Callable<T> action) {
        FutureTask<T> task = new FutureTask<>(action);
        // A failing test cannot keep the JVM alive indefinitely.
        Thread.ofPlatform().daemon().start(task);
        return task;
    }

    private static void revocationBetweenObservationAndExecutionDeniesWithoutEffect() throws Exception {
        Coordinator coordinator = coordinator();
        CountDownLatch observed = new CountDownLatch(1);
        CountDownLatch execute = new CountDownLatch(1);
        FutureTask<Coordinator.Outcome> caller = start(() -> {
            equal(coordinator.observe("alice", "order-1").allowed(), true);
            observed.countDown();
            await(execute);
            return coordinator.approve("alice", "order-1");
        });
        await(observed);
        equal(coordinator.revoke("alice", "order-1"), true);
        execute.countDown();
        equal(caller.get(5, TimeUnit.SECONDS), FORBIDDEN);
        equal(coordinator.snapshot("order-1"), new Coordinator.OrderSnapshot(DRAFT, 0));
    }

    private static void executionBeforeRevocationStaysCommittedAndNextCallIsDenied() throws Exception {
        Coordinator coordinator = coordinator();
        FutureTask<Coordinator.Outcome> caller = start(() -> coordinator.approve("alice", "order-1"));
        equal(caller.get(5, TimeUnit.SECONDS), APPROVED);
        coordinator.revoke("alice", "order-1");
        equal(coordinator.approve("alice", "order-1"), FORBIDDEN);
        equal(coordinator.snapshot("order-1"), new Coordinator.OrderSnapshot(Coordinator.Status.APPROVED, 1));
    }

    private static void competingApprovalsInstallOneTransition() throws Exception {
        Coordinator coordinator = coordinator();
        CyclicBarrier start = new CyclicBarrier(3);
        java.util.concurrent.Callable<Coordinator.Outcome> request = () -> {
            start.await(5, TimeUnit.SECONDS);
            return coordinator.approve("alice", "order-1");
        };
        FutureTask<Coordinator.Outcome> first = start(request);
        FutureTask<Coordinator.Outcome> second = start(request);
        start.await(5, TimeUnit.SECONDS);
        List<Coordinator.Outcome> results = List.of(first.get(5, TimeUnit.SECONDS), second.get(5, TimeUnit.SECONDS));
        equal(results.stream().filter(result -> result == APPROVED).count(), 1L);
        equal(results.stream().filter(result -> result == ALREADY_APPROVED).count(), 1L);
        equal(coordinator.snapshot("order-1").approvals(), 1);
    }

    private static void detachedObservationsAndSnapshotsCannotChangeCoordinatorState() {
        Coordinator coordinator = coordinator();
        Coordinator.Observation observation = coordinator.observe("alice", "order-1");
        Coordinator.OrderSnapshot snapshot = coordinator.snapshot("order-1");
        coordinator.revoke("alice", "order-1");
        // Records are immutable; constructing a replacement changes no stored state.
        Coordinator.OrderSnapshot replacement = new Coordinator.OrderSnapshot(Coordinator.Status.APPROVED, 1);
        equal(observation.allowed(), true);
        equal(snapshot, new Coordinator.OrderSnapshot(DRAFT, 0));
        equal(replacement.status(), Coordinator.Status.APPROVED);
        equal(coordinator.approve("alice", "order-1"), FORBIDDEN);
        equal(coordinator.snapshot("order-1").approvals(), 0);
    }

    public static void main(String[] args) throws Exception {
        revocationBetweenObservationAndExecutionDeniesWithoutEffect();
        executionBeforeRevocationStaysCommittedAndNextCallIsDenied();
        competingApprovalsInstallOneTransition();
        detachedObservationsAndSnapshotsCannotChangeCoordinatorState();
        System.out.println("PASS Java: three controlled thread schedules and detached values");
    }
}
