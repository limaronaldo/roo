//! Validated process boundary and native scenarios shared by the two policies.
use orders_payments_case::*;

#[allow(dead_code)]
#[derive(Debug)]
pub struct Input {
    pub exercise: String,
    pub phase: String,
    pub state: String,
    pub total: i64,
    pub payment_id: String,
    pub last_result: String,
    pub pending_outbox: i64,
    pub requested_payment_id: String,
    pub unit: i64,
    pub quantity: i64,
    pub lookup: String,
}

fn integer(text: &str) -> Result<i64, ()> {
    let digits = text.strip_prefix('-').unwrap_or(text);
    if digits.is_empty() || !digits.bytes().all(|b| b.is_ascii_digit()) {
        return Err(());
    }
    text.parse().map_err(|_| ())
}

fn identity(text: &str) -> bool {
    text == "-"
        || ((1..=64).contains(&text.len()) && text.bytes().all(|b| b.is_ascii_alphanumeric()))
}

fn parse(fields: &[String]) -> Result<Input, ()> {
    let [
        exercise,
        phase,
        state,
        total,
        payment_id,
        last_result,
        pending,
        requested,
        unit,
        quantity,
        lookup,
    ] = fields
    else {
        return Err(());
    };
    let valid_phase = match exercise.as_str() {
        "e1" => phase == "add",
        "e2" => phase == "recover",
        "e3" => phase == "retry",
        "e4" => phase == "redeliver",
        "e5" => matches!(phase.as_str(), "uncertain_commit" | "recover"),
        "e6" => matches!(
            phase.as_str(),
            "payment_response_lost" | "line_response_lost" | "line_inspected"
        ),
        _ => false,
    };
    if !valid_phase
        || !matches!(
            state.as_str(),
            "Draft" | "Pending" | "Paid" | "Declined" | "Refunding" | "Refunded"
        )
        || !identity(payment_id)
        || !identity(requested)
        || !matches!(
            last_result.as_str(),
            "-" | "Added"
                | "InvalidLine"
                | "Overflow"
                | "InvalidOrder"
                | "InvalidState"
                | "IntentConflict"
                | "Approved"
                | "Declined"
                | "Unknown"
                | "NotFound"
                | "AlreadyApplied"
                | "AlreadyDeclined"
                | "LocalPrepareFailed"
                | "LocalCommitFailed"
                | "KeyConflict"
                | "RelayOk"
                | "RelaySendFailed"
                | "RelayAckFailed"
        )
        || !matches!(lookup.as_str(), "ok" | "unavailable")
    {
        return Err(());
    }
    let total = integer(total)?;
    let pending_outbox = integer(pending)?;
    let unit = integer(unit)?;
    let quantity = integer(quantity)?;
    if total < 0 || pending_outbox < 0 {
        return Err(());
    }
    Ok(Input {
        exercise: exercise.clone(),
        phase: phase.clone(),
        state: state.clone(),
        total,
        payment_id: payment_id.clone(),
        last_result: last_result.clone(),
        pending_outbox,
        requested_payment_id: requested.clone(),
        unit,
        quantity,
        lookup: lookup.clone(),
    })
}

pub fn run(decide: fn(&Input) -> String) -> i32 {
    let arguments: Vec<String> = std::env::args().skip(1).collect();
    match arguments.first().map(String::as_str) {
        Some("policy") => match parse(&arguments[1..]) {
            Ok(input) => {
                println!("{}", decide(&input));
                0
            }
            Err(()) => {
                eprintln!("Invalid input.");
                2
            }
        },
        Some("native") if arguments.len() == 3 && arguments[2] == "composition" => {
            match native(&arguments[1], decide) {
                Ok(()) => {
                    println!("PASS {} composition", arguments[1]);
                    0
                }
                Err(CheckError::Behavior(message)) => {
                    eprintln!("BEHAVIOR {}: {message}", arguments[1]);
                    1
                }
                Err(CheckError::Infrastructure(message)) => {
                    eprintln!("Infrastructure error: {message}");
                    2
                }
            }
        }
        _ => {
            eprintln!("Invalid input.");
            2
        }
    }
}

