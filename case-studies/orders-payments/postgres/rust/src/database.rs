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

#[derive(Clone)]
pub struct Database {
    config: Config,
    gate: Option<(String, i64, String)>,
    authorization: Option<(String, String)>,
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
    /// Immutable request authority; the default adapter remains unrestricted.
    pub fn authorized(&self, s: &str, principal: &str) -> Result<Self> {
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
        database.authorization = Some((s.into(), principal.into()));
        Ok(database)
    }
    fn authorize(&self, tx: &mut Transaction<'_>, s: &str) -> Result<()> {
        self.check_authorization_scope(s)?;
        if let Some((bound_scope, principal)) = &self.authorization {
            debug_assert_eq!(bound_scope, s);
            let row = tx.query_opt(
                "SELECT allowed FROM roo_authorization.grants WHERE scope=$1 AND principal=$2 FOR SHARE",
                &[&s, principal],
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
            .is_some_and(|(bound_scope, _)| bound_scope != s)
        {
            return Err(Error::Forbidden);
        }
        Ok(())
    }
    /// Detached advisory observation. It is never execution authority.
    pub fn authorization_allowed(&self, s: &str) -> Result<bool> {
        let Some((bound_scope, principal)) = &self.authorization else {
            return Err(Error::Input("authorization context required"));
        };
        if bound_scope != s {
            return Err(Error::Forbidden);
        }
        let mut client = self.connect()?;
        Ok(client
            .query_opt(
                "SELECT allowed FROM roo_authorization.grants WHERE scope=$1 AND principal=$2",
                &[&s, principal],
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
    _policy_transaction: &'a Transaction<'connection>,
}

impl Database {
    pub fn step(&self, s: &str, action: &Action) -> Result<Outcome> {
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
                self.provider(s,&request,Mode::Approve,false)
            },
            _ => self.operation(s,action)
        }
    }
    fn operation(&self, s: &str, action: &Action) -> Result<Outcome> {
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
            Action::Pay(_, mode, _) | Action::Refund(_, mode, _) => {
                self.provider(s, &request, *mode, false)?
            }
            Action::Reconcile(lookup, _) => {
                if *lookup == Lookup::Unavailable {
                    self.scoped_short(s, |_| Ok((Outcome::Unknown, true)))?
                } else {
                    self.provider(s, &request, Mode::Approve, true)?
                }
            }
            _ => return Err(Error::Input("invalid operation")),
        };
        self.gate("after_effect")?;
        if ![Outcome::Approved, Outcome::Declined].contains(&observation) {
            return Ok(observation);
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
            if Request::from_order(&o)? != request {
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
    fn provider(&self, s: &str, request: &Request, mode: Mode, lookup: bool) -> Result<Outcome> {
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
                let authority = RelayAuthority { scope: s, _policy_transaction: tx };
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

    #[test]
    fn authority_is_an_immutable_single_scope_clone() {
        let base = unconnected();
        let alice = base.authorized("first", "alice").unwrap();
        let bob = base.authorized("second", "bob").unwrap();
        assert!(base.authorization.is_none());
        assert_eq!(alice.authorization, Some(("first".into(), "alice".into())));
        assert_eq!(bob.authorization, Some(("second".into(), "bob".into())));
        assert!(alice.authorized("second", "bob").is_err());
        assert!(matches!(alice.init("second", false), Err(Error::Forbidden)));
        assert!(matches!(
            alice.snapshot("second", "second", "-"),
            Err(Error::Forbidden)
        ));
        assert!(matches!(
            alice.authorization_allowed("second"),
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
            assert!(base.authorized("scope", principal).is_err());
        }
        assert!(base.authorized("scope", &"a".repeat(33)).is_err());
        assert!(base.authorized("scope", &"a".repeat(32)).is_ok());
        assert!(base.authorized("scope", "A_1").is_ok());
        assert!(matches!(
            base.authorization_allowed("scope"),
            Err(Error::Input(_))
        ));
    }
}
