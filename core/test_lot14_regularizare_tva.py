# -*- coding: utf-8 -*-
"""[lotul 14, deficiența 688] Închiderea lunii nu închidea TVA-ul (comanda Costin 14.1, verbatim): „F1 09/2026 e blocată cu «Nimic nu oprește
închiderea», dar balanța lunii are 4426 sold final D 210,00 și 4427 sold final C 210,00, fără 4423/4424; în octombrie soldurile se cumulează
(4426 210,00, 4427 1.696,18). La plătitorii de TVA, închiderea trebuie să propună nota 4427 = 4426 + 4423/4424 pe perioada fiscală a firmei
(lunar sau trimestrial) și să refuze blocarea cât 4426/4427 au sold.”

TEMEI: OMFP 1802/2014, funcțiunea conturilor 4423 / 4424 / 4426 / 4427 (`motor.TEMEI_REGULARIZARE_TVA`). Schemă efemeră din
`tenant_template.sql`, ROLLBACK. Lunile de probă sunt încheiate (09/2026 și mai vechi): controlul „luna în curs” nu intervine.
MUTAȚII (scrise în docstringul fiecărui test): blocajul scos din `uc_comun.controale_inchidere`; sfârșitul de perioadă ignorat; validarea
unei note depășite permisă.
"""
import contextlib
import datetime
from decimal import Decimal as D

import pytest
from psycopg2.extras import RealDictCursor

from core import db as _db, inchidere_an as ia, jurnal_api, tenant_provisioning as _tp, uc_comun, uc_tenants

_SCHEMA = "ztest_lot14_regtva"


