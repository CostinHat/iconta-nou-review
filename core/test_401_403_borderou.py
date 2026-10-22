# -*- coding: utf-8 -*-
"""[deficiențele 401, 402, 403 — retestul Costin 19.10.2026]
  401 „Achiziție de la PF (BA-1, Ion Popescu): apare «Factură» în jurnal și Istoric facturi; e borderou de achiziție; după generare nu se
      arată nota.”
  402 „Achiziție PF: cont de stoc (371/301) acceptat fără articol și cantitate (371 crește, stocul nu); furnizorul doar nume, fără datele
      de identificare cerute pe borderou.”
  403 „Fișa de magazie: documente «Factura #1», «Factura #48», «factură primită #2» (id intern) — toate cu serie, număr, dată.”
Temei: OMFP 2634/2015 anexa 2, „Borderou de achiziție (cod 14-4-13)”: „document de înregistrare în gestiune a bunurilor cumpărate de la
persoane fizice; document justificativ de înregistrare în contabilitate a valorii bunurilor cumpărate”; anexa 1 pct.2 („menționarea
părților care participă la efectuarea operațiunii”) și pct.6 („pot fi înregistrate în contabilitate numai în cazul în care se face dovada
intrării în gestiune a bunurilor respective”). Schemă efemeră din template, în tranzacție anulată."""
import contextlib
import io
from decimal import Decimal

import pytest

from core import db as _db, erori, tenant_provisioning as _tp

SCH = "tenant_test_401_borderou"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _P:
    def __init__(s, c): s._c = c
    def commit(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


@pytest.fixture
def conn(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
                cur.execute("SET search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                            "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")
            from core import auth_api, uc_comun, uc_tenants
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_P(c)))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
            monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
            yield c
        finally:
            c.rollback()


_PF = {"data": "2026-10-19", "furnizor_nume": "Ion Popescu", "furnizor_adresa": "Str. Florilor 1, Ploiești", "furnizor_act": "PH 123456",
       "valoare": 200, "cont_cheltuiala": "371", "articol": "Mere", "cantitate": 100, "um": "kg",
       "articol_nou": True}   # [lotul 11, 450] articolul nou, cerut explicit


def _borderou(corp):
    from core import uc_tenants
    return uc_tenants.achizitie_neinregistrat(1, dict(corp), {"uid": 1})


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def test_402_vanzatorul_se_identifica_si_stocul_cere_articolul(conn):
    with pytest.raises(erori.DateInvalide) as e:
        _borderou({**_PF, "furnizor_adresa": "", "furnizor_act": ""})
    assert [x["camp"] for x in e.value.args[0]["erori_campuri"]] == ["op-furnizor_adresa", "op-furnizor_act"], e.value.args
    with pytest.raises(erori.DateInvalide) as e:
        _borderou({**_PF, "articol": "", "cantitate": ""})
    assert [x["camp"] for x in e.value.args[0]["erori_campuri"]] == ["op-articol", "op-cantitate"], e.value.args


def test_401_402_borderoul_e_document_propriu_si_aduce_marfa_in_gestiune(conn):
    r = _borderou(_PF)
    _i = r["intrare_stoc"]   # [lotul 11, 450] și articolul (id-ul lui) și faptul că a fost creat la cererea explicită
    assert (r["numar"], r["nota"], _i["articol"], _i["cantitate"], _i["articol_nou"], bool(_i["articol_id"])) == \
        ("BA-1", "371 = 401 200,00 lei", "Mere", "100", True, True), r
    with conn.cursor() as cur:
        cur.execute("SELECT tip, directie, tert_nume, tert_adresa, tert_act_identitate FROM facturi WHERE id = %s", (r["factura_id"],))
        assert cur.fetchone() == ("borderou", "primita", "Ion Popescu", "Str. Florilor 1, Ploiești", "PH 123456")
        cur.execute("SELECT a.denumire, a.um, m.cantitate, m.valoare, m.document FROM miscari_stoc m JOIN articole a ON a.id = m.articol_id")
        assert cur.fetchone() == ("Mere", "kg", Decimal("100.000"), Decimal("200.00"), "Borderou de achiziție BA-1 din 19.10.2026")
    from core import jurnal_api
    assert jurnal_api.eticheta_factura("borderou", None, "BA-1", "2026-10-19") == "Borderou de achiziție BA-1 din 19.10.2026"


def test_401_pe_cont_de_cheltuiala_nu_cere_articol(conn):
    r = _borderou({**_PF, "cont_cheltuiala": "6028", "articol": "", "cantitate": ""})
    assert r["intrare_stoc"] is None and r["nota"] == "6028 = 401 200,00 lei", r


def test_403_fisa_numeste_documentul_vechi_din_factura_legata(conn):
    from core import stocuri_cv_api as cv
    art = cv.intrare(conn, SCH, {"denumire": "Marfa A", "um": "buc", "data": "2026-10-01", "cantitate": 5, "pret_unitar": 10})
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, total, tva, tip) VALUES ('F1A1', 'F1A', '2026-10-02', "
                    "'emisa', 24.2, 4.2, 'factura') RETURNING id")
        fid = cur.fetchone()[0]
        # textul scris de versiunile de dinainte de 258 (15.10.2026): id-ul intern
        cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, valoare, document, factura_id) "
                    "VALUES (%s, '2026-10-02', 'iesire', 1, 10, 'Factura #1', %s)", (art["articol_id"], fid))
    f = cv.fisa(conn, SCH, art["articol_id"])
    assert [l["document"] for l in f["linii"]] == [None, "Factură F1A nr. 1 din 02.10.2026"], f["linii"]   # [lotul 11, 443] seria separat
