from app.reconcile import reconcile
from tests.conftest import BH, CT, acct, parents, site


def kinds(props):
    return sorted(p["kind"] for p in props)


def test_exact_match_ok():
    w = [site("Bellhaven of Saline", "980 W Michigan Ave", "Saline", "MI", "48176", phone="(614) 868-2766")]
    a = parents() + [acct("A1", "Bellhaven of Saline", street="980 West Michigan Avenue", city="Saline",
                          state="MI", zip_="48176", phone="(614) 868-2766")]
    res, props = reconcile(w, a, True)
    assert res[0]["classification"] == "MATCH_OK" and props == []


def test_field_update_outdated_name_same_address():
    w = [site("Bellhaven of Chagrin Falls", "150 River St", "Chagrin Falls", "OH", "44022")]
    a = parents() + [acct("A1", "Riverbend Manor Care Center", street="150 River St", city="Chagrin Falls",
                          state="OH", zip_="44022", phone="(555) 000-0000")]
    _, props = reconcile(w, a, True)
    assert kinds(props) == ["FIELD_UPDATE"] and props[0]["ops"][0]["fields"] == {"name": "Bellhaven of Chagrin Falls"}


def test_similar_name_different_address_is_not_matched():
    """Carlisle PA must not match New Carlisle OH; same name in another state must not match."""
    w = [site("Bellhaven of Carlisle", "640 Walnut Bottom Rd", "Carlisle", "PA", "17015"),
         site("Amberly Manor", "4390 Darrow Rd", "Hudson", "OH", "44236")]
    a = parents() + [acct("A1", "Bellhaven of New Carlisle", street="875 Elm St", city="New Carlisle", state="OH",
                          zip_="45344"),
                     acct("A2", "Amberly Manor", parent="X", street="918 S Nevada Ave", city="Colorado Springs",
                          state="CO", zip_="80903")]
    res, props = reconcile(w, a, True)
    # Carlisle PA: genuinely missing -> create proposal. Amberly: same name at a different address -> HOLD
    # (identity unresolved; the Colorado account is never repointed and nothing is created automatically).
    assert kinds(props) == ["CRM_ONLY", "HOLD", "WEBSITE_ONLY"]
    carlisle = next(p for p in props if p["kind"] == "WEBSITE_ONLY")
    assert carlisle["evidence"]["website"]["name"] == "Bellhaven of Carlisle"
    assert all(o["type"] == "create" for o in carlisle["ops"])
    amberly = next(p for p in props if p["kind"] == "HOLD")
    assert amberly["ops"] == [] and amberly["actionable"] is False
    assert "A2" not in {o.get("account_id") for p in props for o in p["ops"]}


def test_ambiguous_same_city_similar_name_conflicting_address():
    w = [site("Bellhaven at Union Square", "118 Union Square Dr", "New Albany", "OH", "43054", phone="(330) 519-9639")]
    a = parents() + [acct("A1", "Union Square Senior Living", parent="JP", street="240 Market St", city="New Albany",
                          state="OH", zip_="43054", phone="(260) 782-4620")]
    _, props = reconcile(w, a, True)
    assert props[0]["kind"] == "HOLD" and props[0]["risk"] == "hold"
    assert props[0]["ops"] == []  # existing account untouched AND nothing created on a guess


def test_po_box_name_match_supported_by_phone():
    w = [site("Bellhaven of Ashtabula", "3156 W Prospect Rd", "Ashtabula", "OH", "44004", phone="(260) 440-4975")]
    a = parents() + [acct("A1", "Bellhaven of Ashtabula", street="PO Box 517", city="Ashtabula", state="OH",
                          zip_="44004", phone="(260) 440-4975")]
    _, props = reconcile(w, a, True)
    assert props[0]["kind"] == "FIELD_UPDATE" and props[0]["confidence"] == "medium"
    assert props[0]["ops"][0]["fields"] == {"billing_street": "3156 W Prospect Rd"}


def test_website_only():
    w = [site("Bellhaven of Batavia", "2000 Hospital Dr", "Batavia", "OH", "45103", care=("Short-Term Rehabilitation & Nursing",))]
    _, props = reconcile(w, parents(), True)
    f = props[0]["ops"][0]["fields"]
    assert props[0]["kind"] == "WEBSITE_ONLY" and f["parent_id"] == BH and f["care_type"] == "Skilled Nursing"


def test_duplicates_survivor_is_bellhaven_parented():
    w = [site("Bellhaven Gardens of Monroe", "750 Stewart Rd", "Monroe", "MI", "48162")]
    a = parents() + [acct("A1", "Cedar Trail of Monroe", parent=CT, street="750 Stewart Road", city="Monroe",
                          state="MI", zip_="48162", phone="(555) 000-0000"),
                     acct("A2", "Bellhaven Gardens of Monroe", street="750 Stewart Rd", city="Monroe", state="MI",
                          zip_="48162", phone="(555) 000-0000")]
    res, props = reconcile(w, a, True)
    assert kinds(props) == ["DUPLICATE"]
    f = props[0]["ops"][0]
    assert f["account_id"] == "A1" and f["fields"]["duplicate_of_account"] == "A2" and f["fields"]["status"] == "Inactive"


def test_crm_only_flagged_not_deactivated():
    a = parents() + [acct("A1", "Bellhaven of Coldwater", street="90 N Michigan Ave", city="Coldwater", state="MI", zip_="49036")]
    _, props = reconcile([site("Other", "1 X St", "Y", "OH", "11111")], a, True)
    p = [p for p in props if p["kind"] == "CRM_ONLY"][0]
    assert p["ops"][0]["fields"]["status"] == "Needs Review"
    assert "parent_id" not in p["ops"][0]["fields"]


def test_failed_scrape_never_flags_crm_only():
    a = parents() + [acct("A1", "Bellhaven of Coldwater", street="90 N Michigan Ave", city="Coldwater", state="MI", zip_="49036")]
    _, props = reconcile([], a, scrape_complete=False)
    assert props == []


def test_superseded_accounts_are_not_candidates():
    w = [site("Bellhaven of Owosso", "1120 W Main St", "Owosso", "MI", "48867")]
    a = parents() + [acct("A1", "Bellhaven of Owosso", street="1120 W Main St", city="Owosso", state="MI", zip_="48867",
                          phone="(555) 000-0000"),
                     acct("A2", "Bellhaven of Owosso", street="1120 West Main Street", city="Owosso", state="MI",
                          zip_="48867", status="Inactive", duplicate_of_account="A1")]
    _, props = reconcile(w, a, True)
    assert props == []
