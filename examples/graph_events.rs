//! Nonowning graph edges and deferred owner-directed event delivery.
use roo::{events::EventQueue, graph::Graph};

fn main() {
    let mut graph = Graph::new();
    let parent = graph.insert("project", None).unwrap();
    let child = graph.insert("task", Some(parent)).unwrap();
    graph.connect(child, parent).unwrap();
    let removed = graph.remove(parent).unwrap();
    assert!(
        graph
            .get(graph.get(child).unwrap().parent().unwrap())
            .is_err()
    );
    let replacement = graph.insert("new project", None).unwrap();
    assert_ne!(parent, replacement);

    let mut queue = EventQueue::new();
    let observer = queue.subscribe().unwrap();
    queue
        .enqueue(observer, format!("removed {}", removed.label()))
        .unwrap();
    for delivery in queue.drain() {
        println!("{}", delivery.message);
    }
    queue.unsubscribe(observer);
    assert!(queue.enqueue(observer, "late event".into()).is_err());
}
