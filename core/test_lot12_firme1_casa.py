# -*- coding: utf-8 -*-
"""Lotul 12, pachetul firme1 — Casă: 481 (grav), 456 (decizia Costin (a)).

481 (Costin, comanda 12.1): „Casă ← Raport Z: Numerarul din Z nu intră în registrul de casă (grav).” Reparat în lotul 11 (455: registrul
  de casă citește din notele care mișcă 5311 — `casa_sold.note_casa`, sursa unică a soldului), deci și Z-urile scrise înainte (citire, nu
  copie). Testul de aici reface drumul lui Costin: raportul Z cu numerar, apoi registrul de casă al lunii — rândul Z-ului, suma și soldul.
  Temei: OMFP 2634/2015 anexa 2, Registrul de casă (cod 14-4-7A): „Registrul de casă se întocmește zilnic, pe baza documentelor
  justificative de încasări și plăți”; la Chitanță (14-4-1): „În condițiile utilizării aparatelor de marcat electronice fiscale [...]
  documentul în baza căruia se înregistrează în contabilitate veniturile aferente încasărilor zilnice este Raportul fiscal de închidere
  zilnică”.
456 (a) (Costin, răspunsul la §6 al raportului 11.4, verbatim în DECIZII: „456 (a)” — „chitanța se emite și pentru încasarea în numerar fără
  factură (avansul)”): încasarea de la client din Casă fără factură primește și ea chitanța, cu seria firmei și PDF. Temei: OMFP 2634/2015
  anexa 2, Chitanța (cod 14-4-1): „Se întocmește pentru fiecare sumă încasată, de către casierul entității”; seria: anexa 1 pct.24.
Schemă efemeră din template, în tranzacție anulată la ieșire.
"""
import contextlib
import io
import pathlib
from decimal import Decimal

import pytest

from core import casa_api as _ca, db as _db, erori as _erori, tenant_provisioning as _tp

_SCH = "efemer_l12_firme1_casa"
_RAD = pathlib.Path(__file__).resolve().parent.parent
CUI_CLIENT = "55229657"   # FISCALOS ICONTA S.R.L. — cifra de control verificată (algoritmul CUI din CLAUDE.md)


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


def _schema(c, monkeypatch, serie):
    with c.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        cur.execute(_tp.parametrizeaza_template(io.open(_RAD / "tenant_template.sql", encoding="utf-8").read(), _SCH))
        cur.execute("SET LOCAL search_path TO %s, public" % _SCH)
        # CUI 14399840 (DANTE INTERNATIONAL SA) — cifra de control verificată
        cur.execute("""INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,email,telefon,caen,declarant_nume,declarant_prenume,
                       declarant_functie,platitor_tva,activitate_exceptata_amef,serie_chitanta,metoda_stoc)
                       VALUES (1,'F1 SRL','RO14399840','s','B','B','e@x.ro','07','4690','P','I','A',true,false,%s,'global_valoric')""",
                    (serie,))
    proxy = _FaraCommit(c)
    from core import uc_tenants, auth_api, uc_comun as _uc
    monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(proxy))
    monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: _SCH)
    monkeypatch.setattr(_uc, "_schema_sau_404", lambda *a, **k: _SCH)


def _fixture(monkeypatch, serie):
    if not _db_ok():
        pytest.skip("DB indisponibil")
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            _schema(c, monkeypatch, serie)
            yield c
        finally:
            c.rollback()


@pytest.fixture
def conn(monkeypatch):
    yield from _fixture(monkeypatch, "CHF1")


@pytest.fixture
def conn_fara_serie(monkeypatch):
    yield from _fixture(monkeypatch, None)


def _chitante(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT serie, numar, data::text, factura_id, client_nume, client_cui, suma, reprezentand, casa_operatiune_id, "
                    "inregistrare_id, anulata FROM chitante ORDER BY id")
        return cur.fetchall()


# ── 481 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_481_numerarul_din_z_intra_in_registrul_de_casa(conn):
    """Raportul Z din 20.10.2026: 131,00 lei (11%), din care numerar 100,00 și card 31,00. Registrul de casă din octombrie: rândul Z-ului,
    încasare de 100,00 lei (numai numerarul — cardul ajunge la bancă), soldul 100,00. Apoi o depunere de 40 lei la bancă: soldul 60,00."""
    from core import uc_tenants

    class _Z:
        data, nui, nr_raport, nr_bonuri, total_11, total_21, numerar, card = "2026-10-20", "8000000481", "0481", 7, 131.0, 0.0, 100.0, 31.0
    r = uc_tenants.horeca_raport_z(1, _Z(), {"uid": 1})
    assert r["ok"] and [(x["debit"], x["credit"], x["suma"]) for x in r["linii"]] == [
        ("5311", "707", "100.00"), ("5125", "707", "31.00"), ("707", "4427", "12.98")], r
    reg = _ca.registru(conn, _SCH, 2026, 10)
    (rz,) = reg["operatiuni"]
    assert (rz["data"], rz["tip"], rz["suma"], rz["sold"], rz["alt_modul"], rz["document"]) == (
        "2026-10-20", "incasare", "100.00", "100.00", True, "Raport Z nr 0481 din 20.10.2026 (casa 8000000481)"), rz
    assert (reg["sold_initial"], reg["sold_final"]) == ("0", "100.00"), reg
    rd = _ca.adauga(conn, _SCH, {"data": "2026-10-21", "categorie": "depunere_banca", "suma": "40"})
    assert "eroare" not in rd, rd
    reg = _ca.registru(conn, _SCH, 2026, 10)
    assert [(o["suma"], o["sold"]) for o in reg["operatiuni"]] == [("100.00", "100.00"), ("40.00", "60.00")], reg["operatiuni"]


