-- Install ../postgres/schema.sql first in the owned synthetic database.
-- This additive policy is used only by explicit HTTP fixture authorization.
-- Keep denied rows as tombstones: UPDATE and execution's FOR SHARE must refer
-- to the same durable row. Grants may precede creation of a scope.
CREATE SCHEMA IF NOT EXISTS roo_authorization;
CREATE TABLE IF NOT EXISTS roo_authorization.grants (
    scope text NOT NULL CHECK (scope ~ '^[A-Za-z0-9_]{1,96}$'),
    principal text NOT NULL CHECK (principal ~ '^[A-Za-z0-9_]{1,32}$'),
    allowed boolean NOT NULL,
    PRIMARY KEY (scope, principal)
);
-- Existing coarse grants remain intact for older binaries. Current fixture
-- authorization reads only operation_grants; no backfill or fallback expands
-- an old grant into permissions. Explicitly grant each desired operation.
CREATE TABLE IF NOT EXISTS roo_authorization.operation_grants (
    scope text NOT NULL CHECK (scope ~ '^[A-Za-z0-9_]{1,96}$'),
    principal text NOT NULL CHECK (principal ~ '^[A-Za-z0-9_]{1,32}$'),
    operation text NOT NULL CHECK (
        operation IN ('read', 'init', 'add', 'pay', 'refund',
                      'reconcile', 'relay', 'provider_conflict')
    ),
    allowed boolean NOT NULL,
    PRIMARY KEY (scope, principal, operation)
);
-- No command receipt is added. HTTP line additions remain non-idempotent.
