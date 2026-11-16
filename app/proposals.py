"""Bellhaven Build / Modify: one guarded Findlay correction, no background writes.

All writes require a deliberate POST with a one-time session token and exact
confirmation phrase. Earlier decisions in the review dashboard never authorize
execution here. Live state is re-read immediately before PATCH.
"""
import html
import json
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app import config
from app.crm import CRMClient
from app.normalize import norm_name, norm_street, norm_zip

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / 'data' / 'snapshot.json'
LEDGER = ROOT / 'data' / 'execution_audit.db'
PARENT_NAME = 'Bellhaven Senior Living (Parent Account)'
FACILITY_NAME = 'Bellhaven Meadows of Findlay'
CONFIRMATION = 'APPLY FINDLAY PARENT CHANGE'
CSRF = secrets.token_urlsafe(32)
router = APIRouter()


def esc(v):
    return html.escape(str(v if v is not None else ''), quote=True)


def unwrap(obj):
    if isinstance(obj, dict) and isinstance(obj.get('data'), dict):
        return obj['data']
    return obj


def audit(event, message, account_id=''):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(LEDGER)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS events ('
                   'at TEXT, event TEXT, account_id TEXT, message TEXT)')
        db.execute('INSERT INTO events VALUES (?, ?, ?, ?)', (
            datetime.now(timezone.utc).isoformat(), event, account_id,
            str(message)[:500]))


def history():
    if not LEDGER.exists():
        return []
    with sqlite3.connect(str(LEDGER)) as db:
        return db.execute('SELECT at, event, account_id, message FROM events '
                          'ORDER BY rowid DESC LIMIT 12').fetchall()


def load_case():
    data = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    matches = [f for f in data['facilities'] if norm_name(f.get('name')) == norm_name(FACILITY_NAME)]
    accounts = [a for a in data['accounts'] if norm_name(a.get('name')) == norm_name(FACILITY_NAME)]
    parents = [a for a in data['accounts'] if a.get('name') == PARENT_NAME]
    if len(matches) != 1 or len(accounts) != 1 or len(parents) != 1:
        raise ValueError('Cannot uniquely identify Findlay facility/account/parent in snapshot')
    return matches[0], accounts[0], parents[0]


def address_equal(f, a):
    return all([
        norm_street(f.get('street')) and norm_street(f.get('street')) == norm_street(a.get('billing_street')),
        norm_zip(f.get('zip')) and norm_zip(f.get('zip')) == norm_zip(a.get('billing_zip')),
        str(f.get('city', '')).strip().casefold() == str(a.get('billing_city', '')).strip().casefold(),
        str(f.get('state', '')).strip().upper() == str(a.get('billing_state', '')).strip().upper(),
    ])


def number(value):
    if value is None or value == '':
        raise ValueError('Missing financial field; cannot proceed')
    return float(value)


def validate(f, snap, parent, current, live_parent):
    """Pure, conservative authorization guard for one known account."""
    reasons = []
    if not isinstance(current, dict) or not isinstance(live_parent, dict):
        return ['CRM detail response is not a supported account object']
    if current.get('account_id') != snap.get('account_id'):
        reasons.append('Live account ID differs from snapshot')
    if live_parent.get('account_id') != parent.get('account_id') or live_parent.get('name') != PARENT_NAME:
        reasons.append('Target parent identity cannot be verified')
    if norm_name(current.get('name')) != norm_name(f.get('name')):
        reasons.append('Live account name does not match the website')
    if not address_equal(f, current):
        reasons.append('Live street, city, state or ZIP does not match website')
    if not address_equal(f, snap):
        reasons.append('Snapshot address does not match website')
    if current.get('status') != 'Active':
        reasons.append('Account is not Active')
    if current.get('chow_current_account') or current.get('duplicate_of_account'):
        reasons.append('Existing CHOW or duplicate pointer requires manual review')
    if str(current.get('updated_at') or '') != str(snap.get('updated_at') or ''):
        reasons.append('Account changed since snapshot; refresh/review before proceeding')
    try:
        revenue = number(current.get('lifetime_revenue'))
        ar = number(current.get('outstanding_ar'))
        if revenue < 0 or ar < 0:
            reasons.append('Unexpected negative financial values')
        if revenue != number(snap.get('lifetime_revenue')) or ar != number(snap.get('outstanding_ar')):
            reasons.append('Financial values changed since snapshot')
        if revenue > 0 and ar > 0:
            reasons.append('CHOW required: both revenue history and outstanding AR are positive')
        if ar != 0:
            reasons.append('Outstanding AR is not zero; hold for manual review')
    except (ValueError, TypeError):
        reasons.append('Financial data is missing or invalid')
    if current.get('parent_id') not in (None, ''):
        if current.get('parent_id') == parent['account_id']:
            reasons.append('Already assigned to correct parent; nothing to change')
        else:
            reasons.append('Unexpected existing parent; only unassigned Findlay allowed')
    return reasons


