//! Aggregate ownership, runtime strategy, and a consuming state transition.
use roo::{
    order::{CustomerId, OrderLine, Quantity},
    strategy::{Discount, Percentage},
    typestate::Draft,
    view::OrderView,
};

fn main() {
    let policy = Percentage::new(10).expect("valid percentage");
    let selected: &dyn Discount = &policy;
    let draft = Draft::new(CustomerId::new("customer-7").unwrap());
    // Empty submission rejects a business state and returns ownership for retry.
    let mut draft = draft.submit(selected).unwrap_err().draft;
    draft
        .add_line(OrderLine::new("rust-book", Quantity::new(2).unwrap(), 2500).unwrap())
        .unwrap();
    let submitted = draft.submit(selected).unwrap();
    let view = OrderView::new(submitted.order());
    assert_eq!(view.customer_id(), "customer-7");
    assert_eq!(submitted.total_cents(), 4500);
    println!(
        "{}: {} line(s), total {} cents",
        view.customer_id(),
        view.line_count(),
        submitted.total_cents()
    );
}
