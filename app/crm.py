"""Thin CRM API client. Token is sent as a Bearer header and never logged or included in errors."""
from __future__ import annotations

from typing import Any, Optional

import httpx

from . import config


class CRMError(Exception):
    pass


def _unwrap(body):
    if isinstance(body, dict) and isinstance(body.get("data"), dict):
        return body["data"]
    return body


class CRMClient:
    def __init__(self, base: Optional[str] = None, token: Optional[str] = None,
                 transport: Optional[httpx.BaseTransport] = None):
        token = token if token is not None else config.CRM_TOKEN
        if not token:
            raise CRMError("CRM_TOKEN is not set (put it in .env)")
        self._http = httpx.Client(
            base_url=base or config.CRM_API_BASE,
            headers={"Authorization": f"Bearer {token}"},
            timeout=20.0,
            transport=transport,
        )

    def _req(self, method: str, path: str, **kw) -> Any:
        r = self._http.request(method, path, **kw)
        if r.status_code >= 400:
            raise CRMError(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
        return r.json()

    # ---- reads ----
    def me(self) -> dict:
        return self._req("GET", "/me")

    def list_accounts(self, page_size: int = 50, **filters) -> list:
        """Fetch every page until `total` is reached (never just page 1). Fails closed on inconsistency."""
        filters = {k: v for k, v in filters.items() if v not in (None, "")}
        out: list = []
        page, total = 1, None
        while True:
            body = self._req("GET", "/accounts", params={**filters, "page": page, "page_size": page_size})
            data = body.get("data", [])
            if total is None:
                total = body.get("total")
            out.extend(data)
            if not data or (total is not None and len(out) >= total):
                break
            page += 1
            if page > 1000:
                raise CRMError("Pagination did not terminate")
        if total is not None and len(out) != total:
            raise CRMError(f"Incomplete account listing: got {len(out)} of {total}")
        if len({a.get("account_id") for a in out}) != len(out):
            raise CRMError("Duplicate account ids across pages (listing changed mid-read); re-run")
        return out

    def get_account(self, account_id: str) -> dict:
        return _unwrap(self._req("GET", f"/accounts/{account_id}"))

    def list_contacts(self, **filters) -> list:
        out, page = [], 1
        while True:
            body = self._req("GET", "/contacts", params={**filters, "page": page, "page_size": 50})
            data = body.get("data", [])
            out.extend(data)
            if not data or len(out) >= body.get("total", len(out)):
                break
            page += 1
        return out

    # ---- writes (only ever called by executor.execute for approved, confirmed proposals) ----
    def create_account(self, fields: dict) -> dict:
        return _unwrap(self._req("POST", "/accounts", json=fields))

    def update_account(self, account_id: str, fields: dict) -> dict:
        return _unwrap(self._req("PATCH", f"/accounts/{account_id}", json=fields))
