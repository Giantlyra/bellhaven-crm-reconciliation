"""Deterministic normalization for names, addresses, phones."""
from __future__ import annotations

import re
from difflib import SequenceMatcher

_STREET_ABBR = {
    "street": "st", "st.": "st", "avenue": "ave", "ave.": "ave", "road": "rd", "rd.": "rd",
    "drive": "dr", "dr.": "dr", "boulevard": "blvd", "blvd.": "blvd", "lane": "ln", "ln.": "ln",
    "pike": "pike", "pk": "pike", "court": "ct", "place": "pl", "parkway": "pkwy", "highway": "hwy",
    "north": "n", "south": "s", "east": "e", "west": "w", "northwest": "nw", "northeast": "ne",
    "southwest": "sw", "southeast": "se", "saint": "st",
}

# Words that carry no identity in a facility name
_NAME_STOP = {"the", "of", "at", "and", "&", "-", "bellhaven", "senior", "living"}
_NAME_SYN = {
    "rehabilitation": "rehab", "healthcare": "health care", "centre": "center",
}


def norm_street(s: str | None) -> str:
    if not s:
        return ""
    s = s.lower().replace(",", " ").replace(".", " ")
    toks = [_STREET_ABBR.get(t, t) for t in s.split()]
    return " ".join(toks)


def street_number(s: str | None) -> str:
    m = re.match(r"\s*(\d+)", s or "")
    return m.group(1) if m else ""


def is_po_box(s: str | None) -> bool:
    return bool(re.match(r"\s*p\.?\s*o\.?\s*box", (s or "").lower()))


def norm_zip(z: str | None) -> str:
    return re.sub(r"\D", "", z or "")[:5]


def norm_phone(p: str | None) -> str:
    d = re.sub(r"\D", "", p or "")
    return d[-10:] if len(d) >= 10 else d


def norm_name(n: str | None) -> str:
    n = (n or "").lower().replace("&", " and ").replace("-", " ")
    for a, b in _NAME_SYN.items():
        n = re.sub(rf"\b{a}\b", b, n)
    n = re.sub(r"[^a-z0-9 ]", " ", n)
    return " ".join(n.split())


def name_core(n: str | None) -> str:
    """Name with brand/stopwords removed, e.g. 'Bellhaven of Owosso' -> 'owosso'."""
    return " ".join(t for t in norm_name(n).split() if t not in _NAME_STOP)


def similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def address_key(street: str | None, zip_: str | None) -> str:
    return f"{norm_street(street)}|{norm_zip(zip_)}"


# Website care offerings -> CRM care_type vocabulary
CARE_MAP = {
    "assisted living": "Assisted Living",
    "memory support": "Memory Care",
    "short-term rehabilitation & nursing": "Skilled Nursing",
    "short term rehabilitation & nursing": "Skilled Nursing",
    "independent living": "Independent Living",
}


def website_care_type(offerings: list[str]) -> str:
    """Primary CRM care_type for a website community (first listed offering)."""
    for o in offerings:
        m = CARE_MAP.get(o.strip().lower())
        if m:
            return m
    return ""


def website_care_types(offerings: list[str]) -> set[str]:
    return {CARE_MAP[o.strip().lower()] for o in offerings if o.strip().lower() in CARE_MAP}
