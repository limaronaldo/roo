#![forbid(unsafe_code)]

use axum::{
    Router,
    body::{Body, to_bytes},
    extract::{Request, State},
    http::{Method, StatusCode, header},
    response::{IntoResponse, Response},
};
use hyper_util::rt::{TokioIo, TokioTimer};
use postgres::{Config, NoTls};
use roo_http_case::{self as boundary, Fault, Route};
use roo_postgres_case::{database::Database, fixture::Action};
use serde_json::Value;
use std::{
    env,
    error::Error,
    io,
    pin::Pin,
    sync::Arc,
    task::{Context, Poll},
    time::Duration,
};
use tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt, ReadBuf};
use tokio::sync::{Semaphore, watch};
use tower::ServiceExt;

const WORKERS: usize = 16;
const BODY_READERS: usize = 16;
const BODY_READ_DEADLINE: Duration = Duration::from_secs(5);
const REQUEST_LINE_LIMIT: usize = 8192;
const REQUEST_LINE_DEADLINE: Duration = Duration::from_secs(5);
const REQUEST_LINE_READERS: usize = 16;
const DRAIN: Duration = Duration::from_secs(180);

#[derive(Clone)]
struct App {
    database: Database,
    test: bool,
    gate: Option<Gate>,
    authorization: bool,
    authorization_gate: Option<Gate>,
    admission: Arc<Semaphore>,
    body_readers: Arc<Semaphore>,
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

// Only a typed length-limit failure is oversize; framing and truncation are not.
fn body_fault(error: &(dyn Error + 'static)) -> Fault {
    let mut cause: Option<&(dyn Error + 'static)> = Some(error);
    while let Some(error) = cause {
        if error
            .downcast_ref::<http_body_util::LengthLimitError>()
            .is_some()
        {
            return Fault::BodyTooLarge;
        }
        cause = error.source();
    }
    Fault::InvalidRequest
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
    let body_permit = match app.body_readers.clone().try_acquire_owned() {
        Ok(v) => v,
        Err(_) => return error(Fault::Busy),
    };
    // Axum enforces the actual streamed byte limit, including chunked requests.
    // The deadline and semaphore bound both memory and time held by a stalled
    // Content-Length or chunked body before database admission.
    let body_result = tokio::time::timeout(
        BODY_READ_DEADLINE,
        to_bytes(request.into_body(), boundary::BODY_LIMIT),
    )
    .await;
    drop(body_permit);
    let body = match body_result {
        Ok(Ok(body)) => body,
        Ok(Err(read_error)) => return error(body_fault(&read_error)),
        Err(_) => return error(Fault::InvalidRequest),
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
    let operation = boundary::operation_for(route, method)?;
    let database = match principal {
        Some(principal) => app
            .database
            .authorized(scope, principal, operation)
            .map_err(|e| boundary::database_fault(e, probe))?,
        None => app.database.clone(),
    };
    if let Route::Authorization(operation) = route {
        let allowed = database
            .operation_allowed(scope)
            .map_err(|e| boundary::database_fault(e, probe))?;
        return Ok((
            200,
            serde_json::json!({"authorization":{"operation":operation.token(),"allowed":allowed}}),
        ));
    }
    if method == Method::POST && app.authorization {
        // Observation is advisory even when denied. Execution rechecks policy
        // under a row lock after the configured deterministic test gate.
        let _ = database
            .operation_allowed(scope)
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
            body_readers: Arc::new(Semaphore::new(BODY_READERS)),
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

// Replay exactly the consumed request line; Hyper remains responsible for HTTP
// framing. A single request per connection prevents later unvalidated targets.
struct PrefixedStream {
    stream: tokio::net::TcpStream,
    prefix: Vec<u8>,
    offset: usize,
}
impl AsyncRead for PrefixedStream {
    fn poll_read(
        mut self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &mut ReadBuf<'_>,
    ) -> Poll<io::Result<()>> {
        if self.offset < self.prefix.len() && buf.remaining() > 0 {
            let end = (self.offset + buf.remaining()).min(self.prefix.len());
            buf.put_slice(&self.prefix[self.offset..end]);
            self.offset = end;
            return Poll::Ready(Ok(()));
        }
        Pin::new(&mut self.stream).poll_read(cx, buf)
    }
}
impl AsyncWrite for PrefixedStream {
    fn poll_write(
        mut self: Pin<&mut Self>,
        cx: &mut Context<'_>,
        buf: &[u8],
    ) -> Poll<io::Result<usize>> {
        Pin::new(&mut self.stream).poll_write(cx, buf)
    }
    fn poll_flush(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<io::Result<()>> {
        Pin::new(&mut self.stream).poll_flush(cx)
    }
    fn poll_shutdown(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<io::Result<()>> {
        Pin::new(&mut self.stream).poll_shutdown(cx)
    }
}

async fn request_line(stream: &mut tokio::net::TcpStream) -> Result<Vec<u8>, ()> {
    let mut line = Vec::with_capacity(128);
    loop {
        if line.len() == REQUEST_LINE_LIMIT {
            return Err(());
        }
        let byte = stream.read_u8().await.map_err(|_| ())?;
        line.push(byte);
        if byte == b'\n' {
            // Check the raw second field before http::Uri can discard a fragment.
            // Strict CRLF and field separation also prevent parser disagreement
            // about which request line was validated (including leading blanks).
            let text = line.strip_suffix(b"\r\n").ok_or(())?;
            let fields: Vec<_> = text.split(|byte| *byte == b' ').collect();
            if fields.len() != 3
                || fields.iter().any(|field| field.is_empty())
                || fields[1].contains(&b'#')
                || !matches!(fields[2], b"HTTP/1.0" | b"HTTP/1.1")
            {
                return Err(());
            }
            return Ok(line);
        }
    }
}

async fn reject_transport(stream: &mut tokio::net::TcpStream, fault: Fault) {
    let body = fault.body().to_string();
    let reason = if fault == Fault::Busy {
        "Service Unavailable"
    } else {
        "Bad Request"
    };
    let response = format!(
        "HTTP/1.1 {} {}\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\nCache-Control: no-store\r\n\r\n{}",
        fault.status(),
        reason,
        body.len(),
        body,
    );
    // A client that never reads must not retain a rejecting connection task.
    let _ = tokio::time::timeout(Duration::from_secs(1), async {
        stream.write_all(response.as_bytes()).await?;
        stream.shutdown().await
    })
    .await;
}

async fn connection(
    mut stream: tokio::net::TcpStream,
    router: Router,
    readers: Arc<Semaphore>,
    mut stopped: watch::Receiver<bool>,
) {
    let permit = match readers.try_acquire_owned() {
        Ok(permit) => permit,
        Err(_) => {
            reject_transport(&mut stream, Fault::Busy).await;
            return;
        }
    };
    let line = tokio::select! {
        biased;
        _ = async {
            // Drop watch::Ref here so select never retains it across a drain await.
            let _ = stopped.wait_for(|stopped| *stopped).await;
        } => return,
        line = tokio::time::timeout(REQUEST_LINE_DEADLINE, request_line(&mut stream)) => line,
    };
    drop(permit);
    let prefix = match line {
        Ok(Ok(line)) => line,
        _ => {
            reject_transport(&mut stream, Fault::InvalidRequest).await;
            return;
        }
    };
    let service =
        hyper::service::service_fn(move |request: hyper::Request<hyper::body::Incoming>| {
            router.clone().oneshot(request.map(Body::new))
        });
    let mut builder = hyper::server::conn::http1::Builder::new();
    builder
        .keep_alive(false)
        .half_close(true)
        .timer(TokioTimer::new())
        .header_read_timeout(REQUEST_LINE_DEADLINE);
    let connection = builder.serve_connection(
        TokioIo::new(PrefixedStream {
            stream,
            prefix,
            offset: 0,
        }),
        service,
    );
    tokio::pin!(connection);
    tokio::select! {
        _ = &mut connection => {},
        _ = async {
            // Drop watch::Ref here so select never retains it across a drain await.
            let _ = stopped.wait_for(|stopped| *stopped).await;
        } => {
            connection.as_mut().graceful_shutdown();
            let _ = connection.await;
        }
    }
}

async fn serve(port: u16, app: App) -> Result<(), ()> {
    let listener = tokio::net::TcpListener::bind(("127.0.0.1", port))
        .await
        .map_err(|_| ())?;
    let port = listener.local_addr().map_err(|_| ())?.port();
    let admission = app.admission.clone();
    let body_readers = app.body_readers.clone();
    let line_readers = Arc::new(Semaphore::new(REQUEST_LINE_READERS));
    let router = Router::new().fallback(handle).with_state(app);
    let (stop, stopped) = watch::channel(false);
    let mut connections = tokio::task::JoinSet::new();
    let termination = termination();
    tokio::pin!(termination);
    // Emit readiness only after binding, never include database configuration.
    println!("{{\"host\":\"127.0.0.1\",\"port\":{port},\"ready\":true}}");
    let mut result = Ok(());
    loop {
        tokio::select! {
            biased;
            _ = &mut termination => break,
            completed = connections.join_next(), if !connections.is_empty() => {
                if completed.is_some_and(|result| result.is_err()) { result = Err(()); }
            }
            accepted = listener.accept() => match accepted {
                Ok((stream, _)) => {
                    connections.spawn(connection(stream, router.clone(), line_readers.clone(), stopped.clone()));
                }
                Err(_) => { result = Err(()); break; }
            }
        }
    }
    drop(listener);
    admission.close();
    body_readers.close();
    line_readers.close();
    let _ = stop.send(true);
    // Stop accepting and drain active handlers, including tracked transport tasks.
    if tokio::time::timeout(DRAIN, async {
        while let Some(completed) = connections.join_next().await {
            if completed.is_err() {
                result = Err(());
            }
        }
    })
    .await
    .is_err()
    {
        return Err(()); // Dropping JoinSet aborts remaining async connections.
    }
    result
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

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn body_read_errors_are_not_all_reported_as_oversize() {
        let oversized = to_bytes(
            Body::from(vec![b'x'; boundary::BODY_LIMIT + 1]),
            boundary::BODY_LIMIT,
        )
        .await
        .expect_err("body above the byte limit must fail");
        assert_eq!(body_fault(&oversized), Fault::BodyTooLarge);

        let truncated = std::io::Error::new(std::io::ErrorKind::UnexpectedEof, "truncated body");
        assert_eq!(body_fault(&truncated), Fault::InvalidRequest);
    }
}