def live_state():
    f, snap, parent = load_case()
    with_client = CRMClient()
    account = unwrap(with_client.get_account(snap['account_id']))
    live_parent = unwrap(with_client.get_account(parent['account_id']))
    return f, snap, parent, account, validate(f, snap, parent, account, live_parent)


def page(message='', success=False):
    try:
        f, snap, parent, current, problems = live_state()
        account_id = snap['account_id']
        old_parent = current.get('parent_name') or '(none)'
        desired = parent['name']
        details = ('<div class="panel"><h3>Findlay — before and after</h3>'
                   '<table><tr><th>Field</th><th>Live CRM</th><th>Proposed</th></tr>'
                   '<tr><td>Account</td><td colspan="2">{}</td></tr>'
                   '<tr><td>Account ID</td><td colspan="2">{}</td></tr>'
                   '<tr><td>Parent</td><td>{}</td><td>{}</td></tr>'
                   '<tr><td>Revenue</td><td colspan="2">{}</td></tr>'
                   '<tr><td>Outstanding AR</td><td colspan="2">{}</td></tr>'
                   '<tr><td>Address</td><td colspan="2">{}, {}, {} {}</td></tr>'
                   '</table><p>Proposed API PATCH: <code>{{"parent_id":"{}"}}</code></p></div>').format(
                       esc(current.get('name')), esc(account_id), esc(old_parent), esc(desired),
                       esc(current.get('lifetime_revenue')), esc(current.get('outstanding_ar')),
                       esc(current.get('billing_street')), esc(current.get('billing_city')),
                       esc(current.get('billing_state')), esc(current.get('billing_zip')),
                       esc(parent['account_id']))
        warnings = ('<ul>' + ''.join('<li>{}</li>'.format(esc(r)) for r in problems) + '</ul>') if problems else '<p>Current live safety checks passed. This is not an approval.</p>'
        if problems:
            action = '<p><strong>BLOCKED:</strong> No execution available until the problems are resolved.</p>'
        else:
            action = ('<div class="panel"><h3>Separate approval required</h3>'
                      '<p>The earlier nine-card APPROVE decision is not authorization for this change. '
                      'This action will modify one assessment CRM record.</p>'
                      '<form method="post" action="/proposals/findlay/apply">'
                      '<input type="hidden" name="csrf" value="{}">'
                      '<label>Type exactly <code>{}</code></label>'
                      '<input name="confirmation" autocomplete="off" required>'
                      '<label><input type="checkbox" name="approved" value="yes" required> '
                      'I reviewed the before/after record and authorize this exact CRM update.</label>'
                      '<button type="submit">Apply verified Findlay parent change</button>'
                      '</form></div>').format(esc(CSRF), CONFIRMATION)
    except Exception as exc:
        details = ''
        warnings = '<p>Unable to load live verification: {}. No update is possible.</p>'.format(esc(str(exc)[:240]))
        action = ''
    lines = ''.join('<li><code>{}</code> — {} — {}</li>'.format(esc(at), esc(event), esc(message))
                    for at, event, _id, message in history())
    alert = ('<div class="message {}">{}</div>'.format('success' if success else 'failure', esc(message))) if message else ''
    return HTMLResponse('''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{{background:#101827;color:#eef4ff;font:16px Arial;margin:0;padding:28px}}
main{{max-width:1000px;margin:auto}}.panel{{background:#202d40;border:1px solid #435a79;border-radius:13px;padding:22px;margin:18px 0}}
p,li{{color:#cad5e7;line-height:1.5}}a{{color:#a3cfff}}table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #44546a;text-align:left;padding:12px}}code{{word-break:break-all}}input[name=confirmation]{{display:block;width:min(100%,480px);padding:11px;margin:12px 0;background:#fff;color:#111;border-radius:6px}}button{{padding:12px 17px;background:#d4e6ff;color:#111;border:0;border-radius:8px;font-weight:bold;cursor:pointer}}.message{{padding:15px;border-radius:9px}}.failure{{background:#52332c}}.success{{background:#275447}}</style></head>
<body><main><p><a href="/investigate">Find Problems</a> · <a href="/records">Data Review</a> · <a href="/">Review Dashboard</a></p>
<h1>Build / Modify — guarded correction</h1><p>Live CRM evidence, read-back validation, and explicit approval. No background writes.</p>
{}{}<div class="panel"><h3>Safety check</h3>{}</div>{}<div class="panel"><h3>Local execution audit</h3><ul>{}</ul></div>
<p>Other 15 flagged cases remain investigation-only. Marietta and Tiffin require the CHOW successor-account workflow and cannot use this direct-parent update.</p>
</main></body></html>'''.format(alert, details, warnings, action, lines or '<li>No executions or attempted changes recorded</li>'))


