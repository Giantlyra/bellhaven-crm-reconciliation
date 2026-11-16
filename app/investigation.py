"""Investigation categories for the cases left open after reconciliation.

DISPLAY ONLY. These labels explain *why* a case is not finished and what the business team must
confirm. They are not statuses and not permissions: nothing in the executor, the batch, or the queue
reads them, and they never change a proposal's status. Status always comes live from the ledger.

Keyed by proposal id in this assessment's ledger, and shown only while the proposal is still open
(not verified, rejected, superseded or resolved).
"""
from __future__ import annotations

CATEGORIES = {
    "CHOW_REBRAND": ("Possible change of ownership / rebrand",
                     "Same building as a Bellhaven community, but a different business name. It may be a former name, "
                     "a former operator, or a separate account. No ownership transition is treated as confirmed."),
    "ADDRESS": ("Address verification",
                "The CRM and the website give different kinds of address (mailing vs physical)."),
    "IDENTITY": ("Identity verification",
                 "The records can't be tied to one facility with enough confidence."),
    "NEW_ACCOUNT": ("New account confirmation",
                    "No CRM account exists for this community; creating one needs business confirmation."),
}

CASES = {
    41: dict(category="CHOW_REBRAND", place="Monroe, MI",
             known="Bellhaven Gardens of Monroe already has a correct Bellhaven account at 750 Stewart Rd. A second record, "
                   "'Cedar Trail of Monroe', sits at the same address under the Cedar Trail parent, with no revenue, no AR and no contacts.",
             uncertain="Whether that Cedar Trail record is the building's former operator (Cedar Trail was acquired in 2026), "
                       "a data-entry error, or a separate facility. A third, Harborview-era record at the same address was kept as history.",
             confirm="Did 750 Stewart Rd ever operate under Cedar Trail?",
             next="Keep held. If confirmed as the former operator, preserve it as history; inactivate only if it is a true duplicate."),
    49: dict(category="CHOW_REBRAND", place="Chagrin Falls, OH",
             known="'Riverbend Manor Care Center' is at the exact website address, is already under Bellhaven, and its contact "
                   "(Dale Mabry, Administrator) matches the website administrator. No billing history.",
             uncertain="Whether Riverbend Manor is a former name of the same facility or a former operator.",
             confirm="Is 'Riverbend Manor' a former name of Bellhaven of Chagrin Falls?",
             next="Keep held. If it is a former name, release with that note; the rename and phone update are ready."),
    66: dict(category="CHOW_REBRAND", place="Portage, MI",
             known="'Sunny Acres Retirement Home' is at the exact website address, already under Bellhaven, Memory Care, "
                   "and the only account in the ZIP. No billing history.",
             uncertain="No contact or other record corroborates that it is the same facility; the name is completely different.",
             confirm="Is Sunny Acres the same facility under a former name?",
             next="Keep held. If confirmed, release with that note; the rename and phone update are ready."),
    46: dict(category="ADDRESS", place="Ashtabula, OH",
             known="Bellhaven of Ashtabula already has an account (name, phone, ZIP and administrator all match). Its billing "
                   "address is PO Box 517; the website gives the physical street, 3156 W Prospect Rd.",
             uncertain="Whether the PO Box is the invoice mailing address that must stay in the billing field.",
             confirm="Should PO Box 517 remain the billing address?",
             next="Preserve the existing account and both addresses. Don't replace the PO Box or create another account "
                  "until finance confirms."),
    38: dict(category="IDENTITY", place="New Albany, OH",
             known="The website lists Bellhaven at Union Square, 118 Union Square Dr. The only CRM account in that ZIP is "
                   "'Union Square Senior Living', 240 Market St, under Juniper Point, with a different phone and administrator.",
             uncertain="Whether these are two different communities or one campus recorded twice.",
             confirm="Is 240 Market St a separate community from 118 Union Square Dr?",
             next="Keep held (evidence leans 'separate'). If separate, the next scan proposes a new Bellhaven account."),
    53: dict(category="IDENTITY", place="Kettering, OH",
             known="Three CRM accounts share the website address (3313 Wilmington Pike). None is under Bellhaven, none has "
                   "the website phone, and none has billing history or contacts.",
             uncertain="Which record, if any, is the live facility. Picking one would be a guess.",
             confirm="Which account is current, or should a new Bellhaven account be designated and the rest kept as history?",
             next="Keep held. Choose a survivor only once the business names it."),
    71: dict(category="NEW_ACCOUNT", place="Hudson, OH",
             known="The website lists Amberly Manor, 4390 Darrow Rd, Hudson OH. No CRM account exists in Hudson. The only CRM "
                   "'Amberly Manor' is in Colorado Springs under another operator, and every attribute except the name differs.",
             uncertain="Only that the community is genuinely new to the CRM rather than recorded under another name. "
                       "This is not an ownership change.",
             confirm="Confirm Amberly Manor (Hudson OH) is a Bellhaven community that should get its own account.",
             next="Creation is prepared ($0 revenue / $0 AR, Bellhaven parent) and needs a typed confirmation on a "
                  "writes-enabled server. Nothing is created until then."),
}

CLOSED = {"verified", "rejected", "superseded", "resolved"}


def for_proposal(p: dict):
    """Return the display card for an open proposal, or None. Pure: never touches the ledger."""
    case = CASES.get(p.get("id"))
    if not case or p.get("status") in CLOSED:
        return None
    label, why = CATEGORIES[case["category"]]
    return dict(case, label=label, why=why, status=p.get("status"))


def summary(proposals: list) -> list:
    """Group the open categorised proposals for the Start Here page: [(label, why, [cards])]."""
    groups = {}
    for p in proposals:
        c = for_proposal(p)
        if c:
            groups.setdefault(c["category"], []).append(dict(c, id=p["id"]))
    return [(CATEGORIES[k][0], CATEGORIES[k][1], sorted(v, key=lambda c: c["id"]))
            for k, v in sorted(groups.items(), key=lambda kv: list(CATEGORIES).index(kv[0]))]
