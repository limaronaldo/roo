//! A repository owns nodes; copyable handles and edges do not own nodes.
//!
//! A handle is local identity, not a persistent domain ID. Store identity is
//! included so two repositories with slot zero cannot accept each other's
//! handles. Generations reject identities from removed and reused slots.
//! Removing a node leaves dangling logical edges; callers resolve them through
//! `get`, which rejects stale handles. This is a deliberate deletion policy.

use std::sync::atomic::{AtomicU64, Ordering};

static NEXT_STORE: AtomicU64 = AtomicU64::new(1);

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct NodeId {
    store: u64,
    slot: usize,
    generation: u64,
}

#[derive(Debug)]
pub struct Node {
    label: String,
    parent: Option<NodeId>,
    edges: Vec<NodeId>,
}
impl Node {
    pub fn label(&self) -> &str {
        &self.label
    }
    pub fn parent(&self) -> Option<NodeId> {
        self.parent
    }
    pub fn edges(&self) -> &[NodeId] {
        &self.edges
    }
}

struct Slot {
    generation: u64,
    node: Option<Node>,
}
pub struct Graph {
    identity: u64,
    slots: Vec<Slot>,
}
#[derive(Debug, PartialEq, Eq)]
pub struct InvalidNodeId;

impl Default for Graph {
    fn default() -> Self {
        Self::new()
    }
}
impl Graph {
    /// Panics only if this process has exhausted all store identities.
    pub fn new() -> Self {
        let identity = NEXT_STORE
            .fetch_update(Ordering::Relaxed, Ordering::Relaxed, |id| id.checked_add(1))
            .expect("store identity space exhausted");
        Self {
            identity,
            slots: Vec::new(),
        }
    }

    pub fn insert(
        &mut self,
        label: impl Into<String>,
        parent: Option<NodeId>,
    ) -> Result<NodeId, InvalidNodeId> {
        if let Some(parent) = parent {
            self.get(parent)?;
        }
        let node = Node {
            label: label.into(),
            parent,
            edges: Vec::new(),
        };
        // Exhausted generations are retired, never wrapped back to old IDs.
        let slot = if let Some(index) = self
            .slots
            .iter()
            .position(|s| s.node.is_none() && s.generation != u64::MAX)
        {
            self.slots[index].node = Some(node);
            index
        } else {
            self.slots.push(Slot {
                generation: 0,
                node: Some(node),
            });
            self.slots.len() - 1
        };
        Ok(NodeId {
            store: self.identity,
            slot,
            generation: self.slots[slot].generation,
        })
    }

    pub fn get(&self, id: NodeId) -> Result<&Node, InvalidNodeId> {
        if id.store != self.identity {
            return Err(InvalidNodeId);
        }
        self.slots
            .get(id.slot)
            .filter(|s| s.generation == id.generation)
            .and_then(|s| s.node.as_ref())
            .ok_or(InvalidNodeId)
    }

    pub fn connect(&mut self, from: NodeId, to: NodeId) -> Result<(), InvalidNodeId> {
        self.get(from)?;
        self.get(to)?;
        let node = self.slots[from.slot].node.as_mut().expect("validated node");
        if !node.edges.contains(&to) {
            node.edges.push(to);
        }
        Ok(())
    }

    pub fn remove(&mut self, id: NodeId) -> Result<Node, InvalidNodeId> {
        self.get(id)?;
        let slot = &mut self.slots[id.slot];
        let node = slot.node.take().expect("validated node");
        slot.generation = slot.generation.saturating_add(1);
        Ok(node)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn reuse_rejects_stale_identity_and_dangling_edge() {
        let mut graph = Graph::new();
        let a = graph.insert("a", None).unwrap();
        let b = graph.insert("b", Some(a)).unwrap();
        graph.connect(b, a).unwrap();
        assert_eq!(graph.remove(a).unwrap().label(), "a");
        let replacement = graph.insert("replacement", None).unwrap();
        assert_eq!(a.slot, replacement.slot);
        assert_ne!(a, replacement);
        assert!(graph.get(a).is_err());
        assert!(graph.get(graph.get(b).unwrap().edges()[0]).is_err());
        assert!(graph.get(graph.get(b).unwrap().parent().unwrap()).is_err());
        assert_eq!(graph.get(replacement).unwrap().label(), "replacement");
    }

    #[test]
    fn foreign_handles_are_rejected_even_for_same_slot_and_generation() {
        let mut first = Graph::new();
        let mut second = Graph::new();
        let a = first.insert("a", None).unwrap();
        let b = second.insert("b", None).unwrap();
        assert_eq!((a.slot, a.generation), (b.slot, b.generation));
        assert!(second.get(a).is_err());
        assert!(second.insert("bad parent", Some(a)).is_err());
        assert_eq!(second.connect(b, a), Err(InvalidNodeId));
    }
}
