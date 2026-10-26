# -*- coding: utf-8 -*-
"""[lotul 13, zona firme2] Deficiența 669 — soldurile pe parteneri preluate, în ofertele Casei și Băncii.

Comanda Costin 13.1, verbatim: „669: Client Alfa Test SRL are 1.500 lei pe 4111 din soldurile pe parteneri preluate, dar la încasare
aplicația spune «Nicio factură emisă neîncasată pentru acest CUI» și tratează suma ca avans (cu efecte de TVA). Soldurile preluate pe
parteneri trebuie să apară ca sume de încasat/plătit, ca să poată fi stinse în prima lună. Aceeași verificare la plata către furnizor și la
potrivirea extrasului bancar.”

Documentul „Sold la <data>” (scris la migrare, `solduri_parteneri_api`, tipul `nomenclator_status_factura.TIP_SOLD_PRELUAT`) e oferit de
AMBELE drumuri — Casa (`casa_api.facturi_partener`, încasare și plată) și Banca (`reconciliere_api.facturi_deschise_detalii`, „Alege
facturile”) —, marcat `preluata`, ca ecranul să-l numească „sold preluat la migrare” (nu „Sold la 30.09.2026 din 30.09.2026”).
CE FACE IMPOSIBIL: soldul preluat lipsă din oricare din cele două oferte (atunci încasarea devine avans, cu TVA); marcajul pierdut.
Schemă efemeră din șablon, tranzacție anulată, perioade sintetice (2099).
TEMEI: OMFP 1802/2014 (Reglementări, funcțiunea conturilor 411 și 401): „În creditul contului 411 "Clienți" se înregistrează: – sumele
încasate de la clienți (512, 531)”; „În debitul contului 401 "Furnizori" se înregistrează: – plățile efectuate către furnizori (512, 531,
541, 542)”. Soldul preluat e chiar creanța / datoria din 411 / 401, deci încasarea / plata îl stinge (nu e avans).
"""
import os

import pytest

from core import casa_api, db as _db, reconciliere_api

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot13_firme2_prel"
CUI_ALFA, CUI_FURN = "40130018", "40130034"   # cifra de control verificată (algoritmul oficial, `tenant_provisioning.cui_valid`)


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
    sablon = open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(sablon, SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
                for nr, directie, cui, nume, total in (("Sold la 31.12.2098", "emisa", CUI_ALFA, "CLIENT ALFA PROBA SRL", 1500),
                                                       ("Sold la 31.12.2098", "primita", CUI_FURN, "FURNIZOR PROBA SRL", 1000)):
                    cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, moneda, directie, status, tert_nume, tert_cui, tip, "
                                "total_lei, tva_lei, sursa_externa) VALUES (%s, '2098-12-31', %s, 0, 'RON', %s, 'importata', %s, %s, "
                                "'preluata', %s, 0, 'preluare')", (nr, total, directie, nume, cui, total))
            yield c
        finally:
            c.rollback()


def test_casa_ofera_soldul_preluat_la_incasare_si_la_plata(conn):
    inc = casa_api.facturi_partener(conn, SCHEMA, "incasare_client", CUI_ALFA)
    pla = casa_api.facturi_partener(conn, SCHEMA, "plata_furnizor", CUI_FURN)
    assert [(f["numar"], f["sold"], f["preluata"]) for f in inc] == [("Sold la 31.12.2098", "1500.00", True)], inc
    assert [(f["numar"], f["sold"], f["preluata"]) for f in pla] == [("Sold la 31.12.2098", "1000.00", True)], pla


def test_banca_ofera_soldurile_preluate_pe_ambele_directii(conn):
    fd = {(f["directie"], f["tert_cui"]): f for f in reconciliere_api.facturi_deschise_detalii(conn, SCHEMA)}
    assert (fd[("emisa", CUI_ALFA)]["numar"], fd[("emisa", CUI_ALFA)]["sold"], fd[("emisa", CUI_ALFA)]["preluata"]) == ("Sold la 31.12.2098", "1500.00", True)
    assert (fd[("primita", CUI_FURN)]["sold"], fd[("primita", CUI_FURN)]["preluata"]) == ("1000.00", True)
