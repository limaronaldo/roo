#![forbid(unsafe_code)]

use axum::{
    Router,
    body::{Body, to_bytes},
    extract::{Request, State},
    http::{Method, StatusCode, header},
    response::{IntoResponse, Response},
};
use postgres::{Config, NoTls};
use roo_http_case::{self as boundary, Fault, Route};
use roo_postgres_case::{database::Database, fixture::Action};
use serde_json::Value;
use std::{env, future::IntoFuture, sync::Arc, time::Duration};
use tokio::sync::{Semaphore, watch};

const WORKERS: usize = 16;
const DRAIN: Duration = Duration::from_secs(180);

#[derive(Clone)]
struct App {
    database: Database,
    test: bool,
    gate: Option<Gate>,
    authorization: bool,
    authorization_gate: Option<Gate>,
    admission: Arc<Semaphore>,
}
#[derive(Clone)]
struct Gate {
    config: Config,
    key: i64,
}
impl Gate {
    fn wait(&self) -> Result<(), Fault> {
        // A separate connection for instrumentation only; no domain SQL or mutation.
        let mut client = self
            .config
            .connect(NoTls)
            .map_err(|_| Fault::DatabaseUnavailable)?;
        client
            .query_one("SELECT pg_advisory_lock($1)", &[&self.key])
            .map_err(|_| Fault::DatabaseUnavailable)?;
        client
            .query_one("SELECT pg_advisory_unlock($1)", &[&self.key])
            .map_err(|_| Fault::DatabaseUnavailable)?;
        Ok(())
    }
}

fn response(status: u16, value: Value, allow: Option<&str>) -> Response {
    let mut response = (
        StatusCode::from_u16(status).unwrap_or(StatusCode::INTERNAL_SERVER_ERROR),
        axum::Json(value),
    )
        .into_response();
    let headers = response.headers_mut();
    headers.insert(
        header::CONNECTION,
        header::HeaderValue::from_static("close"),
    );
    headers.insert(
        header::CACHE_CONTROL,
        header::HeaderValue::from_static("no-store"),
    );
    if let Some(allow) = allow
        && let Ok(value) = header::HeaderValue::from_str(allow)
    {
        headers.insert(header::ALLOW, value);
    }
    response
}
fn error(fault: Fault) -> Response {
    response(fault.status(), fault.body(), None)
}

async fn handle(State(app): State<App>, request: Request<Body>) -> Response {
    let (scope, route) =
        match boundary::route_with_authorization(request.uri(), app.test, app.authorization) {
            Ok(v) => v,
            Err(e) => return error(e),
        };
    if !boundary::method_allowed(route, request.method()) {
        return response(405, Fault::MethodNotAllowed.body(), Some(route.allow()));
    }
    let method = request.method().clone();
    let principal = match boundary::principal(request.headers(), app.authorization) {
        Ok(v) => v,
        Err(e) => return error(e),
    };
    let key = match boundary::headers(request.headers(), route, &method) {
        Ok(v) => v,
        Err(e) => return error(e),
    };
    // Axum enforces the actual streamed byte limit, including chunked requests.
    let body = match to_bytes(request.into_body(), boundary::BODY_LIMIT).await {
        Ok(body) => body,
        Err(_) => return error(Fault::BodyTooLarge),
    };
    let action = if method == Method::GET {
        if !body.is_empty() {
            return error(Fault::InvalidRequest);
        }
        None
    } else {
        match boundary::action(route, &body, app.test, key.as_deref()) {
            Ok(v) => v,
            Err(e) => return error(e),
        }
    };
    let permit = match app.admission.clone().try_acquire_owned() {
        Ok(v) => v,
        Err(_) => return error(Fault::Busy),
    };
    let result = tokio::task::spawn_blocking(move || {
        // Permit follows blocking work even if its HTTP client disconnects.
        let _permit = permit;
        execute(&app, &scope, route, &method, action, principal.as_deref())
    })
    .await;
    match result {
        Ok(Ok((status, body))) => response(status, body, None),
        Ok(Err(fault)) => error(fault),
        Err(_) => error(Fault::InternalError),
    }
}

