package roo.postgres;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import static roo.postgres.Domain.*;

final class Runner {
    private Runner() { }
    static final String HEADER = "scenario\tstate\ttotal\tcharge_count\trefund_count\tevent_count\tconsumer_count\tpending_outbox\tlast_result\tpayment_id\trefund_id\n";
    record Scenario(String id, List<Action> actions) { Scenario { actions = List.copyOf(actions); } }
    static List<Scenario> parse(Path path) throws IOException {
        String text = Files.readString(path, StandardCharsets.UTF_8);
        if (text.indexOf('\r') >= 0) throw new IllegalArgumentException("Expected LF line endings");
        String[] lines = text.split("\n", -1);
        if (lines.length == 0 || !lines[0].equals("scenario\tsteps")) throw new IllegalArgumentException("Invalid fixture header");
        var scenarios = new ArrayList<Scenario>(); var ids = new HashSet<String>();
        for (int i = 1; i < lines.length; i++) {
            if (lines[i].isEmpty()) continue;
            String[] fields = lines[i].split("\t", -1);
            if (fields.length != 2 || !ids.add(scope(fields[0])) || fields[1].isEmpty()) throw new IllegalArgumentException("Invalid fixture row");
            var actions = new ArrayList<Action>();
            for (String textAction : fields[1].split(";", -1)) actions.add(Action.parse(textAction));
            scenarios.add(new Scenario(fields[0], actions));
        }
        return List.copyOf(scenarios);
    }
    static void run(String[] args, boolean template) {
        try {
            // Validate command and the entire input before any connection is opened.
            if (args.length == 0) throw new IllegalArgumentException("Missing command");
            List<Scenario> rows = null; Action action = null; String scope = null; String run = null;
            switch (args[0]) {
                case "fixtures" -> {
                    arity(args, 2); rows = parse(Path.of(args[1])); run = Domain.scope(System.getenv("ROO_RUN_ID"));
                }
                case "init", "snapshot" -> { arity(args, 2); scope = Domain.scope(args[1]); }
                case "step" -> { arity(args, 3); scope = Domain.scope(args[1]); action = Action.parse(args[2]); }
                default -> throw new IllegalArgumentException("Unknown command");
            }
            Database db = new Database(System.getenv()); Store store = new Store(db); Provider provider = new Provider(db);
            Application app = template ? new JdbcTemplateApplication(store, provider, db) : new CompositionApplication(store, provider, db);
            StringBuilder output = new StringBuilder(HEADER);
            if (rows != null) {
                var scopes = new ArrayList<String>();
                for (Scenario row : rows) scopes.add(run + "_" + row.id());
                store.fresh(scopes); // All scopes inserted atomically; an existing row rejects the run.
                for (int i = 0; i < rows.size(); i++) {
                    Scenario row = rows.get(i); Result last = null;
                    for (Action step : row.actions()) last = app.execute(scopes.get(i), step);
                    output.append(store.snapshot(scopes.get(i), row.id(), String.valueOf(last)));
                }
            } else {
                String last = "-";
                if (args[0].equals("init")) store.init(scope);
                if (action != null) last = app.execute(scope, action).name();
                output.append(store.snapshot(scope, scope, last));
            }
            System.out.print(output);
        } catch (SQLException e) {
            String code = e.getSQLState();
            System.err.println("Database failure" + (code != null && code.matches("[A-Z0-9]{5}") ? " (SQLSTATE " + code + ")" : "") + "; inspect retained state before retrying stable identities.");
            System.exit(1);
        } catch (IOException | RuntimeException e) {
            // Never surface exception text: a driver or path exception may contain sensitive input.
            System.err.println("Runner failure: invalid input, configuration, or retained facts."); System.exit(1);
        }
    }
    private static void arity(String[] args, int count) {
        if (args.length != count) throw new IllegalArgumentException("Invalid command arguments");
    }
}