enum CheckError {
    Behavior(String),
    Infrastructure(String),
}
type Check = Result<(), CheckError>;
fn baseline(ok: bool, message: &str) -> Check {
    if ok {
        Ok(())
    } else {
        Err(CheckError::Infrastructure(message.to_owned()))
    }
}
fn verify(ok: bool, message: &str) -> Check {
    if ok {
        Ok(())
    } else {
        Err(CheckError::Behavior(message.to_owned()))
    }
}

struct Lab {
    store: Store,
    provider: Provider,
    consumer: Consumer,
}
impl Lab {
    fn new() -> Self {
        Self {
            store: Store::new(Order::new(
                OrderId::new("O1").expect("valid fixed order identity"),
            )),
            provider: Provider::default(),
            consumer: Consumer::default(),
        }
    }
    fn app(&mut self) -> Application<'_> {
        Application::new(&mut self.store, &mut self.provider, &mut self.consumer)
    }
    fn seed(&mut self, unit: i64, quantity: i64, extra: i64) -> Check {
        let total = unit * quantity + extra;
        baseline(
            self.app().add(unit, quantity) == Outcome::Added,
            "first seed line",
        )?;
        baseline(
            self.app().add(extra, 1) == Outcome::Added,
            "second seed line",
        )?;
        baseline(
            self.store.order().total() == total && self.store.order().line_count() == 2,
            "seed snapshot",
        )
    }
    fn pay(&mut self, id: &str, mode: Mode, failure: Failure) -> Outcome {
        self.app().pay(
            PaymentId::new(id).expect("valid scenario identity"),
            mode,
            failure,
        )
    }
    fn observe(
        &self,
        exercise: &str,
        phase: &str,
        requested: &str,
        line: (i64, i64),
        lookup: &str,
        last: &str,
    ) -> Input {
        let (unit, quantity) = line;
        let order = self.store.order();
        Input {
            exercise: exercise.to_owned(),
            phase: phase.to_owned(),
            state: format!("{:?}", order.state()),
            total: order.total(),
            payment_id: order.payment_id().map_or("-", PaymentId::as_str).to_owned(),
            last_result: last.to_owned(),
            pending_outbox: self.store.pending_outbox() as i64,
            requested_payment_id: requested.to_owned(),
            unit,
            quantity,
            lookup: lookup.to_owned(),
        }
    }
}

fn decision(decide: fn(&Input) -> String, input: &Input, expected: &str) -> Check {
    verify(
        decide(input) == expected,
        "learner selected the wrong next action",
    )
}

// Validate the learner action before executing its actual arguments.
fn perform(
    lab: &mut Lab,
    decide: fn(&Input) -> String,
    input: &Input,
    expected: &str,
) -> Result<Outcome, CheckError> {
    let action = decide(input);
    verify(action == expected, "learner selected the wrong next action")?;
    let fields: Vec<_> = action.split(':').collect();
    let invalid = || CheckError::Behavior("learner returned an invalid action".to_owned());
    match fields.as_slice() {
        ["add", unit, quantity] => {
            let unit = integer(unit).map_err(|_| invalid())?;
            let quantity = integer(quantity).map_err(|_| invalid())?;
            Ok(lab.app().add(unit, quantity))
        }
        ["pay", id, "approve", "none"] => {
            let id = PaymentId::new(id).map_err(|_| invalid())?;
            Ok(lab.app().pay(id, Mode::Approve, Failure::None))
        }
        ["reconcile", lookup, "none"] => {
            let lookup = match *lookup {
                "ok" => Lookup::Ok,
                "unavailable" => Lookup::Unavailable,
                _ => return Err(invalid()),
            };
            Ok(lab.app().reconcile(lookup, Failure::None))
        }
        ["relay", "ok"] => Ok(lab.app().relay(RelayMode::Ok)),
        _ => Err(invalid()),
    }
}