# ── 456 (a) ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_456_avansul_de_la_client_in_numerar_primeste_chitanta_cu_seria_firmei(conn):
    """Încasare de 300 lei de la FISCALOS fără factură (avans): chitanța CHF1 nr. 1, cu data operațiunii, clientul din dispoziție și
    „avans de la client”, legată de operațiune și de notă; documentul operațiunii devine numărul ei; registrul nu mai spune „fără
    chitanță”; PDF-ul se generează."""
    from core import uc_tenants
    r = uc_tenants.casa_adauga(1, {"data": "2026-10-22", "categorie": "incasare_client", "suma": "300", "avans": True,
                                   "partener": "FISCALOS ICONTA S.R.L.", "cui": CUI_CLIENT, "facturi": []}, {"uid": 1})
    (op,) = r["operatiuni"]
    assert [(c["serie"], c["numar"], c["factura_id"], c["operatiune_id"]) for c in r["chitante"]] == [("CHF1", 1, None, op["id"])], r
    assert _chitante(conn) == [("CHF1", 1, "2026-10-22", None, "FISCALOS ICONTA S.R.L.", CUI_CLIENT, Decimal("300.00"),
                                "avans de la client", op["id"], op["inregistrare_id"], False)]
    (rand,) = _ca.registru(conn, _SCH, 2026, 10)["operatiuni"]
    assert (rand["chitanta_id"], rand["fara_chitanta"], rand["document"]) == (r["chitante"][0]["chitanta_id"], False, "CHF1-1"), rand
    pdf, _r = uc_tenants.chitanta_pdf(1, r["chitante"][0]["chitanta_id"], {"uid": 1})
    assert pdf[:5] == b"%PDF-" and len(pdf) > 1000


def test_456_incasarea_facturii_cu_avans_peste_ea_doua_chitante(conn):
    """Factura F1A nr. 12 de 64,46 lei încasată cu 100 lei: partea pe factură și avansul (35,54) — câte o chitanță pe fiecare sumă încasată
    (OMFP 2634/2015, 14-4-1), numerotate în serie."""
    from core import uc_tenants
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (serie, numar, data_emitere, directie, total, tva, tert_nume, tert_cui, status, tip_operatiune) "
                    "VALUES ('F1A', 'F1A12', '2026-10-20', 'emisa', 64.46, 0, 'FISCALOS ICONTA S.R.L.', %s, 'emisa', 'normal') RETURNING id",
                    (CUI_CLIENT,))
        fid = cur.fetchone()[0]
    r = uc_tenants.casa_adauga(1, {"data": "2026-10-22", "categorie": "incasare_client", "suma": "100", "partener": "FISCALOS ICONTA S.R.L.",
                                   "cui": CUI_CLIENT, "facturi": [{"factura_id": fid, "suma": "64.46"}]}, {"uid": 1})
    assert [(c["serie"], c["numar"], c["factura_id"]) for c in r["chitante"]] == [("CHF1", 1, fid), ("CHF1", 2, None)], r
    assert [(x[6], x[7]) for x in _chitante(conn)] == [(Decimal("64.46"), "contravaloare factura F1A nr. 12 din 20.10.2026"),
                                                       (Decimal("35.54"), "avans de la client")]


def test_456_fara_serie_avansul_e_refuzat_numit_si_nimic_scris(conn_fara_serie):
    from core import uc_tenants
    with pytest.raises(_erori.CerereGresita) as e:
        uc_tenants.casa_adauga(1, {"data": "2026-10-22", "categorie": "incasare_client", "suma": "300", "avans": True,
                                   "partener": "FISCALOS ICONTA S.R.L.", "cui": CUI_CLIENT, "facturi": []}, {"uid": 1})
    refuz = e.value.args[0]
    # refuzul seriei (codul, ecranul Date firmă), pe ramura încasării FĂRĂ factură: prefixul avansului, nu cel al facturii
    assert (refuz["cod"], refuz["ecran"]) == (uc_tenants.COD_SERIE_CHITANTA_LIPSA, "date_firma"), refuz
    assert refuz["mesaj"] == uc_tenants.PREFIX_AVANS_FARA_SERIE + uc_tenants.MESAJ_SERIE_CHITANTA_LIPSA, refuz["mesaj"]
    with conn_fara_serie.cursor() as cur:
        cur.execute("SELECT count(*) FROM casa_operatiuni")
        assert cur.fetchone()[0] == 0
