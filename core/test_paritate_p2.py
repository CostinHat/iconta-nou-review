# -*- coding: utf-8 -*-
"""GARD P2 — PARITATE: modelul de citire răspunde EXACT ce răspundea calculul direct.

**CE PAZEȘTE, și de ce e o gardă separată de cele de performanță.** P2 a mutat calculul din cererea
interactivă în recalculare. Măsurătorile arată că a devenit ieftin; ele NU arată că a rămas
adevărat. *O rută poate deveni de o mie de ori mai rapidă răspunzând greșit.*

**CUM SE COMPARĂ, și ce NU se face.** Se cere ruta prin `TestClient` (deci răspunsul pe care îl vede
frontendul) și se construiește, în paralel, răspunsul pe care l-ar fi dat calea DE DINAINTE DE P2 —
bucla per firmă, cu aceleași funcții pe care le chema ruta atunci. Cele două se compară **întregi**,
cu `==`.

Nu se normalizează nimic: nici verdictele (`verde`/`galben`/`rosu`/`gri`), nici sumele, nici
ordinea. O comparație care rotunjește sau sortează înainte de egalitate ascunde exact clasa de
diferență pentru care există proba. Singurul câmp scos din comparație e `prospetime`, și cu motiv
scris: **nu exista** înainte de P2, deci n-are pereche — nu e o diferență trecută cu vederea, e un
câmp fără corespondent.

**PRECONDIȚIA.** Modelul trebuie să fie proaspăt pentru firmele comparate, altfel ruta răspunde
`gri`/`neevaluat` (cum trebuie) și proba n-ar compara două verdicte, ci un verdict cu o absență.
Fixtura recalculează firmele înainte, iar dacă recalcularea eșuează proba PICĂ — nu sare.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

from core import db as _db  # noqa: E402
from core import auth_api  # noqa: E402
from core import firma_rezumat as FR  # noqa: E402

#: Câte firme intră în comparație. Fiecare costă o trecere GREA (~2 s), deci limita e o alegere de
#: durată, nu de acoperire — și se declară aici ca atare.
CATE_FIRME = 6


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def teren():
    """`(uid, firme, azi, token)` — un utilizator real de cabinet și firmele lui, cu model proaspăt."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    import psycopg2.extras as _E
    from core.common import azi_ro
    azi = azi_ro()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute(
                "SELECT u.id FROM public.users u "
                "  JOIN public.tenants t ON t.accounting_firm_id = u.accounting_firm_id "
                " WHERE u.rol = 'admin_firma' AND u.activ AND t.activ "
                "   AND t.schema_name LIKE 'tenant_%' "
                " GROUP BY u.id ORDER BY count(t.id) DESC LIMIT 1")
            r = cur.fetchone()
        if not r:
            pytest.skip("niciun cabinet cu firme reale")
        uid = r[0]
        firme = auth_api.tenantii_userului(c, uid)[:CATE_FIRME]
        with c.cursor(cursor_factory=_E.RealDictCursor) as cur:
            cur.execute("SELECT id, rol, accounting_firm_id FROM public.users WHERE id = %s", (uid,))
            u = dict(cur.fetchone())
    token = auth_api.emite_token(u)

    # PRECONDIȚIE: model proaspăt pentru chiar firmele comparate.
    for f in firme:
        FR.recalculeaza_firma(f["id"], f["schema_name"], azi=azi)
        FR.recalculeaza_greu(f["id"], f["schema_name"], azi=azi,
                             nume=f.get("nume"), cui=f.get("cui"))
    with _db.get_conn() as c:
        model = FR.citeste(c, [f["id"] for f in firme], list(FR.TOATE), azi=azi)
    nepregatite = {(f["id"], a): model[f["id"]][a]["stare"]
                   for f in firme for a in FR.TOATE
                   if model[f["id"]][a]["stare"] != FR.CURENT}
    assert not nepregatite, (
        "modelul n-a rămas curent după recalculare: %s — proba ar compara un verdict cu o absență"
        % nepregatite)
    return uid, firme, azi, token


@pytest.fixture(scope="module")
def client(teren):
    from fastapi.testclient import TestClient
    import main as _main
    c = TestClient(_main.app)
    yield c
    c.close()


