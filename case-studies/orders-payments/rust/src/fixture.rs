//! Exact TSV boundary: validate the full input before executing any scenario.
use crate::*;
use std::collections::HashSet;

pub const HEADER: &str = "scenario\tstate\ttotal\tcharge_count\trefund_count\tevent_count\tconsumer_count\tpending_outbox\tlast_result\tpayment_id\trefund_id";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Number {
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
enum Action {
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
fn parse_action(text: &str) -> Result<Action, String> {
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
fn parse(input: &str) -> Result<Vec<(String, Vec<Action>)>, String> {
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

/// Runs fresh resources per row and returns only normalized TSV on success.
///
/// ```
/// use orders_payments_case::fixture::run;
/// let output = run("scenario\tsteps\nsmall\tadd:5:2;pay:p1:approve:none\n").unwrap();
/// assert!(output.contains("small\tPaid\t10\t1\t0\t1\t0\t1\tApproved\tp1\t-"));
/// assert!(run("scenario\tsteps\nbad\tadd:1:1;relay:typo\n").is_err());
/// ```
pub fn run(input: &str) -> Result<String, String> {
    let scenarios = parse(input)?;
    let mut output = format!("{HEADER}\n");
    for (id, actions) in scenarios {
        let mut store = Store::new(Order::new(OrderId::new("O1")?));
        let mut provider = Provider::default();
        let mut consumer = Consumer::default();
        let mut last = Outcome::InvalidState;
        for action in actions {
            last = match action {
                Action::Conflict(id, Number::Value(amount)) => provider.conflict(&id, amount)?,
                Action::Conflict(_, Number::Overflow) => Outcome::Overflow,
                action => {
                    let mut app = Application::new(&mut store, &mut provider, &mut consumer);
                    match action {
                        Action::Add(Number::Value(unit), Number::Value(qty)) => app.add(unit, qty),
                        Action::Add(_, _) => Outcome::Overflow,
                        Action::Pay(id, m, f) => app.pay(id, m, f),
                        Action::Refund(id, m, f) => app.refund(id, m, f),
                        Action::Reconcile(l, f) => app.reconcile(l, f),
                        Action::Relay(m) => app.relay(m),
                        Action::Conflict(_, _) => unreachable!(),
                    }
                }
            };
        }
        let order = store.order();
        output.push_str(&format!(
            "{id}\t{:?}\t{}\t{}\t{}\t{}\t{}\t{}\t{last}\t{}\t{}\n",
            order.state(),
            order.total(),
            provider.charge_count(),
            provider.refund_count(),
            store.event_count(),
            consumer.count(),
            store.pending_outbox(),
            order.payment_id().map_or("-", PaymentId::as_str),
            order.refund_id().map_or("-", RefundId::as_str)
        ));
    }
    Ok(output)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn numeric_grammar_and_signed_range_are_separate() {
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
            assert!(Number::parse(text).is_err(), "accepted {text:?}");
        }
        let result = run("scenario\tsteps\nx\tadd:999999999999999999999:1\n").unwrap();
        assert!(result.contains("x\tDraft\t0\t0\t0\t0\t0\t0\tOverflow\t-\t-"));
    }
    #[test]
    fn malformed_rows_are_rejected_before_execution() {
        for text in [
            "wrong\tsteps\nx\tadd:1:1",
            "scenario\tsteps\nx\tadd:1:1\nx\trelay:ok",
            "scenario\tsteps\nx\tadd:1:1;",
            "scenario\tsteps\nx\tadd:1:1;pay:p1:approve:none;bogus",
            "scenario\tsteps\nx\tadd:1:1\textra",
            "scenario\tsteps\nx\tadd:1",
            "scenario\tsteps\nx\tadd:1:x",
            "scenario\tsteps\nx\tpay:p1:maybe:none",
            "scenario\tsteps\nx\tpay:p-1:approve:none",
            "scenario\tsteps\nx\trefund:r1:decline:none",
            "scenario\tsteps\nx\treconcile:ok:prepare",
            "scenario\tsteps\nx\trelay:unknown",
            "scenario\tsteps\nx\t",
            "scenario\tsteps\r\nx\tadd:1:1",
        ] {
            assert!(run(text).is_err(), "accepted {text:?}");
        }
    }
    #[test]
    fn invalid_adapter_probes_are_fixture_errors() {
        for steps in [
            "conflict:p1:10",
            "add:10:1;pay:p1:approve:none;conflict:p1:10",
            "add:10:1;pay:p1:approve:none;conflict:p1:0",
        ] {
            assert!(run(&format!("scenario\tsteps\nx\t{steps}\n")).is_err());
        }
    }
}