fn native(exercise: &str, decide: fn(&Input) -> String) -> Check {
    match exercise {
        "e1" => native_add(decide),
        "e2" => native_recover(decide),
        "e3" => native_retry(decide),
        "e4" => native_relay(decide),
        _ => Err(CheckError::Infrastructure(
            "invalid native exercise".to_owned(),
        )),
    }
}

fn native_add(decide: fn(&Input) -> String) -> Check {
    let mut lab = Lab::new();
    lab.seed(100, 2, 50)?;
    for (unit, quantity, outcome) in [
        (13, 0, Outcome::InvalidLine),
        (0, 7, Outcome::InvalidLine),
        (i64::MAX, 2, Outcome::Overflow),
        (i64::MAX, 1, Outcome::Overflow),
    ] {
        let before = lab.store.order().clone();
        let input = lab.observe("e1", "add", "-", (unit, quantity), "ok", "-");
        let actual = perform(&mut lab, decide, &input, &format!("add:{unit}:{quantity}"))?;
        verify(actual == outcome, "expected domain rejection")?;
        verify(
            lab.store.order() == &before
                && lab.store.order().state() == State::Draft
                && lab.provider.charge_count() == 0
                && lab.store.event_count() == 0,
            "rejected line changed committed facts",
        )?;
    }
    let mut lab = Lab::new();
    lab.seed(73, 3, 19)?;
    {
        let (unit, quantity) = (41, 5);
        let before = lab.store.order().clone();
        let mut expected = Lab::new();
        expected.seed(73, 3, 19)?;
        baseline(
            expected.app().add(unit, quantity) == Outcome::Added,
            "valid line reference setup",
        )?;
        let input = lab.observe("e1", "add", "-", (unit, quantity), "ok", "Added");
        let actual = perform(&mut lab, decide, &input, &format!("add:{unit}:{quantity}"))?;
        verify(
            actual == Outcome::Added,
            "valid requested line was not added",
        )?;
        verify(
            lab.store.order() == expected.store.order()
                && lab.store.order().total() == before.total() + unit * quantity
                && lab.store.order().line_count() == before.line_count() + 1
                && lab.store.order().state() == State::Draft
                && lab.store.event_count() == 0
                && lab.provider.charge_count() == 0,
            "valid line facts differ",
        )?;
    }
    Ok(())
}

fn pending(lab: &Lab, id: &str, total: i64) -> bool {
    lab.store.order().state() == State::Pending
        && lab.store.order().total() == total
        && lab.store.order().payment_id().map(PaymentId::as_str) == Some(id)
        && lab.provider.charge_count() == 1
        && lab.store.event_count() == 0
}
fn paid(lab: &Lab, id: &str, total: i64) -> bool {
    if lab.store.order().state() != State::Paid
        || lab.store.order().total() != total
        || lab.store.order().payment_id().map(PaymentId::as_str) != Some(id)
        || lab.provider.charge_count() != 1
        || lab.store.event_count() != 1
    {
        return false;
    }
    lab.store.events().next().is_some_and(|fact| {
        fact.id().as_str() == format!("payment:{id}")
            && fact.kind() == EventKind::PaymentApproved
            && fact.payment_id().as_str() == id
            && fact.order_id().as_str() == "O1"
            && fact.amount().minor() == total
            && fact.currency() == "USD"
            && fact.refund_id().is_none()
    })
}

