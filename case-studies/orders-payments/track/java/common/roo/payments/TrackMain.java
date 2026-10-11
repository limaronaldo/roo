package roo.payments;

/** Shared command protocol for independently compiled starter and completed policies. */
public final class TrackMain {
    private TrackMain() { }

    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("policy")) {
            final TrackInput input;
            try { input = TrackInput.parsePolicyArguments(args); }
            catch (IllegalArgumentException invalid) { invalidArguments(); return; }
            System.out.print(LearnerPolicy.decide(input) + "\n");
            return;
        }
        if (args.length == 3 && args[0].equals("native")
                && args[1].matches("e[1-4]")
                && (args[2].equals("composition") || args[2].equals("inheritance"))) {
            try {
                TrackNative.run(args[1], args[2].equals("inheritance"));
                System.out.println("PASS " + args[1] + " " + args[2]);
            } catch (TrackNative.BehaviorFailure failure) {
                System.err.println("BEHAVIOR " + args[1] + ": " + failure.getMessage());
                System.exit(1);
            }
            return;
        }
        invalidArguments();
    }

    private static void invalidArguments() {
        System.err.println("Invalid track arguments");
        System.exit(2);
    }
}
