# -*- coding: utf-8 -*-
"""PILOT X05 — Navigare ferestre (comanda 16.8): „✕” de 40 × 40 în dreapta sus pe fiecare fereastră de lucru, „←” numai la un pas înapoi real, acțiunea principală o singură dată pe ecran,
ieșirea din cont fără „←”, bannerul de eroare închidere. Fișier propriu, în plasa fixă (scripts/plasa_16_2.manifest), 1 test: test_pilot_X05.

Două părți: (1) parcursul docs/dovezi/16_8/parcurs_16_8.py, ale cărui aserțiuni (docs/dovezi/16_8/pasi.json) le judecă scripts/verifica_pas.verifica_pagina, în CSV-ul propriu din E2E_TEMP,
cu parcurgerea «plasa»; (2) măsurători directe pe DOM, pe care oracolul nu le are (lățimea lui „✕”, poziția lui față de celelalte elemente ale barei, dublarea acțiunii principale numărată pe
butoanele vizibile din conținut), pe aceleași ferestre. Nu salvează nimic; nu scrie niciodată în jurnalul lotului sau capturi în docs/dovezi/.
Deficiențele pe care le dovedește: 759, 760, 786."""
import csv
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import types

import pytest

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

LOT = "16.8"
DOVEZI = os.path.join(RAD, "docs", "dovezi", "16_8")
ADMIN = "dovada.71507@sesiuneab.test"
DEFICIENTE_PROBATE = ("759", "760", "786")   # core/test_deficiente.py::plasa_e2e

# pasul -> (deficiențele dovedite, ce se vede)
HARTA = {
    "a": ("759", "X05 (1): fereastra firmei, prima fereastră: un „✕” în dreapta sus, „←” nevăzut, fără acțiune în bară"),
    "b": ("759, 760", "X05 (2)+(3): Registru jurnal: „✕” și „←”, „+ Notă nouă” o singură dată, în bară"),
    "c": ("759, 760", "X05 (2)+(3): Emite factură (regresie: era deja verde)"),
    "d": ("759, 760", "X05 (2)+(3): Stat de plată F5: „Contabilizează statul” o singură dată, în bară"),
    "e": ("759, 760", "X05 (2)+(3): Plan de conturi F1: „Adaugă” o singură dată, în bară"),
    "f": ("759, 760", "X05 (2)+(3): Model factură F1: „Salvează” o singură dată, în bară"),
    "g": ("759, 760", "X05 (2)+(3): editorul de notă: Salvează inactiv, în bară, o singură dată"),
    "h": ("759", "X05 (4): fereastra mică de stornare: „✕” de 40 × 40"),
    "i": ("760", "X05 (5): D104 pasul 2: „Generează D104” în bară, o singură dată"),
    "j": ("760", "X05 (5): D104 cu secțiunile pliate: butonul rămâne în bară"),
    "k": ("759", "X05 (6): „Ieși din cont” de 40 px, cu pictogramă, fără „←”"),
    "l": ("786", "X05 (7): bannerul de eroare are „✕” de 40 × 40"),
    "m": ("786", "X05 (7): „✕” scoate bannerul"),
    "n": ("786", "X05 (7): o a doua eroare îl arată din nou"),
}