fn execute(
    app: &App,
    scope: &str,
    route: Route,
    method: &Method,
    action: Option<Action>,
    principal: Option<&str>,
) -> Result<(u16, Value), Fault> {
    let probe = route == Route::Probe;
    let database = match principal {
        Some(principal) => app
            .database
            .authorized(scope, principal)
            .map_err(|e| boundary::database_fault(e, probe))?,
        None => app.database.clone(),
    };
    if route == Route::Authorization {
        let allowed = database
            .authorization_allowed(scope)
            .map_err(|e| boundary::database_fault(e, probe))?;
        return Ok((
            200,
            serde_json::json!({"authorization":{"allowed":allowed}}),
        ));
    }
    if method == Method::POST && app.authorization {
        // Observation is advisory even when denied. Execution rechecks policy
        // under a row lock after the configured deterministic test gate.
        let _ = database
            .authorization_allowed(scope)
            .map_err(|e| boundary::database_fault(e, probe))?;
        if let Some(gate) = &app.authorization_gate {
            gate.wait()?;
        }
    }
    let (status, last) = if method == Method::PUT {
        database
            .init(scope, false)
            .map_err(|e| boundary::database_fault(e, probe))?;
        (200, "-".into())
    } else if let Some(action) = action {
        let outcome = database
            .step(scope, &action)
            .map_err(|e| boundary::database_fault(e, probe))?;
        (boundary::domain_status(outcome), outcome.to_string())
    } else {
        (200, "-".into())
    };
    let tsv = database
        .snapshot(scope, scope, &last)
        .map_err(|e| boundary::database_fault(e, probe))?;
    let body = boundary::snapshot(&tsv)?;
    if method == Method::POST
        && let Some(gate) = &app.gate
    {
        gate.wait()?;
    }
    Ok((status, body))
}

fn value(name: &str) -> Result<Option<String>, ()> {
    match env::var(name) {
        Ok(v) => Ok(Some(v)),
        Err(env::VarError::NotPresent) => Ok(None),
        Err(_) => Err(()),
    }
}
fn required(name: &str) -> Result<String, ()> {
    value(name)?.ok_or(())
}
fn decimal(s: &str) -> bool {
    !s.is_empty() && s.bytes().all(|b| b.is_ascii_digit())
}

fn configure() -> Result<(u16, App), ()> {
    // Validate the explicit listener host before constructing any database adapter.
    if required("ROO_HTTP_HOST")? != "127.0.0.1" {
        return Err(());
    }
    let port = required("ROO_HTTP_PORT")?;
    if !decimal(&port) {
        return Err(());
    }
    let port = port.parse::<u16>().map_err(|_| ())?;
    let test = match value("ROO_HTTP_TEST_MODE")?.as_deref() {
        None => false,
        Some("1") => true,
        _ => return Err(()),
    };
    let gate_key = value("ROO_HTTP_GATE_LOCK")?;
    let authorization_mode = value("ROO_HTTP_AUTH_MODE")?;
    let authorization_gate_key = value("ROO_HTTP_AUTH_GATE_LOCK")?;
    let authorization = boundary::AuthorizationConfig::parse(
        authorization_mode.as_deref(),
        authorization_gate_key.as_deref(),
        test,
    )
    .map_err(|_| ())?;
    if !test
        && (gate_key.is_some()
            || value("ROO_GATE_POINT")?.is_some()
            || value("ROO_GATE_LOCK")?.is_some())
    {
        return Err(());
    }
    let database = Database::from_env().map_err(|_| ())?;
    let gate = match gate_key {
        None => None,
        Some(text) => {
            let digits = text.strip_prefix('+').unwrap_or(&text);
            if !decimal(digits) {
                return Err(());
            }
            let key = text.parse::<i64>().map_err(|_| ())?;
            if key <= 0 {
                return Err(());
            }
            let worker = value("ROO_WORKER_ID")?.unwrap_or_else(|| "rust".into());
            // Database::from_env has already validated these same immutable values.
            let mut config = Config::new();
            config
                .host("127.0.0.1")
                .port(required("ROO_PG_PORT")?.parse::<u16>().map_err(|_| ())?)
                .dbname("roo_test")
                .user("roo_test")
                .connect_timeout(Duration::from_secs(5))
                .application_name(&format!("roo:{worker}:http_after_snapshot"))
                .options("-c statement_timeout=30000 -c lock_timeout=30000");
            Some(Gate { config, key })
        }
    };
    let authorization_gate = match authorization.gate_key {
        None => None,
        Some(key) => {
            let worker = value("ROO_WORKER_ID")?.unwrap_or_else(|| "rust".into());
            let mut config = Config::new();
            config
                .host("127.0.0.1")
                .port(required("ROO_PG_PORT")?.parse::<u16>().map_err(|_| ())?)
                .dbname("roo_test")
                .user("roo_test")
                .connect_timeout(Duration::from_secs(5))
                .application_name(&format!(
                    "roo:{worker}:http_after_authorization_observation"
                ))
                .options("-c statement_timeout=30000 -c lock_timeout=30000");
            Some(Gate { config, key })
        }
    };
    Ok((
        port,
        App {
            database,
            test,
            gate,
            authorization: authorization.enabled,
            authorization_gate,
            admission: Arc::new(Semaphore::new(WORKERS)),
        },
    ))
}

