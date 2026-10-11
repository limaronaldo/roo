#![forbid(unsafe_code)]

use axum::http::{HeaderMap, Method, Uri};
use roo_postgres_case::{
    Outcome, database,
    fixture::{self, Action},
};
use serde::{
    Deserialize, Deserializer,
    de::{self, MapAccess, Visitor},
};
use serde_json::{Value, json};
use std::{collections::BTreeMap, fmt};

pub const BODY_LIMIT: usize = 8192;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Fault {
    InvalidRequest,
    RouteNotFound,
    MethodNotAllowed,
    ScopeNotFound,
    UnsupportedMediaType,
    BodyTooLarge,
    NotAcceptable,
    DatabaseUnavailable,
    InternalError,
    Busy,
}
impl Fault {
    pub fn status(self) -> u16 {
        match self {
            Self::InvalidRequest => 400,
            Self::RouteNotFound | Self::ScopeNotFound => 404,
            Self::MethodNotAllowed => 405,
            Self::UnsupportedMediaType => 415,
            Self::BodyTooLarge => 413,
            Self::NotAcceptable => 406,
            Self::DatabaseUnavailable | Self::Busy => 503,
            Self::InternalError => 500,
        }
    }
    pub fn body(self) -> Value {
        let (code, message) = match self {
            Self::InvalidRequest => ("InvalidRequest", "Invalid request"),
            Self::RouteNotFound => ("RouteNotFound", "Route not found"),
            Self::MethodNotAllowed => ("MethodNotAllowed", "Method not allowed"),
            Self::ScopeNotFound => ("ScopeNotFound", "Scope not found"),
            Self::UnsupportedMediaType => ("UnsupportedMediaType", "Unsupported media type"),
            Self::BodyTooLarge => ("BodyTooLarge", "Body too large"),
            Self::NotAcceptable => ("NotAcceptable", "Not acceptable"),
            Self::DatabaseUnavailable => ("DatabaseUnavailable", "Database unavailable"),
            Self::InternalError => ("InternalError", "Internal error"),
            Self::Busy => ("Busy", "Server busy"),
        };
        json!({"error":{"code":code,"message":message}})
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Route {
    Scope,
    Lines,
    Payments,
    Refunds,
    Reconciliation,
    Relay,
    Probe,
}
impl Route {
    pub fn allow(self) -> &'static str {
        if self == Self::Scope {
            "GET, PUT"
        } else {
            "POST"
        }
    }
}

pub fn route(uri: &Uri, test: bool) -> Result<(String, Route), Fault> {
    let path = uri.path();
    if uri.query().is_some()
        || !path
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || matches!(b, b'_' | b'/' | b'-'))
        || path.ends_with('/')
        || path.contains("//")
        || path == "/v1/scopes"
    {
        return Err(Fault::InvalidRequest);
    }
    let parts: Vec<_> = path.split('/').collect();
    if parts.len() < 4 || !parts[0].is_empty() || parts[1] != "v1" || parts[2] != "scopes" {
        return Err(Fault::RouteNotFound);
    }
    let scope = parts[3];
    if scope.is_empty()
        || scope.len() > 96
        || !scope
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'_')
    {
        return Err(Fault::InvalidRequest);
    }
    let kind = match &parts[4..] {
        [] => Route::Scope,
        ["lines"] => Route::Lines,
        ["payments"] => Route::Payments,
        ["refunds"] => Route::Refunds,
        ["reconciliation"] => Route::Reconciliation,
        ["relay"] => Route::Relay,
        ["_test", "provider-conflicts"] if test => Route::Probe,
        ["_test", "provider-conflicts"] => return Err(Fault::RouteNotFound),
        rest if rest.len() > 1 => return Err(Fault::InvalidRequest),
        _ => return Err(Fault::RouteNotFound),
    };
    Ok((scope.into(), kind))
}

pub fn method_allowed(route: Route, method: &Method) -> bool {
    if route == Route::Scope {
        method == Method::GET || method == Method::PUT
    } else {
        method == Method::POST
    }
}

fn one_header<'a>(headers: &'a HeaderMap, name: &str) -> Result<Option<&'a str>, Fault> {
    let mut values = headers.get_all(name).iter();
    let value = values.next();
    if values.next().is_some() {
        return Err(Fault::InvalidRequest);
    }
    value
        .map(|v| v.to_str().map_err(|_| Fault::InvalidRequest))
        .transpose()
}

