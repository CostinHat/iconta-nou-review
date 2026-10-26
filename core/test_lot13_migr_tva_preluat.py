# -*- coding: utf-8 -*-
"""[lotul 13, deficiența 252, decizia Costin 13.1, verbatim: „252: la facturile preluate, dacă fișierul are suma TVA, se ia suma din fișier;
doar unde lipsește se calculează la cota standard, iar factura e marcată «de verificat».”] Migrarea `core/migrare_coloana_tva_preluat.py`
(coloana `facturi.tva_de_verificat` și datele existente) și scrierea marcajului la import.

CE FACE IMPOSIBIL: (a) șablonul firmelor noi fără coloana migrării (blocul din tenant_template.sql = `bloc_template()`); (b) o factură
preluată cu TVA neexigibil, scrisă înainte de reparație (TVA-ul era mereu calculat), rămasă nemarcată după migrare; (c) o factură preluată
fără TVA (regulile generale) marcată fără motiv; (d) migrarea care nu e idempotentă. Schemă efemeră din șablon, tranzacție anulată.
TEMEI: CF art.282 alin.(3), (8) (TVA-ul neexigibil al facturii preluate devine exigibil la încasare) — citat în
`core/test_lot12_migr3_tva_incasare.py`; marcajul: decizia Costin 13.1 (de produs).
"""
import os

import pytest

from core import db as _db, migrare_coloana_tva_preluat as mig, migrari_registru, solduri_parteneri_api as sp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot13_migr_tva"


def _sablon():
    return open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()


def test_sablonul_are_blocul_migrarii_si_migrarea_e_a_registrului():
    assert mig.bloc_template() in _sablon(), "tenant_template.sql n-are blocul `migrare_coloana_tva_preluat.bloc_template()`"
    cale = "core/migrare_coloana_tva_preluat.py"
    assert migrari_registru.e_migrare(cale, open(os.path.join(RAD, cale), encoding="utf-8").read())
    # rulează înaintea lui `migrare_documente_preluate` (aceea scrie coloana): ordinea alfabetică a rulatorului
    assert "core/migrare_coloana_tva_preluat.py" < "core/migrare_documente_preluate.py"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    from core import tenant_provisioning as _tp
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(_sablon(), SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
            yield c
        finally:
            c.rollback()


def test_migrarea_marcheaza_facturile_preluate_cu_tva_si_numai_pe_ele(conn):
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE facturi DROP COLUMN tva_de_verificat")   # schema de dinainte de migrare
        for nr, tva in (("Sold la 31.08.2026", 210), ("FA-2", 0)):
            cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, moneda, directie, status, tert_nume, tert_cui, tip, total_lei, "
                        "tva_lei, sursa_externa) VALUES (%s, '2026-08-31', 1210, %s, 'RON', 'emisa', 'importata', 'ALFA', '14399840', "
                        "'preluata', 1210, %s, 'preluare')", (nr, tva, tva))
    assert mig.aplica(conn, SCHEMA) == 1
    assert mig.verifica(conn, SCHEMA)
    with conn.cursor() as cur:
        cur.execute("SELECT numar, tva_de_verificat FROM facturi ORDER BY numar")
        assert cur.fetchall() == [("FA-2", False), ("Sold la 31.08.2026", True)]
    assert mig.aplica(conn, SCHEMA) == 0                                   # idempotentă


def test_importul_scrie_marcajul_numai_pe_tva_ul_calculat(conn):
    docs = [{"numar": "FB-1", "data": "2026-09-10", "scadenta": None, "suma": 1090, "tva": 90, "directie": "emisa", "tert_nume": "BETA",
             "tert_cui": "14399840", "tva_de_verificat": False},
            {"numar": "FB-2", "data": "2026-09-15", "scadenta": None, "suma": 1210, "tva": 210, "directie": "emisa", "tert_nume": "BETA",
             "tert_cui": "14399840", "tva_de_verificat": True}]
    with conn.cursor() as cur:
        sp._scrie_documente(cur, docs)
        cur.execute("SELECT numar, tva, tva_de_verificat FROM facturi WHERE tip = 'preluata' ORDER BY numar")
        assert [(n, float(t), v) for n, t, v in cur.fetchall()] == [("FB-1", 90.0, False), ("FB-2", 210.0, True)]
