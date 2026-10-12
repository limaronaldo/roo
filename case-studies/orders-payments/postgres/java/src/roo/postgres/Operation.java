package roo.postgres;

/** Closed set of independently authorized HTTP capabilities. */
enum Operation {
    READ("read"),
    INIT("init"),
    ADD("add"),
    PAY("pay"),
    REFUND("refund"),
    RECONCILE("reconcile"),
    RELAY("relay"),
    PROVIDER_CONFLICT("provider_conflict");

    private final String token;

    Operation(String token) { this.token = token; }

    String token() { return token; }

    static Operation fromToken(String token) {
        for (Operation operation : values()) if (operation.token.equals(token)) return operation;
        return null;
    }
}
