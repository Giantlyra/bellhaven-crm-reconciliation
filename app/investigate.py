"""Read-only Bellhaven investigation, sourced from the local CRM/website snapshot."""
import json
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.normalize import norm_name, norm_street, norm_zip

router = APIRouter()
SNAPSHOT = Path(__file__).resolve().parent.parent / 'data' / 'snapshot.json'
PARENT_NAME = 'Bellhaven Senior Living (Parent Account)'


def h(value):
    return escape(str(value if value is not None else ''), quote=True)


def safe_url(url):
    p = urlparse(str(url or ''))
    return url if p.scheme == 'https' and p.hostname == 'analyst-assessment-production.up.railway.app' else ''


def as_number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return None


def rank_candidate(facility, account):
    name = SequenceMatcher(None, norm_name(facility.get('name')),
                           norm_name(account.get('name'))).ratio()
    zip_ok = bool(facility.get('zip') and account.get('billing_zip') and
                  norm_zip(facility.get('zip')) == norm_zip(account.get('billing_zip')))
    street_ok = bool(facility.get('street') and account.get('billing_street') and
                     norm_street(facility.get('street')) == norm_street(account.get('billing_street')))
    city_ok = str(facility.get('city') or '').strip().lower() == str(account.get('billing_city') or '').strip().lower()
    state_ok = str(facility.get('state') or '').strip().lower() == str(account.get('billing_state') or '').strip().lower()
    score = 3 * int(street_ok and zip_ok) + 2 * int(zip_ok) + .8 * int(city_ok and state_ok) + name
    if street_ok and zip_ok:
        evidence = 'Same normalized street + ZIP'
    elif zip_ok:
        evidence = 'Same ZIP; street must be verified'
    else:
        evidence = 'Name similarity only — not identity evidence'
    return score, evidence, street_ok and zip_ok, zip_ok, name


def classify(facility, accounts, index, parent_id):
    matches = index[norm_name(facility.get('name'))]
    if len(matches) == 1 and matches[0].get('parent_id') == parent_id:
        return None
    if len(matches) > 1:
        kind = 'Duplicate-name review'
        candidates = matches
    elif len(matches) == 1:
        kind = 'Parent mismatch'
        candidates = matches
    else:
        kind = 'No exact name match'
        ranked = sorted(accounts, key=lambda a: rank_candidate(facility, a)[0], reverse=True)
        candidates = [a for a in ranked if rank_candidate(facility, a)[3] or rank_candidate(facility, a)[4] >= .75][:3]
    return {'facility': facility, 'kind': kind, 'candidates': candidates}


def report():
    data = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    accounts, facilities = data['accounts'], data['facilities']
    parents = [a for a in accounts if a.get('name') == PARENT_NAME]
    if len(parents) != 1:
        raise ValueError('Bellhaven parent account must be unique in snapshot')
    parent_id = parents[0]['account_id']
    index = defaultdict(list)
    for a in accounts:
        index[norm_name(a.get('name'))].append(a)
    cases = []
    for f in facilities:
        case = classify(f, accounts, index, parent_id)
        if case:
            cases.append(case)
    return accounts, facilities, cases


