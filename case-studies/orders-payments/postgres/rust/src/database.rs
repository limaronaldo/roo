//! Persistence and coordination. Every short transaction borrows its own Client.
use crate::{
    fixture::{Action, Number},
    *,
};
use postgres::{Client, Config, IsolationLevel, NoTls, Row, Transaction};
use std::{env, time::Duration};

#[derive(Debug)]
pub enum Error {
    Input(&'static str),
    Forbidden,
    Database(postgres::Error),
}
impl From<postgres::Error> for Error {
    fn from(e: postgres::Error) -> Self {
        Self::Database(e)
    }
}
impl std::fmt::Display for Error {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Input(s) => f.write_str(s),
            Self::Forbidden => f.write_str("Access forbidden"),
            Self::Database(e) => {
                if let Some(c) = e.code() {
                    write!(f, "database operation failed ({})", c.code())
                } else {
                    f.write_str("database connection or commit failed; inspect persisted state before retry")
                }
            }
        }
    }
}
type Result<T> = std::result::Result<T, Error>;
pub fn scope(s: &str) -> Result<()> {
    if s.is_empty() || !s.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'_') {
        Err(Error::Input("invalid scope"))
    } else {
        Ok(())
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct AuthorizationContext {
    scope: String,
    principal: String,
    operation: Operation,
}

#[derive(Clone)]
pub struct Database {
    config: Config,
    gate: Option<(String, i64, String)>,
    authorization: Option<AuthorizationContext>,
}
impl Database {
    pub fn from_env() -> Result<Self> {
        let get =
            |k| env::var(k).map_err(|_| Error::Input("missing explicit database configuration"));
        if get("ROO_PG_HOST")? != "127.0.0.1"
            || get("ROO_PG_DATABASE")? != "roo_test"
            || get("ROO_PG_USER")? != "roo_test"
        {
            return Err(Error::Input(
                "only explicit loopback roo_test configuration is permitted",
            ));
        }
        let port = get("ROO_PG_PORT")?
            .parse::<u16>()
            .map_err(|_| Error::Input("invalid port"))?;
        if port == 0 {
            return Err(Error::Input("invalid port"));
        }
        let worker = env::var("ROO_WORKER_ID").unwrap_or_else(|_| "rust".into());
        scope(&worker)?;
        if worker.len() > 32 {
            return Err(Error::Input("worker token too long"));
        }
        let gate = match (env::var("ROO_GATE_POINT"), env::var("ROO_GATE_LOCK")) {
            (Err(env::VarError::NotPresent), Err(env::VarError::NotPresent)) => None,
            (Ok(point), Ok(key)) => {
                if ![
                    "inside_prepare",
                    "after_prepare",
                    "after_effect",
                    "after_finalize",
                    "before_delivery",
                    "after_delivery",
                ]
                .contains(&point.as_str())
                {
                    return Err(Error::Input("invalid gate point"));
                }
                let key = key
                    .parse::<i64>()
                    .map_err(|_| Error::Input("invalid gate key"))?;
                if key <= 0 {
                    return Err(Error::Input("invalid gate key"));
                }
                Some((point, key, worker.clone()))
            }
            _ => return Err(Error::Input("gate point and key must be paired")),
        };
        let mut config = Config::new();
        config.host("127.0.0.1").port(port).dbname("roo_test").user("roo_test")
            .connect_timeout(Duration::from_secs(5)).application_name(&format!("roo:{worker}:rust"))
            .options("-c statement_timeout=10000 -c lock_timeout=5000 -c default_transaction_isolation=read\\ committed");
        Ok(Self {
            config,
            gate,
            authorization: None,
        })
    }
    /// Bind one immutable scope, principal, and operation for this request.
    pub fn authorized(&self, s: &str, principal: &str, operation: Operation) -> Result<Self> {
        scope(s)?;
        if principal.is_empty()
            || principal.len() > 32
            || !principal
                .bytes()
                .all(|b| b.is_ascii_alphanumeric() || b == b'_')
        {
            return Err(Error::Input("invalid principal"));
        }
        if self.authorization.is_some() {
            return Err(Error::Input("authorization context already bound"));
        }
        let mut database = self.clone();
        database.authorization = Some(AuthorizationContext {
            scope: s.into(),
            principal: principal.into(),
            operation,
        });
        Ok(database)
    }
    fn authorize(&self, tx: &mut Transaction<'_>, s: &str) -> Result<()> {
        self.check_authorization_scope(s)?;
        if let Some(context) = &self.authorization {
            debug_assert_eq!(context.scope, s);
            let row = tx.query_opt(
                "SELECT allowed FROM roo_authorization.operation_grants WHERE scope=$1 AND principal=$2 AND operation=$3 FOR SHARE",
                &[&s, &context.principal, &context.operation.token()],
            )?;
            if !row.is_some_and(|r| r.get::<_, bool>(0)) {
                return Err(Error::Forbidden);
            }
        }
        Ok(())
    }
    fn check_authorization_scope(&self, s: &str) -> Result<()> {
        if self
            .authorization
            .as_ref()
            .is_some_and(|context| context.scope != s)
        {
            return Err(Error::Forbidden);
        }
        Ok(())
    }
    fn assert_operation(&self, operation: Operation) -> Result<()> {
        if self
            .authorization
            .as_ref()
            .is_some_and(|context| context.operation != operation)
        {
            return Err(Error::Forbidden);
        }
        Ok(())
    }
    /// Detached advisory observation for the immutable request operation.
    pub fn operation_allowed(&self, s: &str) -> Result<bool> {
        let Some(context) = &self.authorization else {
            return Err(Error::Input("operation authorization context required"));
        };
        if context.scope != s {
            return Err(Error::Forbidden);
        }
        let mut client = self.connect()?;
        Ok(client
            .query_opt(
                "SELECT allowed FROM roo_authorization.operation_grants WHERE scope=$1 AND principal=$2 AND operation=$3",
                &[&s, &context.principal, &context.operation.token()],
            )?
            .is_some_and(|r| r.get::<_, bool>(0)))
    }
    fn scoped_short<T>(
        &self,
        s: &str,
        mut body: impl FnMut(&mut Transaction<'_>) -> Result<(T, bool)>,
    ) -> Result<T> {
        self.check_authorization_scope(s)?;
        self.short(|tx| {
            self.authorize(tx, s)?;
            body(tx)
        })
    }
    fn connect(&self) -> Result<Client> {
        Ok(self.config.connect(NoTls)?)
    }
    fn gate(&self, point: &str) -> Result<()> {
        if let Some((target, key, worker)) = &self.gate
            && target == point
        {
            let mut client = self.connect()?;
            client.batch_execute("SET statement_timeout=30000; SET lock_timeout=30000")?;
            client.query_one(
                "SELECT set_config('application_name',$1,false)",
                &[&format!("roo:{worker}:{point}")],
            )?;
            client
                .query_one("SELECT pg_advisory_lock($1)", &[key])
                .map_err(|_| Error::Input("gate wait failed or timed out"))?;
            client
                .query_one("SELECT pg_advisory_unlock($1)", &[key])
                .map_err(|_| Error::Input("gate unlock failed"))?;
        }
        Ok(())
    }
    /// Retries only a known-aborted transaction body. COMMIT errors always escape.
    fn short<T>(
        &self,
        mut body: impl FnMut(&mut Transaction<'_>) -> Result<(T, bool)>,
    ) -> Result<T> {
        for attempt in 0..3 {
            let mut client = self.connect()?;
            let mut tx = client
                .build_transaction()
                .isolation_level(IsolationLevel::ReadCommitted)
                .start()?;
            match body(&mut tx) {
                Ok((value, true)) => {
                    tx.commit()?;
                    return Ok(value);
                }
                Ok((value, false)) => {
                    tx.rollback()?;
                    return Ok(value);
                }
                Err(error) => {
                    let retry = matches!(&error,Error::Database(e) if e.code().is_some_and(|c| ["40001","40P01","55P03"].contains(&c.code())));
                    drop(tx);
                    if !retry || attempt == 2 {
                        return Err(error);
                    }
                }
            }
        }
        unreachable!()
    }
    pub fn init(&self, s: &str, fresh: bool) -> Result<()> {
        if fresh && self.authorization.is_some() {
            return Err(Error::Forbidden);
        }
        self.assert_operation(Operation::Init)?;
        scope(s)?;
        self.scoped_short(s, |tx| {
            let n = tx.execute(
                "INSERT INTO roo_app.orders(scope) VALUES($1) ON CONFLICT DO NOTHING",
                &[&s],
            )?;
            if fresh && n == 0 {
                return Err(Error::Input("fixture scope already exists"));
            }
            Ok(((), true))
        })
    }
    /// Reserve the entire fixture set atomically before any scenario action.
    pub fn reserve_fresh(&self, scopes: &[String]) -> Result<()> {
        if self.authorization.is_some() {
            return Err(Error::Forbidden);
        }
        for s in scopes {
            scope(s)?;
            self.check_authorization_scope(s)?;
        }
        // A common insertion order avoids deadlocks between overlapping sets.
        let mut ordered: Vec<_> = scopes.iter().collect();
        ordered.sort();
        self.short(|tx| {
            // Authorize the complete set before inserting any order.
            for s in &ordered {
                self.authorize(tx, s)?;
            }
            for s in &ordered {
                let inserted = tx.execute(
                    "INSERT INTO roo_app.orders(scope) VALUES($1) ON CONFLICT DO NOTHING",
                    &[s],
                )?;
                if inserted == 0 {
                    return Err(Error::Input("fixture scope already exists"));
                }
            }
            Ok(((), true))
        })
    }
    pub fn snapshot(&self, s: &str, label: &str, last: &str) -> Result<String> {
        scope(s)?;
        self.scoped_short(s, |tx| {
        let r=tx.query_opt("SELECT state,total,payment_id,refund_id,(SELECT count(*) FROM roo_provider.records WHERE scope=$1 AND kind='payment' AND result='Approved'),(SELECT count(*) FROM roo_provider.records WHERE scope=$1 AND kind='refund' AND result='Approved'),(SELECT count(*) FROM roo_app.outbox WHERE scope=$1),(SELECT count(*) FROM roo_consumer.inbox WHERE scope=$1),(SELECT count(*) FROM roo_app.outbox WHERE scope=$1 AND NOT delivered) FROM roo_app.orders WHERE scope=$1",&[&s])?.ok_or(Error::Input("scope does not exist"))?;
        Ok((format!(
            "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n",
            label,
            r.get::<_, String>(0),
            r.get::<_, i64>(1),
            r.get::<_, i64>(4),
            r.get::<_, i64>(5),
            r.get::<_, i64>(6),
            r.get::<_, i64>(7),
            r.get::<_, i64>(8),
            last,
            r.get::<_, Option<String>>(2).as_deref().unwrap_or("-"),
            r.get::<_, Option<String>>(3).as_deref().unwrap_or("-")
        ), true))
        })
    }
}

fn load(tx: &mut Transaction<'_>, s: &str) -> Result<Order> {
    let r=tx.query_opt("SELECT order_id,currency,state,total,payment_id,refund_id FROM roo_app.orders WHERE scope=$1 FOR UPDATE",&[&s])?.ok_or(Error::Input("scope does not exist"))?;
    let mut order = Order::new(
        OrderId::new(&r.get::<_, String>(0))
            .map_err(|_| Error::Input("invalid persisted identity"))?,
    );
    if r.get::<_, String>(1) != "USD" {
        return Err(Error::Input("invalid persisted currency"));
    }
    for line in tx.query(
        "SELECT unit_minor,quantity FROM roo_app.lines WHERE scope=$1 ORDER BY line_no",
        &[&s],
    )? {
        if order.add(line.get(0), line.get(1)) != Outcome::Added {
            return Err(Error::Input("invalid persisted lines"));
        }
    }
    if order.total() != r.get::<_, i64>(3) {
        return Err(Error::Input("persisted total does not match lines"));
    }
    let state = r.get::<_, String>(2);
    if state != "Draft" {
        let p = r
            .get::<_, Option<String>>(4)
            .ok_or(Error::Input("missing payment intent"))?;
        if order.prepare_payment(
            PaymentId::new(&p).map_err(|_| Error::Input("invalid payment identity"))?,
        ) != Outcome::Added
        {
            return Err(Error::Input("invalid payment intent"));
        }
        if state != "Pending" {
            order.finish_payment(state != "Declined");
        }
        if ["Refunding", "Refunded"].contains(&state.as_str()) {
            let id = r
                .get::<_, Option<String>>(5)
                .ok_or(Error::Input("missing refund intent"))?;
            order.prepare_refund(
                RefundId::new(&id).map_err(|_| Error::Input("invalid refund identity"))?,
            );
            if state == "Refunded" {
                order.finish_refund();
            }
        }
    }
    Ok(order)
}
fn save(tx: &mut Transaction<'_>, s: &str, o: &Order) -> Result<()> {
    tx.execute(
        "UPDATE roo_app.orders SET state=$2,total=$3,payment_id=$4,refund_id=$5 WHERE scope=$1",
        &[
            &s,
            &format!("{:?}", o.state()),
            &o.total(),
            &o.payment_id().map(PaymentId::as_str),
            &o.refund_id().map(RefundId::as_str),
        ],
    )?;
    Ok(())
}
#[derive(Clone, Debug, PartialEq, Eq)]
enum Request {
    Payment(domain::PaymentRequest),
    Refund(domain::RefundRequest),
}
impl Request {
    fn parts(&self) -> (&str, &str, &str, &str, i64, &str) {
        match self {
            Self::Payment(p) => (
                "payment",
                p.id.as_str(),
                p.order.as_str(),
                &p.currency,
                p.amount.minor(),
                p.id.as_str(),
            ),
            Self::Refund(r) => (
                "refund",
                r.id.as_str(),
                r.order.as_str(),
                &r.currency,
                r.amount.minor(),
                r.payment.as_str(),
            ),
        }
    }
    fn from_order(o: &Order) -> Result<Self> {
        match o.state() {
            State::Pending => Ok(Self::Payment(
                o.payment().ok_or(Error::Input("missing payment"))?.clone(),
            )),
            State::Refunding => Ok(Self::Refund(
                o.refund().ok_or(Error::Input("missing refund"))?.clone(),
            )),
            _ => Err(Error::Input("no active intent")),
        }
    }
    fn matches(&self, r: &Row) -> bool {
        let (_, _, order, currency, amount, payment) = self.parts();
        r.get::<_, String>(0) == order
            && r.get::<_, String>(1) == currency
            && r.get::<_, i64>(2) == amount
            && r.get::<_, String>(3) == payment
    }
}

enum Prepared {
    Done(Outcome),
    Ready(Request),
}

/// Private delivery authority borrowed from the relay transaction. Its lifetime
/// prevents the independently committed inbox effect from outliving that lock.
struct RelayAuthority<'a, 'connection> {
    scope: &'a str,
    operation: Operation,
    _policy_transaction: &'a Transaction<'connection>,
}

fn action_operation(action: &Action) -> Operation {
    match action {
        Action::Add(_, _) => Operation::Add,
        Action::Pay(_, _, _) => Operation::Pay,
        Action::Refund(_, _, _) => Operation::Refund,
        Action::Reconcile(_, _) => Operation::Reconcile,
        Action::Relay(_) => Operation::Relay,
        Action::Conflict(_, _) => Operation::ProviderConflict,
    }
}

impl Database {
    pub fn step(&self, s: &str, action: &Action) -> Result<Outcome> {
        let operation = action_operation(action);
        self.assert_operation(operation)?;
        scope(s)?;
        match action {
            Action::Add(Number::Value(unit),Number::Value(qty)) => self.scoped_short(s, |tx| {
                let mut o=load(tx,s)?;
                let result=o.add(*unit,*qty);
                if result==Outcome::Added {
                    let n:i64=tx.query_one("SELECT coalesce(max(line_no),0)+1 FROM roo_app.lines WHERE scope=$1",&[&s])?.get(0);
                    tx.execute("INSERT INTO roo_app.lines(scope,line_no,unit_minor,quantity) VALUES($1,$2,$3,$4)",&[&s,&n,unit,qty])?;
                    save(tx,s,&o)?;
                    self.gate("inside_prepare")?;
                }
                Ok((result,true))
            }),
            Action::Add(_,_) | Action::Conflict(_,Number::Overflow) => {
                self.scoped_short(s, |tx| { load(tx,s)?; Ok((Outcome::Overflow,true)) })
            },
            Action::Relay(mode) => self.relay(s,*mode),
            Action::Conflict(id,Number::Value(amount)) => {
                self.scoped_short(s, |tx| {
                    load(tx,s)?;
                    let r=tx.query_opt("SELECT order_id,currency,amount,payment_id,result FROM roo_provider.records WHERE scope=$1 AND kind='payment' AND operation_id=$2",&[&s,&id.as_str()])?.ok_or(Error::Input("conflict requires recorded payment"))?;
                    if *amount<=0 || *amount==r.get::<_,i64>(2) { return Err(Error::Input("conflict requires different positive amount")); }
                    Ok(((),true))
                })?;
                let request=Request::Payment(domain::PaymentRequest { id:id.clone(),order:OrderId::new("O1").map_err(|_|Error::Input("invalid constant"))?,currency:"USD".into(),amount:Money::new(*amount).map_err(|_|Error::Input("invalid conflict amount"))? });
                self.provider(Operation::ProviderConflict, s, &request, Mode::Approve, false)
            },
            _ => self.operation(s,action)
        }
    }
    fn operation(&self, s: &str, action: &Action) -> Result<Outcome> {
        let operation = action_operation(action);
        self.assert_operation(operation)?;
        // The schema forbids a Declined refund record, and the refund intent is
        // committed before the provider is called. Reject before any
        // transaction so a doomed request can never leave a Refunding order.
        if matches!(action, Action::Refund(_, Mode::Decline, _)) {
            self.check_authorization_scope(s)?;
            return Ok(Outcome::InvalidState);
        }
        let failure = match action {
            Action::Pay(_, _, f) | Action::Refund(_, _, f) | Action::Reconcile(_, f) => *f,
            _ => return Err(Error::Input("invalid operation")),
        };
        let prepared = self.scoped_short(s, |tx| {
            let mut o = load(tx, s)?;
            let mut changed = false;
            let done = match action {
                Action::Pay(id, _, _) => {
                    if o.state() != State::Draft && o.payment_id() != Some(id) {
                        Some(Outcome::IntentConflict)
                    } else {
                        match o.state() {
                            State::Draft => {
                                let result = o.prepare_payment(id.clone());
                                if result == Outcome::Added {
                                    changed = true;
                                    None
                                } else {
                                    Some(result)
                                }
                            }
                            State::Pending => None,
                            State::Declined => Some(Outcome::AlreadyDeclined),
                            _ => Some(Outcome::AlreadyApplied),
                        }
                    }
                }
                Action::Refund(id, _, _) => match o.state() {
                    State::Paid => {
                        o.prepare_refund(id.clone());
                        changed = true;
                        None
                    }
                    State::Refunding | State::Refunded => {
                        if o.refund_id() != Some(id) {
                            Some(Outcome::IntentConflict)
                        } else if o.state() == State::Refunded {
                            Some(Outcome::AlreadyApplied)
                        } else {
                            None
                        }
                    }
                    _ => Some(Outcome::InvalidState),
                },
                Action::Reconcile(_, _) => {
                    if [State::Pending, State::Refunding].contains(&o.state()) {
                        None
                    } else {
                        Some(Outcome::InvalidState)
                    }
                }
                _ => return Err(Error::Input("invalid operation")),
            };
            if let Some(result) = done {
                return Ok((Prepared::Done(result), true));
            }
            let request = Request::from_order(&o)?;
            if changed {
                save(tx, s, &o)?;
                self.gate("inside_prepare")?;
                if failure == Failure::Prepare {
                    return Ok((Prepared::Done(Outcome::LocalPrepareFailed), false));
                }
            }
            Ok((Prepared::Ready(request), true))
        })?;
        let request = match prepared {
            Prepared::Done(r) => return Ok(r),
            Prepared::Ready(r) => r,
        };
        self.gate("after_prepare")?;
        let observation = match action {
            Action::Pay(_, mode, _) => self.provider(Operation::Pay, s, &request, *mode, false)?,
            Action::Refund(_, mode, _) => {
                self.provider(Operation::Refund, s, &request, *mode, false)?
            }
            Action::Reconcile(lookup, _) => {
                if *lookup == Lookup::Unavailable {
                    self.scoped_short(s, |_| Ok((Outcome::Unknown, true)))?
                } else {
                    self.provider(Operation::Reconcile, s, &request, Mode::Approve, true)?
                }
            }
            _ => return Err(Error::Input("invalid operation")),
        };
        self.gate("after_effect")?;
        if ![Outcome::Approved, Outcome::Declined].contains(&observation) {
            return Ok(observation);
        }
        self.finalize(operation, s, &request, observation, failure)
    }

    fn finalize(
        &self,
        operation: Operation,
        s: &str,
        request: &Request,
        observation: Outcome,
        failure: Failure,
    ) -> Result<Outcome> {
        self.assert_operation(operation)?;
        let request_matches_operation = matches!(
            (operation, request),
            (Operation::Pay, Request::Payment(_))
                | (Operation::Refund, Request::Refund(_))
                | (
                    Operation::Reconcile,
                    Request::Payment(_) | Request::Refund(_)
                )
        );
        if !request_matches_operation {
            return Err(Error::Input("invalid finalization operation"));
        }
        let (result, committed) = self.scoped_short(s, |tx| {
            let mut o = load(tx, s)?;
            // A payment may already have advanced through a refund in another worker.
            let noop = match &request {
                Request::Payment(p) if o.payment() == Some(p) => match o.state() {
                    State::Paid | State::Refunding | State::Refunded => {
                        Some(Outcome::AlreadyApplied)
                    }
                    State::Declined => Some(Outcome::AlreadyDeclined),
                    _ => None,
                },
                Request::Refund(r) if o.refund() == Some(r) && o.state() == State::Refunded => {
                    Some(Outcome::AlreadyApplied)
                }
                _ => None,
            };
            if let Some(noop) = noop {
                return Ok(((noop, false), true));
            }
            if &Request::from_order(&o)? != request {
                return Err(Error::Input("persisted intent changed during finalization"));
            }
            let event = match request {
                Request::Payment(_) => o.finish_payment(observation == Outcome::Approved),
                Request::Refund(_) => o.finish_refund(),
            };
            save(tx, s, &o)?;
            insert_event(tx, s, &event)?;
            if failure == Failure::Commit {
                Ok(((Outcome::LocalCommitFailed, false), false))
            } else {
                Ok(((observation, true), true))
            }
        })?;
        if committed {
            self.gate("after_finalize")?;
        }
        Ok(result)
    }

    fn provider(
        &self,
        operation: Operation,
        s: &str,
        request: &Request,
        mode: Mode,
        lookup: bool,
    ) -> Result<Outcome> {
        self.assert_operation(operation)?;
        let valid_call = matches!(
            (operation, request, mode, lookup),
            (Operation::Pay, Request::Payment(_), _, false)
                | (Operation::Refund, Request::Refund(_), _, false)
                | (
                    Operation::Reconcile,
                    Request::Payment(_) | Request::Refund(_),
                    Mode::Approve,
                    true
                )
                | (
                    Operation::ProviderConflict,
                    Request::Payment(_),
                    Mode::Approve,
                    false
                )
        );
        if !valid_call {
            return Err(Error::Input("invalid provider operation"));
        }
        self.scoped_short(s, |tx| {
            let (kind,id,order,currency,amount,payment)=request.parts();
            if !lookup { tx.query_one("SELECT pg_advisory_xact_lock(hashtextextended($1,0))",&[&s])?; }
            if let Some(r)=tx.query_opt("SELECT order_id,currency,amount,payment_id,result FROM roo_provider.records WHERE scope=$1 AND kind=$2 AND operation_id=$3",&[&s,&kind,&id])? {
                return Ok((if !request.matches(&r) {Outcome::KeyConflict} else if r.get::<_,String>(4)=="Approved" {Outcome::Approved} else {Outcome::Declined},true));
            }
            if lookup { return Ok((Outcome::NotFound,true)); }
            if mode==Mode::TimeoutBefore { return Ok((Outcome::Unknown,true)); }
            if kind=="refund" {
                let parent=tx.query_opt("SELECT order_id,currency,amount,payment_id,result FROM roo_provider.records WHERE scope=$1 AND kind='payment' AND operation_id=$2",&[&s,&payment])?;
                if !parent.as_ref().is_some_and(|r| request.matches(r) && r.get::<_,String>(4)=="Approved") {return Ok((Outcome::KeyConflict,true));}
                if tx.query_opt("SELECT operation_id FROM roo_provider.records WHERE scope=$1 AND kind='refund' AND payment_id=$2",&[&s,&payment])?.is_some() {return Ok((Outcome::KeyConflict,true));}
            }
            let terminal=if mode==Mode::Decline {"Declined"} else {"Approved"};
            tx.execute("INSERT INTO roo_provider.records(scope,kind,operation_id,order_id,currency,amount,payment_id,result) VALUES($1,$2,$3,$4,$5,$6,$7,$8)",&[&s,&kind,&id,&order,&currency,&amount,&payment,&terminal])?;
            Ok((if mode==Mode::TimeoutAfter {Outcome::Unknown} else if mode==Mode::Decline {Outcome::Declined} else {Outcome::Approved},true))
        })
    }
    fn relay(&self, s: &str, mode: RelayMode) -> Result<Outcome> {
        self.assert_operation(Operation::Relay)?;
        loop {
            let (result,more)=self.scoped_short(s, |tx| {
                load(tx,s)?;
                let Some(row)=tx.query_opt("SELECT event_id,event_kind,order_id,currency,payment_id,refund_id,amount FROM roo_app.outbox WHERE scope=$1 AND NOT delivered ORDER BY seq LIMIT 1",&[&s])? else { return Ok(((Outcome::RelayOk,false),true)); };
                if mode==RelayMode::SendFail {return Ok(((Outcome::RelaySendFailed,false),true));}
                let fact=Fact::from_row(&row);
                // The outer transaction retains the policy lock until delivery/ack
                // completes. Reacquiring it in another transaction could wait behind
                // a revoker that is itself waiting for this outer transaction.
                self.gate("before_delivery")?;
                let authority = RelayAuthority {
                    scope: s,
                    operation: Operation::Relay,
                    _policy_transaction: tx,
                };
                self.inbox_under_relay_authority(authority,&fact)?;
                self.gate("after_delivery")?;
                if mode==RelayMode::AckFail {return Ok(((Outcome::RelayAckFailed,false),false));}
                tx.execute("UPDATE roo_app.outbox SET delivered=true WHERE scope=$1 AND event_id=$2",&[&s,&fact.id])?;
                Ok(((Outcome::RelayOk,true),true))
            })?;
            if !more {
                return Ok(result);
            }
        }
    }
    fn inbox_under_relay_authority(
        &self,
        authority: RelayAuthority<'_, '_>,
        f: &Fact,
    ) -> Result<()> {
        let s = authority.scope;
        if authority.operation != Operation::Relay {
            return Err(Error::Forbidden);
        }
        self.assert_operation(Operation::Relay)?;
        self.check_authorization_scope(s)?;
        self.short(|tx| {
            tx.execute("INSERT INTO roo_consumer.inbox(scope,event_id,event_kind,order_id,currency,payment_id,refund_id,amount) VALUES($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT DO NOTHING",&[&s,&f.id,&f.kind,&f.order,&f.currency,&f.payment,&f.refund,&f.amount])?;
            let r=tx.query_one("SELECT event_id,event_kind,order_id,currency,payment_id,refund_id,amount FROM roo_consumer.inbox WHERE scope=$1 AND event_id=$2",&[&s,&f.id])?;
            if Fact::from_row(&r)!=*f {return Err(Error::Input("inbox event fingerprint conflict"));}
            Ok(((),true))
        })
    }
}
#[derive(Debug, PartialEq, Eq)]
struct Fact {
    id: String,
    kind: String,
    order: String,
    currency: String,
    payment: String,
    refund: Option<String>,
    amount: i64,
}
impl Fact {
    fn from_row(r: &Row) -> Self {
        Self {
            id: r.get(0),
            kind: r.get(1),
            order: r.get(2),
            currency: r.get(3),
            payment: r.get(4),
            refund: r.get(5),
            amount: r.get(6),
        }
    }
    fn from_event(e: &Event) -> Self {
        Self {
            id: e.id().as_str().into(),
            kind: format!("{:?}", e.kind()),
            order: e.order_id().as_str().into(),
            currency: e.currency().into(),
            payment: e.payment_id().as_str().into(),
            refund: e.refund_id().map(|r| r.as_str().into()),
            amount: e.amount().minor(),
        }
    }
}
fn insert_event(tx: &mut Transaction<'_>, s: &str, e: &Event) -> Result<()> {
    let f = Fact::from_event(e);
    tx.execute("INSERT INTO roo_app.outbox(scope,event_id,event_kind,order_id,currency,payment_id,refund_id,amount) VALUES($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT DO NOTHING",&[&s,&f.id,&f.kind,&f.order,&f.currency,&f.payment,&f.refund,&f.amount])?;
    let r=tx.query_one("SELECT event_id,event_kind,order_id,currency,payment_id,refund_id,amount FROM roo_app.outbox WHERE scope=$1 AND event_id=$2",&[&s,&f.id])?;
    if Fact::from_row(&r) != f {
        return Err(Error::Input("outbox event fingerprint conflict"));
    }
    Ok(())
}

#[cfg(test)]
mod authorization_tests {
    use super::*;

    fn unconnected() -> Database {
        Database {
            config: Config::new(),
            gate: None,
            authorization: None,
        }
    }

    fn payment_request() -> Request {
        Request::Payment(domain::PaymentRequest {
            id: PaymentId::new("p1").unwrap(),
            order: OrderId::new("O1").unwrap(),
            currency: "USD".into(),
            amount: Money::new(1).unwrap(),
        })
    }

    #[test]
    fn authority_is_an_immutable_single_scope_clone() {
        let base = unconnected();
        let alice = base.authorized("first", "alice", Operation::Read).unwrap();
        let bob = base.authorized("second", "bob", Operation::Pay).unwrap();
        assert!(base.authorization.is_none());
        assert_eq!(
            alice.authorization,
            Some(AuthorizationContext {
                scope: "first".into(),
                principal: "alice".into(),
                operation: Operation::Read,
            })
        );
        assert_eq!(
            bob.authorization,
            Some(AuthorizationContext {
                scope: "second".into(),
                principal: "bob".into(),
                operation: Operation::Pay,
            })
        );
        assert!(alice.authorized("second", "bob", Operation::Pay).is_err());
        assert!(matches!(alice.init("second", false), Err(Error::Forbidden)));
        assert!(matches!(
            alice.snapshot("second", "second", "-"),
            Err(Error::Forbidden)
        ));
        assert!(matches!(
            alice.operation_allowed("second"),
            Err(Error::Forbidden)
        ));
        assert!(matches!(
            alice.reserve_fresh(&["second".into()]),
            Err(Error::Forbidden)
        ));
        let action = crate::fixture::parse_action("add:1:1").unwrap();
        assert!(matches!(
            alice.step("second", &action),
            Err(Error::Forbidden)
        ));
    }

    #[test]
    fn authority_rejects_invalid_principals_before_any_connection() {
        let base = unconnected();
        for principal in ["", "a,b", "a b", "a-b", "é"] {
            assert!(
                base.authorized("scope", principal, Operation::Read)
                    .is_err()
            );
        }
        assert!(
            base.authorized("scope", &"a".repeat(33), Operation::Read)
                .is_err()
        );
        assert!(
            base.authorized("scope", &"a".repeat(32), Operation::Read)
                .is_ok()
        );
        assert!(base.authorized("scope", "A_1", Operation::Read).is_ok());
        assert!(matches!(
            base.operation_allowed("scope"),
            Err(Error::Input(_))
        ));
    }

    #[test]
    fn operation_context_is_immutable_and_rejects_mismatches_before_connecting() {
        let base = unconnected();
        let actions = [
            ("add:1:1", Operation::Add),
            ("pay:p1:approve:none", Operation::Pay),
            ("refund:r1:approve:none", Operation::Refund),
            ("reconcile:ok:none", Operation::Reconcile),
            ("relay:ok", Operation::Relay),
            ("conflict:p1:2", Operation::ProviderConflict),
        ];
        for operation in Operation::ALL {
            let bound = base.authorized("scope", "alice", operation).unwrap();
            assert_eq!(bound.authorization.as_ref().unwrap().operation, operation);
            assert!(bound.authorized("scope", "bob", Operation::Read).is_err());
            assert!(matches!(bound.reserve_fresh(&[]), Err(Error::Forbidden)));
            assert!(matches!(
                bound.reserve_fresh(&["scope".into()]),
                Err(Error::Forbidden)
            ));
            assert!(matches!(bound.init("scope", true), Err(Error::Forbidden)));
            for (script, action_operation) in actions {
                if operation != action_operation {
                    let action = crate::fixture::parse_action(script).unwrap();
                    assert!(matches!(
                        bound.step("scope", &action),
                        Err(Error::Forbidden)
                    ));
                }
            }
            if operation != Operation::Init {
                assert!(matches!(bound.init("scope", false), Err(Error::Forbidden)));
            }
        }
        let init = base.authorized("scope", "alice", Operation::Init).unwrap();
        assert!(init.assert_operation(Operation::Init).is_ok());
        let read = base.authorized("scope", "alice", Operation::Read).unwrap();
        assert!(matches!(
            read.operation_allowed("other"),
            Err(Error::Forbidden)
        ));
        assert!(matches!(
            base.operation_allowed("scope"),
            Err(Error::Input(_))
        ));
    }

    #[test]
    fn every_fixture_action_has_one_closed_operation() {
        for (script, operation) in [
            ("add:1:1", Operation::Add),
            ("pay:p1:approve:none", Operation::Pay),
            ("refund:r1:approve:none", Operation::Refund),
            ("reconcile:ok:none", Operation::Reconcile),
            ("relay:ok", Operation::Relay),
            ("conflict:p1:2", Operation::ProviderConflict),
        ] {
            assert_eq!(
                action_operation(&crate::fixture::parse_action(script).unwrap()),
                operation
            );
        }
    }

    #[test]
    fn private_provider_finalizer_and_relay_checks_reject_wrong_operations_without_connecting() {
        let base = unconnected();
        let request = payment_request();
        for bound_operation in Operation::ALL {
            let bound = base.authorized("scope", "alice", bound_operation).unwrap();
            let wrong_operation = if bound_operation == Operation::Pay {
                Operation::Refund
            } else {
                Operation::Pay
            };
            assert!(matches!(
                bound.provider(wrong_operation, "scope", &request, Mode::Approve, false),
                Err(Error::Forbidden)
            ));
            assert!(matches!(
                bound.finalize(
                    wrong_operation,
                    "scope",
                    &request,
                    Outcome::Approved,
                    Failure::None
                ),
                Err(Error::Forbidden)
            ));
            if bound_operation != Operation::Relay {
                assert!(matches!(
                    bound.relay("scope", RelayMode::Ok),
                    Err(Error::Forbidden)
                ));
            }
        }
    }

    fn refund(mode: Mode) -> Action {
        Action::Refund(RefundId::new("r1").unwrap(), mode, Failure::None)
    }

    #[test]
    fn declined_refund_is_rejected_before_database_access() {
        // An unconnected handle cannot open a transaction: a database error
        // proves an attempted connection, an Ok outcome proves none was made.
        let base = unconnected();
        assert!(matches!(
            base.step("scope", &refund(Mode::Decline)),
            Ok(Outcome::InvalidState)
        ));
        assert!(matches!(
            base.step("scope", &refund(Mode::Approve)),
            Err(Error::Database(_))
        ));
    }

    #[test]
    fn declined_refund_still_honors_the_bound_operation_and_scope() {
        let base = unconnected();
        let bound = base
            .authorized("scope", "alice", Operation::Refund)
            .unwrap();
        assert!(matches!(
            bound.step("scope", &refund(Mode::Decline)),
            Ok(Outcome::InvalidState)
        ));
        assert!(matches!(
            bound.step("other", &refund(Mode::Decline)),
            Err(Error::Forbidden)
        ));
        let pay = base.authorized("scope", "alice", Operation::Pay).unwrap();
        assert!(matches!(
            pay.step("scope", &refund(Mode::Decline)),
            Err(Error::Forbidden)
        ));
    }
}
