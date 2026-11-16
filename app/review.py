import html
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

# Legacy nine-card console. Mounted at /legacy/cards in app.main. Its decisions are LOCAL DEMO NOTES ONLY:
# they are never imported into the ledger and never authorize a CRM write.
router = APIRouter()

DB = Path(__file__).resolve().parent.parent / "data" / "review.db"
DB.parent.mkdir(parents=True, exist_ok=True)

CASES = [
    ("marietta", "Bellhaven of Marietta", "CHOW",
     "Revenue $51,250 | AR $3,800 | Preserve historical account"),
    ("tiffin", "Bellhaven of Tiffin", "CHOW",
     "Revenue $84,000 | AR $12,400 | Preserve historical account"),
    ("owosso", "Bellhaven of Owosso", "DUPLICATE",
     "Two active CRM records at the same address"),
    ("kettering", "Bellhaven of Kettering", "INVESTIGATE",
     "Three accounts share an address; identity not resolved"),
    ("zanesville", "Bellhaven of Zanesville", "PARENT",
     "Matching street and ZIP; parent correction candidate"),
    ("union-square", "Bellhaven at Union Square", "HOLD",
     "ZIP matches CRM candidate, but street differs"),
    ("findlay", "Bellhaven Meadows of Findlay", "PARENT",
     "Unassigned parent | Revenue $22,000 | AR $0"),
    ("lima", "Bellhaven Crossings of Lima", "PARENT",
     "Wrong parent | Revenue $47,000 | AR $0"),
    ("amberly", "Amberly Manor", "PARENT",
     "Wrong parent | Revenue $0 | AR $0"),
]

def connect():
    db = sqlite3.connect(str(DB))
    db.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            case_id TEXT PRIMARY KEY,
            decision TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    db.commit()
    return db

def escape(value):
    return html.escape(str(value), quote=True)

@router.get("/legacy/cards", response_class=HTMLResponse)
def dashboard():
    with connect() as db:
        decisions = dict(
            db.execute("SELECT case_id, decision FROM decisions").fetchall()
        )
        history = db.execute(
            "SELECT case_id, decision, created_at "
            "FROM events ORDER BY event_id DESC LIMIT 10"
        ).fetchall()

    cards = []
    for case_id, name, kind, detail in CASES:
        decision = decisions.get(case_id, "PENDING")
        buttons = "".join(
            '<form method="post" action="/legacy/cards/decision/{}/{}">'
            '<button class="{}">{}</button></form>'.format(
                escape(case_id), action, css, label
            )
            for action, css, label in (
                ("approve", "approve", "Approve proposal"),
                ("reject", "reject", "Reject"),
                ("hold", "hold", "Hold"),
            )
        )

        cards.append(
            '<article><div class="top"><h3>{}</h3><span>{}</span></div>'
            '<p>{}</p><p class="status">Decision: {}</p>'
            '<div class="buttons">{}</div></article>'.format(
                escape(name), escape(kind), escape(detail),
                escape(decision), buttons
            )
        )

    history_html = "".join(
        "<li>{} — {} — {}</li>".format(
            escape(case_id), escape(decision), escape(created_at)
        )
        for case_id, decision, created_at in history
    ) or "<li>No decisions recorded yet.</li>"

    return """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bellhaven Reconciliation Console</title>
<style>
body{background:#10141d;color:#e9eef7;font-family:Arial,sans-serif;
     margin:0;padding:35px;max-width:1100px;margin:auto}
h1{font-size:30px;margin-bottom:8px}
.subtitle{color:#a3b3c8;margin-bottom:28px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(295px,1fr));gap:15px}
article{background:#1a2230;border:1px solid #354157;border-radius:12px;padding:20px}
.top{display:flex;justify-content:space-between;gap:12px;align-items:center}
h3{margin:0;font-size:18px}
.top span{font-size:12px;color:#8cb8ff}
article p{color:#b8c6d8;line-height:1.5}
.status{font-weight:bold;color:#f4d58d}
.buttons{display:flex;gap:6px;flex-wrap:wrap}
button{border:0;border-radius:6px;padding:9px;cursor:pointer;font-weight:bold}
.approve{background:#56c69d;color:#10251d}
.reject{background:#ed9393;color:#2b0c0c}
.hold{background:#e9cb83;color:#332709}
section{margin-top:35px}
li{margin:9px 0;color:#becbde}
.notice{border-left:3px solid #8cb8ff;padding:12px;background:#1a2230;
        margin-bottom:25px}
</style>
</head>
<body>
<h1>Bellhaven Reconciliation Console</h1>
<p class="subtitle">Clipboard Health | CRM investigation and human review</p>
<div class="notice">
<strong>Review mode:</strong> Decisions are stored locally in SQLite.
Approving a proposal does NOT modify the CRM. Legacy demo decisions — not execution approvals. The live queue is at <a style="color:#8cb8ff" href="/review">Build / Modify</a>.
</div>
<div class="grid">""" + "".join(cards) + """</div>
<section><h2>Decision audit trail</h2><ul>""" + history_html + """</ul></section>
</body>
</html>"""

@router.post("/legacy/cards/decision/{case_id}/{decision}")
def record_decision(case_id: str, decision: str):
    valid_ids = {item[0] for item in CASES}
    if case_id not in valid_ids or decision not in (
        "approve", "reject", "hold"
    ):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid decision")

    now = datetime.now(timezone.utc).isoformat()
    with connect() as db:
        db.execute(
            "INSERT OR REPLACE INTO decisions VALUES (?, ?, ?)",
            (case_id, decision.upper(), now)
        )
        db.execute(
            "INSERT INTO events (case_id, decision, created_at) "
            "VALUES (?, ?, ?)",
            (case_id, decision.upper(), now)
        )
        db.commit()

    return RedirectResponse("/legacy/cards", status_code=303)


# Standalone legacy app (uvicorn app.review:app) still works; prefer `./bh serve` (app.main).
app = FastAPI(title="Bellhaven Reconciliation Console (legacy)")
app.include_router(router)


@app.get("/")
def _root():
    return RedirectResponse("/legacy/cards")


from app.investigate import router as investigation_router
app.include_router(investigation_router)

from app.workspace import install as install_workspace
install_workspace(app)

from app.records import router as records_router
app.include_router(records_router)

from app.proposals import router as proposals_router
app.include_router(proposals_router)