@router.get('/investigate', response_class=HTMLResponse)
def investigation_page():
    if not SNAPSHOT.exists():
        return HTMLResponse('Snapshot missing: collect the CRM and facility data first.', status_code=404)
    try:
        accounts, facilities, cases = report()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        return HTMLResponse('<h1>Snapshot problem</h1><p>' + h(error) + '</p>', status_code=500)

    counts = Counter(case['kind'] for case in cases)
    case_cards = []
    for i, case in enumerate(cases, 1):
        f = case['facility']
        options = []
        for account in case['candidates']:
            score, evidence, strong, same_zip, name_score = rank_candidate(f, account)
            revenue = as_number(account.get('lifetime_revenue'))
            ar = as_number(account.get('outstanding_ar'))
            financial_hold = revenue is None or ar is None or (revenue > 0 and ar > 0)
            notice = ('FINANCIAL HOLD: CHOW review required if changing parent' if financial_hold
                      else 'No automatic action — verify before approving any correction')
            caution = 'Potential address-supported match' if strong else 'Investigate identity — do not assume match'
            options.append('<div class="candidate"><b>' + h(account.get('name')) + '</b>'
                           + '<p class="muted">CRM ID: ' + h(account.get('account_id')) + '</p>'
                           + '<p>Address: ' + h(account.get('billing_street')) + ', ' + h(account.get('billing_city'))
                           + ', ' + h(account.get('billing_state')) + ' ' + h(account.get('billing_zip')) + '</p>'
                           + '<p>Parent: ' + h(account.get('parent_name') or '(none)') + '</p>'
                           + '<p>Revenue: ' + h(account.get('lifetime_revenue')) + ' | Outstanding AR: ' + h(account.get('outstanding_ar')) + '</p>'
                           + '<p><b>Matching evidence:</b> ' + h(evidence) + ' · ' + h(caution) + '</p>'
                           + '<p class="' + ('danger' if financial_hold else 'muted') + '">' + h(notice) + '</p></div>')
        if not options:
            options.append('<p class="danger">No reliable CRM candidate found. Manual investigation required.</p>')
        url = safe_url(f.get('source_url'))
        website_link = ('<a target="_blank" rel="noopener noreferrer" href="' + h(url) + '">Open source facility page</a>'
                        if url else 'Website source URL unavailable')
        case_cards.append('<article><div class="eyebrow">Case ' + str(i) + ' · ' + h(case['kind']) + '</div>'
                          + '<h2>' + h(f.get('name')) + '</h2>'
                          + '<p>Website: ' + h(f.get('street')) + ', ' + h(f.get('city')) + ', '
                          + h(f.get('state')) + ' ' + h(f.get('zip')) + '</p>'
                          + '<p>' + website_link + '</p><h3>CRM candidate evidence</h3>' + ''.join(options) + '</article>')
    css = '''body{font-family:Arial,sans-serif;background:#0e1726;color:#eaf0fa;margin:0;padding:22px}
    main{max-width:1150px;margin:auto}a{color:#9bc8ff}.muted{color:#becce0}.danger{color:#ffb8ac}
    .stat{background:#213149;padding:12px 16px;border-radius:10px;display:inline-block;margin:4px}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px}
    article{background:#19273b;border:1px solid #3b5071;border-radius:12px;padding:18px;min-width:0}
    .candidate{border-left:3px solid #5b94d6;background:#26364b;padding:12px;margin:12px 0}
    .candidate p{font-size:14px;line-height:1.45}.eyebrow{color:#c4cfea;font-size:13px}
    input{background:#26364b;border:1px solid #526e94;color:white;padding:12px;border-radius:8px;width:min(95%,530px);margin:12px 0}
    h2{font-size:20px}h3{font-size:16px}'''
    js = '''const input=document.getElementById('filter');input.addEventListener('input',()=>{
    const q=input.value.toLowerCase();document.querySelectorAll('article').forEach(c=>c.hidden=!c.textContent.toLowerCase().includes(q));});'''
    page = ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            + '<title>Bellhaven | Find Problems</title><style>' + css + '</style></head><body><main>'
            + '<h1>Find Problems — Evidence Review</h1><p>Read-only comparison of your saved website and CRM snapshot. '
            + 'These are review cases, not verified corrections.</p>'
            + '<div class="stat">Website facilities: <b>' + str(len(facilities)) + '</b></div>'
            + '<div class="stat">CRM accounts: <b>' + str(len(accounts)) + '</b></div>'
            + '<div class="stat">Flagged: <b>' + str(len(cases)) + '</b></div>'
            + '<div class="stat">Exact-name clean: <b>' + str(len(facilities) - len(cases)) + '</b></div>'
            + '<p>Breakdown: ' + h(dict(counts)) + '</p>'
            + '<label for="filter">Search facilities or CRM candidates:</label><br><input id="filter" placeholder="Search by name, city, issue or address">'
            + '<div class="grid">' + ''.join(case_cards) + '</div>'
            + '<p><a href="/records">Data Review</a> · <a href="/">Review Dashboard</a></p>'
            + '</main><script>' + js + '</script></body></html>')
    return HTMLResponse(page)
