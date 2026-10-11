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

fn add(input: &Input) -> String {
    format!("add:{}:{}", input.unit, input.quantity)
}

fn recover(input: &Input) -> String {
    if input.state == "Pending" && input.payment_id != "-" {
        format!("reconcile:{}:none", input.lookup)
    } else {
        "inspect".to_owned()
    }
}

fn retry(input: &Input) -> String {
    if input.requested_payment_id == "-" {
        "inspect".to_owned()
    } else {
        format!("pay:{}:approve:none", input.requested_payment_id)
    }
}

fn redeliver(input: &Input) -> String {
    if input.pending_outbox > 0 {
        "relay:ok".to_owned()
    } else {
        "stop".to_owned()
    }
}

fn uncertain_commit(input: &Input) -> String {
    if input.phase == "uncertain_commit" {
        "inspect".to_owned()
    } else {
        recover(input)
    }
}

fn response_lost(input: &Input) -> String {
    match input.phase.as_str() {
        "payment_response_lost" => {
            let id = if input.payment_id != "-" {
                &input.payment_id
            } else {
                &input.requested_payment_id
            };
            if id == "-" {
                "inspect".to_owned()
            } else {
                format!("pay:{id}:approve:none")
            }
        }
        "line_response_lost" => "inspect".to_owned(),
        "line_inspected" => "stop".to_owned(),
        _ => unreachable!("validated phase"),
    }
}
