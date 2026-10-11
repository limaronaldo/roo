package roo.postgres;

abstract class OverrideAlgorithm extends TemplateApplication {
    @Override public Domain.Result execute(String scope, Action action) { return Domain.Result.Approved; }
}
