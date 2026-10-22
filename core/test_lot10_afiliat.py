# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 428, decizia Costin 20.10.2026 „Bifă pe client”] Beneficiarul afiliat rămâne pe regulile generale de exigibilitate.

Decizia, verbatim (DECIZII „Lotul 10: deciziile lui Costin la întrebările din lot”): „Bifă pe client” — câmpul „persoană afiliată (art.7
pct.26)” pe client; factura către el ia regulile generale (4427) chiar dacă firma e în sistem.

Temeiul (`anaf_surse/cod_fiscal_227_2015_consolidat.txt`): CF art.282 alin.(6): „nu aplică sistemul respectiv pentru următoarele operațiuni
care intră sub incidența regulilor generale privind exigibilitatea TVA: [...] d) livrările de bunuri/prestările de servicii pentru care
beneficiarul este o persoană afiliată furnizorului/prestatorului potrivit art. 7 pct. 26.” CF art.7 pct.26: „persoane afiliate - o persoană
este afiliată dacă relația ei cu altă persoană este definită de cel puțin unul dintre următoarele cazuri [...]”.

Profilul (schemă efemeră din `tenant_template.sql`, ROLLBACK): firma în sistem din 01.10.2026 (CUI 14399840); clientul A (18547290) bifat
„persoană afiliată”, clientul B (24736200) nebifat. CUI-urile: cifra de control verificată cu algoritmul din CLAUDE.md.
"""
from decimal import Decimal

import pytest

from core import db as _db, tenant_provisioning as _tp
from core import clienti_api, facturi_api
from core import tva_incasare as _tvi
from core.common import Perioada

_SCHEMA = "test_lot10_afiliat"
D = Decimal
_A, _B = "18547290", "24736200"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _duk(tip):
    try:
        from core import duk
        return duk if duk.poate_valida(tip) else None
    except Exception:
        return None


def test_motorul_exclude_beneficiarul_afiliat():
    f = {"id": 1, "tip": "factura", "directie": "emisa", "tva": 210, "data_emitere": "2026-10-10"}
    # CF art.282 alin.(6) lit.d): „beneficiarul este o persoană afiliată furnizorului/prestatorului potrivit art. 7 pct. 26”
    assert _tvi.regim_din_date(dict(f, beneficiar_afiliat=True), [21], True) == _tvi.REGIM_GENERAL
    assert _tvi.motiv_excludere(dict(f, beneficiar_afiliat=True), [21]) == "beneficiar afiliat (CF art.282 alin.(6) lit.d)"
    assert _tvi.regim_din_date(f, [21], True) == _tvi.REGIM_INCASARE


def _emite(conn, numar, cui, data="2026-10-10"):
    r = facturi_api.creeaza_factura(conn, numar, data, "emisa",
                                    [{"descriere": "servicii", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21}],
                                    tert_nume="CLIENT %s SRL" % cui, tert_cui="RO" + cui, tert_adresa="Str. Probei 1",
                                    tert_oras="Sector 1", tert_judet="B")
    return r["factura_id"], r["contare"]["inregistrare_id"]


def _linii(conn, iid):
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY id", (iid,))
        return [(d, c, D(s)) for d, c, s in cur.fetchall()]


@pytest.fixture(scope="module")
def prob():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, telefon, banca, iban, regim_fiscal, platitor_tva, "
                    "tip_decont, tva_la_incasare, declarant_nume, declarant_prenume, declarant_functie, cont_venit_implicit, forma_juridica, "
                    "capital_subscris) VALUES (1,'AFILIAT SRL','14399840','Str Test 1','Sector 1','B','6920','0722000000','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'L',true,'Popescu','Ion','ADMINISTRATOR','704','SRL',200)")
                cur.execute("INSERT INTO tva_incasare_perioade (de_la) VALUES ('2026-10-01')")
            ca = clienti_api.creeaza_client(conn, "CLIENT AFILIAT SRL", cui="RO " + _A, afiliat=True)["client_id"]
            clienti_api.creeaza_client(conn, "CLIENT NORMAL SRL", cui=_B)
            ids, note = {}, {}
            ids["FA"], note["FA"] = _emite(conn, "A1", _A)
            ids["FB"], note["FB"] = _emite(conn, "B1", _B)
            yield conn, ids, note, ca
        finally:
            conn.rollback()


pytestmark_db = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytestmark_db
def test_bifa_clientului_se_ingheata_pe_factura(prob):
    conn, ids, note, ca = prob
    with conn.cursor() as cur:
        cur.execute("SELECT id, beneficiar_afiliat FROM facturi ORDER BY id")
        st = dict(cur.fetchall())
    # decizia „Bifă pe client”: clientul A (scris „RO 18547290” pe fișă, „RO18547290” pe factură) e afiliat -> factura îl poartă
    assert st == {ids["FA"]: True, ids["FB"]: False}
    # bifa scoasă mâine nu mută regimul facturii de ieri: faptul e al facturii, la emitere
    clienti_api.actualizeaza_client(conn, ca, afiliat=False)
    with conn.cursor() as cur:
        cur.execute("SELECT beneficiar_afiliat FROM facturi WHERE id = %s", (ids["FA"],))
        assert cur.fetchone()[0] is True
    clienti_api.actualizeaza_client(conn, ca, afiliat=True)
    assert clienti_api.detalii_client(conn, ca)["afiliat"] is True
    with conn.cursor() as cur:
        assert clienti_api.client_afiliat(cur, None, _A) is True and clienti_api.client_afiliat(cur, None, "RO" + _B) is False
        assert clienti_api.client_afiliat(cur, None, "") is False


@pytestmark_db
def test_factura_catre_afiliat_ia_regulile_generale(prob):
    conn, ids, note, ca = prob
    # CF art.282 alin.(6) lit.d): „nu aplică sistemul [...] d) [...] beneficiarul este o persoană afiliată” -> TVA exigibil la emitere, 4427
    assert _linii(conn, note["FA"]) == [("4111", "704", D("1000.00")), ("4111", "4427", D("210.00"))]
    # clientul neafiliat, aceeași firmă în sistem: CF art.282 alin.(3) -> 4428
    assert _linii(conn, note["FB"]) == [("4111", "704", D("1000.00")), ("4111", "4428", D("210.00"))]
    # încasarea facturii către afiliat nu mută nimic (TVA-ul era deja exigibil)
    assert _tvi.linii_la_incasare(conn.cursor(), _SCHEMA, ids["FA"], 1210) == []
    assert _tvi.linii_la_incasare(conn.cursor(), _SCHEMA, ids["FB"], 605) == [("4428", "4427", D("105.00"))]
    # CF art.319 alin.(20) lit.p): mențiunea «TVA la încasare» numai unde exigibilitatea intervine la încasare
    assert facturi_api.detalii_factura(conn, ids["FA"])["tva_la_incasare"] is False
    assert facturi_api.detalii_factura(conn, ids["FB"])["tva_la_incasare"] is True


@pytestmark_db
def test_d300_si_d394_declara_afiliatul_la_emitere(prob):
    conn, ids, note, ca = prob
    from core import d300 as _d300, d394 as _d394
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT da")
        cur.execute("UPDATE inregistrari SET status = 'validata'")
    try:
        prof, fac = _d300.pull(conn, _SCHEMA, Perioada(2026, luna=10))
        res = _d300.calcul_d300(prof, Perioada(2026, luna=10), fac)
        # FA (afiliat): exigibil la emitere -> rd.9 1.000 / 210; FB (în sistem, neîncasată) nu intră la rd.9, rămâne la rd.A (OPANAF 174/2026)
        assert (res.R.get("R9_1"), res.R.get("R9_2")) == (1000, 210), res.R
        assert (res.neexigibil.get("tva_a"), res.neexigibil.get("valoare_a")) == (210, 1000), res.neexigibil
        duk = _duk("d300")
        if duk is not None:
            v = duk.valideaza(_d300.build_xml(res), "d300", an=2026, luna=10, timeout=180)
            assert v.get("stare") == "valid", v
        xml, r394 = _d394.genereaza(conn, _SCHEMA, Perioada(2026, luna=10))
        # OPANAF 2194/2025 pct.5.1: „TVA colectată aferentă facturilor încasate” — nimic încasat; FA nu e o factură în sistem
        assert not r394.informatii.get("tvaCol21"), r394.informatii
        duk = _duk("d394")
        if duk is not None:
            v = duk.valideaza(xml, "d394", an=2026, luna=10, timeout=180)
            assert v.get("stare") == "valid", v
    finally:
        with conn.cursor() as cur:
            cur.execute("ROLLBACK TO SAVEPOINT da")


@pytestmark_db
def test_ecranul_clientilor_vede_si_beneficiarii_fara_fisa(prob):
    conn, ids, note, ca = prob
    with conn.cursor() as cur:
        cur.execute("SAVEPOINT pf")
        cur.execute("DELETE FROM clienti WHERE cui = %s", (_B,))
    try:
        # beneficiarul B al unei facturi emise, fără fișă: apare, ca bifa să se poată pune și pe el
        assert [(p["cui"], p["facturi"]) for p in clienti_api.parteneri_fara_fisa(conn)] == [(_B, 1)]
        # [lotul 11, decizia Costin 10.3] „CUI-ul se păstrează fără «RO» și fără spații”: clientul scris „RO <cod>” e păstrat „<cod>”
        assert {c["cui"]: c["afiliat"] for c in clienti_api.lista_clienti(conn)} == {_A: True}
    finally:
        with conn.cursor() as cur:
            cur.execute("ROLLBACK TO SAVEPOINT pf")