pub fn headers(
    headers: &HeaderMap,
    route: Route,
    method: &Method,
) -> Result<Option<String>, Fault> {
    for name in [
        "content-type",
        "accept",
        "idempotency-key",
        "x-roo-test-drop-response",
    ] {
        one_header(headers, name)?;
    }
    if headers.contains_key("x-roo-test-drop-response") {
        return Err(Fault::InvalidRequest);
    }
    if let Some(accept) = one_header(headers, "accept")?
        && !matches!(accept.trim(), "application/json" | "*/*")
    {
        return Err(Fault::NotAcceptable);
    }
    let id = one_header(headers, "idempotency-key")?;
    if let Some(id) = id
        && (!matches!(route, Route::Payments | Route::Refunds) || !identity(id))
    {
        return Err(Fault::InvalidRequest);
    }
    if method != Method::GET {
        let content = one_header(headers, "content-type")?.ok_or(Fault::UnsupportedMediaType)?;
        let fields: Vec<_> = content.split(';').map(str::trim).collect();
        let valid_charset = fields.len() == 1
            || fields
                .get(1)
                .and_then(|parameter| parameter.split_once('='))
                .is_some_and(|(name, value)| {
                    name.trim().eq_ignore_ascii_case("charset")
                        && value.trim().eq_ignore_ascii_case("utf-8")
                });
        if !fields[0].eq_ignore_ascii_case("application/json") || fields.len() > 2 || !valid_charset
        {
            return Err(Fault::UnsupportedMediaType);
        }
    }
    Ok(id.map(str::to_owned))
}

struct Fields(BTreeMap<String, String>);
impl<'de> Deserialize<'de> for Fields {
    fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        struct Object;
        impl<'de> Visitor<'de> for Object {
            type Value = Fields;
            fn expecting(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
                f.write_str("a string-valued object")
            }
            fn visit_map<M: MapAccess<'de>>(self, mut map: M) -> Result<Fields, M::Error> {
                let mut fields = BTreeMap::new();
                while let Some(key) = map.next_key::<String>()? {
                    if fields.contains_key(&key) {
                        return Err(de::Error::custom("duplicate property"));
                    }
                    let value = map.next_value::<String>()?;
                    fields.insert(key, value);
                }
                Ok(Fields(fields))
            }
        }
        deserializer.deserialize_map(Object)
    }
}

fn identity(s: &str) -> bool {
    !s.is_empty() && s.len() <= 64 && s.bytes().all(|b| b.is_ascii_alphanumeric())
}
fn integer(s: &str) -> bool {
    if s.len() > 128 {
        return false;
    }
    let digits = s.strip_prefix(['+', '-']).unwrap_or(s);
    !digits.is_empty() && digits.bytes().all(|b| b.is_ascii_digit())
}

