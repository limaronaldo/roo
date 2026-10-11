package roo.payments;

import static roo.payments.Adapters.*;

/** Concrete policy supplies stable adapters; it cannot replace the algorithm. */
public final class InMemoryTemplateApplication extends TemplateApplication {
    private final StorePort local;
    private final ProviderPort remote;
    public InMemoryTemplateApplication(StorePort local, ProviderPort remote) {
        this.local = java.util.Objects.requireNonNull(local);
        this.remote = java.util.Objects.requireNonNull(remote);
    }
    @Override protected StorePort store() { return local; }
    @Override protected ProviderPort provider() { return remote; }
}
