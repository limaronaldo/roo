package roo.postgres;

import static roo.postgres.Domain.*;

import java.io.ByteArrayInputStream;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Pure protocol boundaries; no listener, database connection, or environment changes. */
public final class HttpUnitTests {
    private HttpUnitTests() { }
    private static int checks;
    private static final Map<String, List<String>> JSON = Map.of("Content-Type", List.of("application/json"));
    private static void check(boolean value) { if (!value) throw new AssertionError("HTTP protocol check failed"); checks++; }
    private static HttpProtocol.Input parse(String path, String method, String body, boolean test) throws Exception {
        return HttpProtocol.validate(URI.create(path), method, JSON, body.getBytes(StandardCharsets.UTF_8), test);
    }
    private static void rejects(String path, String method, Map<String, List<String>> headers, byte[] body, boolean test, int status, String code) throws Exception {
        try { HttpProtocol.validate(URI.create(path), method, headers, body, test); throw new AssertionError("Accepted rejected request"); }
        catch (HttpProtocol.Rejection rejected) { check(rejected.status == status && rejected.code.equals(code)); }
    }
    private static void bad(String body) throws Exception {
        rejects("/v1/scopes/demo/payments", "POST", JSON, body.getBytes(StandardCharsets.UTF_8), false, 400, "InvalidRequest");
    }
    private static void authorizationRejects(String path, String method, Map<String, List<String>> headers,
        byte[] body, int status, String code, String allow) throws Exception {
        try { HttpProtocol.validate(URI.create(path), method, headers, body, true, true); throw new AssertionError("Accepted rejected authorization request"); }
        catch (HttpProtocol.Rejection rejected) {
            check(rejected.status == status && rejected.code.equals(code) && java.util.Objects.equals(rejected.allow, allow));
        }
    }
    private static Operation operation(String path, String method, String body) throws Exception {
        var headers = new HashMap<>(JSON);
        headers.put("X-Roo-Principal", List.of("caller"));
        return HttpProtocol.validate(URI.create(path), method, headers, body.getBytes(StandardCharsets.UTF_8), true, true).operation();
    }
    private static void invalidConfig(Map<String, String> env) {
        try { HttpService.Config.parse(env); throw new AssertionError("Accepted invalid authorization configuration"); }
        catch (IllegalArgumentException expected) { checks++; }
    }
    private static void authorizationChecks() throws Exception {
        byte[] empty = new byte[0];
        Map<String, List<String>> caller = Map.of("X-Roo-Principal", List.of("caller_1"));
        check(HttpProtocol.principal(Map.of(), false) == null);
        check(HttpProtocol.principal(caller, true).equals("caller_1"));
        authorizationRejects("/v1/scopes/demo", "GET", Map.of(), empty, 401, "PrincipalRequired", null);
        for (String principal : List.of("", " caller", "caller ", "a-b", "a,b", "é", "a".repeat(33)))
            authorizationRejects("/v1/scopes/demo", "GET", Map.of("X-Roo-Principal", List.of(principal)), empty, 400, "InvalidRequest", null);
        authorizationRejects("/v1/scopes/demo", "GET", Map.of("X-Roo-Principal", List.of("caller", "caller")), empty, 400, "InvalidRequest", null);
        authorizationRejects("/v1/scopes/demo", "GET", Map.of("X-Roo-Principal", List.of("caller"), "x-roo-principal", List.of("caller")), empty, 400, "InvalidRequest", null);
        check(HttpProtocol.principal(Map.of("x-roo-principal", List.of("a".repeat(32))), true).length() == 32);
        check(HttpProtocol.validate(URI.create("/v1/scopes/missing/authorization/read"), "GET", caller, empty, true, true).route().resource().equals("authorization"));
        check(operation("/v1/scopes/demo", "GET", "") == Operation.READ);
        check(operation("/v1/scopes/demo", "PUT", "{}") == Operation.INIT);
        check(operation("/v1/scopes/demo/lines", "POST", "{\"unit_minor\":\"1\",\"quantity\":\"1\"}") == Operation.ADD);
        check(operation("/v1/scopes/demo/payments", "POST", "{\"payment_id\":\"p1\"}") == Operation.PAY);
        check(operation("/v1/scopes/demo/refunds", "POST", "{\"refund_id\":\"r1\"}") == Operation.REFUND);
        check(operation("/v1/scopes/demo/reconciliation", "POST", "{}") == Operation.RECONCILE);
        check(operation("/v1/scopes/demo/relay", "POST", "{}") == Operation.RELAY);
        check(operation("/v1/scopes/demo/_test/provider-conflicts", "POST", "{\"payment_id\":\"p1\",\"different_amount\":\"2\"}") == Operation.PROVIDER_CONFLICT);
        check(operation("/v1/scopes/demo/authorization/provider_conflict", "GET", "") == Operation.PROVIDER_CONFLICT);
        authorizationRejects("/v1/scopes/demo/authorization", "GET", caller, empty, 400, "InvalidRequest", null);
        authorizationRejects("/v1/scopes/demo/authorization/unknown", "GET", caller, empty, 400, "InvalidRequest", null);
        rejects("/v1/scopes/demo/authorization", "GET", caller, empty, true, 404, "RouteNotFound");
        rejects("/v1/scopes/demo/authorization/read", "GET", caller, empty, true, 404, "RouteNotFound");
        rejects("/v1/scopes/demo/authorization/read/extra", "GET", caller, empty, true, 400, "InvalidRequest");
        authorizationRejects("/v1/scopes/demo/authorization/read/extra", "GET", caller, empty, 400, "InvalidRequest", null);
        rejects("/v1/scopes/demo/unknown", "GET", Map.of("Accept", List.of("text/html")), empty, true, 404, "RouteNotFound");
        rejects("/v1/scopes/demo/payments", "DELETE", JSON, new byte[8193], true, 405, "MethodNotAllowed");
        authorizationRejects("/v1/scopes/demo/payments", "POST", JSON, new byte[8193], 401, "PrincipalRequired", null);
        for (String method : List.of("PUT", "POST", "DELETE", "HEAD"))
            authorizationRejects("/v1/scopes/demo/authorization/read", method, caller, empty, 405, "MethodNotAllowed", "GET");
        authorizationRejects("/v1/scopes/demo/authorization/read", "GET", caller, "{}".getBytes(StandardCharsets.UTF_8), 400, "InvalidRequest", null);
        authorizationRejects("/v1/scopes/demo/authorization/read", "GET", Map.of("X-Roo-Principal", List.of("caller"), "Idempotency-Key", List.of("p1")), empty, 400, "InvalidRequest", null);
        authorizationRejects("/v1/scopes/demo/authorization/read?x=1", "GET", caller, empty, 400, "InvalidRequest", null);
        check(new String(HttpProtocol.authorization(Operation.READ, true), StandardCharsets.UTF_8)
            .equals("{\"authorization\":{\"operation\":\"read\",\"allowed\":true}}"));
        check(new String(HttpProtocol.error("PrincipalRequired"), StandardCharsets.UTF_8).equals("{\"error\":{\"code\":\"PrincipalRequired\",\"message\":\"Principal required\"}}"));
        check(new String(HttpProtocol.error("Forbidden"), StandardCharsets.UTF_8).equals("{\"error\":{\"code\":\"Forbidden\",\"message\":\"Access forbidden\"}}"));
        var env = new HashMap<String, String>();
        env.put("ROO_HTTP_HOST", "127.0.0.1"); env.put("ROO_HTTP_PORT", "0");
        check(!HttpService.Config.parse(env).authorization());
        env.put("ROO_HTTP_AUTH_MODE", "fixture"); invalidConfig(env);
        env.put("ROO_HTTP_TEST_MODE", "1"); check(HttpService.Config.parse(env).authorization());
        env.put("ROO_HTTP_AUTH_MODE", "unknown"); invalidConfig(env);
        env.put("ROO_HTTP_AUTH_MODE", ""); invalidConfig(env);
        env.remove("ROO_HTTP_AUTH_MODE"); env.put("ROO_HTTP_AUTH_GATE_LOCK", "1"); invalidConfig(env);
        env.put("ROO_HTTP_AUTH_MODE", "fixture");
        check(HttpService.Config.parse(env).authorizationGate() == 1L);
        env.put("ROO_HTTP_AUTH_GATE_LOCK", "9223372036854775807");
        check(HttpService.Config.parse(env).authorizationGate() == Long.MAX_VALUE);
        for (String key : List.of("", "0", "-1", "+1", " 1", "1 ", "1.0", "9223372036854775808")) {
            env.put("ROO_HTTP_AUTH_GATE_LOCK", key); invalidConfig(env);
        }
        env.put("ROO_HTTP_AUTH_GATE_LOCK", "1"); env.remove("ROO_HTTP_TEST_MODE"); invalidConfig(env);
        Database base = new Database(Map.of("ROO_PG_HOST", "127.0.0.1", "ROO_PG_PORT", "1",
            "ROO_PG_DATABASE", "roo_test", "ROO_PG_USER", "roo_test"));
        Database guarded = base.authorized("demo", "caller", Operation.READ);
        // These reject before opening a connection, proving accidental scope reuse cannot
        // turn a guarded adapter into authority for another scope or an unscoped callback.
        try { guarded.transaction("other", Operation.READ, c -> { throw new AssertionError("Callback entered"); }); throw new AssertionError("Scope mismatch accepted"); }
        catch (Database.Forbidden expected) { checks++; }
        try { guarded.transaction(c -> { throw new AssertionError("Callback entered"); }); throw new AssertionError("Unscoped callback accepted"); }
        catch (Database.Forbidden expected) { checks++; }
        try { guarded.observeAuthorization("demo", "caller", Operation.INIT); throw new AssertionError("Operation mismatch accepted"); }
        catch (Database.Forbidden expected) { checks++; }
        try { guarded.observeAuthorization("demo", "other", Operation.READ); throw new AssertionError("Principal mismatch accepted"); }
        catch (Database.Forbidden expected) { checks++; }
        try { guarded.transaction("demo", Operation.INIT, c -> { throw new AssertionError("Callback entered"); }); throw new AssertionError("Operation substitution accepted"); }
        catch (Database.Forbidden expected) { checks++; }
        try { new Store(guarded).init("demo"); throw new AssertionError("Mismatched init entered database"); }
        catch (Database.Forbidden expected) { checks++; }
        try { new Store(guarded).add("demo", Action.parse("add:1:1")); throw new AssertionError("Mismatched add entered database"); }
        catch (Database.Forbidden expected) { checks++; }
        try { new Store(guarded).prepare("demo", Action.parse("pay:p1:approve:none")); throw new AssertionError("Mismatched prepare entered database"); }
        catch (Database.Forbidden expected) { checks++; }
        try { new Store(guarded).relay("demo", Relay.ok); throw new AssertionError("Mismatched relay entered database"); }
        catch (Database.Forbidden expected) { checks++; }
        try { new Store(guarded).fresh(List.of("fresh")); throw new AssertionError("Bound fixture setup entered database"); }
        catch (Database.Forbidden expected) { checks++; }
        Request payment = new Request("payment", "p1", new OrderId("O1"), new Money(100, "USD"), new PaymentId("p1"));
        try { new Provider(guarded).lookup("demo", payment, false); throw new AssertionError("Mismatched lookup entered database"); }
        catch (Database.Forbidden expected) { checks++; }
        try { new Provider(guarded).call("demo", payment, Mode.approve); throw new AssertionError("Mismatched provider call entered database"); }
        catch (Database.Forbidden expected) { checks++; }
        try { new Provider(guarded).conflict("demo", new PaymentId("p1"), "2"); throw new AssertionError("Mismatched conflict entered database"); }
        catch (Database.Forbidden expected) { checks++; }
        try { new Store(guarded).finish("demo", payment, Result.Unknown, Failure.none); throw new AssertionError("Mismatched finish entered database"); }
        catch (Database.Forbidden expected) { checks++; }
        try { guarded.authorized("demo", "other", Operation.READ); throw new AssertionError("Context rebound"); }
        catch (IllegalStateException expected) { checks++; }
        // A request clone does not bind or mutate the shared base adapter.
        check(base.authorized("other", "other", Operation.PAY) != guarded);
        try { base.authorized("demo", "bad-principal", Operation.READ); throw new AssertionError("Invalid context accepted"); }
        catch (IllegalArgumentException expected) { checks++; }
        try { base.authorized("demo", "caller", null); throw new AssertionError("Unbound operation accepted"); }
        catch (IllegalArgumentException expected) { checks++; }
    }
    public static void main(String[] args) throws Exception {
        authorizationChecks();
        check(parse("/v1/scopes/demo", "PUT", "{}", false).action() == null);
        check(parse("/v1/scopes/demo/payments", "POST", "{\"payment_id\":\"p1\"}", false).action().equals(Action.parse("pay:p1:approve:none")));
        check(parse("/v1/scopes/demo/refunds", "POST", "{\"refund_id\":\"r1\",\"mode\":\"timeout_after\",\"failure\":\"commit\"}", true).action().equals(Action.parse("refund:r1:timeout_after:commit")));
        check(parse("/v1/scopes/demo/lines", "POST", "{\"unit_minor\":\"+9223372036854775808\",\"quantity\":\"-1\"}", false).action().equals(Action.parse("add:+9223372036854775808:-1")));
        for (String body : List.of("", "null", "[]", "42", "{}", "{\"payment_id\":1}", "{\"payment_id\":null}",
            "{\"payment_id\":\"p1\",\"payment_id\":\"p2\"}", "{\"payment_id\":\"p1\"} {}",
            "{\"payment_id\":\"p1\",\"amount\":\"1\"}", "{\"payment_id\":\"p_1\"}",
            "{\"payment_id\":\"p1\",\"mode\":\"approve\"}")) bad(body);
        rejects("/v1/scopes/demo/payments", "POST", JSON, new byte[]{(byte) 0xc3, 0x28}, false, 400, "InvalidRequest");
        for (String path : List.of("/v1/scopes/demo/", "/v1/scopes/demo?x=1", "/v1/scopes/%64emo", "/v1/scopes/a-b", "/v1/scopes/demo/payments/extra"))
            rejects(path, "POST", JSON, "{}".getBytes(StandardCharsets.UTF_8), false, 400, "InvalidRequest");
        rejects("/v1/scopes/demo/unknown", "POST", JSON, new byte[0], false, 404, "RouteNotFound");
        rejects("/v1/scopes/demo/_test/provider-conflicts", "POST", JSON, new byte[0], false, 404, "RouteNotFound");
        rejects("/v1/scopes/demo/payments", "GET", JSON, new byte[0], false, 405, "MethodNotAllowed");
        rejects("/v1/scopes/demo", "GET", JSON, new byte[]{32}, false, 400, "InvalidRequest");
        rejects("/v1/scopes/demo", "PUT", Map.of(), "{}".getBytes(StandardCharsets.UTF_8), false, 415, "UnsupportedMediaType");
        rejects("/v1/scopes/demo", "PUT", Map.of(), new byte[0], false, 415, "UnsupportedMediaType");
        rejects("/v1/scopes/demo/payments", "GET", JSON, new byte[8193], false, 405, "MethodNotAllowed");
        rejects("/v1/scopes/demo#fragment", "GET", Map.of(), new byte[0], false, 400, "InvalidRequest");
        rejects("/v1/scopes/demo", "GET", Map.of("Accept", List.of("text/plain")), new byte[0], false, 406, "NotAcceptable");
        check(HttpProtocol.preflight(URI.create("/v1/scopes/demo"), "GET",
            Map.of("Accept", List.of("Application/JSON")), false, false).scope().equals("demo"));
        rejects("/v1/scopes/demo", "GET", Map.of("Accept", List.of("application/json, */*")), new byte[0], false, 406, "NotAcceptable");
        rejects("/v1/scopes/demo", "GET", Map.of("Accept", List.of("application/json", "application/json")), new byte[0], false, 400, "InvalidRequest");
        rejects("/v1/scopes/demo", "GET", Map.of("X-Roo-Test-Drop-Response", List.of("1")), new byte[0], false, 400, "InvalidRequest");
        rejects("/v1/scopes/demo", "GET", Map.of("Idempotency-Key", List.of("p1")), new byte[0], false, 400, "InvalidRequest");
        var keyed = new HashMap<>(JSON);
        keyed.put("Idempotency-Key", List.of("p1"));
        byte[] payment = "{\"payment_id\":\"p1\"}".getBytes(StandardCharsets.UTF_8);
        check(HttpProtocol.validate(URI.create("/v1/scopes/demo/payments"), "POST", keyed, payment, false).action().field(1).equals("p1"));
        for (List<String> values : List.of(List.of("p2"), List.of("p1,p1"), List.of("p1", "p1"))) {
            keyed.put("Idempotency-Key", values);
            rejects("/v1/scopes/demo/payments", "POST", keyed, payment, false, 400, "InvalidRequest");
        }
        rejects("/v1/scopes/demo", "PUT", JSON, new byte[8193], false, 413, "BodyTooLarge");
        check(HttpProtocol.read(new ByteArrayInputStream(new byte[8192])).length == 8192);
        try { HttpProtocol.read(new ByteArrayInputStream(new byte[8193])); throw new AssertionError("Stream cap missing"); }
        catch (HttpProtocol.Rejection tooLarge) { check(tooLarge.status == 413); }
        for (String amount : List.of("1.0", " 1", "1e2", "1".repeat(129)))
            rejects("/v1/scopes/demo/lines", "POST", JSON, ("{\"unit_minor\":\"" + amount + "\",\"quantity\":\"1\"}").getBytes(StandardCharsets.UTF_8), false, 400, "InvalidRequest");
        rejects("/v1/scopes/demo/refunds", "POST", JSON, "{\"refund_id\":\"r1\",\"mode\":\"decline\"}".getBytes(StandardCharsets.UTF_8), true, 400, "InvalidRequest");
        rejects("/v1/scopes/demo/reconciliation", "POST", JSON, "{\"failure\":\"prepare\"}".getBytes(StandardCharsets.UTF_8), true, 400, "InvalidRequest");
        rejects("/v1/scopes/demo/_test/provider-conflicts", "POST", JSON, "{\"payment_id\":\"p1\",\"different_amount\":\"9223372036854775808\"}".getBytes(StandardCharsets.UTF_8), true, 400, "InvalidRequest");
        for (Domain.Result result : Domain.Result.values()) check(HttpProtocol.status(result) >= 200 && HttpProtocol.status(result) <= 503);
        check(HttpProtocol.status(Domain.Result.Declined) == 200);
        check(HttpProtocol.status(Domain.Result.NotFound) == 202);
        check(HttpProtocol.status(Domain.Result.KeyConflict) == 409);
        String snapshot = new String(HttpProtocol.snapshot("demo\tPaid\t250\t1\t0\t1\t0\t1\tApproved\tp1\t-\n"), StandardCharsets.UTF_8);
        check(snapshot.contains("\"total\":\"250\"") && snapshot.contains("\"refund_id\":\"-\""));
        check(new String(HttpProtocol.error("Busy"), StandardCharsets.UTF_8).equals("{\"error\":{\"code\":\"Busy\",\"message\":\"Server busy\"}}"));
        var env = new HashMap<String, String>();
        env.put("ROO_HTTP_HOST", "127.0.0.1"); env.put("ROO_HTTP_PORT", "0");
        check(HttpService.Config.parse(env).port() == 0);
        env.put("ROO_HTTP_GATE_LOCK", "1");
        try { HttpService.Config.parse(env); throw new AssertionError("Ungated test mode accepted"); }
        catch (IllegalArgumentException expected) { checks++; }
        env.put("ROO_HTTP_TEST_MODE", "1"); check(HttpService.Config.parse(env).gate() == 1L);
        env.put("ROO_HTTP_HOST", "0.0.0.0");
        try { HttpService.Config.parse(env); throw new AssertionError("Non-loopback host accepted"); }
        catch (IllegalArgumentException expected) { checks++; }
        System.out.println("Java HTTP pure protocol checks: " + checks);
    }
}