fn native_recover(decide: fn(&Input) -> String) -> Check {
    for (id, unit, quantity, extra) in [("p1", 100, 2, 50), ("Recover27", 211, 3, 5)] {
        let total = unit * quantity + extra;
        let mut lab = Lab::new();
        lab.seed(unit, quantity, extra)?;
        baseline(
            lab.pay(id, Mode::Approve, Failure::Commit) == Outcome::LocalCommitFailed,
            "terminal commit failure result",
        )?;
        baseline(pending(&lab, id, total), "terminal commit failure snapshot")?;
        let input = lab.observe("e2", "recover", "-", (0, 0), "ok", "LocalCommitFailed");
        let actual = perform(&mut lab, decide, &input, "reconcile:ok:none")?;
        verify(
            actual == Outcome::Approved && paid(&lab, id, total),
            "recovery did not finalize the existing effect",
        )?;
    }
    let mut lab = Lab::new();
    lab.seed(47, 7, 9)?;
    baseline(
        lab.pay("Lookup9", Mode::Approve, Failure::Commit) == Outcome::LocalCommitFailed,
        "unavailable lookup setup result",
    )?;
    baseline(
        pending(&lab, "Lookup9", 338),
        "unavailable lookup setup snapshot",
    )?;
    let before = lab.store.order().clone();
    let input = lab.observe(
        "e2",
        "recover",
        "-",
        (0, 0),
        "unavailable",
        "LocalCommitFailed",
    );
    let actual = perform(&mut lab, decide, &input, "reconcile:unavailable:none")?;
    verify(
        actual == Outcome::Unknown && lab.store.order() == &before && pending(&lab, "Lookup9", 338),
        "unavailable lookup changed pending intent",
    )
}

fn native_retry(decide: fn(&Input) -> String) -> Check {
    let mut lab = Lab::new();
    lab.seed(137, 2, 31)?;
    baseline(
        lab.pay("Retry42", Mode::TimeoutAfter, Failure::None) == Outcome::Unknown
            && pending(&lab, "Retry42", 305),
        "timeout-after snapshot",
    )?;
    let before = lab.store.order().clone();
    let changed = lab.observe("e3", "retry", "Changed43", (0, 0), "ok", "Unknown");
    let actual = perform(&mut lab, decide, &changed, "pay:Changed43:approve:none")?;
    verify(
        actual == Outcome::IntentConflict
            && lab.store.order() == &before
            && pending(&lab, "Retry42", 305),
        "changed caller identity replaced intent",
    )?;
    let retry = lab.observe("e3", "retry", "Retry42", (0, 0), "ok", "IntentConflict");
    let actual = perform(&mut lab, decide, &retry, "pay:Retry42:approve:none")?;
    verify(
        actual == Outcome::Approved && paid(&lab, "Retry42", 305),
        "same identity did not finalize once",
    )?;
    let fixture = fixture::run("scenario\tsteps\nchanged\tadd:137:2;add:31:1;pay:Retry42:timeout_after:none;pay:Retry42:approve:none;conflict:Retry42:306\n")
        .map_err(|_| CheckError::Infrastructure("fingerprint fixture failed".to_owned()))?;
    verify(
        fixture.lines().nth(1)
            == Some("changed\tPaid\t305\t1\t0\t1\t0\t1\tKeyConflict\tRetry42\t-"),
        "changed fingerprint did not preserve the original effect",
    )
}

fn native_relay(decide: fn(&Input) -> String) -> Check {
    let mut lab = Lab::new();
    lab.seed(83, 4, 17)?;
    baseline(
        lab.pay("Relay58", Mode::Approve, Failure::None) == Outcome::Approved
            && paid(&lab, "Relay58", 349),
        "approved relay seed",
    )?;
    baseline(
        lab.app().relay(RelayMode::AckFail) == Outcome::RelayAckFailed
            && lab.consumer.count() == 1
            && lab.store.pending_outbox() == 1,
        "acknowledgement failure snapshot",
    )?;
    let fact = lab.consumer.facts()[0].clone();
    baseline(
        lab.store.events().next() == Some(&fact),
        "delivered fact content",
    )?;
    let input = lab.observe("e4", "redeliver", "-", (0, 0), "ok", "RelayAckFailed");
    let actual = perform(&mut lab, decide, &input, "relay:ok")?;
    verify(
        actual == Outcome::RelayOk
            && lab.consumer.facts() == [fact.clone()]
            && lab.store.pending_outbox() == 0
            && lab.store.events().next() == Some(&fact)
            && paid(&lab, "Relay58", 349),
        "redelivery duplicated or changed a fact",
    )?;
    let input = lab.observe("e4", "redeliver", "-", (0, 0), "ok", "RelayOk");
    decision(decide, &input, "stop")
}
