package roo.postgres;

import java.sql.SQLException;
import static roo.postgres.Domain.*;

interface Application {
    Result execute(String scope, Action action) throws SQLException;
}
