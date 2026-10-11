package roo.payments;

import static roo.payments.Domain.*;
import static roo.payments.Adapters.*;

public interface Application {
    Result add(long unit, long quantity);
    Result pay(PaymentId id, Mode mode, Failure failure);
    Result refund(RefundId id, Mode mode, Failure failure);
    Result reconcile(boolean unavailable, Failure failure);
}
