# -*- coding: utf-8 -*-
"""GARD — factura emisă pe baza bonului fiscal se numără O SINGURĂ DATĂ (decizia Costin A, 02.10.2026).

Defectul (verificat în cod înainte de reparație): factura nu avea nicio legătură cu bonul. O vânzare pe bon, deja în
raportul Z, apoi facturată la cererea clientului, intra de două ori în D300 rd.9/10 (facturile + Z), de două ori în D394
(op1 cu partener — corect — și op2 Î1 — greșit), de două ori în evidență (nota automată `4111 = 707 + 4427` peste nota
Z) și putea descărca stocul a doua oară.

Temei: HG 1/2016 pct.97 alin.(1): „Pe facturile emise și achitate pe bază de bonuri fiscale … fiind suficientă mențiunea
«conform bon fiscal nr./data»”; HG 479/2003 anexa art.2 (factura „la data eliberării bonului fiscal”); OPANAF 2194/2025
anexa D394 lit.G (Î1 „cu excepția celor pentru care s-au emis facturi”). Probele trec prin CODUL REAL al rutelor, pe o
schemă efemeră, în tranzacție anulată.
"""
import contextlib
import glob
import os
import xml.etree.ElementTree as ET

import pytest

from core import d300 as _d300
from core import d394 as _d394
from core import db as _db
from core import facturi as _fc
from core import tenant_provisioning as _tp
from core.common import Perioada

_SCHEMA = "tenant_test_bon_factura"
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


class _Z:   # raportul Z al zilei: 1210 lei la 21% (TVA 210), 160 bonuri
    data = "2026-06-10"
    nui = "8000000101"
    nr_raport = "0031"
    nr_bonuri = 160
    total_11 = 0.0
    total_21 = 1210.0
    numerar = 1210.0
    card = 0.0


_LINIE = {"descriere": "Meniu zilei", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21, "um": "buc", "cont_venit": "707"}


@pytest.fixture
def conn_b(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, telefon, banca, iban, "
                    "regim_fiscal, platitor_tva, tip_decont, tva_la_incasare,declarant_nume,declarant_prenume,declarant_functie) "
                    "VALUES (1,'HORECA SRL','14399840','Str Test 1','Bucuresti','B','5610','0722000000','BCR',"
                    "'RO49AAAA1B31007593840000','real',true,'L',false,'Popescu','Ion','ADMINISTRATOR')")
            proxy = _FaraCommit(conn)
            from core import uc_tenants, auth_api, uc_comun as _uc
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: _SCHEMA)
            monkeypatch.setattr(_uc, "_cere_luna_deschisa", lambda *a, **k: None)
            monkeypatch.setattr(_uc, "_schema_sau_404", lambda *a, **k: _SCHEMA)
            yield conn
        finally:
            conn.rollback()


def _factura(conn, numar, **marca):
    from core import facturi_api
    r = facturi_api.creeaza_factura(conn, numar, "2026-06-10", "emisa", [dict(_LINIE)], tert_nume="CLIENT SRL",
                                    tert_cui="RO14399840", status="emisa", **marca)
    with conn.cursor() as cur:   # notele automate intră ciornă; contabilul le validează
        cur.execute("UPDATE inregistrari SET status='validata' WHERE factura_id=%s", (r["factura_id"],))
    return r


def _z_validat():
    from core import uc_tenants
    uc_tenants.horeca_raport_z(1, _Z(), {"uid": 1})


# ── emiterea ───────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_marca_cere_numarul_si_data_doar_pe_factura_emisa(conn_b):
    from core import facturi_api
    # HG 1/2016 pct.97 alin.(1): „conform bon fiscal nr./data” — amândouă
    with pytest.raises(ValueError):
        facturi_api.creeaza_factura(conn_b, "B1", "2026-06-10", "emisa", [dict(_LINIE)], tert_nume="C", tert_pf=True,
                                    bon_fiscal_nr="0042")
    with pytest.raises(ValueError):   # bonul nu poate fi după factură (HG 479/2003 anexa art.2)
        facturi_api.creeaza_factura(conn_b, "B2", "2026-06-10", "emisa", [dict(_LINIE)], tert_nume="C", tert_pf=True,
                                    bon_fiscal_nr="0042", bon_fiscal_data="2026-06-11")
    with pytest.raises(ValueError):   # o factură PRIMITĂ nu se marchează
        facturi_api.creeaza_factura(conn_b, "B3", "2026-06-10", "primita", [dict(_LINIE)], tert_nume="F",
                                    tert_cui="RO14399840", bon_fiscal_nr="0042", bon_fiscal_data="2026-06-10")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_din_bon_nu_primeste_nota_de_vanzare(conn_b):
    # vânzarea e în nota Z; MUTAȚIE: fără refuzul EMISA_DIN_BON în contabilizeaza -> 4111 = 707 + 4427 a doua oară -> pică
    r = _factura(conn_b, "B10", bon_fiscal_nr="0042", bon_fiscal_data="2026-06-10")
    assert r["contare"]["stare"] == "neaplicabil"
    with conn_b.cursor() as cur:
        cur.execute("SELECT count(*) FROM inregistrari WHERE factura_id=%s", (r["factura_id"],))
        assert cur.fetchone()[0] == 0


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_storno_ul_mosteneste_marca(conn_b):
    from core import facturi_api
    r = _factura(conn_b, "B11", bon_fiscal_nr="0042", bon_fiscal_data="2026-06-10")
    s = facturi_api.storneaza(conn_b, r["factura_id"])
    d = facturi_api.detalii_factura(conn_b, s["factura_id"])
    assert (d["bon_fiscal_nr"], str(d["bon_fiscal_data"])) == ("0042", "2026-06-10") and _fc.e_din_bon_fiscal(d)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_factura_din_bon_nu_descarca_stocul(conn_b):
    from core import uc_tenants, erori
    from types import SimpleNamespace as NS
    date = NS(moneda="RON", data_emitere="2026-06-10", data_scadenta=None, tert_nume="CLIENT SRL", tert_cui="RO14399840",
              tert_adresa=None, client_id=None, curs_manual=None, tip="factura", tert_tara="RO", tip_operatiune="normal",
              data_curs_manual=None, pleaca_marfa=True, bon_fiscal_nr="0042", bon_fiscal_data="2026-06-10",
              linii=[NS(model_dump=lambda: dict(_LINIE, articol_id=1))])
    with pytest.raises(erori.DateInvalide):   # marfa a ieșit cu bonul: a doua descărcare e refuzată
        uc_tenants.facturi_emite(1, date, {"uid": 1})


