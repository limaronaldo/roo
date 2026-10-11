package roo.postgres;

import java.util.List;
import static roo.postgres.Domain.*;

record Action(String op, List<String> fields) {
    Action { fields = List.copyOf(fields); }
    String field(int i) { return fields.get(i); }
    Failure failure() { return Failure.valueOf(field(op.equals("reconcile") ? 2 : 3)); }
    static void number(String s) {
        if (!s.matches("[+-]?[0-9]+")) throw new IllegalArgumentException("Malformed integer");
    }
    static Action parse(String text) {
        String[] f = text.split(":", -1);
        switch (f[0]) {
            case "add" -> { count(f, 3); number(f[1]); number(f[2]); }
            case "pay", "refund" -> {
                count(f, 4); token(f[1]); Mode mode = Mode.valueOf(f[2]); Failure.valueOf(f[3]);
                if (f[0].equals("refund") && mode == Mode.decline) throw new IllegalArgumentException("Invalid refund mode");
            }
            case "reconcile" -> {
                count(f, 3);
                if (!f[1].equals("ok") && !f[1].equals("unavailable")) throw new IllegalArgumentException("Invalid lookup");
                if (Failure.valueOf(f[2]) == Failure.prepare) throw new IllegalArgumentException("Invalid reconcile failure");
            }
            case "relay" -> { count(f, 2); Relay.valueOf(f[1]); }
            case "conflict" -> { count(f, 3); token(f[1]); number(f[2]); }
            default -> throw new IllegalArgumentException("Unknown action");
        }
        return new Action(f[0], List.of(f));
    }
    private static void count(String[] f, int n) {
        if (f.length != n) throw new IllegalArgumentException("Invalid action field count");
    }
}
