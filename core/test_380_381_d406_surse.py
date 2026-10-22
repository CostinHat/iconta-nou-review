# -*- coding: utf-8 -*-
"""380 / 381 (comanda Costin 8.2, verbatim în DECIZII „Comanda 8.2”):
380 — „Contul de venit vine dintr-o singură sursă, iar nepotrivirea jurnal–facturi se semnalează înainte de «Pune în De depus»”;
381 — „Nota pe 401/4111 cere partenerul la introducere, iar D406 semnalează liniile de terți fără partener.”
Temeiul D406: schema ANAF SAF-T (`anaf_surse/d406_schema_anaf.xlsx`), GL.28 / GL.29 — CustomerID / SupplierID pe liniile de terți.
"""
import pytest

from core import contare_facturi as cf
from core import db as _db, jurnal_api, tenant_provisioning as _tp

_SCHEMA = "test_381_partener"


def test_380_contul_de_venit_are_o_singura_sursa():
    """Nota de contare și D406 iau contul liniei prin ACEEAȘI funcție. MUTAȚIA: `return "707"` pus primul în `cont_venit_linie` -> ROȘU."""
    assert cf.cont_venit_linie("704") == "704"                       # contul liniei câștigă
    assert cf.cont_venit_linie("", "706") == "706"                   # apoi contul implicit al firmei
    assert cf.cont_venit_linie(None, None) == "707"                  # apoi 707
    # OMFP 1802/2014, funcțiunea contului 419 („Clienți - creditori”): avansul încasat pe factură de avans
    assert cf.cont_venit_linie("704", None, "avans") == cf.CONT_AVANS_CLIENT


def test_380_d406_citeste_contul_prin_aceeasi_functie():
    """Garda structurală: `d406` nu mai are un cont de venit propriu pe liniile facturilor de vânzare — îl ia din `contare_facturi`."""
    import ast
    import inspect
    from core import d406
    arb = ast.parse(inspect.getsource(d406))
    importuri = {(n.module, a.name, a.asname) for n in ast.walk(arb) if isinstance(n, ast.ImportFrom) for a in n.names}
    assert ("core.contare_facturi", "cont_venit_linie", "_cont_venit_linie") in importuri, \
        "d406 nu citește contul de venit prin contare_facturi.cont_venit_linie"
    apeluri = [n for n in ast.walk(arb) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "_cont_venit_linie"]
    assert len(apeluri) >= 2, "liniile facturilor de vânzare nu trec toate prin funcția comună"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
            cur.execute("SET search_path TO %s, public" % _SCHEMA)
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("deb, cre", [("401", "5311"), ("5311", "4111"), ("5121", "401")])
def test_381_nota_pe_tert_fara_partener_e_refuzata(conn, deb, cre):
    """MUTAȚIA: verificarea partenerului scoasă din `_linii_valide` -> nota intră -> ROȘU."""
    r = jurnal_api.creeaza(conn, _SCHEMA, "Plata furnizor", "2026-10-03", [{"debit": deb, "credit": cre, "suma": 500}], "OP 1")
    # [lotul 11, 440] câmpul ecranului „Notă nouă” (`je-pnume-0` = partenerul liniei 1), în lista erorilor; linia rămâne dată
    assert not r.get("ok") and ([c["camp"] for c in r["erori_campuri"]], r.get("linia")) == (["je-pnume-0"], 1), r


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_381_nota_cu_partener_intra_si_il_pastreaza(conn):
    r = jurnal_api.creeaza(conn, _SCHEMA, "Plata furnizor", "2026-10-03",
                           [{"debit": "401", "credit": "5311", "suma": 500, "partener_cui": "RO14399840",
                             "partener_nume": "DANTE INTERNATIONAL SA"}], "OP 1")
    assert r.get("ok"), r
    with conn.cursor() as cur:
        cur.execute("SELECT partener_cui, partener_nume FROM inregistrari_linii WHERE inregistrare_id = %s", (r["id"],))
        # [lotul 11, decizia 10.3 pct.4] partenerul e păstrat, în forma păstrată a CUI-ului (fără „RO”, triggerul `trg_cui_fara_ro`)
        assert cur.fetchall() == [("14399840", "DANTE INTERNATIONAL SA")]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_381_cui_cu_cifra_de_control_gresita_e_refuzat(conn):
    r = jurnal_api.creeaza(conn, _SCHEMA, "Plata furnizor", "2026-10-03",
                           [{"debit": "401", "credit": "5311", "suma": 500, "partener_cui": "14399841", "partener_nume": "X"}], "OP 1")
    assert not r.get("ok") and ([c["camp"] for c in r["erori_campuri"]], r.get("linia")) == (["je-pcui-0"], 1), r
