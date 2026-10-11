package roo.postgres;

/** HTTP entrypoint using the accepted final Template Method coordinator. */
public final class HttpTemplateServer {
    private HttpTemplateServer() { }
    public static void main(String[] args) { HttpService.run(args, true); }
}
