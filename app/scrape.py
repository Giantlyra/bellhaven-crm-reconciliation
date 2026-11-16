"""Bellhaven website scraper.

Discovers facilities from every directory page AND from any /communities/<slug>
link elsewhere on the site (the homepage announces a community that the
directory omits). Every record keeps its source URL + timestamp as evidence.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from . import config

DETAIL_RE = re.compile(r"^/communities/[a-z0-9-]+/?$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class ScrapeResult:
    def __init__(self):
        self.facilities: list[dict] = []
        self.errors: list[dict] = []
        self.directory_count: int | None = None   # "N communities listed"
        self.homepage_count: int | None = None    # "serve N communities"
        self.directory_slugs: set[str] = set()
        self.complete = False                     # True only if every page loaded


def _get(client: httpx.Client, url: str) -> str:
    r = client.get(url)
    r.raise_for_status()
    return r.text


def _detail_links(soup: BeautifulSoup, base: str) -> set[str]:
    out = set()
    for a in soup.find_all("a", href=True):
        path = urlparse(urljoin(base, a["href"])).path
        if DETAIL_RE.match(path):
            out.add(path.rstrip("/"))
    return out


def parse_detail(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    rec: dict = {"source_url": url, "name": soup.h1.get_text(strip=True) if soup.h1 else ""}
    fields = {}
    for dt in soup.select("dl.detail dt"):
        dd = dt.find_next_sibling("dd")
        if dd:
            fields[dt.get_text(strip=True).lower()] = dd
    addr = fields.get("address")
    if addr:
        lines = [s.strip() for s in addr.get_text("\n").split("\n") if s.strip()]
        rec["street"] = lines[0] if lines else ""
        m = re.match(r"(.+?),\s*([A-Z]{2})\s+(\d{5})", lines[-1]) if len(lines) > 1 else None
        if m:
            rec["city"], rec["state"], rec["zip"] = m.group(1), m.group(2), m.group(3)
    care = fields.get("care offerings")
    rec["care_offerings"] = [b.get_text(strip=True) for b in care.select(".badge")] if care else []
    if care and not rec["care_offerings"]:
        rec["care_offerings"] = [care.get_text(strip=True)]
    rec["administrator"] = fields["administrator"].get_text(strip=True) if "administrator" in fields else ""
    rec["phone"] = fields["phone"].get_text(strip=True) if "phone" in fields else ""
    rec["content_hash"] = hashlib.sha256(html.encode()).hexdigest()[:16]
    rec["retrieved_at"] = _now()
    return rec


def scrape(base: str | None = None, transport: httpx.BaseTransport | None = None) -> ScrapeResult:
    base = (base or config.SITE_BASE).rstrip("/")
    res = ScrapeResult()
    slugs: set[str] = set()
    with httpx.Client(timeout=20.0, transport=transport, follow_redirects=True) as c:
        # Homepage: count + any announced communities
        try:
            home = BeautifulSoup(_get(c, base + "/"), "html.parser")
            m = re.search(r"serve\s+(\d+)\s+communities", home.get_text(" "))
            res.homepage_count = int(m.group(1)) if m else None
            slugs |= _detail_links(home, base + "/")
        except Exception as e:  # noqa: BLE001
            res.errors.append({"url": base + "/", "error": str(e)})

        # Directory: follow "Next" pagination until it stops
        url, seen_pages = base + "/communities", set()
        while url and url not in seen_pages:
            seen_pages.add(url)
            try:
                soup = BeautifulSoup(_get(c, url), "html.parser")
            except Exception as e:  # noqa: BLE001
                res.errors.append({"url": url, "error": str(e)})
                break
            m = re.search(r"(\d+)\s+communities listed", soup.get_text(" "))
            if m:
                res.directory_count = int(m.group(1))
            page_links = _detail_links(soup, url)
            res.directory_slugs |= page_links
            slugs |= page_links
            nxt = soup.find("a", string=re.compile(r"Next"))
            url = urljoin(url, nxt["href"]) if nxt else None

        # Detail pages
        for path in sorted(slugs):
            durl = base + path
            try:
                rec = parse_detail(_get(c, durl), durl)
                rec["in_directory"] = path in res.directory_slugs
                rec["slug"] = path.rsplit("/", 1)[-1]
                res.facilities.append(rec)
            except Exception as e:  # noqa: BLE001
                res.errors.append({"url": durl, "error": str(e)})

    res.complete = not res.errors and len(res.facilities) > 0
    return res
