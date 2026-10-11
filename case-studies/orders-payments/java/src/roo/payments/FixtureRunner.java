package roo.payments;

import java.io.IOException;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import static roo.payments.Domain.*;
import static roo.payments.Adapters.*;

/** Structural validation precedes any execution or normalized output. */
final class FixtureRunner {
    private FixtureRunner() { }
    private record Step(String op, String[] fields) { }
    private record Scenario(String id, List<Step> steps) { }
    static void run(String[] args, boolean inheritance) {
        try {
            if (args.length != 1) throw new IllegalArgumentException("Expected one fixture path");
            List<Scenario> rows = parse(Path.of(args[0]));
            StringBuilder output = new StringBuilder("scenario\tstate\ttotal\tcharge_count\trefund_count\tevent_count\tconsumer_count\tpending_outbox\tlast_result\tpayment_id\trefund_id\n");
            for (Scenario row : rows) {
                Store store = new Store(); Provider provider = new Provider(); Consumer consumer = new Consumer();
                Application app = inheritance ? new InMemoryTemplateApplication(store, provider) : new CompositionApplication(store, provider);
                Result last = null;
                for (Step step : row.steps()) last = execute(step, app, store, provider, consumer);
                Order order = store.load();
                output.append(row.id()).append('\t').append(order.state()).append('\t').append(order.total())
                    .append('\t').append(provider.chargeCount()).append('\t').append(provider.refundCount())
                    .append('\t').append(store.events().size()).append('\t').append(consumer.count())
                    .append('\t').append(store.pending()).append('\t').append(last)
                    .append('\t').append(order.payment() == null ? "-" : order.payment().id().value())
                    .append('\t').append(order.refund() == null ? "-" : order.refund().id().value()).append('\n');
            }
            System.out.print(output);
        } catch (IOException | RuntimeException failure) {
            System.err.println("Fixture failure: " + failure.getMessage()); System.exit(1);
        }
    }
    static Result numericAdd(Application app, String unit, String quantity) {
        try { return app.add(Long.parseLong(unit), Long.parseLong(quantity)); }
        catch (NumberFormatException overflow) { return Result.Overflow; }
    }
    private static Result execute(Step step, Application app, Store store, Provider provider, Consumer consumer) {
        String[] f = step.fields();
        return switch (step.op()) {
            case "add" -> numericAdd(app, f[1], f[2]);
            case "pay" -> app.pay(new PaymentId(f[1]), Mode.valueOf(f[2]), Failure.valueOf(f[3]));
            case "refund" -> app.refund(new RefundId(f[1]), Mode.valueOf(f[2]), Failure.valueOf(f[3]));
            case "reconcile" -> app.reconcile(f[1].equals("unavailable"), Failure.valueOf(f[2]));
            case "relay" -> store.relay(consumer, Relay.valueOf(f[1]));
            case "conflict" -> {
                yield conflict(provider, new PaymentId(f[1]), f[2]);
            }
            default -> throw new IllegalArgumentException("Unknown operation");
        };
    }
    static Result conflict(Provider provider, PaymentId id, String text) {
        BigInteger amount = new BigInteger(text);
        if (amount.compareTo(BigInteger.valueOf(Long.MAX_VALUE)) > 0
            || amount.compareTo(BigInteger.valueOf(Long.MIN_VALUE)) < 0) return Result.Overflow;
        PaymentRequest old = provider.recorded(id);
        if (old == null || amount.signum() <= 0 || amount.longValue() == old.amount().minor())
            throw new IllegalArgumentException("Invalid conflict probe");
        return provider.charge(new PaymentRequest(id, new OrderId("O1"), new Money(amount.longValue(), "USD")), Mode.approve);
    }
    private static List<Scenario> parse(Path path) throws IOException {
        String text = Files.readString(path, StandardCharsets.UTF_8);
        if (text.indexOf('\r') >= 0) throw new IllegalArgumentException("Expected LF line endings");
        String[] lines = text.split("\n", -1);
        if (lines.length == 0 || !lines[0].equals("scenario\tsteps")) throw new IllegalArgumentException("Invalid fixture header");
        var ids = new HashSet<String>(); var scenarios = new ArrayList<Scenario>();
        for (int i = 1; i < lines.length; i++) {
            if (lines[i].isEmpty()) continue;
            String[] row = lines[i].split("\t", -1);
            if (row.length != 2 || !row[0].matches("[A-Za-z0-9_]+") || !ids.add(row[0]) || row[1].isEmpty()) throw new IllegalArgumentException("Invalid fixture row " + (i + 1));
            var steps = new ArrayList<Step>();
            for (String action : row[1].split(";", -1)) {
                String[] f = action.split(":", -1);
                switch (f[0]) {
                    case "add" -> { count(f, 3); number(f[1]); number(f[2]); }
                    case "pay", "refund" -> {
                        count(f, 4); token(f[1]); Mode mode = Mode.valueOf(f[2]); Failure.valueOf(f[3]);
                        if (f[0].equals("refund") && mode == Mode.decline) throw new IllegalArgumentException("Invalid refund mode");
                    }
                    case "reconcile" -> {
                        count(f, 3);
                        if (!f[1].equals("ok") && !f[1].equals("unavailable")) throw new IllegalArgumentException("Invalid lookup");
                        Failure failure = Failure.valueOf(f[2]);
                        if (failure == Failure.prepare) throw new IllegalArgumentException("Invalid reconcile failure");
                    }
                    case "relay" -> { count(f, 2); Relay.valueOf(f[1]); }
                    case "conflict" -> { count(f, 3); token(f[1]); number(f[2]); }
                    default -> throw new IllegalArgumentException("Unknown action");
                }
                steps.add(new Step(f[0], f));
            }
            scenarios.add(new Scenario(row[0], List.copyOf(steps)));
        }
        return List.copyOf(scenarios);
    }
    private static void count(String[] fields, int count) {
        if (fields.length != count) throw new IllegalArgumentException("Invalid action field count");
    }
    private static void number(String value) {
        if (!value.matches("[+-]?[0-9]+")) throw new IllegalArgumentException("Malformed integer");
    }
}