pub fn action(
    route: Route,
    body: &[u8],
    test: bool,
    key: Option<&str>,
) -> Result<Option<Action>, Fault> {
    if body.len() > BODY_LIMIT {
        return Err(Fault::BodyTooLarge);
    }
    let text = std::str::from_utf8(body).map_err(|_| Fault::InvalidRequest)?;
    let Fields(fields) = serde_json::from_str::<Fields>(text).map_err(|_| Fault::InvalidRequest)?;
    let ordinary: &[&str] = match route {
        Route::Scope | Route::Reconciliation | Route::Relay => &[],
        Route::Lines => &["unit_minor", "quantity"],
        Route::Payments => &["payment_id"],
        Route::Refunds => &["refund_id"],
        Route::Probe => &["payment_id", "different_amount"],
    };
    let controls: &[&str] = match route {
        Route::Payments | Route::Refunds => &["mode", "failure"],
        Route::Reconciliation => &["lookup", "failure"],
        Route::Relay => &["mode"],
        _ => &[],
    };
    if fields
        .keys()
        .any(|k| !(ordinary.contains(&k.as_str()) || test && controls.contains(&k.as_str())))
        || ordinary.iter().any(|k| !fields.contains_key(*k))
    {
        return Err(Fault::InvalidRequest);
    }
    let field = |name: &str| fields.get(name).map(String::as_str).unwrap_or("");
    let optional =
        |name: &str, default: &str| fields.get(name).cloned().unwrap_or_else(|| default.into());
    for name in ["payment_id", "refund_id"] {
        if fields.contains_key(name) && !identity(field(name)) {
            return Err(Fault::InvalidRequest);
        }
    }
    for name in ["unit_minor", "quantity", "different_amount"] {
        if fields.contains_key(name) && !integer(field(name)) {
            return Err(Fault::InvalidRequest);
        }
    }
    if let Some(key) = key {
        let id = match route {
            Route::Payments => field("payment_id"),
            Route::Refunds => field("refund_id"),
            _ => return Err(Fault::InvalidRequest),
        };
        if key != id {
            return Err(Fault::InvalidRequest);
        }
    }
    let script = match route {
        Route::Scope => return Ok(None),
        Route::Lines => format!("add:{}:{}", field("unit_minor"), field("quantity")),
        Route::Payments => format!(
            "pay:{}:{}:{}",
            field("payment_id"),
            optional("mode", "approve"),
            optional("failure", "none")
        ),
        Route::Refunds => format!(
            "refund:{}:{}:{}",
            field("refund_id"),
            optional("mode", "approve"),
            optional("failure", "none")
        ),
        Route::Reconciliation => format!(
            "reconcile:{}:{}",
            optional("lookup", "ok"),
            optional("failure", "none")
        ),
        Route::Relay => format!("relay:{}", optional("mode", "ok")),
        Route::Probe => {
            if !test
                || field("different_amount")
                    .parse::<i64>()
                    .ok()
                    .filter(|v| *v > 0)
                    .is_none()
            {
                return Err(Fault::InvalidRequest);
            }
            format!(
                "conflict:{}:{}",
                field("payment_id"),
                field("different_amount")
            )
        }
    };
    fixture::parse_action(&script)
        .map(Some)
        .map_err(|_| Fault::InvalidRequest)
}

pub fn domain_status(outcome: Outcome) -> u16 {
    use Outcome::*;
    match outcome {
        Added | Approved | Declined | AlreadyApplied | AlreadyDeclined | RelayOk => 200,
        Unknown | NotFound => 202,
        InvalidState | IntentConflict | KeyConflict => 409,
        InvalidLine | Overflow | InvalidOrder => 422,
        LocalPrepareFailed | LocalCommitFailed | RelaySendFailed | RelayAckFailed => 503,
    }
}

pub fn database_fault(error: database::Error, probe: bool) -> Fault {
    match error {
        database::Error::Database(_) => Fault::DatabaseUnavailable,
        database::Error::Input("scope does not exist") => Fault::ScopeNotFound,
        database::Error::Input("gate wait failed or timed out" | "gate unlock failed") => {
            Fault::DatabaseUnavailable
        }
        database::Error::Input(
            "conflict requires recorded payment"
            | "conflict requires different positive amount"
            | "invalid conflict amount",
        ) if probe => Fault::InvalidRequest,
        database::Error::Input(_) => Fault::InternalError,
    }
}

