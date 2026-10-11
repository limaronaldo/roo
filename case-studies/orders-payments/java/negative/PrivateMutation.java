package roo.payments;

// Expected diagnostic: add(long,long) has private access in Domain.Order.
final class PrivateMutation {
    void bypass(Domain.Order order) { order.add(1, 1); }
}
