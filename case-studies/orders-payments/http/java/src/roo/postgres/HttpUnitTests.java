package roo.postgres;

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
    public static void main(String[] args) throws Exception {
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
        rejects("/v1/scopes/demo", "GET", Map.of("Accept", List.of("text/plain")), new byte[0], false, 406, "NotAcceptable");
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
