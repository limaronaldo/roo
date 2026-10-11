//! Run with: cargo run --offline --manifest-path case-studies/orders-payments/rust/Cargo.toml --example recovery
use orders_payments_case::*;
fn main() {
    let mut store = Store::new(Order::new(OrderId::new("O1").unwrap()));
    let mut provider = Provider::default();
    let mut consumer = Consumer::default();
    {
        let mut checkout = Application::new(&mut store, &mut provider, &mut consumer);
        assert_eq!(checkout.add(100, 2), Outcome::Added);
        assert_eq!(checkout.add(50, 1), Outcome::Added);
        println!(
            "Payment observation: {}",
            checkout.pay(
                PaymentId::new("p1").unwrap(),
                Mode::TimeoutAfter,
                Failure::None
            )
        );
    }
    println!(
        "Committed state: {:?}; remote charges: {}",
        store.order().state(),
        provider.charge_count()
    );
    {
        let mut recovery = Application::new(&mut store, &mut provider, &mut consumer);
        println!(
            "Recovery: {}",
            recovery.reconcile(Lookup::Ok, Failure::None)
        );
        println!(
            "Refund: {}",
            recovery.refund(RefundId::new("r1").unwrap(), Mode::Approve, Failure::None)
        );
        println!("First relay: {}", recovery.relay(RelayMode::AckFail));
        println!("Retry relay: {}", recovery.relay(RelayMode::Ok));
    }
    assert_eq!(store.order().state(), State::Refunded);
    assert_eq!(provider.charge_count(), 1);
    assert_eq!(provider.refund_count(), 1);
    assert_eq!(consumer.count(), 2);
    println!(
        "Final state: {:?}; unique facts: {}",
        store.order().state(),
        consumer.count()
    );
}
