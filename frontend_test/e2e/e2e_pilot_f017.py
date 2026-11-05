# -*- coding: utf-8 -*-
"""PILOT F017 — Chitanțe emise (comanda 16.2-B): încasarea în numerar a unei facturi, cu chitanță, parcursă pe ecran ca un contabil.
Fișier propriu, în afara lanțului `e2e_pilot_luna.py` (consumă F1A18 și seria CHF1 a lui F1 din snapshotul 16.0; de aceea stă ultimul în plasa fixă).

Testul apelează parcursul lotului (docs/dovezi/16_2_B/parcurs_16_2_B.py, aceleași acțiuni ca la parcurgerile «înainte» / «după») și verifică aceleași aserțiuni
din docs/dovezi/16_2_B/pasi.json prin `scripts/verifica_pas.verifica_pagina` (oracolul: operator + valoare, comparate cu pagina vie). În plasă își scrie rândurile
într-un CSV propriu din E2E_TEMP, cu parcurgerea «plasa» și PARCURS_SHA = HEAD — niciodată în jurnalul lotului și niciodată capturi în docs/dovezi/.
Deficiențele pe care le dovedește: 278.1, 456, 98, 455, 753, 729.1, 758 (id-ul aserțiunii e în mesajul fiecărei picături)."""
import csv
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import types

import pytest

from conftest import BAZA, _db, sesiune, sql

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))   # scripts/ nu e pachet (ca la conftest.py al plasei, cu rădăcina)
sys.path.insert(0, RAD)

LOT = "16.2-B"
DOVEZI = os.path.join(RAD, "docs", "dovezi", "16_2_B")
UTILIZATOR = "dovada.71507@sesiuneab.test"   # contul cabinetului „Cabinet Test Sesiunea B” (administratorul)
TENANT_F1 = "tenant_9049"
DEFICIENTE_PROBATE = ("278.1", "456", "98", "455", "753", "729.1", "758")   # core/test_deficiente.py::plasa_e2e


def _preconditii():
    """Starea din care pornește scenariul (snapshotul 16.0): F1A18 și F1A19 deschise, CHF1 nr. 1 ultima chitanță, registrul Casei 11/2026 cu un singur rând.
    Un test al plasei care a consumat-o înaintea lui = pică explicit, nu «pică» pe aserțiuni."""
    from core import casa_api, reconciliere, reconciliere_api
    with _db().get_conn() as conn:
        try:
            deschise = reconciliere.facturi_partener(reconciliere_api.facturi_deschise(conn, TENANT_F1), "410001005", "incasare")
            registru = casa_api.registru(conn, TENANT_F1, 2026, 11)
        finally:
            conn.rollback()
    numere = sorted(str(f.get("numar")) for f in deschise if str(f.get("numar") or "").startswith("F1A"))
    chitante = sql("SELECT serie, numar FROM %s.chitante WHERE NOT anulata ORDER BY id" % TENANT_F1)
    rele = []
    if numere != ["F1A18", "F1A19"]:
        rele.append("facturile deschise ale clientului 410001005: %s (așteptat F1A18, F1A19)" % numere)
    if [(c[0], c[1]) for c in chitante][-1:] != [("CHF1", 1)]:
        rele.append("ultima chitanță a lui F1: %s (așteptat CHF1 nr. 1)" % (chitante[-1:],))
    if len(registru["operatiuni"]) != 1:
        rele.append("registrul Casei F1 11/2026 are %d rânduri (așteptat 1)" % len(registru["operatiuni"]))
    if rele:
        pytest.fail("precondiție consumată de plasă: " + "; ".join(rele))


def _incarca_parcursul():
    spec = importlib.util.spec_from_file_location("parcurs_16_2_B", os.path.join(DOVEZI, "parcurs_16_2_B.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_pilot_F017(browser, monkeypatch):
    from core import ceas_proba
    _preconditii()
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    monkeypatch.setenv("PARCURS_SHA", sha)
    temp = os.path.join(os.environ.get("E2E_TEMP", "/tmp/e2e_poarta"), "pilot_f017")
    shutil.rmtree(temp, ignore_errors=True)   # cheia lot/parcurgere/pas/sha/verificator nu se repetă într-o rulare nouă a plasei
    os.makedirs(temp)
    jurnal = os.path.join(temp, "jurnal_verificare.csv")
    pasi_json = os.path.join(DOVEZI, "pasi.json")
    ctx = types.SimpleNamespace(lot=LOT, parcurgere="plasa", verificator="code", pasi_json=pasi_json, csv=jurnal, sha=sha,
                                director=os.path.join(temp, "plasa", "code"))
    os.makedirs(ctx.director, exist_ok=True)
    b = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(UTILIZATOR))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        _incarca_parcursul().ruleaza(pg, ctx)
    finally:
        b.close()
    asertiuni = [a["id"] for a in json.load(open(pasi_json, encoding="utf-8"))["asertiuni"]]
    verdicte = {}
    if os.path.exists(jurnal):
        with open(jurnal, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["parcurgere"] == "plasa" and r["commit"].startswith(sha[:8]):
                    verdicte[r["pas"]] = r["verdict"]
    picate = ["%s: %s" % (i, verdicte.get(i, "neexecutat")) for i in asertiuni if verdicte.get(i) != "trece"]
    assert not picate, "aserțiuni F017 care nu trec (id: verdict): %s" % "; ".join(picate)