# ── D300 și D394 ────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_numara_vanzarea_o_singura_data(conn_b):
    # Z: baza 1000 / TVA 210; factură din bon 100 / 21 + o factură obișnuită 100 / 21
    # MUTAȚIE: fără excluderea din repo_d300 -> 1200 / 252 -> pică (și calea a doua o blochează)
    _z_validat()
    _factura(conn_b, "B20", bon_fiscal_nr="0042", bon_fiscal_data="2026-06-10")
    _factura(conn_b, "B21")
    _xml, res = _d300.genereaza(conn_b, _SCHEMA, Perioada(2026, luna=6))
    assert (res.R.get("R9_1"), res.R.get("R9_2")) == (1100, 231)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d394_factura_in_op1_iar_op2_fara_suma_ei(conn_b):
    # OPANAF 2194/2025 lit.G: Î1 „cu excepția celor pentru care s-au emis facturi” — total 1210 - 121 = 1089;
    # factura rămâne în op1 (partener cu CUI). MUTAȚIE: fără scăderea din _op2_din_rapoarte_z -> total 1210 -> pică
    _z_validat()
    _factura(conn_b, "B30", bon_fiscal_nr="0042", bon_fiscal_data="2026-06-10")
    xml, res = _d394.genereaza(conn_b, _SCHEMA, Perioada(2026, luna=6))
    rad = ET.fromstring(xml.split("?>", 1)[1])
    ns = rad.tag.split("}")[0] + "}"
    (o2,) = [dict(e.attrib) for e in rad.iter(ns + "op2")]
    op1 = [dict(e.attrib) for e in rad.iter(ns + "op1")]
    assert (o2["total"], o2["baza21"], o2["TVA21"], o2["nrBF"]) == ("1089", "900", "189", "160")
    assert [(o["tip"], o["baza"], o["tva"]) for o in op1] == [("L", "100", "21")]
    try:
        from core import duk
        if duk.poate_valida("d394"):
            v = duk.valideaza(xml, "d394", an=2026, luna=6, timeout=180)
            assert v.get("stare") == "valid", v.get("erori")
    except ImportError:
        pass


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d394_factura_din_bon_fara_raport_z_e_refuzata_numit(conn_b):
    # o factură care declară un bon dintr-o lună fără raport Z nu are din ce se scădea: refuz numit, nu op2 negativ
    _factura(conn_b, "B40", bon_fiscal_nr="0042", bon_fiscal_data="2026-06-10")
    with pytest.raises(ValueError) as e:
        _d394.genereaza(conn_b, _SCHEMA, Perioada(2026, luna=6))
    assert (e.value.cod, e.value.rapoarte) == ("D394_Z_INCOMPLET", ["B40"])


def test_pdf_poarta_mentiunea_bonului(monkeypatch):
    from core import factura_pdf
    texte, Orig = [], factura_pdf.Paragraph

    def P(text, *a, **k):
        texte.append(text)
        return Orig(text, *a, **k)
    monkeypatch.setattr(factura_pdf, "Paragraph", P)
    f = {"numar": "B50", "directie": "emisa", "data_emitere": "2026-06-10", "moneda": "RON", "tert_nume": "CLIENT SRL",
         "total": 121, "tva": 21, "bon_fiscal_nr": "0042", "bon_fiscal_data": "2026-06-10",
         "linii": [{"descriere": "Meniu", "cantitate": 1, "um": "buc", "pret_unitar": 100, "cota_tva": 21}]}
    factura_pdf.genereaza_pdf({"nume": "HORECA SRL", "cui": "14399840", "platitor_tva": True}, f)
    # HG 1/2016 pct.97 alin.(1): mențiunea „conform bon fiscal nr./data”
    assert texte.count(_fc.mentiune_bon(f)) == 1 and _fc.mentiune_bon(f) == "conform bon fiscal nr. 0042/10.06.2026"


def test_definitia_sta_intr_un_singur_loc():
    # sursa unică (decizia A): predicatul „factură din bon” se scrie doar în core/facturi.py; ceilalți îl importă
    gasite = []
    for f in glob.glob(os.path.join(_RAD, "core", "*.py")) + glob.glob(os.path.join(_RAD, "*.py")):
        if os.path.basename(f) in ("facturi.py", "test_factura_bon_fiscal.py") or os.path.basename(f).startswith("migrare_"):
            continue
        t = open(f, encoding="utf-8").read()
        if t.count("bon_fiscal_nr IS NULL") + t.count("bon_fiscal_nr IS NOT NULL") + t.count("bon_fiscal_nr is None"):
            gasite.append(os.path.basename(f))
    assert gasite == []
