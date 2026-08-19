# -*- coding: utf-8 -*-
"""[Regula 5 + Regula 10 + Regula 6] GARDA: auto-derivarea d301_operatiuni -> D390 (cod A/S).

Decizia Costin 18.08.2026 (audit tenant_006): achizitiile IC ale unui neplatitor art.317, inregistrate O SINGURA
data in ecranul D301 (d301_operatiuni cu furnizor), alimenteaza AUTOMAT D390 - tip 1/3 (bunuri) -> cod A, tip 5
(servicii IC) -> cod S; tip 2 (transport nou) + tip 4 (art.307 mixt) EXCLUSE. Se deriveaza DOAR operatiunile cu
TARA furnizorului (codT obligatoriu in D390). Cele DOUA cai independente - generatorul (d390.operatiuni_din_d301)
si reconcilierea a-doua-cale (d390_reconciliere._pull_d301) - trebuie sa dea ACELASI rezultat, altfel gardul de
reconciliere blocheaza fals (aggregation-loss). Testul cade daca o cale ignora d301 sau maparea drifteaza.
"""
import os
import pytest


SCH = "_t_d390auto_%d" % os.getpid()


def _db():
    cale = os.path.expanduser("~/.iconta/db.env")
    if not os.path.exists(cale):
        return None
    for l in open(cale, encoding="utf-8"):
        l = l.strip()
        if l and not l.startswith("#") and "=" in l:
            k, v = l.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    try:
        from core import db
        db.init_pool()
        return db
    except Exception:
        return None


@pytest.fixture
def schema_d301():
    db = _db()
    if not db:
        pytest.skip("fara db.env local")
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)
            c.execute('CREATE SCHEMA "%s"' % SCH)
            c.execute('CREATE TABLE "%s".d301_operatiuni (id serial, an int, luna int, tip int, '
                      'nr_doc text, data_doc text, tip_valuta text DEFAULT \'EUR\', tva numeric DEFAULT 0, '
                      'val_valuta numeric, curs numeric, partener_tara varchar(2) DEFAULT \'\', '
                      'partener_cod varchar(20) DEFAULT \'\', partener_den text DEFAULT \'\', '
                      'temei_307 text)' % SCH)
    try:
        yield db
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as c:
                c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)


def _ins(db, tip, val, curs, tara, cod="", den="", temei=None):
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('INSERT INTO "%s".d301_operatiuni (an,luna,tip,val_valuta,curs,partener_tara,partener_cod,partener_den,temei_307) '
                      "VALUES (2026,6,%%s,%%s,%%s,%%s,%%s,%%s,%%s)" % SCH, (tip, val, curs, tara, cod, den, temei))


def test_mapare_tip_cod_si_filtrul_tarii(schema_d301):
    db = schema_d301
    from core.d390 import operatiuni_din_d301
    _ins(db, 1, 100, 5, "DE", "123", "Furnizor DE")     # bunuri -> A
    _ins(db, 3, 200, 5, "FR")                            # accizabile -> A
    _ins(db, 5, 300, 5, "IT")                            # servicii IC -> S
    _ins(db, 2, 400, 5, "DE")                            # transport nou -> EXCLUS
    _ins(db, 4, 500, 5, "DE")                            # art.307 mixt -> EXCLUS
    _ins(db, 1, 600, 5, "")                              # bunuri FARA tara -> EXCLUS (nu formeaza linie D390)
    with db.get_conn() as conn:
        linii = operatiuni_din_d301(conn, SCH, 2026, 6)
    coduri = sorted((o["tip"], o["tara"], o["baza"]) for o in linii)
    assert coduri == [("A", "DE", 500), ("A", "FR", 1000), ("S", "IT", 1500)], \
        "maparea tip->cod / filtrul tarii gresit: %s" % coduri


def test_cele_doua_cai_coincid(schema_d301):
    """Generatorul (operatiuni_din_d301) si reconcilierea (_pull_d301) - independente - dau acelasi set,
    altfel gardul de reconciliere a-doua-cale ar bloca fals cu 'aggregation-loss'."""
    db = schema_d301
    from core.d390 import operatiuni_din_d301
    from core.d390_reconciliere import _pull_d301
    _ins(db, 1, 10500, 4.9772, "DE", "129273398", "Muster GmbH")
    _ins(db, 5, 1000, 5, "FR", "12345678901", "Service FR")
    _ins(db, 1, 999, 5, "")                              # fara tara -> ambele il exclud
    with db.get_conn() as conn:
        g = sorted((o["tip"], o["tara"], o["cod"], o["baza"]) for o in operatiuni_din_d301(conn, SCH, 2026, 6))
    with db.get_conn() as conn:
        r = sorted((o["tip"], o["tara"], o["cod"], o["baza"]) for o in _pull_d301(conn, SCH, 2026, 6))
    assert g == r, "generatorul si reconcilierea difera pe d301: %s vs %s" % (g, r)
    assert len(g) == 2, "operatiunea fara tara nu trebuie sa formeze linie: %s" % g


