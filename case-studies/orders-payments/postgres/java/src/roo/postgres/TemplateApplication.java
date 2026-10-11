package roo.postgres;

import java.sql.SQLException;
import static roo.postgres.Domain.*;

/**
 * Template Method fixes the complete prepare/effect/finalize ordering in a final
 * algorithm. Narrow hooks choose stable adapters; subclasses cannot replace the
 * algorithm, mutate facts, or reorder the persistence and provider phases.
 * Hook implementations remain trusted capabilities with documented contracts.
 */
public abstract class TemplateApplication implements Application {
    protected TemplateApplication() { }
    protected abstract Store store();
    protected abstract Provider provider();
    protected abstract Database database();
    @Override public final Result execute(String scope, Action action) throws SQLException {
        switch (action.op()) {
            case "add": return store().add(scope, action);
            case "relay": return store().relay(scope, Relay.valueOf(action.field(1)));
            case "conflict": return provider().conflict(scope, new PaymentId(action.field(1)), action.field(2));
            default: break;
        }
        Prepared prepared = store().prepare(scope, action);
        if (prepared.rejection() != null) return prepared.rejection();
        database().gate("after_prepare");
        Request request = prepared.request();
        Result observed = action.op().equals("reconcile")
            ? provider().lookup(scope, request, action.field(1).equals("unavailable"))
            : provider().call(scope, request, Mode.valueOf(action.field(2)));
        database().gate("after_effect");
        Store.Finalized finalized = store().finish(scope, request, observed, action.failure());
        if (finalized.committed()) database().gate("after_finalize");
        return finalized.result();
    }
}