async fn termination() {
    #[cfg(unix)]
    {
        match tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate()) {
            Ok(mut term) => {
                tokio::select! { _ = tokio::signal::ctrl_c() => {}, _ = term.recv() => {} }
            }
            Err(_) => {
                let _ = tokio::signal::ctrl_c().await;
            }
        }
    }
    #[cfg(not(unix))]
    {
        let _ = tokio::signal::ctrl_c().await;
    }
}

async fn serve(port: u16, app: App) -> Result<(), ()> {
    let listener = tokio::net::TcpListener::bind(("127.0.0.1", port))
        .await
        .map_err(|_| ())?;
    let port = listener.local_addr().map_err(|_| ())?.port();
    let admission = app.admission.clone();
    let router = Router::new().fallback(handle).with_state(app);
    let (stop, mut stopped) = watch::channel(false);
    let server = axum::serve(listener, router).with_graceful_shutdown(async move {
        let _ = stopped.wait_for(|stopped| *stopped).await;
    });
    // Emit readiness only after binding, never include database configuration.
    println!("{{\"host\":\"127.0.0.1\",\"port\":{port},\"ready\":true}}");
    let server = server.into_future();
    tokio::pin!(server);
    tokio::select! {
        result = &mut server => result.map_err(|_| ()),
        _ = termination() => {
            admission.close();
            let _ = stop.send(true);
            // Stop accepting, drain active handlers; hanging clients are bounded too.
            tokio::time::timeout(DRAIN, &mut server).await.map_err(|_| ())?.map_err(|_| ())
        }
    }
}

fn main() {
    std::panic::set_hook(Box::new(|_| eprintln!("Internal server error")));
    let (port, app) = match configure() {
        Ok(v) => v,
        Err(_) => {
            eprintln!("Invalid server configuration");
            std::process::exit(1);
        }
    };
    let runtime = match tokio::runtime::Builder::new_multi_thread()
        .worker_threads(4)
        .max_blocking_threads(WORKERS)
        .enable_all()
        .build()
    {
        Ok(v) => v,
        Err(_) => {
            eprintln!("Server startup failed");
            std::process::exit(1);
        }
    };
    let result = runtime.block_on(serve(port, app));
    // Blocking tasks cannot be cancelled; retain a final bounded drain at teardown.
    runtime.shutdown_timeout(DRAIN);
    if result.is_err() {
        eprintln!("Server stopped with an error");
        std::process::exit(1);
    }
}
