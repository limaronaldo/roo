package roo.payments;

/** Edit these six decisions, then rebuild the starter and run one exercise at a time. */
public final class LearnerPolicy {
    private LearnerPolicy() { }

    public static String decide(TrackInput input) {
        return switch (input.exercise()) {
            case "e1" -> add(input);
            case "e2" -> recover(input);
            case "e3" -> retry(input);
            case "e4" -> redeliver(input);
            case "e5" -> uncertainCommit(input);
            case "e6" -> lostResponse(input);
            default -> throw new IllegalArgumentException("Unknown exercise");
        };
    }

    private static String add(TrackInput input) {
        // TODO: Forward the caller's unit and quantity, including invalid domain inputs.
        return "stop";
    }

    private static String recover(TrackInput input) {
        // TODO: Reconcile an observed Pending intent using the caller's lookup availability.
        return "stop";
    }

    private static String retry(TrackInput input) {
        // TODO: Retry the requested identity; let the domain detect changed intent identity.
        return "stop";
    }

    private static String redeliver(TrackInput input) {
        // TODO: Relay pending events; stop when the observed outbox is empty.
        return "stop";
    }

    private static String uncertainCommit(TrackInput input) {
        // TODO: Inspect uncertainty first, then recover an observed persisted Pending intent.
        return "stop";
    }

    private static String lostResponse(TrackInput input) {
        // TODO: Replay payment identity safely; inspect lost line responses and stop after inspection.
        return "stop";
    }
}
