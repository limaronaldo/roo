package roo.authorization;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;

/** Reads commands, never expected results. Inputs contain trusted synthetic identities. */
public final class FixtureRunner {
    private FixtureRunner() {}

    private static String state(Coordinator coordinator, String orderId) {
        Coordinator.OrderSnapshot snapshot = coordinator.snapshot(orderId);
        return snapshot.status().name().toLowerCase(Locale.ROOT) + "/" + snapshot.approvals();
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            throw new IllegalArgumentException("Expected one fixture path");
        }
        String scenario = "";
        Coordinator coordinator = new Coordinator(List.of());
        int step = 0;
        for (String line : Files.readAllLines(Path.of(args[0]), StandardCharsets.UTF_8)) {
            if (line.startsWith("#")) {
                continue;
            }
            String[] fields = line.split("\t", -1);
            if (fields.length != 4) {
                throw new IllegalArgumentException("Expected four tab-separated input columns");
            }
            if (!scenario.equals(fields[0])) {
                scenario = fields[0];
                coordinator = new Coordinator(List.of("order-1", "order-2"));
                step = 0;
            }
            step++;
            String principal = fields[2];
            String orderId = fields[3];
            String result = switch (fields[1]) {
                case "grant" -> coordinator.grant(principal, orderId) ? "granted" : "unchanged";
                case "revoke" -> coordinator.revoke(principal, orderId) ? "revoked" : "unchanged";
                case "observe" -> coordinator.observe(principal, orderId).allowed() ? "allowed" : "denied";
                case "approve" -> coordinator.approve(principal, orderId).name().toLowerCase(Locale.ROOT);
                default -> throw new IllegalArgumentException("Unknown fixture action");
            };
            System.out.println(scenario + "\t" + step + "\t" + result + "\t"
                    + state(coordinator, "order-1") + "\t" + state(coordinator, "order-2"));
        }
    }
}
