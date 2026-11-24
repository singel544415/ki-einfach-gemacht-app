#!/usr/bin/env python3
"""Local, dependency-free checks for the public static website."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [
    ROOT / "index.html",
    ROOT / "privacy.html",
    ROOT / "terms.html",
    ROOT / "support.html",
]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.lang: str | None = None
        self.viewport = False
        self.icon_href: str | None = None
        self.title_parts: list[str] = []
        self._in_title = False
        self._main_count = 0
        self._h1_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        elif tag == "meta" and values.get("name") == "viewport":
            self.viewport = True
        elif tag == "link" and "icon" in (values.get("rel") or "").split():
            self.icon_href = values.get("href")
        elif tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")
        elif tag == "title":
            self._in_title = True
        elif tag == "main":
            self._main_count += 1
        elif tag == "h1":
            self._h1_count += 1
        if values.get("id"):
            self.ids.add(values["id"] or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    for path in HTML_FILES:
        require(path.is_file(), f"Fehlende Seite: {path.name}")
        page = parse(path)
        require(page.lang == "de", f"{path.name}: lang=de fehlt")
        require(page.viewport, f"{path.name}: Viewport-Meta fehlt")
        require(bool(page.icon_href), f"{path.name}: Icon-Link fehlt")
        require((path.parent / (page.icon_href or "")).is_file(), f"{path.name}: Icon-Datei fehlt")
        require(bool("".join(page.title_parts).strip()), f"{path.name}: Titel fehlt")
        require(page._main_count == 1, f"{path.name}: genau ein main erwartet")
        require(page._h1_count == 1, f"{path.name}: genau eine h1 erwartet")

        for href in page.links:
            parsed = urlparse(href)
            if parsed.scheme in {"http", "https", "mailto"} or href.startswith("#"):
                continue
            target = (path.parent / parsed.path).resolve()
            require(target.is_file(), f"{path.name}: defekter Link {href}")
            if parsed.fragment:
                target_page = parse(target)
                require(parsed.fragment in target_page.ids, f"{path.name}: fehlendes Ziel {href}")

    index = (ROOT / "index.html").read_text(encoding="utf-8").lower()
    for phrase in [
        "desktop-anwendung",
        "pilotphase",
        "tiktok",
        "freigabe",
        "ki-generiert",
        "datenschutz",
        "nutzungsbedingungen",
        "support",
        "datenlöschung",
        "assets/review-candidate.png",
        "assets/review-settings.png",
        "tatsächliche anwendung",
    ]:
        require(phrase in index, f"index.html: Pflichtinhalt fehlt: {phrase}")

    privacy = (ROOT / "privacy.html").read_text(encoding="utf-8").lower()
    for phrase in ["kontotrennung", "zugangstoken", "widerruf", "löschung"]:
        require(phrase in privacy, f"privacy.html: Pflichtinhalt fehlt: {phrase}")

    support = (ROOT / "support.html").read_text(encoding="utf-8").lower()
    for phrase in ["datenlöschung", "tiktok-konto", "lokal", "github"]:
        require(phrase in support, f"support.html: Pflichtinhalt fehlt: {phrase}")

    css = (ROOT / "style.css").read_text(encoding="utf-8").lower()
    for phrase in [":focus-visible", "prefers-reduced-motion", "@media", "skip-link"]:
        require(phrase in css, f"style.css: Accessibility/Responsive-Regel fehlt: {phrase}")

    print(f"OK: {len(HTML_FILES)} HTML-Seiten, interne Links und Pflichtinhalte geprüft")


if __name__ == "__main__":
    main()
