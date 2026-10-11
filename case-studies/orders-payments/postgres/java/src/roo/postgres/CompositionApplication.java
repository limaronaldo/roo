package roo.postgres;

import java.sql.SQLException;
import java.util.Objects;
import static roo.postgres.Domain.*;

/** Composition: the coordinator receives its capabilities directly. */
final class CompositionApplication implements Application {
    private final Store store;
    private final Provider provider;
    private final Database db;
    CompositionApplication(Store store, Provider provider, Database db) {
        this.store = Objects.requireNonNull(store); this.provider = Objects.requireNonNull(provider); this.db = Objects.requireNonNull(db);
    }
    @Override public Result execute(String scope, Action action) throws SQLException {
        switch (action.op()) {
            case "add": return store.add(scope, action);
            case "relay": return store.relay(scope, Relay.valueOf(action.field(1)));
            case "conflict": return provider.conflict(scope, new PaymentId(action.field(1)), action.field(2));
            default: break;
        }
        Prepared prepared = store.prepare(scope, action);
        if (prepared.rejection() != null) return prepared.rejection();
        // The adapter has committed and closed the app transaction before this boundary.
        db.gate("after_prepare");
        Request request = prepared.request();
        Result observed = action.op().equals("reconcile")
            ? provider.lookup(scope, request, action.field(1).equals("unavailable"))
            : provider.call(scope, request, Mode.valueOf(action.field(2)));
        db.gate("after_effect");
        Store.Finalized finalized = store.finish(scope, request, observed, action.failure());
        if (finalized.committed()) db.gate("after_finalize");
        return finalized.result();
    }
}
