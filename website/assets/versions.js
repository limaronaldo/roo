/* Native, keyboard-accessible selector; each option has a build-checked URL. */
(function () {
  function versionTarget(value, samePage, currentHref) {
    const current = new URL(currentHref);
    const target = new URL(value, current.origin);
    if (target.origin !== current.origin) throw new Error("Expected a local documentation edition");
    if (samePage) {
      target.search = current.search;
      target.hash = current.hash;
    }
    return target.href;
  }
  if (typeof module !== "undefined") module.exports = { versionTarget };
  if (typeof document === "undefined") return;
  const selector = document.getElementById("roo-version");
  if (!selector) return;
  selector.addEventListener("change", function () {
    const option = selector.selectedOptions[0];
    window.location.assign(versionTarget(option.value, option.dataset.samePage === "true", window.location.href));
  });
})();
