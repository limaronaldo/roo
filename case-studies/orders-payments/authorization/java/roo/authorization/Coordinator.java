package roo.authorization;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/** Local policy and order state share one execution lock; principals are trusted inputs. */
public final class Coordinator {
    public enum Status { DRAFT, APPROVED }
    public enum Outcome { APPROVED, FORBIDDEN, NOT_FOUND, ALREADY_APPROVED }
    public record Observation(boolean allowed) {}
    public record OrderSnapshot(Status status, int approvals) {}
    private record Grant(String principal, String orderId) {}

    private final Object lock = new Object();
    private final Map<String, OrderSnapshot> orders = new HashMap<>();
    private final Set<Grant> grants = new HashSet<>();

    public Coordinator(List<String> orderIds) {
        for (String id : orderIds) {
            orders.put(id, new OrderSnapshot(Status.DRAFT, 0));
        }
    }

    /** Trusted fixture administration, not an operation exposed to a caller. */
    public boolean grant(String principal, String orderId) {
        synchronized (lock) {
            return grants.add(new Grant(principal, orderId));
        }
    }

    public boolean revoke(String principal, String orderId) {
        synchronized (lock) {
            return grants.remove(new Grant(principal, orderId));
        }
    }

    public Observation observe(String principal, String orderId) {
        synchronized (lock) {
            return new Observation(grants.contains(new Grant(principal, orderId)));
        }
    }

    /** Permission check and transition share one critical section. */
    public Outcome approve(String principal, String orderId) {
        synchronized (lock) {
            // Check permission before lookup, including on duplicate calls.
            if (!grants.contains(new Grant(principal, orderId))) {
                return Outcome.FORBIDDEN;
            }
            OrderSnapshot order = orders.get(orderId);
            if (order == null) {
                return Outcome.NOT_FOUND;
            }
            if (order.status() == Status.APPROVED) {
                return Outcome.ALREADY_APPROVED;
            }
            orders.put(orderId, new OrderSnapshot(Status.APPROVED, 1));
            return Outcome.APPROVED;
        }
    }

    /** Trusted test inspection, not an authorized public read endpoint. */
    public OrderSnapshot snapshot(String orderId) {
        synchronized (lock) {
            return orders.get(orderId);
        }
    }
}
