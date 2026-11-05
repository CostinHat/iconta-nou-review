# -*- coding: utf-8 -*-
"""PILOT F054 — Editor note contabile (comanda 16.6): Registru jurnal › + Notă nouă, parcurs pe ecran ca un contabil și ca un angajat fără dreptul de validare.
Fișier propriu, în plasa fixă (scripts/plasa_16_2.manifest). Rulează după e2e_pilot_f017 (plasa rulează fișierele în ordine alfabetică, scripts/poarta_lot.sh:185), deci baza are în plus nota 216
a lui F017 (5311 = 4111, 1210,00, 03.11.2026): aserțiunile sunt pe id-urile notelor 207, 212–215 și 203, niciodată pe totaluri sau contoare ale lunii.

Testul apelează cele două parcursuri ale lotului (docs/dovezi/16_6/parcurs_16_6.py, cu administratorul, și parcurs_16_6_angajat.py, cu un angajat fără dreptul de validare; aceleași acțiuni ca la
parcurgerile «înainte» / «după») și verifică aserțiunile din docs/dovezi/16_6/pasi.json prin `scripts/verifica_pas.verifica_pagina` (operator + valoare, comparate cu pagina vie). În plasă își scrie
rândurile într-un CSV propriu din E2E_TEMP, cu parcurgerea «plasa» și PARCURS_SHA = HEAD — niciodată în jurnalul lotului și niciodată capturi în docs/dovezi/.
Din scenariul F054 (docs/scenarii_pilot.txt): nota 207 de 10,00 fără document (610, 617), data propusă 03.11.2026 și 15.10.2026 (602.1), suma 25,00 și lipsurile din «Completează: …» (729.2),
nota 203 validată de 13.800,00 și nota angajatului de 25,00 la validare în cabinet (48). Fiecare picătură își numește poziția, deficiența și cifrele.
Deficiențele pe care le dovedește: 729.2, 602.1, 610, 617, 48."""
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

LOT = "16.6"
DOVEZI = os.path.join(RAD, "docs", "dovezi", "16_6")
ADMIN = "dovada.71507@sesiuneab.test"      # administratorul cabinetului „Cabinet Test Sesiunea B”, cu dreptul de validare
ANGAJAT = "dovada.71508@sesiuneab.test"    # angajat, nivel asistent, fără dreptul de validare
TENANT_F1 = "tenant_9049"
ID_F1 = 105779
DESCRIERE_ANGAJAT = "F054 nota de proba"
DEFICIENTE_PROBATE = ("729.2", "602.1", "610", "617", "48")   # core/test_deficiente.py::plasa_e2e

# pasul -> (deficiențele dovedite de el, cifrele din scenariul F054 pe care le citează)
HARTA = {
    "a": ("617", "F054 (1): cinci note în 11/2026, toate ciorne: 207 de 10,00 fără document și 212–215 din NIR nr 7"),
    "b": ("617", "F054 (1): căutarea 7588 lasă nota 207 de 10,00"),
    "c": ("617", "F054 (1): căutarea NIR nr 7 lasă 212–215"),
    "d": ("617", "F054 (1): filtrul fără document lasă nota 207 de 10,00"),
    "e": ("617", "F054 (1): filtrul validată nu lasă nicio notă din cele cinci"),
    "f": ("610", "F054 (2): Validează inactiv pe nota 207 de 10,00, motivul o singură dată în detaliu"),
    "g": ("610", "F054 (2): clicul pe Validează inactiv nu scrie niciun refuz"),
    "h": ("729.2, 602.1", "F054 (3): data propusă 03.11.2026, Salvează inactiv: Completează: contul debit, contul credit, suma"),
    "i": ("729.2", "F054 (3): clicul pe Salvează inactiv nu scrie niciun mesaj"),
    "j": ("602.1", "F054 (4): în 10/2026 data rămâne goală, Salvează numește data"),
    "k": ("729.2", "F054 (4): cu două linii lipsurile poartă prefixul linia N"),
    "l": ("729.2", "F054 (4): după ștergerea liniei 2 revine forma fără prefix"),
    "m": ("729.2, 602.1", "F054 (5): data 15.10.2026 nu mai lipsește"),
    "n": ("729.2", "F054 (5): 4111, 707, 25,00 cer partenerul"),
    "o": ("729.2", "F054 (5): cu Client Test SRL, Salvează devine activ"),
    "p": ("729.2", "F054 (5): linia 2 goală: Completează: linia 2: contul debit, contul credit, suma"),
    "q": ("729.2", "F054 (5): linia 2 cu 4111, 707, 25,00 cere partenerul liniei 2"),
    "r": ("729.2", "F054 (5): după ștergerea liniei 2 Salvează e activ"),
    "s": ("729.2, 602.1", "F054 (5): data golită: Completează: data"),
    "t": ("48", "F054 (6): nota 203 validată, nr. crt. 41, 13.800,00: Validează, Editează, Șterge inactive"),
    "u": ("729.2, 602.1", "F054 (7): angajat, data propusă 03.11.2026, Salvează inactiv"),
    "v": ("729.2", "F054 (7): angajat, 628 = 5121, 25,00: Salvează activ"),
    "w": ("48", "F054 (7): nota de 25,00 apare La validare în cabinet"),
    "x": ("48", "F054 (7): Editează și Șterge inactive, motivul că nota așteaptă validarea"),
}


