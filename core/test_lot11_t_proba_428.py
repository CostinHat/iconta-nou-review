# -*- coding: utf-8 -*-
"""Lotul 11, 428 (PRIORITAR) — proba în lanț pe CODUL RUTELOR, pe o schemă efemeră din tenant_template, în tranzacție anulată: perioada
scrisă cum o scrie „Date firmă” (`regim_tva_incasare.salveaza`), factura emisă cum o emite formularul (`facturi_api.emite_factura`, cu
contarea automată), încasarea din Casă legată de factură (`casa_api.adauga` cu `facturi`), validarea notelor, apoi D300 și D394 pe lună.
E stratul de sub `frontend_test/e2e/e2e_lot11_t.py::test_def_428_tva_la_incasare_pe_pasii_contabilului` (ecranele) — rulează în poartă la
fiecare commit, nu numai în plasă.

Temei: CF art.282 alin.(3) (exigibilitatea la încasare), alin.(8) („fiecare încasare totală sau parțială se consideră că include și taxa
aferentă”), alin.(7) lit.a) (factura emisă înainte de intrare: regulile generale); CF art.319 alin.(20) lit.p) („mențiunea «TVA la
încasare»”); OPANAF 2194/2025 (D394) pct.5.1 („TVA colectată aferentă facturilor încasate în perioada de raportare”)."""
import datetime as _dt
import re
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tp
from core.common import Perioada

_SCHEMA = "tenant_test_lot11_t428"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _FaraCommit:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


@pytest.fixture
def conn_428():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)   # pe tranzacție: nu rămâne pe conexiunea din pool (core/test_lot10_search_path_pool.py)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, banca, iban, regim_fiscal, platitor_tva, tip_decont, "
                    "tva_la_incasare, platitor_tva_anaf_inceput, declarant_nume, declarant_prenume, declarant_functie, forma_juridica, "
                    "capital_subscris, telefon) VALUES (1,'T428 SRL','14399840','Str Test 1','Bucuresti','B','6920','BCR','RO49AAAA1B31007593840000',"
                    "'real',true,'lunar',false,'2025-01-01','Popescu','Ion','ADMINISTRATOR','SRL',200,'0712345678')")
            yield _FaraCommit(conn)
        finally:
            conn.rollback()


def _emite(conn, data):
    from core import facturi_api
    facturi_api.seteaza_numerotare(conn, serie="T", numar_start=1)
    r = facturi_api.emite_factura(conn, [{"descriere": "Servicii de consultanță", "cantitate": 1, "um": "ora", "pret_unitar": 1000,
                                          "cota_tva": 21, "cota_propusa": 21}],
                                  tert_nume="Client Incasare SRL", tert_cui="18547290", tert_adresa="Str. Probei 1", tert_oras="Sector 1",
                                  tert_judet="B", data_emitere=data, data_scadenta=data, tert_platitor_tva=True)
    assert r.get("ok"), r
    return r


def _note(conn, fid):
    with conn.cursor() as cur:
        cur.execute("SELECT l.cont_debit, l.cont_credit, l.suma FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                    "WHERE i.factura_id = %s ORDER BY i.id, l.id", (fid,))
        return [(a, b, Decimal(c)) for a, b, c in cur.fetchall()]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_428_in_sistem_4428_mentiunea_incasarea_d300_d394(conn_428):
    from core import casa_api, d300, d394, regim_tva_incasare as _rg, tva_incasare as _tvi, duk
    with conn_428.cursor() as cur:
        assert _rg.salveaza(cur, True, de_la="2026-07-01", user_id=1)["ok"]
    r = _emite(conn_428, "2026-07-10")
    fid = r["factura_id"]
    # CF art.282 alin.(3): emisă în sistem -> TVA pe 4428; contarea spune regimul
    assert r["contare"].get("regim_tva_incasare") == _tvi.REGIM_INCASARE, r["contare"]
    assert ("4111", "4428", Decimal("210.00")) in _note(conn_428, fid) and not [n for n in _note(conn_428, fid) if n[1] == "4427"]
    # CF art.319 alin.(20) lit.p): mențiunea, pe detaliu / PDF / XML din aceeași definiție
    from core import facturi_api
    assert _tvi.MENTIUNE in (facturi_api.detalii_factura(conn_428, fid) or {}).get("mentiuni", [])
    # încasarea din Casă, 605 lei, legată de factură -> 4428 = 4427 105 (CF art.282 alin.(8))
    rc = casa_api.adauga(conn_428, _SCHEMA, {"data": "2026-07-15", "categorie": "incasare_client", "suma": "605", "document": "DI 1",
                                             "partener": "Client Incasare SRL", "cui": "18547290",
                                             "facturi": [{"factura_id": fid, "suma": "605"}]})
    assert not rc.get("eroare"), rc
    assert ("4428", "4427", Decimal("105.00")) in _note(conn_428, fid), _note(conn_428, fid)
    with conn_428.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata', document_ref = COALESCE(NULLIF(document_ref, ''), 'DI 1') "
                    "WHERE status <> 'validata'")
    xml, res = d300.genereaza(conn_428, _SCHEMA, Perioada(2026, luna=7))
    # CF art.282 alin.(3): exigibilă numai partea încasată — rândul 9: 500 / 105
    assert (res.R.get("R9_1"), res.R.get("R9_2")) == (500, 105), res.R
    assert duk.valideaza(xml, "d300", an=2026, luna=7)["stare"] in ("valid", "gri")
    xml394, _r394 = d394.genereaza(conn_428, _SCHEMA, Perioada(2026, luna=7))
    m = dict(re.findall(r'\b(sistemTVA|tvaCol21)="([^"]*)"', xml394))
    assert m == {"sistemTVA": "1", "tvaCol21": "105"}, m


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_428_factura_inainte_de_intrare_ramane_pe_4427_si_ecranul_o_spune(conn_428):
    from core import regim_tva_incasare as _rg, tva_incasare as _tvi
    with conn_428.cursor() as cur:
        assert _rg.salveaza(cur, True, de_la="2026-11-01", user_id=1)["ok"]
        msg = _tvi.regim_emitere_la(cur, None, _dt.date(2026, 10, 21))
    r = _emite(conn_428, "2026-10-21")
    # CF art.282 alin.(7) lit.a): factura emisă înainte de intrarea în sistem -> regulile generale: 4427, fără mențiune
    assert r["contare"]["regim_tva_incasare"] == _tvi.REGIM_GENERAL
    assert ("4111", "4427", Decimal("210.00")) in _note(conn_428, r["factura_id"])
    assert msg["aplica"] is False and msg["mesaj"] == (   # mesajul întreg, pe câmpul lui (core/test_garzi_pe_text.py)
        "Factura din 21.10.2026: firma aplică sistemul TVA la încasare abia de la 01.11.2026. O factură emisă înainte de intrarea în "
        "sistem rămâne pe regulile generale: TVA exigibil la emitere (4427), fără mențiunea „TVA la încasare” (Cod fiscal art. 282 alin. "
        "(7) lit. a)). Dacă firma aplica sistemul și la această dată, corectează perioada în Date firmă."), msg
