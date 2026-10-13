package attacker;

import roo.payments.Adapters;

// Expected diagnostic: Store is not public in Adapters; cannot be accessed from outside package.
final class ExternalStoreMutation {
    void bypass() {
        Adapters.Store store = new Adapters.Store();
        store.commit(null, null, false);
    }
}