def _preconditii():
    """Starea din care pornește scenariul (snapshotul 16.0): cele cinci ciorne 207 (10,00, fără document) și 212–215 (NIR nr 7) din 11/2026, nota validată 203 (31.08.2026, 13.800,00) și nicio
    notă a angajatului rămasă dintr-o rulare dinainte. Un test al plasei care a consumat-o înaintea lui (sau o rulare fără restaurarea bazei) = pică explicit, nu «pică» pe aserțiuni."""
    note = sql("SELECT id, status, to_char(data, 'YYYY-MM-DD'), coalesce(document_ref, ''), "
               "(SELECT sum(suma)::text FROM \"%s\".inregistrari_linii WHERE inregistrare_id = i.id) "
               "FROM \"%s\".inregistrari i WHERE id IN (207, 212, 213, 214, 215, 203) ORDER BY id" % (TENANT_F1, TENANT_F1))
    de_id = {r[0]: r for r in note}
    rele = []
    for nid in (207, 212, 213, 214, 215):
        r = de_id.get(nid)
        if r is None or r[1] != "ciorna" or r[2] != "2026-11-02":
            rele.append("nota %d: %s (așteptat ciornă din 02.11.2026)" % (nid, r))
    if de_id.get(207) and (de_id[207][3] != "" or de_id[207][4] != "10.00"):
        rele.append("nota 207: document %r, suma %s (așteptat fără document, 10,00)" % (de_id[207][3], de_id[207][4]))
    for nid in (212, 213, 214, 215):
        if de_id.get(nid) and not de_id[nid][3].startswith("NIR nr 7"):
            rele.append("nota %d: document %r (așteptat NIR nr 7 din 02.11.2026)" % (nid, de_id[nid][3]))
    r = de_id.get(203)
    if r is None or r[1] != "validata" or r[2] != "2026-08-31" or r[4] != "13800.00":
        rele.append("nota 203: %s (așteptat validată din 31.08.2026, 13.800,00)" % (r,))
    if sql("SELECT id FROM \"%s\".inregistrari WHERE descriere = %%s" % TENANT_F1, (DESCRIERE_ANGAJAT,)):
        rele.append("există deja o notă «%s» (baza nu a fost restaurată înaintea rulării)" % DESCRIERE_ANGAJAT)
    if rele:
        pytest.fail("precondiție consumată de plasă: " + "; ".join(rele))


