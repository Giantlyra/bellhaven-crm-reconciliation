"""Reconciliation Engine: deterministic, explainable matching of website facilities to CRM accounts.

Matching tiers
  1. exact normalized street + ZIP                              -> high
  2. same street number + ZIP + street text similarity >= 0.8   -> high
  3. same city/state + name-core similarity >= 0.85, supported by
     phone match or a non-physical (PO Box) CRM address        -> medium
  4. name + locality similar but address/phone conflict         -> HOLD (human review, no write)
Name similarity alone never drives a consequential change.

Every proposal carries:
  risk        low | medium | high | hold
  actionable  False for HOLD items: they have no executable operations at all
  evidence    website record + CRM record(s) + match basis + alternatives considered
"""
from __future__ import annotations

from datetime import date

from . import normalize as N
from .policy import baseline, chow_required, financials, has_billing_history


def is_parent_account(a: dict) -> bool:
    return (a.get("name") or "").endswith("(Parent Account)")


def superseded(a: dict) -> bool:
    """Accounts already resolved as duplicates or CHOW predecessors are not matching candidates."""
    return bool(a.get("duplicate_of_account") or a.get("chow_current_account"))


def find_parent_id(accounts: list, name_prefix: str):
    hits = [a["account_id"] for a in accounts
            if is_parent_account(a) and a["name"].lower().startswith(name_prefix.lower())]
    return hits[0] if len(hits) == 1 else None


def _addr_tier(w: dict, a: dict) -> int:
    """2 = exact address, 1 = strong address, 0 = none."""
    if not N.norm_zip(w.get("zip")) or N.norm_zip(w.get("zip")) != N.norm_zip(a.get("billing_zip")):
        return 0
    ws, cs = N.norm_street(w.get("street")), N.norm_street(a.get("billing_street"))
    if ws and ws == cs:
        return 2
    if N.street_number(ws) and N.street_number(ws) == N.street_number(cs) and N.similarity(ws, cs) >= 0.8:
        return 1
    return 0


def _same_locality(w: dict, a: dict) -> bool:
    return ((w.get("city") or "").lower() == (a.get("billing_city") or "").lower()
            and (w.get("state") or "").upper() == (a.get("billing_state") or "").upper())


def _name_sim(w: dict, a: dict) -> float:
    return N.similarity(N.name_core(w["name"]), N.name_core(a.get("name")))


def _website_fields(w: dict) -> dict:
    return {
        "name": w["name"], "billing_street": w.get("street", ""), "billing_city": w.get("city", ""),
        "billing_state": w.get("state", ""), "billing_zip": w.get("zip", ""), "phone": w.get("phone", ""),
        "care_type": N.website_care_type(w.get("care_offerings", [])),
    }


def field_diffs(w: dict, a: dict) -> dict:
    """Fields where the CRM disagrees with the website (website is source of truth). Never parent/financials."""
    d = {}
    if w["name"].strip() != (a.get("name") or "").strip():
        d["name"] = w["name"]
    if w.get("street") and N.norm_street(w["street"]) != N.norm_street(a.get("billing_street")):
        d["billing_street"] = w["street"]
    if w.get("city") and w["city"].lower() != (a.get("billing_city") or "").lower():
        d["billing_city"] = w["city"]
    if w.get("state") and w["state"].upper() != (a.get("billing_state") or "").upper():
        d["billing_state"] = w["state"]
    if w.get("zip") and N.norm_zip(w["zip"]) != N.norm_zip(a.get("billing_zip")):
        d["billing_zip"] = w["zip"]
    if w.get("phone") and N.norm_phone(w["phone"]) != N.norm_phone(a.get("phone")):
        d["phone"] = w["phone"]
    care = N.website_care_types(w.get("care_offerings", []))
    if care and a.get("care_type") not in care:
        d["care_type"] = N.website_care_type(w["care_offerings"])
    return d


CRM_KEYS = ["account_id", "name", "parent_id", "parent_name", "billing_street", "billing_city", "billing_state",
            "billing_zip", "phone", "care_type", "status", "lifetime_revenue", "outstanding_ar",
            "chow_current_account", "duplicate_of_account", "note", "updated_at"]


def _crm_view(a: dict) -> dict:
    return {k: a.get(k) for k in CRM_KEYS}


def _append_note(existing, text: str) -> str:
    existing = (existing or "").strip()
    return f"{existing}\n{text}" if existing else text


