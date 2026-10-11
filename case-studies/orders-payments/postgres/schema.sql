-- Install once into the integrator's dedicated synthetic test database.
-- No reset, DROP, role creation, credentials, or external database access.
BEGIN;
CREATE SCHEMA IF NOT EXISTS roo_app;
CREATE SCHEMA IF NOT EXISTS roo_provider;
CREATE SCHEMA IF NOT EXISTS roo_consumer;

CREATE TABLE roo_app.orders (
    scope text PRIMARY KEY CHECK (scope ~ '^[A-Za-z0-9_]+$'),
    order_id text NOT NULL DEFAULT 'O1' CHECK (order_id ~ '^[A-Za-z0-9]+$'),
    currency text NOT NULL DEFAULT 'USD' CHECK (currency = 'USD'),
    state text NOT NULL DEFAULT 'Draft'
        CHECK (state IN ('Draft','Pending','Paid','Declined','Refunding','Refunded')),
    total bigint NOT NULL DEFAULT 0 CHECK (total >= 0),
    payment_id text CHECK (payment_id ~ '^[A-Za-z0-9]+$'),
    refund_id text CHECK (refund_id ~ '^[A-Za-z0-9]+$'),
    CHECK ((state = 'Draft') = (payment_id IS NULL)),
    CHECK ((state IN ('Refunding','Refunded')) = (refund_id IS NOT NULL)),
    CHECK (state = 'Draft' OR total > 0)
);

CREATE TABLE roo_app.lines (
    scope text NOT NULL REFERENCES roo_app.orders(scope) ON DELETE CASCADE,
    line_no bigint NOT NULL CHECK (line_no > 0),
    unit_minor bigint NOT NULL CHECK (unit_minor > 0),
    quantity bigint NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (scope, line_no),
    CHECK (unit_minor::numeric * quantity::numeric <= 9223372036854775807)
);

CREATE TABLE roo_app.outbox (
    scope text NOT NULL REFERENCES roo_app.orders(scope) ON DELETE CASCADE,
    event_id text NOT NULL,
    seq bigint GENERATED ALWAYS AS IDENTITY,
    event_kind text NOT NULL CHECK (event_kind IN
        ('PaymentApproved','PaymentDeclined','RefundApproved')),
    order_id text NOT NULL CHECK (order_id ~ '^[A-Za-z0-9]+$'),
    currency text NOT NULL CHECK (currency = 'USD'),
    payment_id text NOT NULL CHECK (payment_id ~ '^[A-Za-z0-9]+$'),
    refund_id text CHECK (refund_id ~ '^[A-Za-z0-9]+$'),
    amount bigint NOT NULL CHECK (amount > 0),
    delivered boolean NOT NULL DEFAULT false,
    PRIMARY KEY (scope, event_id),
    CHECK ((event_kind = 'RefundApproved') = (refund_id IS NOT NULL)),
    CHECK (event_id = CASE WHEN event_kind = 'RefundApproved'
        THEN 'refund:' || refund_id ELSE 'payment:' || payment_id END)
);
CREATE INDEX outbox_pending ON roo_app.outbox(scope, seq) WHERE NOT delivered;

-- Independent simulator records: deliberately no FK to application state.
-- A successful terminal record itself counts as the durable simulated effect.
CREATE TABLE roo_provider.records (
    scope text NOT NULL CHECK (scope ~ '^[A-Za-z0-9_]+$'),
    kind text NOT NULL CHECK (kind IN ('payment','refund')),
    operation_id text NOT NULL CHECK (operation_id ~ '^[A-Za-z0-9]+$'),
    order_id text NOT NULL CHECK (order_id ~ '^[A-Za-z0-9]+$'),
    currency text NOT NULL CHECK (currency = 'USD'),
    amount bigint NOT NULL CHECK (amount > 0),
    payment_id text NOT NULL CHECK (payment_id ~ '^[A-Za-z0-9]+$'),
    result text NOT NULL CHECK (result IN ('Approved','Declined')),
    PRIMARY KEY (scope, kind, operation_id),
    CHECK (kind <> 'payment' OR operation_id = payment_id),
    CHECK (kind <> 'refund' OR result = 'Approved')
);
-- A confirmed charge can receive at most one full refund, even with another key.
CREATE UNIQUE INDEX provider_one_refund
    ON roo_provider.records(scope, payment_id) WHERE kind = 'refund';

-- Independent inbox: consumer commit survives app acknowledgement rollback.
CREATE TABLE roo_consumer.inbox (
    scope text NOT NULL CHECK (scope ~ '^[A-Za-z0-9_]+$'),
    event_id text NOT NULL,
    event_kind text NOT NULL CHECK (event_kind IN
        ('PaymentApproved','PaymentDeclined','RefundApproved')),
    order_id text NOT NULL CHECK (order_id ~ '^[A-Za-z0-9]+$'),
    currency text NOT NULL CHECK (currency = 'USD'),
    payment_id text NOT NULL CHECK (payment_id ~ '^[A-Za-z0-9]+$'),
    refund_id text CHECK (refund_id ~ '^[A-Za-z0-9]+$'),
    amount bigint NOT NULL CHECK (amount > 0),
    PRIMARY KEY (scope, event_id),
    CHECK ((event_kind = 'RefundApproved') = (refund_id IS NOT NULL)),
    CHECK (event_id = CASE WHEN event_kind = 'RefundApproved'
        THEN 'refund:' || refund_id ELSE 'payment:' || payment_id END)
);
COMMIT;