def _incarca(nume):
    spec = importlib.util.spec_from_file_location(nume, os.path.join(DOVEZI, nume + ".py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _cerere(pg, metoda, cale, corp=None):
    """Cererea pe care ar trimite-o ecranul, cu sesiunea omului (pentru refuzurile serverului), ca în e2e_bloc_b.py."""
    return pg.evaluate("""([m, c, b]) => fetch(c, {method: m, headers: {'Authorization': 'Bearer ' + sessionStorage.getItem('iconta_token'),
        'Content-Type': 'application/json'}, body: b ? JSON.stringify(b) : undefined}).then(r => r.status)""", [metoda, cale, corp])


def test_pilot_F054(browser, monkeypatch):
    from core import ceas_proba
    _preconditii()
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    monkeypatch.setenv("PARCURS_SHA", sha)
    temp = os.path.join(os.environ.get("E2E_TEMP", "/tmp/e2e_poarta"), "pilot_f054")
    shutil.rmtree(temp, ignore_errors=True)   # cheia lot/parcurgere/pas/sha/verificator nu se repetă într-o rulare nouă a plasei
    os.makedirs(temp)
    jurnal = os.path.join(temp, "jurnal_verificare.csv")
    pasi_json = os.path.join(DOVEZI, "pasi.json")
    ctx = types.SimpleNamespace(lot=LOT, parcurgere="plasa", verificator="code", pasi_json=pasi_json, csv=jurnal, sha=sha,
                                director=os.path.join(temp, "plasa", "code"))
    os.makedirs(ctx.director, exist_ok=True)
    cereri_admin, status_angajat = [], {}
    # administratorul: pașii a–t; nu salvează nimic, iar clicul pe butonul inactiv nu trimite nicio cerere (610, 729.2)
    b = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.on("request", lambda r: cereri_admin.append((r.method, r.url)) if r.method != "GET" and ("/jurnal" in r.url or "/valideaza" in r.url) else None)
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        _incarca("parcurs_16_6").ruleaza(pg, ctx)
    finally:
        b.close()
    # angajatul fără dreptul de validare: a doua sesiune, pașii u–x; scrie nota de 25,00, care intră la validare în cabinet (48)
    b2 = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    try:
        b2.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b2.add_init_script(sesiune(ANGAJAT))
        pg2 = b2.new_page()
        pg2.goto(BAZA + "/", wait_until="load", timeout=30000)
        _incarca("parcurs_16_6_angajat").ruleaza(pg2, ctx)
        nota = sql("SELECT id FROM \"%s\".inregistrari WHERE descriere = %%s ORDER BY id DESC" % TENANT_F1, (DESCRIERE_ANGAJAT,))
        if nota:   # serverul refuză modificarea și ștergerea directe ale notei aflate la validare (48), iar nota rămâne neschimbată
            nid = nota[0][0]
            status_angajat["put"] = _cerere(pg2, "PUT", "/tenants/%d/jurnal/%d" % (ID_F1, nid),
                                            {"data": "2026-11-03", "descriere": DESCRIERE_ANGAJAT + " schimbat", "document_ref": "Chitanță de probă din 03.11.2026",
                                             "linii": [{"debit": "628", "credit": "5121", "suma": 999}]})   # corp complet: refuzul ≥ 400 nu poate veni din câmpuri lipsă
            status_angajat["delete"] = _cerere(pg2, "DELETE", "/tenants/%d/jurnal/%d" % (ID_F1, nid))
            status_angajat["nota"] = sql("SELECT descriere, (SELECT sum(suma)::text FROM \"%s\".inregistrari_linii WHERE inregistrare_id = i.id) "
                                         "FROM \"%s\".inregistrari i WHERE id = %%s" % (TENANT_F1, TENANT_F1), (nid,))
    finally:
        b2.close()
    asertiuni = [a["id"] for a in json.load(open(pasi_json, encoding="utf-8"))["asertiuni"]]
    verdicte = {}
    if os.path.exists(jurnal):
        with open(jurnal, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["parcurgere"] == "plasa" and r["commit"].startswith(sha[:8]):
                    verdicte[r["pas"]] = r["verdict"]
    picate = ["%s [deficiența %s; %s]: %s" % (i, HARTA[i.split(".")[0]][0], HARTA[i.split(".")[0]][1], verdicte.get(i, "neexecutat"))
              for i in asertiuni if verdicte.get(i) != "trece"]
    assert not picate, "aserțiuni F054 care nu trec (id [deficiență; cifre din scenariu]: verdict): %s" % "; ".join(picate)
    assert not cereri_admin, "F054 (2)/(3), 610 și 729.2: clicurile pe butoanele inactive au trimis cereri de scriere: %s" % cereri_admin
    assert status_angajat.get("put", 0) >= 400 and status_angajat.get("delete", 0) >= 400, \
        "F054 (7), 48: serverul trebuie să refuze PUT și DELETE pe nota de 25,00 aflată la validare: %s" % status_angajat
    assert status_angajat["nota"] == [(DESCRIERE_ANGAJAT, "25.00")], "F054 (7), 48: nota de 25,00 s-a schimbat: %s" % status_angajat["nota"]
