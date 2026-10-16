# -*- coding: utf-8 -*-
"""272 — Date firmă: CUI-ul nu se modifică din acest ecran, de niciun rol; corectura e operațiunea separată a administratorului, cu
avertisment (comanda Costin 16.10.2026, „Lotul 6, comanda 1” pct.8, verbatim în DECIZII). Înainte: un asistent junior schimba CUI-ul unei
firme existente, cu documente, din formular. Temei: N/A — regulă de produs (cine și pe ce drum schimbă identitatea fiscală a firmei).
Schemă efemeră din template, ștearsă la ieșire."""
import io

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov
from core import firma_profil_api as _fp

_SCH = "efemer_272"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn():
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui) VALUES (1, 'F SRL', 'RO14399840')" % _SCH)
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
        c.rollback()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def test_272_date_firma_refuza_alt_cui_si_lasa_acelasi(conn):
    """MUTAȚIE: refuzul `COD_CUI_NEMODIFICABIL` scos din `salveaza_date` -> CUI-ul se schimbă din formular -> pică."""
    r = _fp.salveaza_date(conn, {"cui": "RO18547290", "telefon": "07"}, tenant_id=1, user_id=1)
    assert (r["ok"], r.get("cod"), r.get("camp")) == (False, _fp.COD_CUI_NEMODIFICABIL, "cui"), r
    with conn.cursor() as cur:
        cur.execute("SELECT cui, telefon FROM firma_profil WHERE id = 1")
        assert cur.fetchone() == ("RO14399840", None), "refuzul nu lasă nimic scris"
    r = _fp.salveaza_date(conn, {"cui": "ro14399840 ", "telefon": "07"}, tenant_id=1, user_id=1)
    assert r["ok"], r
    with conn.cursor() as cur:
        cur.execute("SELECT cui, telefon FROM firma_profil WHERE id = 1")
        assert cur.fetchone() == ("RO14399840", "07"), "același CUI trece, nerescris"


def test_272_corectura_cere_avertismentul_confirmat_si_cui_valid(conn):
    r = _fp.corecteaza_cui(conn, 1, "RO18547290", 1)
    assert (r["cod"], r["avertisment"]) == ("CONFIRMARE_CERUTA", _fp.AVERTISMENT_CORECTURA_CUI % ("RO14399840", "RO18547290")), r
    assert _fp.corecteaza_cui(conn, 1, "RO14399841", 1, confirmat=True)["camp"] == "cui"
    assert _fp.corecteaza_cui(conn, 1, "ro14399840", 1, confirmat=True)["cod"] == "CUI_NESCHIMBAT"   # același CUI, altă scriere


def test_272_ruta_corecturii_cere_administratorul():
    """Garda rutei e dreptul de administrator (`drepturi.ADMIN`), nu „poate pregăti”: un asistent nu o are, de niciun nivel. Citit din
    dependența rutei înregistrate (`nivel_drept`, același atribut din care `GET /eu/drepturi` ascunde butonul).
    Că `readonly` arată needitabil prin regula GLOBALĂ (DS cap.6 v2.92) păzește verificatorul (FEREASTRA_LOT6 / READONLY_GLOBAL); că
    CUI-ul din Date firmă e needitabil, iar corectura trece prin avertisment, păzește e2e-ul 272 (`e2e_lot6.py`)."""
    import main
    from core import drepturi
    r = [x for x in main.app.routes if getattr(x, "path", "") == "/tenants/{tenant_id}/cui/corectura" and x.methods == {"POST"}]
    assert len(r) == 1
    niveluri = [getattr(d.call, "nivel_drept", None) for d in r[0].dependant.dependencies]
    assert niveluri.count(drepturi.ADMIN) == 1, niveluri
