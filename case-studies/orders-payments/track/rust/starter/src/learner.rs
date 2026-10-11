//! Edit the six caller decisions independently; domain behavior stays in the base crate.
use crate::shared::Input;

pub fn decide(input: &Input) -> String {
    match input.exercise.as_str() {
        "e1" => add(input),
        "e2" => recover(input),
        "e3" => retry(input),
        "e4" => redeliver(input),
        "e5" => uncertain_commit(input),
        "e6" => response_lost(input),
        _ => unreachable!("input has already been validated"),
    }
}

fn add(_input: &Input) -> String {
    // TODO: Forward the requested line, including domain-invalid values.
    "stop".to_owned()
}

fn recover(_input: &Input) -> String {
    // TODO: Recover a persisted pending payment through lookup.
    "stop".to_owned()
}

fn retry(_input: &Input) -> String {
    // TODO: Retry the caller payment identity, leaving conflict detection to the domain.
    "stop".to_owned()
}

fn redeliver(_input: &Input) -> String {
    // TODO: Redeliver a pending immutable fact, then stop when clear.
    "stop".to_owned()
}

fn uncertain_commit(_input: &Input) -> String {
    // TODO: Inspect uncertainty before recovering the observed persisted intent.
    "stop".to_owned()
}

fn response_lost(_input: &Input) -> String {
    // TODO: Distinguish payment identity replay from an unreceipted line append.
    "stop".to_owned()
}
