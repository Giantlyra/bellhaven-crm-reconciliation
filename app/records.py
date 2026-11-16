import json
from pathlib import Path
from collections import defaultdict
from html import escape

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.normalize import norm_name

router = APIRouter()
SNAPSHOT = Path(__file__).resolve().parent.parent / "data" / "snapshot.json"

@router.get("/records", response_class=HTMLResponse)
def records():
    data = json.loads(SNAPSHOT.read_text())
    accounts = data["accounts"]
    facilities = data["facilities"]

    by_name = defaultdict(list)
    for account in accounts:
        by_name[norm_name(account.get("name"))].append(account)

    rows = []
    for facility in facilities:
        matches = by_name[norm_name(facility["name"])]

        if not matches:
            status = "INVESTIGATE: No exact name match"
        elif len(matches) > 1:
            status = "INVESTIGATE: Multiple CRM matches"
        elif matches[0].get("parent_name") != "Bellhaven Senior Living (Parent Account)":
            status = "INVESTIGATE: Parent mismatch"
        else:
            status = "MATCHED"

        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                escape(facility["name"]),
                escape(", ".join(a["name"] for a in matches) or "No exact match"),
                escape(status)
            )
        )

    return HTMLResponse("""
    <html><head><style>
    body {{background:#101827;color:white;font-family:Arial;padding:30px}}
    table {{width:100%;border-collapse:collapse}}
    th,td {{border-bottom:1px solid #40516a;padding:12px;text-align:left}}
    th {{background:#30415b}}
    a {{color:#8cc8ff}}
    </style></head><body>
    <h1>Legacy exact-name review (pre-Findlay snapshot)</h1><p>Superseded by the address-aware <a href="/data">Data Review</a>.</p>
    <p>CRM accounts: {} | Website facilities: {}</p>
    <table>
    <tr><th>Website Facility</th><th>CRM Match</th><th>Status</th></tr>
    {}
    </table></body></html>
    """.format(len(accounts), len(facilities), "".join(rows)))
