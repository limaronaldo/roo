//! The channel moves command ownership; a scoped worker shares an immutable
//! policy by borrowing it. No shared mutable aggregate or reference count is
//! needed. The worker returns ownership of the submitted order through join.
use roo::{
    order::{CustomerId, OrderLine, Quantity},
    strategy::Percentage,
    typestate::{Draft, Submitted},
};
use std::{sync::mpsc, thread};

struct SubmitCommand {
    draft: Draft,
}

fn main() {
    let policy = Percentage::new(20).unwrap();
    let (sender, receiver) = mpsc::channel::<SubmitCommand>();
    let submitted: Submitted = thread::scope(|scope| {
        let shared_policy = &policy;
        let worker = scope.spawn(move || {
            let command = receiver.recv().expect("command sender remains alive");
            command
                .draft
                .submit(shared_policy)
                .expect("validated nonempty order")
        });
        let mut draft = Draft::new(CustomerId::new("customer-9").unwrap());
        draft
            .add_line(OrderLine::new("book", Quantity::new(1).unwrap(), 1000).unwrap())
            .unwrap();
        sender
            .send(SubmitCommand { draft })
            .expect("worker receiver remains alive");
        worker.join().expect("worker must finish successfully")
    });
    assert_eq!(submitted.total_cents(), 800);
    println!(
        "Transferred command produced total {} cents",
        submitted.total_cents()
    );
}
