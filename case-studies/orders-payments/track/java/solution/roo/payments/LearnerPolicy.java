package roo.payments;

/** Completed caller decisions use only observations and requested input. */
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
        return "add:" + input.unit() + ":" + input.quantity();
    }

    private static String recover(TrackInput input) {
        return input.state() == Domain.State.Pending && !input.paymentId().equals("-")
                ? "reconcile:" + input.lookup() + ":none" : "inspect";
    }

    private static String retry(TrackInput input) {
        return payOrInspect(input.requestedPaymentId());
    }

    private static String redeliver(TrackInput input) {
        return input.pendingOutbox() > 0 ? "relay:ok" : "stop";
    }

    private static String uncertainCommit(TrackInput input) {
        return input.phase().equals("uncertain_commit") ? "inspect" : recover(input);
    }

    private static String lostResponse(TrackInput input) {
        return switch (input.phase()) {
            case "payment_response_lost" -> payOrInspect(input.paymentId().equals("-")
                    ? input.requestedPaymentId() : input.paymentId());
            case "line_response_lost" -> "inspect";
            case "line_inspected" -> "stop";
            default -> throw new IllegalArgumentException("Unknown phase");
        };
    }

    private static String payOrInspect(String identity) {
        return identity.equals("-") ? "inspect" : "pay:" + identity + ":approve:none";
    }
}
