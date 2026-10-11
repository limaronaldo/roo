"""Check rendered site navigation, links, fragments, assets, and search data."""

import json
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
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "html":
            self.lang = attrs.get("lang")
        for attribute in ("href", "src"):
            if attrs.get(attribute):
                self.links.append(attrs[attribute])


def main():
    manifest = json.loads((SITE / "source-manifest.json").read_text())
    rendered = {p: Page(p.read_text()) for p in SITE.rglob("*.html")}
    errors = []
    checked = 0
    for path, page in rendered.items():
        if page.lang != "en":
            errors.append(f"Expected English HTML metadata: {path.relative_to(SITE)}")
        relative = path.relative_to(SITE).as_posix()
        url = urljoin(BASE, relative)
        for link in page.links:
            target = urlsplit(urljoin(url, link))
            if target.scheme not in {"http", "https"} or target.netloc != "limaronaldo.github.io":
                continue
            if not target.path.startswith("/roo/"):
                errors.append(f"Link escapes the project base path: {relative}: {link}")
                continue
            destination = SITE / unquote(target.path.removeprefix("/roo/"))
            if destination.is_dir():
                destination /= "index.html"
            if not destination.is_file():
                errors.append(f"Missing local target: {relative}: {link}")
            elif target.fragment and destination in rendered and unquote(target.fragment) not in rendered[destination].ids:
                errors.append(f"Missing local fragment: {relative}: {link}")
            checked += 1
    expected = []
    for source in manifest["pages"]:
        page = Path(source["page"])
        destination = SITE / (page.parent / "index.html" if page.name in {"index.md", "README.md"} else page.with_suffix("") / "index.html")
        if destination not in rendered:
            errors.append(f"Navigation page was not rendered: {source['page']}")
        expected.append(destination)
    search = json.loads((SITE / "search/search_index.json").read_text())
    indexed = {row["location"].split("#")[0] for row in search["docs"]}
    for destination in expected:
        location = destination.relative_to(SITE).as_posix().removesuffix("index.html")
        if location not in indexed:
            errors.append(f"Navigation page is absent from search: {location}")
    report = {"status": "FAIL" if errors else "PASS", "pages": len(expected), "html_files": len(rendered), "local_references": checked, "search_entries": len(search["docs"]), "errors": errors}
    (ROOT / ".site-build/validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