def _decisive(w: dict, a: dict, bh: str) -> tuple:
    """Survivor criteria that are actual evidence (not tiebreaks)."""
    rev, _ = financials(a)
    return (a.get("parent_id") == bh, (rev or 0) > 0,
            bool(w.get("phone")) and N.norm_phone(a.get("phone")) == N.norm_phone(w.get("phone")))


def _survivor_rank(w: dict, a: dict, bh: str):
    return _decisive(w, a, bh) + (
        a.get("status") == "Active", _addr_tier(w, a),
        N.similarity(N.norm_name(w["name"]), N.norm_name(a.get("name"))), a["account_id"])


def _hold(subject_key, title, account_ids, reason, w_ev, crm, alternatives, basis, warnings=()):
    return {
        "kind": "HOLD", "title": title, "subject_key": subject_key, "account_ids": account_ids,
        "confidence": "low", "risk": "hold", "actionable": False, "hold_reason": reason,
        "explanation": reason + " No CRM change is proposed; a human must resolve identity/ownership first.",
        "warnings": list(warnings),
        "evidence": {"website": w_ev, "crm": crm, "alternatives": alternatives, "basis": basis},
        "current": {}, "proposed": {}, "ops": [], "baseline": {},
    }


def reconcile(facilities: list, accounts: list, scrape_complete: bool, today=None, resolutions=None) -> tuple:
    """Returns (match_results, proposals). Pure function: no I/O.

    resolutions: {subject_key: {"decision": ..., "account_id": ..., "id": ...}} recorded by an operator for a
    HOLD subject (see cli `resolve`). Supported:
      distinct  - web:<slug> identity HOLD: the look-alike CRM account(s) are a different facility -> create proposal
      survivor  - web:<slug> indistinguishable-group HOLD: account_id is the survivor -> normal duplicate/parent/
                  field proposals. Ignored if that account is no longer in the group.
    A resolution only changes what is PROPOSED; every proposal still goes through policy and human approval."""
    resolutions = resolutions or {}
    today = today or date.today().isoformat()
    tag = f"[Bellhaven reconciliation {today}]"
    bh = find_parent_id(accounts, "Bellhaven Senior Living")
    if not bh:
        raise ValueError("Bellhaven parent account not found exactly once in CRM; refusing to reconcile")
    parent_names = {a["account_id"]: a["name"] for a in accounts if is_parent_account(a)}
    pool = [a for a in accounts if not is_parent_account(a) and not superseded(a)]
    results, proposals, claimed = [], [], set()

    for w in facilities:
        ev_web = {k: w.get(k) for k in ("name", "street", "city", "state", "zip", "phone", "care_offerings",
                                        "administrator", "source_url", "retrieved_at", "in_directory")}
        addr = sorted([a for a in pool if _addr_tier(w, a)], key=lambda a: -_addr_tier(w, a))
        name_loc = [a for a in pool if a not in addr and _same_locality(w, a) and _name_sim(w, a) >= 0.85]
        same_name_elsewhere = [a for a in pool if a not in addr and a not in name_loc
                               and N.norm_name(a.get("name")) == N.norm_name(w["name"])]
        alternatives = [_crm_view(a) for a in name_loc + same_name_elsewhere]
        slug = w.get("slug") or w["name"]
        resolution = resolutions.get(f"web:{slug}") or {}
        distinct = resolution.get("decision") == "distinct"

        group, confidence, basis = [], None, ""
        if addr:
            group, confidence = addr, "high"
            basis = "address+ZIP match (" + ", ".join(
                f"{a['account_id']}: {'exact' if _addr_tier(w, a) == 2 else 'strong'}" for a in addr) + ")"
        else:
            supported = [a for a in name_loc if N.norm_phone(a.get("phone")) == N.norm_phone(w.get("phone"))
                         or N.is_po_box(a.get("billing_street"))]
            if len(supported) == 1:
                group, confidence = supported, "medium"
                a = supported[0]
                why = []
                if N.norm_phone(a.get("phone")) == N.norm_phone(w.get("phone")):
                    why.append("phone matches")
                if N.is_po_box(a.get("billing_street")):
                    why.append("CRM street is a PO Box (mailing address, not the facility)")
                if N.norm_zip(a.get("billing_zip")) == N.norm_zip(w.get("zip")):
                    why.append("ZIP matches")
                basis = f"name + city/state match supported by: {', '.join(why)}"
                alternatives = [x for x in alternatives if x["account_id"] != a["account_id"]]

        res = {"facility": w["name"], "source_url": w.get("source_url"), "in_directory": w.get("in_directory", True),
               "website": ev_web}

        # ---------- no confident match ----------
        if not group:
            if name_loc and not distinct:
                reason = ("A same-city CRM account has a similar name but its street/phone conflict with the website "
                          "(" + "; ".join(f"{a['account_id']} '{a['name']}' at {a.get('billing_street')}, "
                                          f"{a.get('billing_zip')}" for a in name_loc) + ").")
                res.update(classification="HOLD", account_ids=[], basis=reason, candidates=alternatives)
                proposals.append(_hold(f"web:{slug}", f"HOLD — identity unresolved: {w['name']}", [],
                                       reason, ev_web, None, alternatives, "name+city only; address conflicts"))
            elif same_name_elsewhere and not distinct:
                reason = ("An identically named CRM account exists at a different address (" + "; ".join(
                    f"{a['account_id']} at {a.get('billing_street')}, {a.get('billing_city')} {a.get('billing_state')}"
                    f" under {a.get('parent_name') or 'no parent'}" for a in same_name_elsewhere) +
                    "). Same name, different location: it must not be re-parented, and creating a new account "
                    "needs confirmation that the two are distinct facilities.")
                res.update(classification="HOLD", account_ids=[], basis=reason, candidates=alternatives)
                proposals.append(_hold(f"web:{slug}", f"HOLD — same name, different address: {w['name']}", [],
                                       reason, ev_web, None, alternatives, "name only; address conflicts"))
            else:
                fields = {**_website_fields(w), "parent_id": bh, "status": "Active",
                          "note": f"{tag} Created from Bellhaven website listing {w.get('source_url')}."}
                warnings = ["Creates a new CRM account. Verify the facility is not in the CRM under another name "
                            "or address before approving."]
                if not w.get("in_directory", True):
                    warnings.append("Listed on the homepage/detail page but missing from the directory pagination.")
                basis = "no address match"
                if distinct and (name_loc or same_name_elsewhere):
                    look = name_loc + same_name_elsewhere
                    basis = (f"operator identity resolution #{resolution.get('id')}: look-alike account(s) "
                             + ", ".join(a["account_id"] for a in look) + " are a different facility")
                    warnings.append("Identity decided by the operator, not by evidence the engine can verify: "
                                    + ", ".join(f"{a['account_id']} '{a['name']}' at {a.get('billing_street')}, "
                                                f"{a.get('billing_city')} {a.get('billing_state')}" for a in look)
                                    + " is left untouched. Note: " + (resolution.get("note") or "(none)"))
                res.update(classification="WEBSITE_ONLY", account_ids=[], basis=basis)
                proposals.append({
                    "kind": "WEBSITE_ONLY", "title": f"Create account: {w['name']}", "subject_key": f"web:{slug}",
                    "account_ids": [], "confidence": "medium", "risk": "high", "actionable": True,
                    "explanation": ("No CRM account matches this community's street+ZIP, and no same-city account has "
                                    "a similar name. Similar names in other cities were deliberately not used."),
                    "warnings": warnings,
                    "evidence": {"website": ev_web, "crm": None, "alternatives": alternatives,
                                 "basis": basis},
                    "current": {}, "proposed": fields,
                    "ops": [{"type": "create", "ref": "new", "fields": fields}], "baseline": {},
                })
            results.append(res)
            continue

        # ---------- matched; pick survivor if several ----------
        claimed |= {a["account_id"] for a in group}
        group = sorted(group, key=lambda a: _survivor_rank(w, a, bh), reverse=True)
        chosen = resolution.get("account_id") if resolution.get("decision") == "survivor" else None
        if chosen and chosen in {a["account_id"] for a in group}:
            group = sorted(group, key=lambda a: a["account_id"] != chosen)   # stable: chosen first
        else:
            chosen = None
        res.update(account_ids=[a["account_id"] for a in group], basis=basis,
                   crm=[_crm_view(a) for a in group], candidates=alternatives)

        if len(group) > 1 and not chosen and _decisive(w, group[0], bh) == _decisive(w, group[1], bh):
            reason = (f"{len(group)} CRM accounts sit at this address ({basis}) and none is distinguishable by "
                      "evidence (Bellhaven parent, billing history, website phone all tie). Choosing a survivor "
                      "would be a guess.")
            res.update(classification="HOLD", survivor=None)
            proposals.append(_hold(f"web:{slug}", f"HOLD — {len(group)} indistinguishable accounts: {w['name']}",
                                   [a["account_id"] for a in group], reason, ev_web, None,
                                   [_crm_view(a) for a in group] + alternatives, basis,
                                   warnings=[f"{a['account_id']} '{a['name']}' parent="
                                             f"{a.get('parent_name') or 'none'}" for a in group]))
            results.append(res)
            continue

        surv, losers = group[0], group[1:]
        res.update(survivor=surv["account_id"], duplicates=[a["account_id"] for a in losers])

        dup_holds = []
        for lo in losers:
            hist = has_billing_history(lo)
            cross_parent = lo.get("parent_id") != surv.get("parent_id")
            if hist is None or hist:
                rev, ar = financials(lo)
                reason = (f"Same-address account {lo['account_id']} '{lo['name']}' looks like a duplicate of "
                          f"{surv['account_id']} but carries billing history or unreadable financials "
                          f"(revenue={lo.get('lifetime_revenue')!r}, AR={lo.get('outstanding_ar')!r}). Inactivating "
                          "it could orphan revenue/AR; needs finance review (possibly CHOW).")
                dup_holds.append(lo["account_id"])
                proposals.append(_hold(f"dup:{lo['account_id']}", f"HOLD — duplicate with billing history: "
                                       f"{lo['name']}", [lo["account_id"], surv["account_id"]], reason, ev_web,
                                       _crm_view(lo), [_crm_view(surv)], basis))
                continue
            note = _append_note(lo.get("note"), f"{tag} Duplicate of {surv['account_id']} ({surv['name']}): same "
                                f"facility at {w.get('street')}, {w.get('city')} {w.get('zip')}.")
            fields = {"duplicate_of_account": surv["account_id"], "status": "Inactive", "note": note}
            d_s, d_l = _decisive(w, surv, bh), _decisive(w, lo, bh)
            won_on = [lbl for lbl, s, l in zip(("under Bellhaven parent", "has billing history",
                                                 "phone matches website"), d_s, d_l) if s and not l]
            warns = []
            if chosen:
                won_on = won_on or [f"operator identity resolution #{resolution.get('id')}"]
                warns.append(f"Survivor chosen by the operator (resolution #{resolution.get('id')}); the evidence "
                             f"alone did not separate these accounts. Note: {resolution.get('note') or '(none)'}")
            if cross_parent:
                warns.append(f"Losing account is under a different parent ({lo.get('parent_name') or 'none'}). With "
                             "$0 revenue/AR there is no billing history to preserve, but confirm it is not a "
                             "separate facility before inactivating.")
            proposals.append({
                "kind": "DUPLICATE",
                "title": f"Duplicate: {lo['name']} ({lo['account_id']}) → {surv['name']} ({surv['account_id']})",
                "subject_key": f"dup:{lo['account_id']}", "account_ids": [lo["account_id"], surv["account_id"]],
                "confidence": confidence, "risk": "high" if cross_parent else "medium", "actionable": True,
                "explanation": (f"{len(group)} CRM accounts resolve to website community '{w['name']}' by {basis}. "
                                f"Survivor {surv['account_id']} wins on: {', '.join(won_on)}. Losing account has "
                                "$0 revenue and $0 AR. Action: link duplicate_of_account, set Inactive, append note "
                                "(no merge API; nothing deleted)."),
                "warnings": warns,
                "evidence": {"website": ev_web, "crm": _crm_view(lo), "survivor": _crm_view(surv),
                             "alternatives": alternatives, "basis": basis,
                             "survivor_criteria": {"survivor": dict(zip(("bh_parent", "revenue", "phone"), d_s)),
                                                   "loser": dict(zip(("bh_parent", "revenue", "phone"), d_l))}},
                "current": {k: lo.get(k) for k in fields}, "proposed": fields,
                "ops": [{"type": "update", "account_id": lo["account_id"], "fields": fields}],
                "baseline": {lo["account_id"]: baseline(lo, tuple(fields)),
                             surv["account_id"]: baseline(surv)},
            })

        diffs = field_diffs(w, surv)
        wrong_parent = surv.get("parent_id") != bh
        common = {"evidence": {"website": ev_web, "crm": _crm_view(surv), "alternatives": alternatives,
                               "basis": basis, "duplicates": [a["account_id"] for a in losers]}}
        cls = []

        if wrong_parent:
            cur_parent = parent_names.get(surv.get("parent_id"), "none") if surv.get("parent_id") else "none"
            req, why = chow_required(surv)
            rename = N.name_core(surv.get("name")) != N.name_core(w["name"])
            if req is None:
                cls.append("HOLD")
                proposals.append(_hold(f"acct:{surv['account_id']}:parent", f"HOLD — financials unreadable: "
                                       f"{surv['name']}", [surv["account_id"]], why, ev_web, _crm_view(surv),
                                       alternatives, basis))
            elif req:
                cls.append("CHOW")
                new_fields = {**_website_fields(w), "parent_id": bh, "status": "Active",
                              "note": f"{tag} CHOW successor of {surv['account_id']} ({surv['name']}, formerly under "
                                      f"{cur_parent}). Source: {w.get('source_url')}."}
                proposals.append({
                    **common, "kind": "CHOW", "title": f"CHOW successor: {surv['name']} ({cur_parent} → Bellhaven)",
                    "subject_key": f"acct:{surv['account_id']}:parent", "account_ids": [surv["account_id"]],
                    "confidence": confidence, "risk": "high", "actionable": True,
                    "explanation": (f"Website lists this community under Bellhaven but the CRM account is under "
                                    f"{cur_parent}. {why} The original account keeps its parent, name and "
                                    "financials; only chow_current_account is set on it."),
                    "warnings": [why, "Two-step write: POST successor, then PATCH link. A failure after step 1 "
                                      "resumes at step 2 without creating a second successor."],
                    "current": {"parent": cur_parent, "chow_current_account": surv.get("chow_current_account")},
                    "proposed": {"new_account": new_fields, "old_account.chow_current_account": "<new account id>"},
                    "ops": [{"type": "create", "ref": "new", "fields": new_fields},
                            {"type": "update", "account_id": surv["account_id"],
                             "fields": {"chow_current_account": "$ref:new"}}],
                    "baseline": {surv["account_id"]: baseline(surv)},
                })
            else:
                cls.append("WRONG_PARENT")
                fields = {"parent_id": bh}
                warns = [why]
                if rename:
                    warns.append(f"CRM name '{surv['name']}' differs from website '{w['name']}' and the parent "
                                 "differs too: consistent with a rebrand/acquisition, but ownership is inferred from "
                                 "address only. Verify before approving.")
                proposals.append({
                    **common, "kind": "WRONG_PARENT",
                    "title": f"Re-parent: {surv['name']} ({cur_parent} → Bellhaven)",
                    "subject_key": f"acct:{surv['account_id']}:parent", "account_ids": [surv["account_id"]],
                    "confidence": "medium" if rename else confidence, "risk": "high", "actionable": True,
                    "explanation": (f"Website lists this community under Bellhaven; CRM parent is {cur_parent}. "
                                    f"Matched by {basis}. Only parent_id is changed; name/phone fixes are a "
                                    "separate proposal."),
                    "warnings": warns,
                    "current": {"parent_id": surv.get("parent_id"), "parent_name": cur_parent},
                    "proposed": fields,
                    "ops": [{"type": "update", "account_id": surv["account_id"], "fields": fields}],
                    "baseline": {surv["account_id"]: baseline(surv)},
                })

        # A CHOW predecessor is a preserved historical record: the successor carries the website values.
        if diffs and "CHOW" not in cls and surv["account_id"] not in dup_holds:
            alias = "name" in diffs and N.name_core(surv.get("name")) != N.name_core(w["name"])
            cls.append("ALIAS" if alias else "FIELD_UPDATE")
            risk = "medium" if ("name" in diffs or confidence != "high"
                                or {"billing_street", "billing_zip"} & set(diffs)) else "low"
            proposals.append({
                **common, "kind": "FIELD_UPDATE", "title": f"Update {', '.join(diffs)}: {surv['name']}",
                "subject_key": f"acct:{surv['account_id']}:fields", "account_ids": [surv["account_id"]],
                "confidence": confidence, "risk": risk, "actionable": True,
                "explanation": (f"Matched by {basis}. CRM values differ from the live website listing (website is "
                                "source of truth for name, address, phone, care type)."
                                + (" Name differs materially: treat as an alias/rename and confirm." if alias else "")),
                "warnings": [],
                "current": {k: surv.get(k) for k in diffs}, "proposed": diffs,
                "ops": [{"type": "update", "account_id": surv["account_id"], "fields": diffs}],
                "baseline": {surv["account_id"]: baseline(surv, tuple(diffs))},
            })
        if not cls:
            cls.append("MATCH_OK")
        if losers:
            cls.append("DUPLICATE")
        res["classification"] = " + ".join(cls)
        results.append(res)

    # ---------- CRM accounts under Bellhaven that the website does not list ----------
    if scrape_complete:
        for a in pool:
            if a.get("parent_id") != bh or a["account_id"] in claimed:
                continue
            others = [o for o in pool if o["account_id"] != a["account_id"] and o.get("parent_id")
                      and o.get("parent_id") != bh and _addr_tier(
                          {"street": a.get("billing_street"), "zip": a.get("billing_zip")}, o)]
            res = {"facility": None, "account_ids": [a["account_id"]], "crm_name": a["name"],
                   "crm": [_crm_view(a)], "candidates": [_crm_view(o) for o in others]}
            req, why = chow_required(a)
            if len(others) == 1 and req:
                o = others[0]
                res["classification"] = "CRM_ONLY + CHOW"
                res["basis"] = "same address under a different parent"
                proposals.append({
                    "kind": "CHOW", "title": f"CHOW link: {a['name']} → {o['name']} ({o.get('parent_name')})",
                    "subject_key": f"acct:{a['account_id']}:chow", "account_ids": [a["account_id"], o["account_id"]],
                    "confidence": "medium", "risk": "high", "actionable": True,
                    "explanation": (f"'{a['name']}' is under Bellhaven in the CRM but is not on the Bellhaven website. "
                                    f"Account {o['account_id']} '{o['name']}' sits at the same address under "
                                    f"{o.get('parent_name')}, indicating the facility changed ownership away from "
                                    f"Bellhaven. {why} A current-owner account already exists, so no new account is "
                                    "created; the old account is linked to it via chow_current_account."),
                    "warnings": [why, "Ownership change inferred from website absence + same-address account. "
                                      "Confirm with the account owner before approving."],
                    "evidence": {"website": None, "crm": _crm_view(a), "current_owner_account": _crm_view(o),
                                 "alternatives": [], "basis": "same address under a different parent"},
                    "current": {"chow_current_account": a.get("chow_current_account")},
                    "proposed": {"chow_current_account": o["account_id"]},
                    "ops": [{"type": "update", "account_id": a["account_id"],
                             "fields": {"chow_current_account": o["account_id"]}}],
                    "baseline": {a["account_id"]: baseline(a), o["account_id"]: baseline(o)},
                })
            elif a.get("status") != "Needs Review":
                res["classification"] = "CRM_ONLY"
                res["basis"] = "no website match"
                extra = (f" Same-address account under another parent: {', '.join(o['account_id'] for o in others)}."
                         if others else "")
                note = _append_note(a.get("note"), f"{tag} Not listed on the Bellhaven website (all directory "
                                    f"pages + homepage checked); ownership needs verification.{extra}")
                fields = {"status": "Needs Review", "note": note}
                proposals.append({
                    "kind": "CRM_ONLY", "title": f"Flag for review: {a['name']} not on website",
                    "subject_key": f"acct:{a['account_id']}:crm_only", "account_ids": [a["account_id"]],
                    "confidence": "medium", "risk": "medium", "actionable": True,
                    "explanation": ("Account is under the Bellhaven parent but no website community matches it by "
                                    "address or by name+city. Not deactivated or re-parented: the new owner is "
                                    "unknown. Proposed: status Needs Review with an explanatory note."),
                    "warnings": [why] if (financials(a)[0] or 0) > 0 else [],
                    "evidence": {"website": None, "crm": _crm_view(a), "alternatives": [_crm_view(o) for o in others],
                                 "basis": "no website match"},
                    "current": {k: a.get(k) for k in fields}, "proposed": fields,
                    "ops": [{"type": "update", "account_id": a["account_id"], "fields": fields}],
                    "baseline": {a["account_id"]: baseline(a, ("note",))},
                })
            else:
                res["classification"] = "CRM_ONLY (already Needs Review)"
            results.append(res)

    return results, proposals
