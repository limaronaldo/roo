package roo.postgres;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.core.StreamReadConstraints;
import com.fasterxml.jackson.core.StreamReadFeature;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Immutable transport input; all syntax validation precedes database admission. */
final class HttpProtocol {
    private HttpProtocol() { }
    static final int BODY_LIMIT = 8192;
    static final JsonFactory JSON = JsonFactory.builder()
        .enable(StreamReadFeature.STRICT_DUPLICATE_DETECTION)
        .streamReadConstraints(StreamReadConstraints.builder().maxNestingDepth(4)
            .maxStringLength(BODY_LIMIT).maxNameLength(128).maxNumberLength(128).build()).build();
    static final List<String> KEYS = List.of("scenario", "state", "total", "charge_count", "refund_count",
        "event_count", "consumer_count", "pending_outbox", "last_result", "payment_id", "refund_id");
    static final class Rejection extends Exception {
        private static final long serialVersionUID = 1L;
        final int status;
        final String code;
        final String allow;
        Rejection(int status, String code) { this(status, code, null); }
        Rejection(int status, String code, String allow) { this.status = status; this.code = code; this.allow = allow; }
    }
    record Route(String scope, String resource, String allow) { }
    record Input(Route route, String method, Action action) { }
    static Rejection invalid() { return new Rejection(400, "InvalidRequest"); }
    static Route route(URI uri, boolean test) throws Rejection {
        String path = uri.getRawPath();
        if (uri.getRawQuery() != null || uri.getRawFragment() != null || path == null
            || !path.matches("/[A-Za-z0-9_/-]*") || path.contains("//") || path.endsWith("/")) throw invalid();
        String[] parts = path.split("/", -1);
        if (parts.length < 3 || !parts[1].equals("v1") || !parts[2].equals("scopes")) throw new Rejection(404, "RouteNotFound");
        if (parts.length < 4 || !parts[3].matches("[A-Za-z0-9_]{1,96}")) throw invalid();
        if (parts.length == 4) return new Route(parts[3], "scope", "GET, PUT");
        if (parts.length == 5 && Set.of("lines", "payments", "refunds", "reconciliation", "relay").contains(parts[4]))
            return new Route(parts[3], parts[4], "POST");
        if (parts.length == 6 && parts[4].equals("_test") && parts[5].equals("provider-conflicts")) {
            if (test) return new Route(parts[3], "conflict", "POST");
            throw new Rejection(404, "RouteNotFound");
        }
        if (parts.length > 5) throw invalid();
        throw new Rejection(404, "RouteNotFound");
    }
    static String header(Map<String, List<String>> headers, String name) throws Rejection {
        List<String> values = null;
        for (var item : headers.entrySet()) if (item.getKey().equalsIgnoreCase(name)) {
            if (values != null) throw invalid();
            values = item.getValue();
        }
        if (values == null) return null;
        if (values.size() != 1) throw invalid();
        return values.get(0);
    }
    static byte[] read(InputStream stream) throws IOException, Rejection {
        var out = new ByteArrayOutputStream();
        byte[] buffer = new byte[1024];
        for (int n; (n = stream.read(buffer)) != -1;) {
            if (out.size() + n > BODY_LIMIT) throw new Rejection(413, "BodyTooLarge");
            out.write(buffer, 0, n);
        }
        return out.toByteArray();
    }
    static Map<String, String> object(byte[] body) throws Rejection {
        final String text;
        try { text = StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(body)).toString(); }
        catch (CharacterCodingException bad) { throw invalid(); }
        try (JsonParser parser = JSON.createParser(text)) {
            if (parser.nextToken() != JsonToken.START_OBJECT) throw invalid();
            var fields = new HashMap<String, String>();
            while (parser.nextToken() != JsonToken.END_OBJECT) {
                if (parser.currentToken() != JsonToken.FIELD_NAME) throw invalid();
                String key = parser.currentName();
                if (parser.nextToken() != JsonToken.VALUE_STRING) throw invalid();
                fields.put(key, parser.getText());
            }
            if (parser.nextToken() != null) throw invalid();
            return Map.copyOf(fields);
        } catch (IOException bad) { throw invalid(); }
    }
    static Input validate(URI uri, String method, Map<String, List<String>> headers, byte[] body, boolean test) throws Rejection {
        if (body.length > BODY_LIMIT) throw new Rejection(413, "BodyTooLarge");
        String content = header(headers, "Content-Type"), accept = header(headers, "Accept");
        String key = header(headers, "Idempotency-Key");
        if (header(headers, "X-Roo-Test-Drop-Response") != null) throw invalid();
        if (accept != null && !Set.of("application/json", "*/*").contains(accept.trim())) throw new Rejection(406, "NotAcceptable");
        Route route = route(uri, test);
        boolean scope = route.resource().equals("scope");
        if (!(scope ? method.equals("GET") || method.equals("PUT") : method.equals("POST")))
            throw new Rejection(405, "MethodNotAllowed", route.allow());
        if (key != null && !Set.of("payments", "refunds").contains(route.resource())) throw invalid();
        if (method.equals("GET")) {
            if (body.length != 0) throw invalid();
            return new Input(route, method, null);
        }
        if (content == null || !content.trim().matches("(?i)application/json(?:\\s*;\\s*charset\\s*=\\s*utf-8)?"))
            throw new Rejection(415, "UnsupportedMediaType");
        Map<String, String> fields = object(body);
        Set<String> required;
        Set<String> optional;
        switch (route.resource()) {
            case "scope", "reconciliation", "relay" -> required = Set.of();
            case "lines" -> required = Set.of("unit_minor", "quantity");
            case "payments" -> required = Set.of("payment_id");
            case "refunds" -> required = Set.of("refund_id");
            case "conflict" -> required = Set.of("payment_id", "different_amount");
            default -> throw invalid();
        }
        optional = !test ? Set.of() : switch (route.resource()) {
            case "payments", "refunds" -> Set.of("mode", "failure");
            case "reconciliation" -> Set.of("lookup", "failure");
            case "relay" -> Set.of("mode");
            default -> Set.of();
        };
        if (!fields.keySet().containsAll(required)) throw invalid();
        for (String name : fields.keySet()) if (!required.contains(name) && !optional.contains(name)) throw invalid();
        for (String name : List.of("payment_id", "refund_id")) if (fields.containsKey(name)
            && !fields.get(name).matches("[A-Za-z0-9]{1,64}")) throw invalid();
        for (String name : List.of("unit_minor", "quantity", "different_amount")) if (fields.containsKey(name)) {
            String value = fields.get(name);
            if (value.length() > 128 || !value.matches("[+-]?[0-9]+")) throw invalid();
        }
        if (key != null && (!key.matches("[A-Za-z0-9]{1,64}") || !key.equals(fields.get(route.resource().equals("payments") ? "payment_id" : "refund_id")))) throw invalid();
        if (route.resource().equals("conflict")) {
            Long amount = Store.integer(fields.get("different_amount"));
            if (amount == null || amount <= 0) throw invalid();
        }
        String action = switch (route.resource()) {
            case "scope" -> null;
            case "lines" -> "add:" + fields.get("unit_minor") + ":" + fields.get("quantity");
            case "payments", "refunds" -> (route.resource().equals("payments") ? "pay:" + fields.get("payment_id") : "refund:" + fields.get("refund_id"))
                + ":" + fields.getOrDefault("mode", "approve") + ":" + fields.getOrDefault("failure", "none");
            case "reconciliation" -> "reconcile:" + fields.getOrDefault("lookup", "ok") + ":" + fields.getOrDefault("failure", "none");
            case "relay" -> "relay:" + fields.getOrDefault("mode", "ok");
            case "conflict" -> "conflict:" + fields.get("payment_id") + ":" + fields.get("different_amount");
            default -> throw invalid();
        };
        try { return new Input(route, method, action == null ? null : Action.parse(action)); }
        catch (IllegalArgumentException bad) { throw invalid(); }
    }
    static int status(Domain.Result result) {
        return switch (result) {
            case Added, Approved, Declined, AlreadyApplied, AlreadyDeclined, RelayOk -> 200;
            case Unknown, NotFound -> 202;
            case InvalidState, IntentConflict, KeyConflict -> 409;
            case InvalidLine, Overflow, InvalidOrder -> 422;
            case LocalPrepareFailed, LocalCommitFailed, RelaySendFailed, RelayAckFailed -> 503;
        };
    }
    static byte[] snapshot(String tsv) throws IOException {
        String[] values = tsv.stripTrailing().split("\t", -1);
        if (values.length != KEYS.size()) throw new IllegalStateException("Invalid snapshot shape");
        var bytes = new ByteArrayOutputStream();
        try (JsonGenerator out = JSON.createGenerator(bytes)) {
            out.writeStartObject(); out.writeObjectFieldStart("snapshot");
            for (int i = 0; i < KEYS.size(); i++) out.writeStringField(KEYS.get(i), values[i]);
            out.writeEndObject(); out.writeEndObject();
        }
        return bytes.toByteArray();
    }
    static byte[] error(String code) throws IOException {
        String message = switch (code) {
            case "InvalidRequest" -> "Invalid request";
            case "RouteNotFound" -> "Route not found";
            case "MethodNotAllowed" -> "Method not allowed";
            case "ScopeNotFound" -> "Scope not found";
            case "UnsupportedMediaType" -> "Unsupported media type";
            case "BodyTooLarge" -> "Body too large";
            case "NotAcceptable" -> "Not acceptable";
            case "DatabaseUnavailable" -> "Database unavailable";
            case "Busy" -> "Server busy";
            default -> "Internal error";
        };
        var bytes = new ByteArrayOutputStream();
        try (JsonGenerator out = JSON.createGenerator(bytes)) {
            out.writeStartObject(); out.writeObjectFieldStart("error");
            out.writeStringField("code", code); out.writeStringField("message", message);
            out.writeEndObject(); out.writeEndObject();
        }
        return bytes.toByteArray();
    }
}
