package roo.postgres;

/** HTTP entrypoint using the accepted composition coordinator. */
public final class HttpCompositionServer {
    private HttpCompositionServer() { }
    public static void main(String[] args) { HttpService.run(args, false); }
}
