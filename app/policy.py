"""Risk & Validation Engine: deterministic financial / safety rules. No probabilistic judgment here.

CHOW SOP: if an account must move to a different parent AND it has revenue
history (lifetime_revenue > 0) AND outstanding_ar > 0, the existing account must
not be re-parented. Instead: leave it exactly as it is, create a new account
under the correct parent, and set chow_current_account on the OLD account to the
new account's id. Otherwise re-parent directly (still only after human approval).

Missing or malformed financial values are NEVER treated as zero.

Every rule here is re-applied by the executor against a FRESH read of the CRM
immediately before any write (see check_ops / successor_conflicts).
"""
from __future__ import annotations

from typing import Any, Optional

from . import normalize as N

# Values that must not have moved between proposal time and write time.
GUARD_FIELDS = ("parent_id", "lifetime_revenue", "outstanding_ar", "status",
                "chow_current_account", "duplicate_of_account")
# Identity fields: if these change the record may no longer be the facility we matched.
IDENTITY_FIELDS = ("name", "billing_street", "billing_city", "billing_state", "billing_zip")

RISK_ORDER = ["low", "medium", "high", "hold"]


def parse_money(v: Any) -> Optional[float]:
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str) and v.strip():
        try:
            return float(v.replace(",", "").replace("$", ""))
        except ValueError:
            return None
    return None


def financials(acct: dict) -> tuple:
    return parse_money(acct.get("lifetime_revenue")), parse_money(acct.get("outstanding_ar"))


def has_billing_history(acct: dict) -> Optional[bool]:
    """True if revenue or AR is non-zero, None if unknown (treated as blocking by callers)."""
    rev, ar = financials(acct)
    if rev is None or ar is None:
        return None
    return rev != 0 or ar != 0


def chow_required(acct: dict) -> tuple:
    """True -> CHOW required, False -> direct re-parent allowed, None -> uncertain (block)."""
    rev, ar = financials(acct)
    if rev is None or ar is None:
        return None, (f"Financial values missing/malformed (lifetime_revenue={acct.get('lifetime_revenue')!r}, "
                      f"outstanding_ar={acct.get('outstanding_ar')!r}); parent change blocked pending review.")
    if rev < 0 or ar < 0:
        return None, f"Negative financial values (revenue={rev}, AR={ar}); blocked pending finance review."
    if rev > 0 and ar > 0:
        return True, (f"Protected billing account: lifetime_revenue=${rev:,.0f} AND outstanding_ar=${ar:,.0f} > 0. "
                      "Per SOP the existing account is NOT re-parented; a new account is created under the correct "
                      "parent and linked via chow_current_account.")
    why = "no revenue history" if rev <= 0 else "outstanding AR is $0"
    return False, (f"Direct re-parent allowed by SOP: {why} (lifetime_revenue=${rev:,.0f}, "
                   f"outstanding_ar=${ar:,.0f}). Still requires explicit human approval.")


def check_ops(ops: list, fresh: dict) -> list:
    """Re-validate approved operations against freshly-read CRM state. Returns violations."""
    problems = []
    for op in ops:
        if op["type"] != "update":
            continue
        acct = fresh.get(op["account_id"])
        if acct is None:
            problems.append(f"Account {op['account_id']} could not be re-read")
            continue
        f = op["fields"]
        if "parent_id" in f and f["parent_id"] != acct.get("parent_id"):
            req, why = chow_required(acct)
            if req is None:
                problems.append(why)
            elif req:
                problems.append(f"SOP violation: would re-parent protected account {op['account_id']}. {why}")
        if f.get("status") == "Inactive":
            if acct.get("chow_current_account"):
                problems.append(f"Account {op['account_id']} has a CHOW link; refusing to inactivate without review")
            hist = has_billing_history(acct)
            if hist is None:
                problems.append(f"Account {op['account_id']} financials missing/malformed; refusing to inactivate")
            elif hist:
                problems.append(f"Account {op['account_id']} carries billing history; inactivating it would orphan "
                                "revenue/AR — requires finance review, not a duplicate cleanup")
        if "duplicate_of_account" in f and f["duplicate_of_account"]:
            surv = fresh.get(f["duplicate_of_account"])
            if surv is None:
                problems.append(f"Survivor {f['duplicate_of_account']} could not be re-read")
            elif surv.get("status") != "Active" or surv.get("duplicate_of_account"):
                problems.append(f"Survivor {f['duplicate_of_account']} is no longer an active, non-duplicate account")
        if "chow_current_account" in f and acct.get("chow_current_account") not in (None, "", f["chow_current_account"]):
            problems.append(f"Account {op['account_id']} already has chow_current_account="
                            f"{acct.get('chow_current_account')!r}; refusing to overwrite")
    return problems


def successor_conflicts(create_fields: dict, candidates: list, exclude: set) -> list:
    """Before a CHOW/new-account POST: any existing account already at this address under the target parent
    means a successor (or the facility) may already exist -> block rather than create a duplicate."""
    out = []
    want = N.address_key(create_fields.get("billing_street"), create_fields.get("billing_zip"))
    for a in candidates:
        if a.get("account_id") in exclude:
            continue
        if a.get("parent_id") != create_fields.get("parent_id"):
            continue
        if N.address_key(a.get("billing_street"), a.get("billing_zip")) == want:
            out.append(f"Account {a['account_id']} '{a.get('name')}' already exists at this address under the target "
                       "parent; possible existing successor — refusing to create another")
    return out


def baseline(acct: dict, extra_fields: tuple = ()) -> dict:
    keys = GUARD_FIELDS + IDENTITY_FIELDS + tuple(k for k in extra_fields if k not in GUARD_FIELDS + IDENTITY_FIELDS)
    return {k: acct.get(k) for k in keys}
