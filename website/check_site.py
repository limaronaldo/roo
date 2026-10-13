"""Check rendered site navigation, links, fragments, assets, and search data."""

import json
import hashlib
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / ".site-build/site"
BASE = "https://limaronaldo.github.io/roo/"


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.lang = None
        self.options = []
        self.canonical = None
        self.contract_keys = []
        self._term = None
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "dt":
            self._term = ""
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "option":
            self.options.append(attrs)
            if attrs.get("value"):
                self.links.append(attrs["value"])
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        for attribute in ("href", "src"):
            if attrs.get(attribute):
                self.links.append(attrs[attribute])


    def handle_data(self, data):
        if self._term is not None:
            self._term += data

    def handle_endtag(self, tag):
        if tag == "dt" and self._term is not None:
            self.contract_keys.append(self._term.strip().lower())
            self._term = None


def homepage_errors(page, edition, versions, require_contract=True):
    errors = []
    expected = (["owner", "identity", "mutation authority", "access", "horizon", "execution", "failure"]
                if edition == "v0.1.0" else
                ["custodian", "identity", "coordinator", "authorization", "access", "horizon", "execution", "failure"])
    if require_contract and page.contract_keys != expected:
        errors.append(f"Homepage contract does not match its edition: {edition}")
    homes = {version["url"] for version in versions}
    prefix = f"/roo/{edition}/"
    for link in page.links:
        target = urlsplit(urljoin(BASE + edition + "/", link))
        if target.netloc == "limaronaldo.github.io" and target.path.startswith("/roo/"):
            if not target.path.startswith(prefix) and target.path not in homes:
                errors.append(f"Homepage link leaves its edition: {edition}: {link}")
    return errors


def main(site_root=SITE, validation_path=None):
    site = Path(site_root)
    validation = Path(validation_path) if validation_path else site.parent / "validation.json"
    versions = json.loads((site / "versions.json").read_text())
    rendered = {p: Page(p.read_text()) for p in site.rglob("*.html")}
    errors = []
    checked = 0
    for path, page in rendered.items():
        if page.lang != "en":
            errors.append(f"Expected English HTML metadata: {path.relative_to(site)}")
        relative = path.relative_to(site).as_posix()
        url = urljoin(BASE, relative)
        for link in page.links:
            target = urlsplit(urljoin(url, link))
            if target.scheme not in {"http", "https"} or target.netloc != "limaronaldo.github.io":
                continue
            if not target.path.startswith("/roo/"):
                errors.append(f"Link escapes the project base path: {relative}: {link}")
                continue
            destination = site / unquote(target.path.removeprefix("/roo/"))
            if destination.is_dir():
                destination /= "index.html"
            if not destination.is_file():
                errors.append(f"Missing local target: {relative}: {link}")
            elif target.fragment and destination in rendered and unquote(target.fragment) not in rendered[destination].ids:
                errors.append(f"Missing local fragment: {relative}: {link}")
            checked += 1
    editions = []
    for version in versions["versions"]:
        edition = site / version["id"]
        manifest = json.loads((edition / "source-manifest.json").read_text())
        homepage = rendered.get(edition / "index.html")
        if homepage:
            errors.extend(homepage_errors(homepage, version["id"], versions["versions"],
                require_contract="docs/02-relationship-design/" in version["routes"]))
        expected = []
        release_sources = 0
        for source in manifest["pages"]:
            page = Path(source["page"])
            relative = page.parent / "index.html" if page.name in {"index.md", "README.md"} else page.with_suffix("") / "index.html"
            destination = edition / relative
            location = relative.as_posix().removesuffix("index.html")
            if destination not in rendered:
                errors.append(f"Navigation page was not rendered: {version['id']}/{source['page']}")
                continue
            html = rendered[destination]
            if html.canonical != BASE + version["id"] + "/" + location:
                errors.append(f"Incorrect edition canonical URL: {destination.relative_to(site)}")
            selected = [o for o in html.options if "selected" in o]
            if len(selected) != 1 or selected[0]["value"] != version["url"] + location:
                errors.append(f"Incorrect selected edition: {destination.relative_to(site)}")
            wanted = {v["url"] + (location if location in v["routes"] else "") for v in versions["versions"]}
            if {o["value"] for o in html.options} != wanted:
                errors.append(f"Incorrect version destinations: {destination.relative_to(site)}")
            if source["origin"] == "release":
                original = subprocess.check_output(["git", "show", f"{source['commit']}:{source['source']}"], cwd=ROOT)
                release_sources += 1
            else:
                original = (ROOT / source["source"]).read_bytes()
            if hashlib.sha256(original).hexdigest() != source["sha256"]:
                errors.append(f"Source hash mismatch: {version['id']}/{source['source']}")
            expected.append(destination)
        search = json.loads((edition / "search/search_index.json").read_text())
        indexed = {row["location"].split("#")[0] for row in search["docs"]}
        for destination in expected:
            location = destination.relative_to(edition).as_posix().removesuffix("index.html")
            if location not in indexed:
                errors.append(f"Navigation page is absent from edition search: {version['id']}/{location}")
        editions.append({"id": version["id"], "pages": len(expected), "release_sources_verified": release_sources, "search_entries": len(search["docs"]), "documentation_commit": manifest["documentation_commit"], "homepage_contract_keys": homepage.contract_keys if homepage else []})
    for location, target in versions["redirects"].items():
        old = rendered.get(site / location / "index.html")
        if not old or target not in old.links:
            errors.append(f"Missing legacy URL redirect: {location}")
    report = {"status": "FAIL" if errors else "PASS", "editions": editions, "html_files": len(rendered), "local_references": checked, "legacy_redirects": len(versions["redirects"]), "errors": errors}
    validation.parent.mkdir(parents=True, exist_ok=True)
    validation.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