@router.get('/proposals', response_class=HTMLResponse)
def proposals():
    return page()


@router.post('/proposals/findlay/apply', response_class=HTMLResponse)
def execute(request: Request, csrf: str = Form(''), confirmation: str = Form(''), approved: str = Form('')):
    # Browser cross-origin forms cannot know this server's in-memory token.
    if request.client is None or request.client.host not in ('127.0.0.1', '::1'):
        return HTMLResponse('Local access only', status_code=403)
    # Same process-level gate as the main executor. Findlay is already applied and verified (legacy receipt);
    # in dry-run this route refuses before reading or writing anything, including the legacy audit file.
    if not config.WRITES_ENABLED:
        return HTMLResponse('Live CRM writes are disabled (dry-run). Findlay is already applied and verified; '
                            'no retry is needed.', status_code=403)
    origin = request.headers.get('origin', '')
    if origin and (urlparse(origin).hostname not in ('127.0.0.1', 'localhost')):
        return HTMLResponse('Invalid origin', status_code=403)
    if not secrets.compare_digest(csrf, CSRF) or confirmation != CONFIRMATION or approved != 'yes':
        audit('DENIED', 'Missing or incorrect explicit confirmation')
        return page('No CRM change: confirmation failed.')
    try:
        f, snap, parent, current, problems = live_state()
        if problems:
            audit('BLOCKED', '; '.join(problems), snap['account_id'])
            return page('No CRM change: ' + '; '.join(problems))
        account_id = snap['account_id']
        # One narrowly scoped field, on one exact account, after fresh verification.
        audit('STARTED', 'PATCH parent_id to Bellhaven parent', account_id)
        crm = CRMClient()
        crm.update_account(account_id, {'parent_id': parent['account_id']})
        after = unwrap(crm.get_account(account_id))
        if after.get('account_id') != account_id or after.get('parent_id') != parent['account_id']:
            audit('UNVERIFIED', 'PATCH returned but read-back did not match; inspect CRM', account_id)
            return page('PATCH may have occurred but read-back mismatch: inspect CRM manually before retry.')
        audit('VERIFIED', 'Read-back parent_id matches target; financial fields were not sent', account_id)
        return page('SUCCESS: Findlay parent changed and CRM read-back verified.', True)
    except Exception as exc:
        audit('ERROR', type(exc).__name__ + ': ' + str(exc)[:200])
        return page('Execution halted or response uncertain. Check audit and CRM before retrying: ' + type(exc).__name__)