pub fn snapshot(tsv: &str) -> Result<Value, Fault> {
    let values: Vec<_> = tsv.strip_suffix('\n').unwrap_or(tsv).split('\t').collect();
    let keys: Vec<_> = fixture::HEADER.split('\t').collect();
    if values.len() != keys.len() {
        return Err(Fault::InternalError);
    }
    let object: serde_json::Map<String, Value> = keys
        .into_iter()
        .zip(values)
        .map(|(k, v)| (k.into(), Value::String(v.into())))
        .collect();
    Ok(json!({"snapshot": object}))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn rejects_ambiguous_and_non_string_objects() {
        for body in [
            r#"{"unit_minor":"1","unit_minor":"2","quantity":"1"}"#,
            r#"{"unit_minor":1,"quantity":"1"}"#,
            r#"{"unit_minor":"1","quantity":"1","extra":"x"}"#,
            r#"{"unit_minor":"1","quantity":"1"} {}"#,
            "null",
            "[]",
            "",
            r#"{"unit_minor":"1"}"#,
        ] {
            assert!(action(Route::Lines, body.as_bytes(), false, None).is_err());
        }
        assert!(action(Route::Scope, b"{}", false, None).unwrap().is_none());
        assert!(action(Route::Scope, &[0xff], false, None).is_err());
    }
    #[test]
    fn preserves_numeric_domain_boundary() {
        for value in ["+1", "-1", "0", "9223372036854775808"] {
            let body = json!({"unit_minor":value,"quantity":"2"}).to_string();
            assert!(action(Route::Lines, body.as_bytes(), false, None).is_ok());
        }
        for value in ["", "+", "1e3", " 1", "１２"] {
            assert!(!integer(value));
        }
        assert!(integer(&"9".repeat(128)));
        assert!(!integer(&"9".repeat(129)));
        assert_eq!(
            action(Route::Scope, &vec![b' '; BODY_LIMIT + 1], false, None).unwrap_err(),
            Fault::BodyTooLarge
        );
    }
    #[test]
    fn controls_and_idempotency_are_narrow() {
        assert!(
            action(
                Route::Payments,
                br#"{"payment_id":"p1","mode":"approve"}"#,
                false,
                None
            )
            .is_err()
        );
        assert!(
            action(
                Route::Payments,
                br#"{"payment_id":"p1"}"#,
                false,
                Some("p1")
            )
            .is_ok()
        );
        assert!(
            action(
                Route::Payments,
                br#"{"payment_id":"p1"}"#,
                false,
                Some("p2")
            )
            .is_err()
        );
        assert!(
            action(
                Route::Refunds,
                br#"{"refund_id":"r1","mode":"decline"}"#,
                true,
                None
            )
            .is_err()
        );
        assert!(
            action(
                Route::Reconciliation,
                br#"{"failure":"prepare"}"#,
                true,
                None
            )
            .is_err()
        );
    }
    #[test]
    fn route_and_status_distinctions() {
        for path in ["/v1/scopes", "/v1/scopes/s/unknown.ext"] {
            assert_eq!(
                route(&path.parse().unwrap(), false).unwrap_err(),
                Fault::InvalidRequest
            );
        }
        assert_eq!(
            route(&"/v1/scopes/s?x=1".parse().unwrap(), false).unwrap_err(),
            Fault::InvalidRequest
        );
        assert_eq!(
            route(&"/v1/scopes/s/lines/extra".parse().unwrap(), false).unwrap_err(),
            Fault::InvalidRequest
        );
        assert_eq!(
            route(
                &"/v1/scopes/s/_test/provider-conflicts".parse().unwrap(),
                false
            )
            .unwrap_err(),
            Fault::RouteNotFound
        );
        assert_eq!(domain_status(Outcome::NotFound), 202);
        assert_eq!(
            database_fault(database::Error::Input("scope does not exist"), false),
            Fault::ScopeNotFound
        );
        let body = snapshot("demo\tPaid\t2\t1\t0\t1\t0\t1\tApproved\tp1\t-\n").unwrap();
        assert_eq!(body["snapshot"].as_object().unwrap().len(), 11);
        assert!(
            body["snapshot"]
                .as_object()
                .unwrap()
                .values()
                .all(Value::is_string)
        );
    }
    #[test]
    fn header_policy() {
        let mut h = HeaderMap::new();
        h.insert(
            "content-type",
            "Application/JSON; charset=UTF-8".parse().unwrap(),
        );
        assert!(headers(&h, Route::Payments, &Method::POST).is_ok());
        h.insert(
            "content-type",
            "application/json; charset = utf-8".parse().unwrap(),
        );
        assert!(headers(&h, Route::Payments, &Method::POST).is_ok());
        h.append("content-type", "application/json".parse().unwrap());
        assert_eq!(
            headers(&h, Route::Payments, &Method::POST).unwrap_err(),
            Fault::InvalidRequest
        );
        h.remove("content-type");
        h.insert("idempotency-key", "p1,p1".parse().unwrap());
        assert_eq!(
            headers(&h, Route::Payments, &Method::POST).unwrap_err(),
            Fault::InvalidRequest
        );
        h.remove("idempotency-key");
        h.insert("x-roo-test-drop-response", "1".parse().unwrap());
        assert_eq!(
            headers(&h, Route::Scope, &Method::GET).unwrap_err(),
            Fault::InvalidRequest
        );
    }
}
