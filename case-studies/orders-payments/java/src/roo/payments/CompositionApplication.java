package roo.payments;

import static roo.payments.Domain.*;
import static roo.payments.Adapters.*;

/** Coordination by injected capabilities; no implementation inheritance. */
public final class CompositionApplication implements Application {
    private final StorePort local;
    private final ProviderPort remote;
    public CompositionApplication(StorePort local, ProviderPort remote) {
        this.local = java.util.Objects.requireNonNull(local);
        this.remote = java.util.Objects.requireNonNull(remote);
    }
    private StorePort store() { return local; }
    private ProviderPort provider() { return remote; }
    @Override public final Result add(long unit, long quantity) {
        Order candidate = store().load();
        Result result = Domain.add(candidate, unit, quantity);
        if (result == Result.Added && !store().commit(candidate, null, false)) throw new IllegalStateException("Infallible add commit failed");
        return result;
    }
    @Override public final Result pay(PaymentId id, Mode mode, Failure failure) {
        Order candidate = store().load();
        if (candidate.state() != State.Draft) {
            if (!candidate.payment().id().equals(id)) return Result.IntentConflict;
            if (candidate.state() == State.Declined) return Result.AlreadyDeclined;
            if (candidate.state() != State.Pending) return Result.AlreadyApplied;
        } else {
            if (candidate.total() == 0) return Result.InvalidOrder;
            Domain.preparePayment(candidate, id);
            if (!store().commit(candidate, null, failure == Failure.prepare)) return Result.LocalPrepareFailed;
        }
        // Reload: the remote effect uses only an intent that actually committed.
        Order persisted = store().load();
        return finish(persisted, provider().charge(persisted.payment(), mode), failure);
    }
    @Override public final Result refund(RefundId id, Mode mode, Failure failure) {
        // The bounded protocol does not support a declined refund; reject before any write.
        if (mode == Mode.decline) return Result.InvalidState;
        Order candidate = store().load();
        if (candidate.state() != State.Paid && candidate.state() != State.Refunding && candidate.state() != State.Refunded) return Result.InvalidState;
        if (candidate.refund() != null) {
            if (!candidate.refund().id().equals(id)) return Result.IntentConflict;
            if (candidate.state() == State.Refunded) return Result.AlreadyApplied;
        } else {
            Domain.prepareRefund(candidate, id);
            if (!store().commit(candidate, null, failure == Failure.prepare)) return Result.LocalPrepareFailed;
        }
        Order persisted = store().load();
        return finish(persisted, provider().refund(persisted.refund(), mode), failure);
    }
    @Override public final Result reconcile(boolean unavailable, Failure failure) {
        Order candidate = store().load();
        Result result;
        if (candidate.state() == State.Pending) result = provider().paymentStatus(candidate.payment(), unavailable);
        else if (candidate.state() == State.Refunding) result = provider().refundStatus(candidate.refund(), unavailable);
        else return Result.InvalidState;
        return finish(candidate, result, failure);
    }
    private Result finish(Order candidate, Result result, Failure failure) {
        if (result != Result.Approved && result != Result.Declined) return result;
        Event event = Domain.finish(candidate, result);
        return store().commit(candidate, event, failure == Failure.commit) ? result : Result.LocalCommitFailed;
    }
}
