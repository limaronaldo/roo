package roo.postgres;

final class JdbcTemplateApplication extends TemplateApplication {
    private final Store local;
    private final Provider remote;
    private final Database db;
    JdbcTemplateApplication(Store local, Provider remote, Database db) { this.local = local; this.remote = remote; this.db = db; }
    @Override protected Store store() { return local; }
    @Override protected Provider provider() { return remote; }
    @Override protected Database database() { return db; }
}