@pytest.fixture
def firma():
    """Firmă plătitoare de TVA, lunară; se schimbă din test (`UPDATE firma_profil`)."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as c:
                c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                c.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                c.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                c.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, tip_decont, regim_fiscal) "
                          "VALUES (1, 'PROBA TVA SRL', '14399840', true, 'L', 'micro') ON CONFLICT (id) DO NOTHING")
                c.execute("UPDATE firma_profil SET data_infiintare = '2025-01-10', platitor_tva = true, tip_decont = 'L' WHERE id = 1")
                yield conn, c
        finally:
            conn.rollback()


def _nota(c, zi, debit, credit, suma, status="validata"):
    c.execute("INSERT INTO inregistrari (data, status, sursa, descriere, document_ref) VALUES (%s, %s, 'manual', 'Probă', 'NC T14') RETURNING id",
              (zi, status))
    nid = c.fetchone()["id"]
    c.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)", (nid, debit, credit, suma))
    return nid


def _septembrie(c, deductibil=210, colectat=210):
    """F1 09/2026: TVA deductibilă 210 (factura furnizorului) și colectată (vânzare) — fără nicio regularizare."""
    _nota(c, datetime.date(2026, 9, 10), "4426", "401", D(deductibil))
    _nota(c, datetime.date(2026, 9, 20), "4111", "4427", D(colectat))


def _blocaje(conn, luna, an=2026):
    return {b["cod"]: b for b in uc_comun.controale_inchidere(conn, _SCHEMA, an, luna)["blocaje"]}


def test_luna_cu_4426_si_4427_cu_sold_nu_se_poate_inchide_si_aplicatia_propune_nota(firma):
    """688 — pe datele din comandă (4426 D 210, 4427 C 210 la 30.09.2026), închiderea lui 09/2026 e OPRITĂ de TVA-ul neregularizat, cu
    sumele în text; propunerea scrie ciorna `4427 = 4426` 210 (fără 4423 / 4424, diferența e zero), datată 30.09, sursa `regularizare_tva`;
    până la validare blocajul rămâne („de validat”); după validare luna se închide fără el, iar în octombrie soldurile nu se mai cumulează.
    MUTAȚIE: blocajul `TVA_NEREGULARIZAT` scos din `controale_inchidere` -> prima aserțiune pică."""
    conn, c = firma
    _septembrie(c)
    b = _blocaje(conn, 9)
    assert {"TVA_NEREGULARIZAT"} <= set(b), sorted(b)
    assert b["TVA_NEREGULARIZAT"]["mesaj"].count("210,00 lei") == 2 and not b["TVA_NEREGULARIZAT"]["de_validat"], b["TVA_NEREGULARIZAT"]   # sumele din text: cele două solduri
    r = ia.propune_tva_luna(c, _SCHEMA, 2026, 9)
    assert [(n["descriere"], n["linii"]) for n in r["note"]] == [("Regularizarea TVA la 30.09.2026", [("4427", "4426", "210.00")])], r
    c.execute("SELECT status, sursa, data FROM inregistrari WHERE id = %s", (r["note"][0]["id"],))
    assert tuple(c.fetchone().values()) == ("ciorna", "regularizare_tva", datetime.date(2026, 9, 30))
    b = _blocaje(conn, 9)
    assert b["TVA_NEREGULARIZAT"]["de_validat"] is True and {"CIORNE"} <= set(b), sorted(b)     # propusă, încă nevalidată
    assert jurnal_api.valideaza(conn, _SCHEMA, r["note"][0]["id"]) == {"ok": True}
    assert {"TVA_NEREGULARIZAT", "CIORNE"}.isdisjoint(_blocaje(conn, 9))
    assert ia.tva_de_regularizat(c, _SCHEMA, 2026, 10) is None            # octombrie pornește de la zero, nu cumulat


def test_diferenta_merge_in_4423_sau_4424(firma):
    """Colectată mai mare -> `4427 = 4426` și `4427 = 4423` (de plată); deductibilă mai mare -> `4427 = 4426` și `4424 = 4426` (de recuperat).
    Textul blocajului spune în care. MUTAȚIE: latura diferenței inversată în `motor.regularizare_tva` -> pică."""
    conn, c = firma
    _septembrie(c, deductibil=210, colectat=1050)
    r = ia.propune_tva_luna(c, _SCHEMA, 2026, 9)
    assert r["note"][0]["linii"] == [("4427", "4426", "210.00"), ("4427", "4423", "840.00")], r
    assert {"TVA_NEREGULARIZAT"} <= set(_blocaje(conn, 9))      # blocajul rămâne cât nota propusă nu e validată
    c.execute("DELETE FROM inregistrari")
    _septembrie(c, deductibil=500, colectat=200)
    r = ia.propune_tva_luna(c, _SCHEMA, 2026, 9)
    assert r["note"][0]["linii"] == [("4427", "4426", "200.00"), ("4424", "4426", "300.00")], r


def test_trimestrial_regularizeaza_numai_la_sfarsitul_trimestrului(firma):
    """Firma trimestrială: lunile 7 și 8 nu cer regularizare (soldurile se acumulează în trimestru), luna 9 da; propunerea pe luna 8 se
    refuză cu motivul. MUTAȚIE: `sfarsit_de_perioada_tva` care ignoră tipul perioadei -> luna 8 ar fi oprită -> pică."""
    conn, c = firma
    c.execute("UPDATE firma_profil SET tip_decont = 'T' WHERE id = 1")
    _nota(c, datetime.date(2026, 7, 10), "4426", "401", D(100))
    _nota(c, datetime.date(2026, 8, 10), "4111", "4427", D(300))
    assert {"TVA_NEREGULARIZAT"}.isdisjoint(_blocaje(conn, 7)) and {"TVA_NEREGULARIZAT"}.isdisjoint(_blocaje(conn, 8))
    with pytest.raises(ValueError, match="nu încheie o perioadă fiscală"):
        ia.propune_tva_luna(c, _SCHEMA, 2026, 8)
    assert {"TVA_NEREGULARIZAT"} <= set(_blocaje(conn, 9))
    r = ia.propune_tva_luna(c, _SCHEMA, 2026, 9)
    assert r["note"][0]["linii"] == [("4427", "4426", "100.00"), ("4427", "4423", "200.00")], r


def test_firma_neplatitoare_si_luna_fara_sold_nu_au_blocaj(firma):
    """Neplătitoarea de TVA nu are regularizare; plătitoarea fără sold pe 4426 / 4427 (decont nul) nici. MUTAȚIE: `platitor_tva` ignorat -> pică."""
    conn, c = firma
    _septembrie(c)
    c.execute("UPDATE firma_profil SET platitor_tva = false WHERE id = 1")
    assert {"TVA_NEREGULARIZAT"}.isdisjoint(_blocaje(conn, 9))
    c.execute("UPDATE firma_profil SET platitor_tva = true WHERE id = 1")
    c.execute("DELETE FROM inregistrari")
    _nota(c, datetime.date(2026, 9, 10), "5121", "707", D(100))
    assert {"TVA_NEREGULARIZAT"}.isdisjoint(_blocaje(conn, 9))


def test_nota_depasita_nu_se_valideaza(firma):
    """O operațiune validată după propunere schimbă soldurile 4426 / 4427: nota propusă nu mai e regularizarea lor și validarea ei e
    REFUZATĂ (cod REGULARIZARE_TVA_NEVALIDABILA); o nouă propunere o înlocuiește. MUTAȚIE: apelul `refuz_validare_tva_luna` scos din
    `jurnal_api.valideaza` -> nota depășită se validează -> pică."""
    conn, c = firma
    _septembrie(c)
    n1 = ia.propune_tva_luna(c, _SCHEMA, 2026, 9)["note"][0]["id"]
    _nota(c, datetime.date(2026, 9, 25), "4111", "4427", D(21))
    rez = jurnal_api.valideaza(conn, _SCHEMA, n1)
    assert rez.get("cod") == "REGULARIZARE_TVA_NEVALIDABILA", rez
    r2 = ia.propune_tva_luna(c, _SCHEMA, 2026, 9)
    assert r2["inlocuite"] == [n1] and r2["note"][0]["linii"] == [("4427", "4426", "210.00"), ("4427", "4423", "21.00")], r2
    assert jurnal_api.valideaza(conn, _SCHEMA, r2["note"][0]["id"]) == {"ok": True}


class _FaraCommit:
    """Conexiunea fixturii, cu `commit` fără efect: use-case-ul ei face commit, iar schema fixturii trăiește numai în tranzacția ei (rollback)."""

    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, nume):
        return getattr(self._conn, nume)

    def commit(self):
        pass


def test_ruta_propunerii_intoarce_nota_propusa_si_apare_in_blocaj(firma, monkeypatch):
    """688, ruta `POST /tenants/{id}/inchidere/regularizare-tva` (`uc_tenants.tenant_regularizare_tva_luna`): propune ciorna și o întoarce cu
    liniile ei; o a doua apăsare o înlocuiește (nu o dublează). MUTAȚIE: `propune_tva_luna` scos din use-case -> pică."""
    conn, c = firma
    _septembrie(c)
    monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_FaraCommit(conn)))
    monkeypatch.setattr(uc_tenants.auth_api, "schema_tenant", lambda *a, **k: _SCHEMA)
    r = uc_tenants.tenant_regularizare_tva_luna(1, 2026, 9, {"uid": 1})
    assert r["ok"] and r["nimic"] is False, r
    assert [n["linii"] for n in r["note"]] == [[{"debit": "4427", "credit": "4426", "suma": "210.00"}]], r["note"]
    r2 = uc_tenants.tenant_regularizare_tva_luna(1, 2026, 9, {"uid": 1})
    assert len(r2["note"]) == 1 and r2["inlocuite"], r2

