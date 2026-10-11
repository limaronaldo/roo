package roo.postgres;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.Map;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.Semaphore;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

/** Stateless adapter composition shared by the two independently selectable coordinators. */
final class HttpService {
    private HttpService() { }
    record Config(int port, boolean test, Long gate, String worker) {
        static Config parse(Map<String, String> env) {
            if (!"127.0.0.1".equals(env.get("ROO_HTTP_HOST"))) throw new IllegalArgumentException("Invalid host");
            String port = env.get("ROO_HTTP_PORT");
            if (port == null || !port.matches("[0-9]{1,5}") || Integer.parseInt(port) > 65535) throw new IllegalArgumentException("Invalid port");
            String test = env.get("ROO_HTTP_TEST_MODE");
            if (test != null && !test.equals("1")) throw new IllegalArgumentException("Invalid test mode");
            String gate = env.get("ROO_HTTP_GATE_LOCK");
            if (test == null && (gate != null || env.containsKey("ROO_GATE_POINT") || env.containsKey("ROO_GATE_LOCK")))
                throw new IllegalArgumentException("Test mode required");
            Long key = null;
            if (gate != null) {
                if (!gate.matches("[0-9]+")) throw new IllegalArgumentException("Invalid gate");
                key = Long.valueOf(gate);
                if (key <= 0) throw new IllegalArgumentException("Invalid gate");
            }
            String worker = env.getOrDefault("ROO_WORKER_ID", "java");
            if (!worker.matches("[A-Za-z0-9_]{1,32}")) throw new IllegalArgumentException("Invalid worker");
            return new Config(Integer.parseInt(port), test != null, key, worker);
        }
    }
    static void run(String[] args, boolean template) {
        HttpServer server = null;
        ThreadPoolExecutor workers = null;
        try {
            if (args.length != 0) throw new IllegalArgumentException("Unexpected arguments");
            Map<String, String> env = Map.copyOf(System.getenv());
            Config config = Config.parse(env);
            Database db = new Database(env);
            Store store = new Store(db);
            Provider provider = new Provider(db);
            Application app = template ? new JdbcTemplateApplication(store, provider, db) : new CompositionApplication(store, provider, db);
            var admission = new Semaphore(16);
            workers = new ThreadPoolExecutor(32, 32, 0L, TimeUnit.MILLISECONDS,
                new ArrayBlockingQueue<>(64), new ThreadPoolExecutor.CallerRunsPolicy());
            server = HttpServer.create(new InetSocketAddress("127.0.0.1", config.port()), 64);
            server.setExecutor(workers);
            server.createContext("/", exchange -> handle(exchange, config, db, store, app, admission));
            HttpServer listener = server;
            ThreadPoolExecutor pool = workers;
            AtomicBoolean stopped = new AtomicBoolean();
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                if (!stopped.compareAndSet(false, true)) return;
                listener.stop(60);
                pool.shutdown();
                try {
                    if (!pool.awaitTermination(60, TimeUnit.SECONDS)) pool.shutdownNow();
                } catch (InterruptedException interrupted) { pool.shutdownNow(); Thread.currentThread().interrupt(); }
            }, "roo-http-shutdown"));
            server.start();
            System.out.println("{\"host\":\"127.0.0.1\",\"port\":" + server.getAddress().getPort() + ",\"ready\":true}");
            System.out.flush();
        } catch (IOException | RuntimeException failure) {
            if (server != null) server.stop(0);
            if (workers != null) workers.shutdownNow();
            System.err.println("HTTP startup failed: invalid configuration or unavailable listener.");
            System.exit(1);
        }
    }
    private static void handle(HttpExchange exchange, Config config, Database db, Store store, Application app, Semaphore admission) {
        boolean admitted = false;
        try (exchange) {
            try {
                byte[] body = HttpProtocol.read(exchange.getRequestBody());
                HttpProtocol.Input input = HttpProtocol.validate(exchange.getRequestURI(), exchange.getRequestMethod(), exchange.getRequestHeaders(), body, config.test());
                admitted = admission.tryAcquire();
                if (!admitted) throw new HttpProtocol.Rejection(503, "Busy");
                String scope = input.route().scope();
                if (input.method().equals("PUT")) store.init(scope);
                else {
                    // Only this read's documented missing-row exception becomes a 404.
                    try { store.snapshot(scope, scope, "-"); }
                    catch (IllegalArgumentException missing) { throw new HttpProtocol.Rejection(404, "ScopeNotFound"); }
                }
                Domain.Result result = null;
                if (input.action() != null) {
                    if (input.route().resource().equals("conflict")) {
                        try { result = app.execute(scope, input.action()); }
                        catch (IllegalArgumentException badProbe) { throw HttpProtocol.invalid(); }
                    } else result = app.execute(scope, input.action());
                }
                byte[] response = HttpProtocol.snapshot(store.snapshot(scope, scope, result == null ? "-" : result.name()));
                if (input.method().equals("POST")) gate(db, config);
                send(exchange, result == null ? 200 : HttpProtocol.status(result), response);
            } catch (HttpProtocol.Rejection rejected) {
                if (rejected.allow != null) exchange.getResponseHeaders().set("Allow", rejected.allow);
                send(exchange, rejected.status, HttpProtocol.error(rejected.code));
            } catch (SQLException unavailable) {
                send(exchange, 503, HttpProtocol.error("DatabaseUnavailable"));
            } catch (RuntimeException unexpected) {
                send(exchange, 500, HttpProtocol.error("InternalError"));
            } finally {
                if (admitted) admission.release();
            }
        } catch (IOException disconnected) {
            // A transport loss never causes command replay or implies rollback.
            System.err.println("HTTP connection ended before response delivery.");
        }
    }
    private static void gate(Database db, Config config) throws SQLException {
        if (config.gate() == null) return;
        try (Connection connection = db.open(true)) {
            try (PreparedStatement statement = connection.prepareStatement("SELECT set_config('application_name', ?, false)")) {
                statement.setString(1, "roo:" + config.worker() + ":http_after_snapshot"); statement.execute();
            }
            try (PreparedStatement statement = connection.prepareStatement("SELECT pg_advisory_lock(?)")) {
                statement.setLong(1, config.gate()); statement.execute();
            }
            try (PreparedStatement statement = connection.prepareStatement("SELECT pg_advisory_unlock(?)")) {
                statement.setLong(1, config.gate()); statement.execute();
            }
        }
    }
    private static void send(HttpExchange exchange, int status, byte[] body) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        exchange.getResponseHeaders().set("Cache-Control", "no-store");
        exchange.getResponseHeaders().set("Connection", "close");
        exchange.sendResponseHeaders(status, body.length);
        exchange.getResponseBody().write(body);
    }
}