def _get(client, teren, ruta):
    _uid, _firme, _azi, token = teren
    r = client.get(ruta, headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200, "%s -> %s %s" % (ruta, r.status_code, r.text[:200])
    return r.json()


def _fara_prospetime(d):
    """Scoate DOAR `prospetime`. Vezi antetul: e singurul câmp fără corespondent înainte de P2."""
    if isinstance(d, list):
        return [_fara_prospetime(x) for x in d]
    if isinstance(d, dict):
        return {k: _fara_prospetime(v) for k, v in d.items() if k != "prospetime"}
    return d


def _doar(firme_raspuns, ids):
    return [f for f in firme_raspuns if f.get("tenant_id") in ids]


# ============================================================================
#  RUTELE UȘOARE
# ============================================================================
def test_paritate_migrare_solduri(client, teren):
    _uid, firme, _azi, _t = teren
    ids = {f["id"] for f in firme}
    din_model = _doar(_get(client, teren, "/migrare/solduri")["firme"], ids)

    # CALEA DE DINAINTE DE P2: `solduri_api.rezumat`, per firmă, în schema ei.
    from core import solduri_api
    inainte = []
    for f in firme:
        with _db.get_conn(f["schema_name"]) as c:
            r = solduri_api.rezumat(c)
        inainte.append({"tenant_id": f["id"], "nume": f["nume"], "cui": f["cui"],
                        "are_solduri": bool(r["are_solduri"]), "randuri": r["randuri"] or 0})
    assert _fara_prospetime(din_model) == inainte


def test_paritate_migrare_plan_conturi(client, teren):
    _uid, firme, _azi, _t = teren
    ids = {f["id"] for f in firme}
    din_model = _doar(_get(client, teren, "/migrare/plan-conturi")["firme"], ids)

    inainte = []
    for f in firme:
        with _db.get_conn(f["schema_name"]) as c:
            with c.cursor() as cur:
                cur.execute("SELECT count(*) FROM plan_conturi")
                n = cur.fetchone()[0]
        inainte.append({"tenant_id": f["id"], "nume": f["nume"], "cui": f["cui"],
                        "nr_conturi": n})
    assert _fara_prospetime(din_model) == inainte


def test_paritate_migrare_vector(client, teren):
    _uid, firme, _azi, _t = teren
    ids = {f["id"] for f in firme}
    din_model = _doar(_get(client, teren, "/migrare/vector")["firme"], ids)

    # Forma răspunsului e a RUTEI, nu a aspectului: ea publică `are_vector` (nu `completat`) și
    # adaugă `regim_contabil`, derivat din `tip_firma` prin primitiva unică. Proba trebuie s-o
    # reproducă exact — o comparație pe câmpurile pe care mi le amintesc eu n-ar fi paritate.
    from core import vector_fiscal_api
    from core.migrare_api import regim_contabil
    inainte = []
    for f in firme:
        with _db.get_conn(f["schema_name"]) as c:
            v = vector_fiscal_api.citeste(c) or {}
        inainte.append({"tenant_id": f["id"], "nume": f["nume"], "cui": f["cui"],
                        "are_vector": bool(v.get("completat")),
                        "regim_fiscal": v.get("regim_fiscal"),
                        "regim_contabil": regim_contabil(f.get("tip_firma")),
                        "platitor_tva": v.get("platitor_tva"),
                        "tip_decont": v.get("tip_decont"),
                        "operatiuni_ic": v.get("operatiuni_ic")})
    assert _fara_prospetime(din_model) == inainte


# ============================================================================
#  RUTELE GRELE — aici stă tot ce s-a mutat
# ============================================================================
def test_paritate_control_fiscal(client, teren):
    """Verdictul semaforului, câmp cu câmp. **Fără nicio normalizare a stărilor sau a numerelor.**"""
    _uid, firme, azi, _t = teren
    ids = {f["id"] for f in firme}
    din_model = _doar(_get(client, teren, "/control-fiscal")["firme"], ids)

    # CALEA DE DINAINTE DE P2: bucla per firmă din rută, cu aceleași funcții.
    import main as _main
    from core import control_fiscal_api as _cf
    ctx = {"uid": _uid}
    inainte = []
    for f in firme:
        schema, tid = f["schema_name"], f["id"]
        with _db.get_conn(schema) as cs, _db.get_conn() as cp:
            r = _cf.evalueaza_firma(cs, cp, tid, schema, azi)
        contabil, _vc = _main._construieste_contabil(schema, tid, ctx, azi.year, azi.month,
                                                     r.get("regim_tva_anaf"))
        inainte.append({"tenant_id": tid, "nume": f["nume"], "cui": f["cui"],
                        "stare": _main.pastila_firma(r["stare"], contabil),
                        "lipsa": len(r.get("lipsa") or []),
                        "urmarit": len(r.get("urmarit") or []),
                        "neclar": len(r.get("neclar") or []),
                        "contabil": contabil})
    got = _fara_prospetime(din_model)
    assert [x["stare"] for x in got] == [x["stare"] for x in inainte], "verdictele diferă"
    assert got == inainte


def test_paritate_termene(client, teren):
    """Răspunsul ÎNTREG al rutei, nu doar câmpuri alese.

    `termene_api.portofoliu` grupează pe dată și tip; o diferență într-o singură firmă schimbă
    numărătorile din grup. De-aia se compară agregatul, nu bucățile."""
    _uid, firme, azi, _t = teren
    din_model = _get(client, teren, "/termene")

    import main as _main
    from core import termene_api
    ctx = {"uid": _uid}
    # Bucla de dinainte de P2 — pe TOATE firmele utilizatorului, fiindcă ruta agreghează pe toate.
    with _db.get_conn() as c:
        toate = auth_api.tenantii_userului(c, _uid)
    ev, neev = [], []
    for f in toate:
        e, n = _main._termene_una_firma(f, ctx, azi)
        if e:
            ev.append(e)
        if n:
            neev.append(n)
    inainte = termene_api.portofoliu(ev, azi, neev)
    assert _fara_prospetime(din_model) == _fara_prospetime(inainte)


# ============================================================================
#  CE ÎNSEAMNĂ PARITATE — proba că proba are dinți
# ============================================================================
def test_comparatia_ar_vedea_o_diferenta(client, teren):
    """MUTAȚIE pe propriul mod de eșec: dacă modelul ar servi o valoare stricat de alta, comparația
    trebuie să PICE. Fără proba asta, un `==` pe două structuri goale ar trece la fel de verde."""
    _uid, firme, _azi, _t = teren
    ids = {f["id"] for f in firme}
    din_model = _doar(_get(client, teren, "/migrare/plan-conturi")["firme"], ids)
    assert din_model, "nicio firmă în comparație — proba n-ar putea eșua"
    stricat = _fara_prospetime(din_model)
    stricat[0] = dict(stricat[0], nr_conturi=(stricat[0]["nr_conturi"] or 0) + 1)
    assert stricat != _fara_prospetime(din_model), (
        "comparația nu deosebește două răspunsuri diferite — toate probele de mai sus sunt goale")
