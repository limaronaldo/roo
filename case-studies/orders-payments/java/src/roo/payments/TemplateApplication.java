package roo.payments;

import static roo.payments.Domain.*;
import static roo.payments.Adapters.*;

/**
 * Template Method: final public algorithms fix ordering and private finalization.
 * The only subclass variation is the store/provider capability returned by a hook.
 * Hooks must return stable adapters for the lifetime of this coordinator and obey
 * the ports' detached-commit and idempotent-provider contracts.
 */
public abstract class TemplateApplication implements Application {
    protected TemplateApplication() { }
    protected abstract StorePort store();
    protected abstract ProviderPort provider();
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