def test_achizitii_d301_numara_doar_mapabile_fara_tara(schema_d301):
    """[refinare tip 2/4] achizitii_d301 (folosit la refuzul-pe-zero) numara DOAR operatiunile care AR TREBUI
    in D390 dar nu au aparut: tip 1/3/5 FARA tara. tip 2/4 (nu intra in D390) NU se numara nici cu tara -
    altfel avertismentul ar spune fals 'lipseste tara' pt o operatiune care nu apartine D390."""
    db = schema_d301
    from core.d390 import achizitii_d301
    _ins(db, 1, 100, 5, "")      # bunuri fara tara -> numarat
    _ins(db, 3, 100, 5, "")      # accizabile fara tara -> numarat
    _ins(db, 5, 100, 5, "")      # servicii fara tara -> numarat
    _ins(db, 2, 100, 5, "DE")    # transport CU tara -> NU (nu intra in D390)
    _ins(db, 4, 100, 5, "DE")    # mixt CU tara -> NU
    _ins(db, 1, 100, 5, "DE")    # bunuri CU tara -> NU (a intrat deja in D390)
    with db.get_conn() as conn:
        assert achizitii_d301(conn, SCH, 2026, 6) == 3, "numara doar tip 1/3/5 fara tara"


def test_excluse_d301_tip4_neconfirmat_semnaleaza(schema_d301):
    """[temei_307] excluse_d301 face excluderea din D390 AUDITABILA: tip 4 FARA temei_307 -> SEMNAL
    (NECONFIRMAT); tip 4 CU temei -> exclusa cu eticheta + temei citat, fara semnal; tip 1 cu tara ->
    se deriveaza in D390 (cod A), NU e exclusa. Ruleaza pe operatiuni reale, nu pe lista goala."""
    db = schema_d301
    from core.d390 import excluse_d301
    _ins(db, 4, 100, 5, "DE", "777888", "Gaz X")                            # tip 4 fara temei -> semnal
    _ins(db, 4, 100, 5, "DE", "888", "Gaz confirmat", temei="gaz_energie")  # tip 4 cu temei -> fara semnal
    _ins(db, 1, 100, 5, "DE", "136695976", "Bunuri")                        # tip 1 cu tara -> derivata (nu exclusa)
    with db.get_conn() as conn:
        ex = {e["id"].split(" (")[0]: e for e in excluse_d301(conn, SCH, 2026, 6)}
    assert "Gaz X" in ex and ex["Gaz X"]["semnal"] is True and "NECONFIRMAT" in ex["Gaz X"]["motiv"], ex
    assert "Gaz confirmat" in ex and ex["Gaz confirmat"]["semnal"] is False and "307" in ex["Gaz confirmat"]["temei"], ex
    assert "Bunuri" not in ex, "tip 1 cu tara se deriveaza in D390, nu e exclusa"


def test_lista_temei_neconfirmat_pe_tip4(schema_d301):
    """[temei_307] lista marcheaza temei_neconfirmat=True pe tip 4 fara temei; False pe tip 4 cu temei
    si pe alte tipuri; expune temei_307 + eticheta."""
    db = schema_d301
    from core import d301_operatiuni_api as api
    _ins(db, 4, 100, 5, "DE", "777", "Gaz fara temei")
    _ins(db, 4, 100, 5, "DE", "778", "Gaz cu temei", temei="gaz_energie")
    _ins(db, 1, 100, 5, "DE", "136695976", "Bunuri tip1")
    with db.get_conn() as conn:
        ops = {o["partener_den"]: o for o in api.lista(conn, SCH, 2026, 6)["operatiuni"]}
    assert ops["Gaz fara temei"]["temei_neconfirmat"] is True, ops["Gaz fara temei"]
    assert ops["Gaz cu temei"]["temei_neconfirmat"] is False and ops["Gaz cu temei"]["temei_307"] == "gaz_energie"
    assert ops["Bunuri tip1"]["temei_neconfirmat"] is False
