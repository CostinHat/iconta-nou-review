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
                      'd390_confirmat_local boolean DEFAULT false)' % SCH)
    try:
        yield db
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as c:
                c.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCH)


def _ins(db, tip, val, curs, tara, cod="", den=""):
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('INSERT INTO "%s".d301_operatiuni (an,luna,tip,val_valuta,curs,partener_tara,partener_cod,partener_den) '
                      "VALUES (2026,6,%%s,%%s,%%s,%%s,%%s,%%s)" % SCH, (tip, val, curs, tara, cod, den))


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


def test_d390_posibil_serviciu_semnaleaza_tip4_cu_cod(schema_d301):
    """[mis-clasificare] lista marcheaza d390_posibil_serviciu=True DOAR pe tip 4 cu cod TVA furnizor
    (codul exclude alin.6 nereg -> posibil serviciu IC pus gresit ca tip 4, ar trebui tip 5 -> D390 cod S).
    tip 4 fara cod (posibil alin.6) si tip 5 -> False."""
    db = schema_d301
    from core import d301_operatiuni_api as api
    _ins(db, 4, 100, 5, "DE", "123456", "Furnizor DE")   # tip 4 CU cod -> suspect
    _ins(db, 4, 100, 5, "DE", "", "Fara cod")            # tip 4 FARA cod -> nu
    _ins(db, 5, 100, 5, "IT", "999", "Serviciu IT")      # tip 5 -> nu (deja corect)
    with db.get_conn() as conn:
        ops = {o["partener_den"]: o for o in api.lista(conn, SCH, 2026, 6)["operatiuni"]}
    assert ops["Furnizor DE"]["d390_posibil_serviciu"] is True, "tip 4 cu cod trebuie semnalat"
    assert ops["Fara cod"]["d390_posibil_serviciu"] is False, "tip 4 fara cod nu se semnaleaza"
    assert ops["Serviciu IT"]["d390_posibil_serviciu"] is False, "tip 5 nu se semnaleaza"


def test_confirma_local_stinge_indiciul_reversibil(schema_d301):
    """[fals-pozitiv benign] confirma_local pe o operatiune tip 4 -> d390_posibil_serviciu devine False
    (indiciul se stinge); reversibil (valoare=False -> revine). Rezolva gaz/energie legitim (alin.3/5)."""
    db = schema_d301
    from core import d301_operatiuni_api as api
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('INSERT INTO "%s".d301_operatiuni (an,luna,tip,val_valuta,curs,partener_tara,partener_cod,partener_den) '
                      "VALUES (2026,6,4,100,5,%%s,%%s,%%s) RETURNING id" % SCH, ("DE", "999", "Gaz DE"))
            oid = c.fetchone()[0]

    def flag():
        with db.get_conn() as conn:
            return [o["d390_posibil_serviciu"] for o in api.lista(conn, SCH, 2026, 6)["operatiuni"] if o["id"] == oid][0]

    assert flag() is True, "tip 4 cu cod, neconfirmat -> indiciul apare"
    with db.get_conn() as conn:
        api.confirma_local(conn, SCH, 2026, 6, oid, True)
    assert flag() is False, "dupa confirmare -> indiciul se stinge"
    with db.get_conn() as conn:
        api.confirma_local(conn, SCH, 2026, 6, oid, False)
    assert flag() is True, "anularea confirmarii readuce indiciul (reversibil)"


def test_confirmare_per_furnizor_persista_intre_luni(schema_d301):
    """[per-furnizor 18.08.2026] Confirmarea unei operatiuni tip 4 de la un furnizor (tara+cod) stinge
    indiciul si pentru VIITOARELE operatiuni de la ACELASI furnizor (alta luna) - nu re-confirmi lunar.
    Cea mostenita e marcata d390_furnizor_confirmat (nu d390_confirmat_local)."""
    db = schema_d301
    from core import d301_operatiuni_api as api
    with db.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('INSERT INTO "%s".d301_operatiuni (an,luna,tip,val_valuta,curs,partener_tara,partener_cod,partener_den) '
                      "VALUES (2026,6,4,100,5,%%s,%%s,%%s) RETURNING id" % SCH, ("DE", "777", "Gaz X"))
            id1 = c.fetchone()[0]
            c.execute('INSERT INTO "%s".d301_operatiuni (an,luna,tip,val_valuta,curs,partener_tara,partener_cod,partener_den) '
                      "VALUES (2026,7,4,200,5,%%s,%%s,%%s) RETURNING id" % SCH, ("DE", "777", "Gaz X"))
            id2 = c.fetchone()[0]

    def op(an, luna, oid):
        with db.get_conn() as conn:
            return [x for x in api.lista(conn, SCH, an, luna)["operatiuni"] if x["id"] == oid][0]

    assert op(2026, 6, id1)["d390_posibil_serviciu"] is True
    assert op(2026, 7, id2)["d390_posibil_serviciu"] is True
    with db.get_conn() as conn:
        api.confirma_local(conn, SCH, 2026, 6, id1, True)
    # operatiunea confirmata direct
    assert op(2026, 6, id1)["d390_confirmat_local"] is True
    # operatiunea din alta luna, acelasi furnizor -> indiciul stins prin MOSTENIRE
    o2 = op(2026, 7, id2)
    assert o2["d390_posibil_serviciu"] is False, "furnizor confirmat -> indiciul se stinge si pe alta luna"
    assert o2["d390_furnizor_confirmat"] is True, "marcata ca furnizor confirmat (mostenit, nu propriu)"
    assert o2["d390_confirmat_local"] is False, "operatiunea din iulie NU e confirmata direct"
