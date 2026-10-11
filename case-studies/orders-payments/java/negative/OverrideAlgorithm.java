package roo.payments;

// Expected diagnostic: pay(...) cannot override pay(...); overridden method is final.
abstract class OverrideAlgorithm extends TemplateApplication {
    @Override public Domain.Result pay(Domain.PaymentId id, Adapters.Mode mode, Adapters.Failure failure) {
        return Domain.Result.Approved;
    }
}
