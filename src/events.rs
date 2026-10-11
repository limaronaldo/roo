//! An owner-directed Observer queue stores identities, not subscriber borrows.
//!
//! Delivery is deferred until the owner drains the queue. Unsubscription also
//! suppresses already queued notifications. IDs are scoped to a queue, like
//! graph handles. Consumers choose how to dispatch returned owned deliveries.

use std::collections::{HashSet, VecDeque};
use std::sync::atomic::{AtomicU64, Ordering};

static NEXT_QUEUE: AtomicU64 = AtomicU64::new(1);
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct ObserverId {
    queue: u64,
    sequence: u64,
}
#[derive(Debug, PartialEq, Eq)]
pub struct Delivery {
    pub observer: ObserverId,
    pub message: String,
}
pub struct EventQueue {
    identity: u64,
    next_observer: u64,
    subscribers: HashSet<ObserverId>,
    pending: VecDeque<Delivery>,
}
impl Default for EventQueue {
    fn default() -> Self {
        Self::new()
    }
}
impl EventQueue {
    /// Panics only if this process exhausts queue identities.
    pub fn new() -> Self {
        let identity = NEXT_QUEUE
            .fetch_update(Ordering::Relaxed, Ordering::Relaxed, |id| id.checked_add(1))
            .expect("queue identity space exhausted");
        Self {
            identity,
            next_observer: 0,
            subscribers: HashSet::new(),
            pending: VecDeque::new(),
        }
    }
    /// Returns `None` if this queue has exhausted subscriber identities.
    pub fn subscribe(&mut self) -> Option<ObserverId> {
        let next = self.next_observer.checked_add(1)?;
        let id = ObserverId {
            queue: self.identity,
            sequence: self.next_observer,
        };
        self.next_observer = next;
        self.subscribers.insert(id);
        Some(id)
    }
    pub fn unsubscribe(&mut self, id: ObserverId) -> bool {
        self.subscribers.remove(&id)
    }
    /// Returns an undelivered owned message if the subscriber is not active.
    pub fn enqueue(&mut self, id: ObserverId, message: String) -> Result<(), String> {
        if !self.subscribers.contains(&id) {
            return Err(message);
        }
        self.pending.push_back(Delivery {
            observer: id,
            message,
        });
        Ok(())
    }
    pub fn drain(&mut self) -> Vec<Delivery> {
        self.pending
            .drain(..)
            .filter(|delivery| self.subscribers.contains(&delivery.observer))
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn unsubscribe_suppresses_pending_delivery_and_preserves_rejected_payload() {
        let mut queue = EventQueue::new();
        let old = queue.subscribe().unwrap();
        queue.enqueue(old, "already queued".into()).unwrap();
        assert!(queue.unsubscribe(old));
        let new = queue.subscribe().unwrap();
        assert_ne!(old, new);
        queue.enqueue(new, "live".into()).unwrap();
        assert_eq!(
            queue.enqueue(old, "retry elsewhere".into()),
            Err("retry elsewhere".into())
        );
        assert_eq!(
            queue.drain(),
            vec![Delivery {
                observer: new,
                message: "live".into()
            }]
        );
        assert!(queue.drain().is_empty());
    }
    #[test]
    fn foreign_subscriber_is_rejected() {
        let mut first = EventQueue::new();
        let mut second = EventQueue::new();
        let id = first.subscribe().unwrap();
        second.subscribe().unwrap();
        assert!(second.enqueue(id, "foreign".into()).is_err());
        assert!(!second.unsubscribe(id));
    }
}
