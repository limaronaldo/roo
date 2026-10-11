//! Exact TSV boundary: validate the full input before executing any scenario.
use crate::*;
use std::collections::HashSet;

pub const HEADER: &str = "scenario\tstate\ttotal\tcharge_count\trefund_count\tevent_count\tconsumer_count\tpending_outbox\tlast_result\tpayment_id\trefund_id";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Number {
    Value(i64),
    Overflow,
}
impl Number {
    fn parse(text: &str) -> Result<Self, String> {
        let digits = text.strip_prefix(['+', '-']).unwrap_or(text);
        if digits.is_empty() || !digits.bytes().all(|b| b.is_ascii_digit()) {
            return Err(format!("malformed integer: {text}"));
        }
        Ok(text.parse::<i64>().map_or(Self::Overflow, Self::Value))
    }
}
#[derive(Debug)]
pub enum Action {
    Add(Number, Number),
    Pay(PaymentId, Mode, Failure),
    Refund(RefundId, Mode, Failure),
    Reconcile(Lookup, Failure),
    Relay(RelayMode),
    Conflict(PaymentId, Number),
}
fn mode(text: &str, refund: bool) -> Result<Mode, String> {
    match text {
        "approve" => Ok(Mode::Approve),
        "decline" if !refund => Ok(Mode::Decline),
        "timeout_before" => Ok(Mode::TimeoutBefore),
        "timeout_after" => Ok(Mode::TimeoutAfter),
        _ => Err(format!("invalid mode: {text}")),
    }
}
fn failure(text: &str, prepare: bool) -> Result<Failure, String> {
    match text {
        "none" => Ok(Failure::None),
        "prepare" if prepare => Ok(Failure::Prepare),
        "commit" => Ok(Failure::Commit),
        _ => Err(format!("invalid failure: {text}")),
    }
}
pub fn parse_action(text: &str) -> Result<Action, String> {
    let fields: Vec<_> = text.split(':').collect();
    match fields.as_slice() {
        ["add", unit, qty] => Ok(Action::Add(Number::parse(unit)?, Number::parse(qty)?)),
        ["pay", id, m, f] => Ok(Action::Pay(
            PaymentId::new(id)?,
            mode(m, false)?,
            failure(f, true)?,
        )),
        ["refund", id, m, f] => Ok(Action::Refund(
            RefundId::new(id)?,
            mode(m, true)?,
            failure(f, true)?,
        )),
        ["reconcile", lookup, f] => {
            let lookup = match *lookup {
                "ok" => Lookup::Ok,
                "unavailable" => Lookup::Unavailable,
                _ => return Err(format!("invalid lookup: {lookup}")),
            };
            Ok(Action::Reconcile(lookup, failure(f, false)?))
        }
        ["relay", m] => {
            let m = match *m {
                "ok" => RelayMode::Ok,
                "send_fail" => RelayMode::SendFail,
                "ack_fail" => RelayMode::AckFail,
                _ => return Err(format!("invalid relay: {m}")),
            };
            Ok(Action::Relay(m))
        }
        ["conflict", id, amount] => Ok(Action::Conflict(
            PaymentId::new(id)?,
            Number::parse(amount)?,
        )),
        _ => Err(format!("unknown operation or wrong field count: {text}")),
    }
}
pub fn parse(input: &str) -> Result<Vec<(String, Vec<Action>)>, String> {
    if input.contains('\r') {
        return Err("LF line endings required".to_owned());
    }
    let mut lines = input.split('\n');
    if lines.next() != Some("scenario\tsteps") {
        return Err("expected scenario/steps TSV header".to_owned());
    }
    let mut seen = HashSet::new();
    let mut scenarios = Vec::new();
    for (offset, line) in lines.enumerate() {
        if line.is_empty() {
            continue;
        }
        let fields: Vec<_> = line.split('\t').collect();
        let [id, steps] = fields.as_slice() else {
            return Err(format!("line {} requires two columns", offset + 2));
        };
        if id.is_empty() || !id.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'_') {
            return Err(format!("invalid scenario ID: {id}"));
        }
        if !seen.insert((*id).to_owned()) {
            return Err(format!("duplicate scenario: {id}"));
        }
        let actions = steps
            .split(';')
            .map(parse_action)
            .collect::<Result<Vec<_>, _>>()?;
        scenarios.push(((*id).to_owned(), actions));
    }
    Ok(scenarios)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn numeric_grammar_distinguishes_overflow_from_malformed_text() {
        assert_eq!(
            Number::parse("9223372036854775807").unwrap(),
            Number::Value(i64::MAX)
        );
        assert_eq!(
            Number::parse("-9223372036854775808").unwrap(),
            Number::Value(i64::MIN)
        );
        for text in [
            "9223372036854775808",
            "-9223372036854775809",
            "999999999999999999999999999999",
        ] {
            assert_eq!(Number::parse(text).unwrap(), Number::Overflow);
        }
        for text in ["", "+", "-", "1.0", " 1", "1 ", "1e3", "--1", "１２"] {
            assert!(Number::parse(text).is_err());
        }
    }
    #[test]
    fn full_fixture_is_parsed_before_execution() {
        for input in [
            "bad\tsteps\nx\tadd:1:1",
            "scenario\tsteps\nx\tadd:1:1\nx\trelay:ok",
            "scenario\tsteps\nx\tadd:1:1;",
            "scenario\tsteps\nx\tadd:1:1;bogus",
            "scenario\tsteps\nx\tadd:1:x",
            "scenario\tsteps\nx\trefund:r1:decline:none",
            "scenario\tsteps\nx\treconcile:ok:prepare",
            "scenario\tsteps\r\nx\tadd:1:1",
        ] {
            assert!(parse(input).is_err(), "accepted {input:?}");
        }
        let rows = parse("scenario\tsteps\nx\tadd:1:1;pay:p1:approve:none\n").unwrap();
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0].1.len(), 2);
    }
}
