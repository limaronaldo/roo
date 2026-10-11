package roo.postgres;

final class PrivateMutation {
    void violate(Domain.Order order) { order.total = 0; }
}
