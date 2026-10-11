package roo.payments;

import java.util.Arrays;
import java.util.Set;

/** Validated caller observations; policy evaluation never trusts these as test evidence. */
public record TrackInput(String exercise, String phase, Domain.State state, long total,
        String paymentId, String lastResult, long pendingOutbox, String requestedPaymentId,
        long unit, long quantity, String lookup) {
    private static final Set<String> LOOKUPS = Set.of("ok", "unavailable");

    public static TrackInput parse(String[] fields) {
        if (fields.length != 11) throw new IllegalArgumentException();
        String exercise = fields[0];
        String phase = fields[1];
        boolean allowed = switch (exercise) {
            case "e1" -> phase.equals("add");
            case "e2" -> phase.equals("recover");
            case "e3" -> phase.equals("retry");
            case "e4" -> phase.equals("redeliver");
            case "e5" -> Set.of("uncertain_commit", "recover").contains(phase);
            case "e6" -> Set.of("payment_response_lost", "line_response_lost", "line_inspected").contains(phase);
            default -> false;
        };
        if (!allowed) throw new IllegalArgumentException();
        Domain.State state = Domain.State.valueOf(fields[2]);
        long total = integer(fields[3]);
        identity(fields[4]);
        if (!fields[5].equals("-")) Domain.Result.valueOf(fields[5]);
        long pending = integer(fields[6]);
        identity(fields[7]);
        long unit = integer(fields[8]);
        long quantity = integer(fields[9]);
        if (total < 0 || pending < 0 || !LOOKUPS.contains(fields[10])) throw new IllegalArgumentException();
        return new TrackInput(exercise, phase, state, total, fields[4], fields[5], pending,
                fields[7], unit, quantity, fields[10]);
    }

    public static TrackInput parsePolicyArguments(String[] args) {
        if (args.length != 12 || !args[0].equals("policy")) throw new IllegalArgumentException();
        return parse(Arrays.copyOfRange(args, 1, args.length));
    }

    static long integer(String text) {
        if (!text.matches("-?[0-9]+")) throw new IllegalArgumentException();
        return Long.parseLong(text);
    }

    static void identity(String text) {
        if (!text.equals("-") && !text.matches("[A-Za-z0-9]{1,64}")) throw new IllegalArgumentException();
    }
}
