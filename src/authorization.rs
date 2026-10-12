//! Caller permission and invariant coordination meet at one execution boundary.
//!
//! Observations are detached hints, never credentials. Policy changes and order
//! approval acquire the same lock, so a completed revocation affects the next
//! approval even if its caller previously observed permission. This is a local,
//! in-memory example with trusted principals, not authentication or API security.

use std::collections::{HashMap, HashSet};
use std::sync::{Mutex, MutexGuard};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Status {
    Draft,
    Approved,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct OrderSnapshot {
    pub status: Status,
    pub approvals: u32,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Observation {
    pub allowed: bool,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Error {
    Forbidden,
    NotFound,
    AlreadyApproved,
    Unavailable,
}

struct State {
    orders: HashMap<String, OrderSnapshot>,
    grants: HashSet<(String, String)>,
}

/// Owns both local policy and order state. No mutable state escapes its lock.
pub struct Coordinator {
    state: Mutex<State>,
}

impl Coordinator {
    pub fn new(order_ids: &[&str]) -> Self {
        Self {
            state: Mutex::new(State {
                orders: order_ids
                    .iter()
                    .map(|id| {
                        (
                            (*id).to_owned(),
                            OrderSnapshot {
                                status: Status::Draft,
                                approvals: 0,
                            },
                        )
                    })
                    .collect(),
                grants: HashSet::new(),
            }),
        }
    }

    fn lock(&self) -> Result<MutexGuard<'_, State>, Error> {
        // Poisoned state is unavailable; never continue by bypassing the check.
        self.state.lock().map_err(|_| Error::Unavailable)
    }

    /// Trusted fixture administration, not an operation exposed to a caller.
    pub fn grant(&self, principal: &str, order_id: &str) -> Result<bool, Error> {
        Ok(self
            .lock()?
            .grants
            .insert((principal.to_owned(), order_id.to_owned())))
    }

    /// Returns only after the policy change holds under the execution lock.
    pub fn revoke(&self, principal: &str, order_id: &str) -> Result<bool, Error> {
        Ok(self
            .lock()?
            .grants
            .remove(&(principal.to_owned(), order_id.to_owned())))
    }

    pub fn observe(&self, principal: &str, order_id: &str) -> Result<Observation, Error> {
        Ok(Observation {
            allowed: self
                .lock()?
                .grants
                .contains(&(principal.to_owned(), order_id.to_owned())),
        })
    }

    /// Rechecks current permission and installs the transition in one section.
    /// Revocation ordered after this section cannot undo a completed approval.
    pub fn approve(&self, principal: &str, order_id: &str) -> Result<(), Error> {
        let mut state = self.lock()?;
        // Check permission before looking up state, including on duplicate calls.
        if !state
            .grants
            .contains(&(principal.to_owned(), order_id.to_owned()))
        {
            return Err(Error::Forbidden);
        }
        let order = state.orders.get_mut(order_id).ok_or(Error::NotFound)?;
        if order.status == Status::Approved {
            return Err(Error::AlreadyApproved);
        }
        *order = OrderSnapshot {
            status: Status::Approved,
            approvals: 1,
        };
        Ok(())
    }

    /// Trusted test inspection, not an authorized public read endpoint.
    pub fn snapshot(&self, order_id: &str) -> Result<Option<OrderSnapshot>, Error> {
        Ok(self.lock()?.orders.get(order_id).copied())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::{Barrier, mpsc};
    use std::thread;
    use std::time::Duration;

    const WAIT: Duration = Duration::from_secs(5);

    #[test]
    fn revocation_between_observation_and_execution_denies_without_effect() {
        let coordinator = Coordinator::new(&["order-1"]);
        coordinator.grant("alice", "order-1").unwrap();
        thread::scope(|scope| {
            let (observed_tx, observed_rx) = mpsc::channel();
            let (execute_tx, execute_rx) = mpsc::channel();
            let worker_coordinator = &coordinator;
            let caller = scope.spawn(move || {
                let observation = worker_coordinator.observe("alice", "order-1").unwrap();
                observed_tx.send(observation).unwrap();
                execute_rx.recv_timeout(WAIT).unwrap();
                // The prior observation cannot be supplied as a credential.
                worker_coordinator.approve("alice", "order-1")
            });
            assert!(observed_rx.recv_timeout(WAIT).unwrap().allowed);
            assert!(coordinator.revoke("alice", "order-1").unwrap());
            execute_tx.send(()).unwrap();
            assert_eq!(caller.join().unwrap(), Err(Error::Forbidden));
        });
        assert_eq!(
            coordinator.snapshot("order-1").unwrap().unwrap(),
            OrderSnapshot {
                status: Status::Draft,
                approvals: 0
            }
        );
    }

    #[test]
    fn execution_before_revocation_stays_committed_and_next_call_is_denied() {
        let coordinator = Coordinator::new(&["order-1"]);
        coordinator.grant("alice", "order-1").unwrap();
        thread::scope(|scope| {
            let (completed_tx, completed_rx) = mpsc::channel();
            let worker_coordinator = &coordinator;
            let caller = scope.spawn(move || {
                completed_tx
                    .send(worker_coordinator.approve("alice", "order-1"))
                    .unwrap();
            });
            assert_eq!(completed_rx.recv_timeout(WAIT).unwrap(), Ok(()));
            coordinator.revoke("alice", "order-1").unwrap();
            caller.join().unwrap();
        });
        assert_eq!(
            coordinator.approve("alice", "order-1"),
            Err(Error::Forbidden)
        );
        assert_eq!(
            coordinator.snapshot("order-1").unwrap().unwrap(),
            OrderSnapshot {
                status: Status::Approved,
                approvals: 1
            }
        );
    }

    #[test]
    fn competing_approvals_install_one_transition() {
        let coordinator = Coordinator::new(&["order-1"]);
        coordinator.grant("alice", "order-1").unwrap();
        let start = Barrier::new(3);
        thread::scope(|scope| {
            let request = || {
                start.wait();
                coordinator.approve("alice", "order-1")
            };
            let first = scope.spawn(request);
            let second = scope.spawn(request);
            start.wait();
            let results = [first.join().unwrap(), second.join().unwrap()];
            assert_eq!(results.iter().filter(|result| result.is_ok()).count(), 1);
            assert_eq!(
                results
                    .iter()
                    .filter(|result| **result == Err(Error::AlreadyApproved))
                    .count(),
                1
            );
        });
        assert_eq!(
            coordinator.snapshot("order-1").unwrap().unwrap().approvals,
            1
        );
    }

    #[test]
    fn detached_observations_and_snapshots_cannot_change_coordinator_state() {
        let coordinator = Coordinator::new(&["order-1"]);
        coordinator.grant("alice", "order-1").unwrap();
        let mut observation = coordinator.observe("alice", "order-1").unwrap();
        let mut snapshot = coordinator.snapshot("order-1").unwrap().unwrap();
        coordinator.revoke("alice", "order-1").unwrap();
        observation.allowed = true;
        snapshot.status = Status::Approved;
        snapshot.approvals = 1;
        assert!(observation.allowed);
        assert_eq!(snapshot.status, Status::Approved);
        assert_eq!(
            coordinator.approve("alice", "order-1"),
            Err(Error::Forbidden)
        );
        assert_eq!(
            coordinator.snapshot("order-1").unwrap().unwrap().approvals,
            0
        );
    }
}