# măsurătorile directe, în pagina vie: ultima fereastră care nu e fundal (`.fereastra-overlay:not(.fundal) .fereastra`)
JS_FEREASTRA = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return {fereastra: false};
  const vizibil = (e) => !!(e.offsetParent || e.getClientRects().length) && getComputedStyle(e).visibility !== 'hidden';
  const ant = F.querySelector('.fereastra-antet');
  const xs = [...ant.querySelectorAll('button')].filter((b) => vizibil(b) && b.innerText.replace(/\\s+/g, ' ').trim() === '✕';
  const r = xs.length === 1 ? xs[0].getBoundingClientRect() : null;
  const alte = [...ant.querySelectorAll('button, input, select, a[href]')].filter((e) => vizibil(e) && e !== xs[0] && !e.closest('#cautare-fereastra-rez'));
  const jos = F.querySelector('.fereastra-jos');
  const principale = jos ? [...jos.querySelectorAll('.fj-principal')].map((b) => b.innerText.replace(/\\s+/g, ' ').trim()) : [];
  const continut = [...F.querySelectorAll('button, a.buton-primar, a.buton-secundar, [role=button]')]
    .filter((b) => vizibil(b) && !(jos && jos.contains(b)) && !ant.contains(b) && !b.closest('table, template, details'))
    .map((b) => b.innerText.replace(/\\s+/g, ' ').trim());
  return {fereastra: true, nr_x: xs.length, dim: r ? [Math.round(r.width), Math.round(r.height)] : null,
          dreapta: r ? alte.every((e) => e.getBoundingClientRect().right <= r.right + 1) : null,
          sus: r ? (r.top >= ant.getBoundingClientRect().top - 1 && r.bottom <= ant.getBoundingClientRect().bottom + 1) : null,
          principale, dubluri: principale.filter((t) => continut.includes(t))};
}"""


def _incarca(nume):
    spec = importlib.util.spec_from_file_location(nume, os.path.join(DOVEZI, nume + ".py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def test_pilot_X05(browser, monkeypatch):
    from core import ceas_proba
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    monkeypatch.setenv("PARCURS_SHA", sha)
    temp = os.path.join(os.environ.get("E2E_TEMP", "/tmp/e2e_poarta"), "pilot_x05")
    shutil.rmtree(temp, ignore_errors=True)
    os.makedirs(temp)
    jurnal = os.path.join(temp, "jurnal_verificare.csv")
    pasi_json = os.path.join(DOVEZI, "pasi.json")
    ctx = types.SimpleNamespace(lot=LOT, parcurgere="plasa", verificator="code", pasi_json=pasi_json, csv=jurnal, sha=sha,
                                director=os.path.join(temp, "plasa", "code"))
    os.makedirs(ctx.director, exist_ok=True)
    masuri = {}
    b = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        parcurs = _incarca("parcurs_16_8")
        parcurs.ruleaza(pg, ctx)
        # (2) măsurători directe, pe aceleași ferestre, deschise de funcțiile parcursului (nu de un al doilea parcurs)
        parcurs.firma(pg)
        masuri["firma"] = pg.evaluate(JS_FEREASTRA)
        pg.click("#fa-jurnal"); pg.wait_for_selector("#j-nota-noua", state="attached", timeout=20000); pg.wait_for_timeout(700)
        masuri["jurnal"] = pg.evaluate(JS_FEREASTRA)
        parcurs.firma(pg); pg.click("#fa-facturi"); pg.click("#fac-emite"); pg.wait_for_selector("#em-emite", state="attached", timeout=20000); pg.wait_for_timeout(700)
        masuri["emite"] = pg.evaluate(JS_FEREASTRA)
        parcurs.firma(pg, "F5 SRL Salariati"); pg.click("#fa-salariati"); pg.wait_for_selector("#sp-contare", state="attached", timeout=30000); pg.wait_for_timeout(700)
        masuri["stat"] = pg.evaluate(JS_FEREASTRA)
        parcurs.firma(pg); pg.click("#fa-planconturi"); pg.wait_for_selector("#pcf-adauga", state="attached", timeout=20000); pg.wait_for_timeout(700)
        masuri["plan"] = pg.evaluate(JS_FEREASTRA)
        parcurs.firma(pg); pg.click("#fa-facturi"); pg.click("#fac-model"); pg.wait_for_selector("#mf-salveaza", state="attached", timeout=20000); pg.wait_for_timeout(700)
        masuri["model"] = pg.evaluate(JS_FEREASTRA)
        parcurs.firma(pg); pg.click("#fa-facturi"); pg.click("#fac-istoric"); pg.click("#fac-prev")
        pg.locator("button.fac-frand-btn").first.click(); pg.click("#fd-storno"); pg.wait_for_selector(".fereastra.fer-mic", timeout=20000); pg.wait_for_timeout(500)
        masuri["mica"] = pg.evaluate(JS_FEREASTRA)
        parcurs.firma(pg); pg.click("#fa-declaratii"); pg.locator("li.ds-lista-rand", has_text="D104").first.click(); pg.click("#dec-continua")
        pg.wait_for_selector("#d104-regen", state="attached", timeout=30000); pg.wait_for_timeout(700)
        masuri["d104"] = pg.evaluate(JS_FEREASTRA)
        pg.goto(BAZA + "/", wait_until="domcontentloaded"); pg.wait_for_selector("#nav-iesire", timeout=30000)
        masuri["iesire"] = pg.evaluate("() => { const e = document.querySelector('#nav-iesire'), r = e.getBoundingClientRect(); return {dim: [Math.round(r.width), Math.round(r.height)], titlu: e.title, eticheta: e.getAttribute('aria-label')}; }")
        pg.evaluate(parcurs.EROARE); pg.wait_for_selector("#eroare-globala .nav-x", timeout=5000)
        masuri["banner"] = pg.evaluate("() => { const r = document.querySelector('#eroare-globala .nav-x').getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; }")
    finally:
        b.close()
    asertiuni = [a["id"] for a in json.load(open(pasi_json, encoding="utf-8"))["asertiuni"]]
    verdicte = {}
    if os.path.exists(jurnal):
        with open(jurnal, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r["parcurgere"] == "plasa" and r["commit"].startswith(sha[:8]):
                    verdicte[r["pas"]] = r["verdict"]
    picate = ["%s [deficiența %s; %s]: %s" % (i, HARTA[i.split(".")[0]][0], HARTA[i.split(".")[0]][1], verdicte.get(i, "neexecutat"))
              for i in asertiuni if verdicte.get(i) != "trece"]
    assert not picate, "aserțiuni X05 care nu trec (id [deficiență; ce se vede]: verdict): %s" % "; ".join(picate)
    rele = []
    for nume, m in masuri.items():
        if nume in ("iesire", "banner"):
            continue
        if not m.get("fereastra"):
            rele.append("%s: nicio fereastră deschisă" % nume); continue
        if m["nr_x"] != 1 or m["dim"] != [40, 40]:
            rele.append("%s: „✕” x%s, dimensiune %s (așteptat 1 × [40, 40], 759)" % (nume, m["nr_x"], m["dim"]))
        if not m["dreapta"] or not m["sus"]:
            rele.append("%s: „✕” nu e în dreapta sus a barei (dreapta=%s, sus=%s, 759)" % (nume, m["dreapta"], m["sus"]))
        if m["dubluri"]:
            rele.append("%s: acțiunea principală %s apare și în conținut (760)" % (nume, m["dubluri"]))
    for nume in ("jurnal", "emite", "stat", "plan", "model", "d104"):
        if nume in masuri and len(masuri[nume].get("principale", [])) != 1:
            rele.append("%s: bara de jos are %s butoane principale (așteptat unul, 760)" % (nume, masuri[nume].get("principale")))
    if masuri["iesire"]["dim"] != [40, 40]:
        rele.append("iesire: %s (așteptat [40, 40], 759)" % masuri["iesire"]["dim"])
    if masuri["banner"] != [40, 40]:
        rele.append("banner: „✕” %s (așteptat [40, 40], 786)" % masuri["banner"])
    assert not rele, "măsurători directe X05: %s" % "; ".join(rele)
