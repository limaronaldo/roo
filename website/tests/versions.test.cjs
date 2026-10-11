const { test } = require("node:test");
const assert = require("node:assert/strict");
const { versionTarget } = require("../assets/versions.js");

test("switching a nested chapter keeps its query and section", () => {
  assert.equal(
    versionTarget("/roo/dev/docs/01-foundations/", true,
      "https://limaronaldo.github.io/roo/v0.1.0/docs/01-foundations/?q=ownership#relationships"),
    "https://limaronaldo.github.io/roo/dev/docs/01-foundations/?q=ownership#relationships"
  );
});

test("a missing counterpart opens the destination home without stale fragments", () => {
  assert.equal(
    versionTarget("/roo/v0.1.0/", false,
      "https://limaronaldo.github.io/roo/dev/docs/new/?q=unreleased#new-section"),
    "https://limaronaldo.github.io/roo/v0.1.0/"
  );
});

test("local preview keeps its origin and project path", () => {
  assert.equal(
    versionTarget("/roo/v0.1.0/templates/relationship-contract/", true,
      "http://localhost:8000/roo/dev/templates/relationship-contract/"),
    "http://localhost:8000/roo/v0.1.0/templates/relationship-contract/"
  );
});

test("a selector destination cannot change the site origin", () => {
  assert.throws(() => versionTarget("https://example.com/", true,
    "https://limaronaldo.github.io/roo/dev/"), /local documentation edition/);
});
