import httpx

from app import executor as X
from app import ledger as L
from app.crm import CRMClient
from app.pipeline import run_pipeline
from app.scrape import ScrapeResult, scrape
from tests.conftest import CT, FakeCRM, acct, approve_exec, parents, site

FACS = [site("Bellhaven of Zanesville", "2680 Maple Ave", "Zanesville", "OH", "43701"),
        site("Bellhaven of Batavia", "2000 Hospital Dr", "Batavia", "OH", "45103")]
ACCTS = parents() + [acct("A1", "Cedar Trail of Zanesville", parent=CT, street="2680 Maple Avenue", city="Zanesville",
                          state="OH", zip_="43701", phone="(555) 000-0000")]


def fake_scrape(facs=FACS, complete=True):
    def _s():
        r = ScrapeResult()
        r.facilities, r.complete = [dict(f) for f in facs], complete
        return r
    return _s


def test_rerun_does_not_repropose_decided_items(ledger):
    crm = FakeCRM(ACCTS)
    r1 = run_pipeline(crm, ledger, fake_scrape())
    assert r1["new"] == 3   # re-parent, separate rename, create
    props = {p["kind"]: p for p in ledger.proposals()}
    assert approve_exec(crm, ledger, props["WRONG_PARENT"]["id"])["status"] == L.VERIFIED
    X.reject(ledger, props["WEBSITE_ONLY"]["id"])
    r2 = run_pipeline(crm, ledger, fake_scrape())
    assert r2["new"] == 0  # applied one now matches; rejected one recognised by fingerprint
    assert ledger.get_proposal(props["WEBSITE_ONLY"]["id"])["status"] == L.REJECTED
    assert len(ledger.proposals()) == 3


def test_rerun_unchanged_is_noop(ledger):
    crm = FakeCRM(ACCTS)
    run_pipeline(crm, ledger, fake_scrape())
    r2 = run_pipeline(crm, ledger, fake_scrape())
    assert r2["new"] == 0 and r2["known"] == 3


def test_material_change_creates_new_proposal_and_supersedes_pending(ledger):
    crm = FakeCRM(ACCTS)
    run_pipeline(crm, ledger, fake_scrape())
    changed = [dict(FACS[0]), dict(FACS[1], phone="(999) 111-2222")]
    r2 = run_pipeline(crm, ledger, fake_scrape(changed))
    assert r2["new"] == 1
    assert len(ledger.proposals(status=L.SUPERSEDED)) == 1


def test_pipeline_never_writes(ledger):
    crm = FakeCRM(ACCTS)
    run_pipeline(crm, ledger, fake_scrape())
    assert crm.writes() == []


def test_crm_pagination_fetches_all_pages():
    rows = [{"account_id": f"A{i}"} for i in range(121)]

    def handler(req):
        page, size = int(req.url.params["page"]), int(req.url.params["page_size"])
        assert req.headers["authorization"] == "Bearer t"
        return httpx.Response(200, json={"data": rows[(page - 1) * size: page * size], "page": page,
                                         "page_size": size, "total": len(rows)})
    c = CRMClient(base="http://crm", token="t", transport=httpx.MockTransport(handler))
    assert len(c.list_accounts()) == 121


DETAIL = """<h1>{n}</h1><dl class="detail"><dt>Address</dt><dd>1 Main St<br>Town, OH 44000</dd>
<dt>Care Offerings</dt><dd><span class="badge">Assisted Living</span></dd><dt>Administrator</dt><dd>A B</dd>
<dt>Phone</dt><dd>(555) 111-2222</dd></dl>"""


def _site_transport(fail_path=None):
    def handler(req):
        p = req.url.path
        if p == fail_path:
            return httpx.Response(500)
        if p == "/":
            return httpx.Response(200, text='serve 3 communities <a href="/communities/c">new</a>')
        if p == "/communities":
            pg = req.url.params.get("page", "1")
            if pg == "1":
                return httpx.Response(200, text='2 communities listed <a href="/communities/a">a</a>'
                                                '<a href="/communities?page=2">Next →</a>')
            return httpx.Response(200, text='2 communities listed <a href="/communities/b">b</a>')
        return httpx.Response(200, text=DETAIL.format(n=p.rsplit("/", 1)[-1].upper()))
    return httpx.MockTransport(handler)


def test_website_pagination_and_homepage_only_listing():
    r = scrape("http://site", transport=_site_transport())
    assert sorted(f["name"] for f in r.facilities) == ["A", "B", "C"]
    assert r.homepage_count == 3 and r.directory_count == 2 and r.complete
    assert [f["name"] for f in r.facilities if not f["in_directory"]] == ["C"]
    assert r.facilities[0]["zip"] == "44000"


def test_failed_scrape_page_marks_incomplete_and_skips_crm_only(ledger):
    r = scrape("http://site", transport=_site_transport(fail_path="/communities/b"))
    assert not r.complete and r.errors
    crm = FakeCRM(parents() + [acct("X1", "Bellhaven of B", street="1 Main St", city="Elsewhere", state="OH",
                                    zip_="40000")])
    run_pipeline(crm, ledger, lambda: r)
    assert not ledger.proposals(kind="CRM_ONLY")
