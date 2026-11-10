# -*- coding: utf-8 -*-
"""PĂZIREA BUTONULUI PRINCIPAL DIN BARA DE JOS — arhitect, 10.11.2026 (după retestul lotului 17.5-F: Produse a pierdut bara, nimic din poartă nu o păzea).

Parcurge FIECARE card al ferestrei firmei F1 (enumerat din pagină) la 1366×768, cu contul administratorului, ceas înghețat, fără să apese nimic care scrie,
și compară butonul principal din bara de jos (`.fj-butoane .fj-principal`: textul; starea inactiv/activ numai la rândurile [ȚINTĂ], pe F1) cu fișierul de referință harta_bara_jos.txt (ținut de arhitect;
cautat în docs/dovezi/17_5_H/, apoi în ~/ghid_incoming). Verificări suplimentare pe ecran: aceleași carduri pe firma F5 (textul butonului, unde bara are unul), Încasări/plăți F4 cu formularul deschis («Adaugă (ciornă)») și
Facturi primite (SPV), deschisă din fereastra Facturi, cu starea SPV din producție («conectată, fără drept») dată de test; Prime, sporuri, ore suplimentare F5 e păzită de pașii f.3 și a.7 și de e2e_piese, nu de acest test. O fereastră care pierde sau schimbă butonul principal face testul să pice; fereastra din lista
«FĂRĂ buton principal» care primește unul trebuie declarată în hartă de arhitect. Rândurile marcate [ȚINTĂ] din hartă sunt reparații cerute de comandă: pică până la reparație.
Nu salvează nimic."""
import os
import re
import sys

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
ADMIN = "dovada.71507@sesiuneab.test"
TOP = ".fereastra-overlay:not(.fundal) "
HARTA_CAI = (os.path.join(RAD, "docs", "dovezi", "17_5_H", "harta_bara_jos.txt"), os.path.expanduser("~/ghid_incoming/harta_bara_jos.txt"))

JS_CARDURI = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) button[id^="fa-"]')].map(b => [b.id, (b.innerText || '').trim().split('\\n')[0]])"""
JS_BARA = """() => {
  const F = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop(); if (!F) return null;
  const pr = F.querySelector('.fj-butoane .fj-principal');
  const inchide = [...F.querySelectorAll('.fereastra-corp button')].filter(b => (b.textContent || '').trim() === 'Închide' && b.getBoundingClientRect().width > 5).length;
  return { principal: pr ? pr.textContent.trim() : '', inactiv: pr ? !!pr.disabled : false, h: pr ? Math.round(pr.getBoundingClientRect().height) : 0, inchide };
}"""
JS_DESCHIDE_GRUPURI = "() => document.querySelectorAll('.fereastra-overlay:not(.fundal) .firme-grup-btn[aria-expanded=false]').forEach(b => b.click())"
JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""


def _cheie(t):
    t = re.sub(r"^[^A-Za-zĂÂÎȘȚăâîșț]+", "", t or "").strip()
    return t.split(" (")[0].strip()


def _harta():
    for cale in HARTA_CAI:
        if os.path.exists(cale):
            text = open(cale, encoding="utf-8").read()
            break
    else:
        raise AssertionError("BB0: lipsește harta_bara_jos.txt (docs/dovezi/17_5_H/ sau ~/ghid_incoming)")
    cu, fara = {}, set()
    for rand in text.split("\n"):
        if rand.startswith("FĂRĂ buton principal"):
            fara = {_cheie(x) for x in rand.split(":", 1)[1].split(",") if x.strip()}
        elif " | " in rand and not rand.startswith(("HARTA", "Scrisă", "Notă", "Format")):
            parti = [p.strip() for p in rand.split(" | ")]
            if len(parti) >= 3:
                cu[_cheie(parti[0])] = (parti[1], parti[2].split("[")[0].strip() if "ȚINTĂ" in parti[2] else "orice")   # starea activ/inactiv depinde de date: se compara numai la randurile-tinta
    return cu, fara


def _parcurs():
    import importlib.util
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_bara_jos_17_5_H(browser):
    from core import ceas_proba
    cu, fara = _harta()
    parcurs = _parcurs()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        vazute = set()
        for firma in ("F1 Comert Stoc", "F5 SRL Salariati"):
            parcurs.firma(pg, firma)
            pg.evaluate(JS_DESCHIDE_GRUPURI)
            carduri = pg.evaluate(JS_CARDURI)
            for sel, eticheta0 in carduri:
                eticheta = _cheie(eticheta0)
                if not eticheta:
                    continue
                try:
                    parcurs.firma(pg, firma)
                    if pg.evaluate(JS_DESCHIDE_CARD, "#" + sel) != "ok":
                        continue
                    pg.click(TOP + "#" + sel, timeout=10000)
                    pg.wait_for_timeout(2500)
                    m = pg.evaluate(JS_BARA) or {}
                except Exception as e:   # noqa: BLE001
                    rele.append("BB1 %s %s: fereastra nu s-a deschis (%s)" % (firma[:2], eticheta, str(e)[:60]))
                    continue
                if firma.startswith("F1"):
                    vazute.add(eticheta)
                princ, inactiv = m.get("principal", ""), m.get("inactiv", False)
                if eticheta in cu:
                    text_h, stare_h = cu[eticheta]
                    if princ != text_h and (princ or firma.startswith("F1")):
                        rele.append("BB2 %s %s: butonul principal din bara de jos e %r, în hartă %r" % (firma[:2], eticheta, princ, text_h))
                    elif stare_h != "orice" and firma.startswith("F1") and stare_h.startswith("inactiv") != inactiv:   # starea activ/inactiv depinde de date: se compara numai pe F1, firma cu date
                        rele.append("BB3 %s %s: butonul %r e %s, în hartă %s" % (firma[:2], eticheta, princ, "inactiv" if inactiv else "activ", stare_h))
                elif eticheta in fara:
                    if princ:
                        rele.append("BB4 %s %s: e în lista «fără buton principal», dar are %r în bara de jos; se declară în hartă" % (firma[:2], eticheta, princ))
                elif firma.startswith("F1"):
                    rele.append("BB6 %s: fereastră nouă sau redenumită, absentă din harta_bara_jos.txt; arhitectul o adaugă" % eticheta)
                if m.get("inchide"):
                    rele.append("BB5 %s %s: «Închide» în corpul ferestrei (%d)" % (firma[:2], eticheta, m["inchide"]))
        # Facturi primite (SPV) nu e card: se deschide din fereastra Facturi (butonul #fac-primite), pe F1
        try:
            # 823.1: defectul apare la firma CONECTATĂ la SPV, dar FĂRĂ DREPT (starea din producție a firmelor F1–F8); în baza de test F1 e neconectată,
            # deci testul îi dă el această stare, schimbând numai trei câmpuri din răspunsul real al rutei /spv/stare
            def _fara_drept(ruta):
                rasp = ruta.fetch()
                d = rasp.json()
                d.update({"conectat": True, "are_drept": False, "acoperire": "neacoperit"})
                ruta.fulfill(response=rasp, json=d)
            pg.route("**/tenants/*/spv/stare", _fara_drept)
            parcurs.firma(pg, "F1 Comert Stoc")
            pg.evaluate(JS_DESCHIDE_GRUPURI)
            sel = [s_ for s_, e_ in pg.evaluate(JS_CARDURI) if _cheie(e_) == "Facturi"]
            if not sel:
                rele.append("BB9 Facturi primite: cardul Facturi nu s-a găsit pe F1")
            else:
                pg.evaluate(JS_DESCHIDE_CARD, "#" + sel[0])
                pg.click(TOP + "#" + sel[0], timeout=10000)
                pg.wait_for_timeout(2500)
                pg.click(TOP + "#fac-primite", timeout=10000)
                pg.wait_for_timeout(2500)
                m = pg.evaluate(JS_BARA) or {}
                vazute.add("Facturi primite")
                if "Facturi primite" in cu:
                    text_h, stare_h = cu["Facturi primite"]
                    princ, inactiv = m.get("principal", ""), m.get("inactiv", False)
                    if princ != text_h:
                        rele.append("BB2 F1 Facturi primite: butonul principal din bara de jos e %r, în hartă %r" % (princ, text_h))
                    elif stare_h != "orice" and stare_h.startswith("inactiv") != inactiv:
                        rele.append("BB3 F1 Facturi primite (firmă conectată la SPV, fără drept): butonul %r e %s, în hartă %s" % (princ, "inactiv" if inactiv else "activ", stare_h))
                    elif stare_h.startswith("inactiv") and "motiv" in stare_h:
                        motiv = pg.evaluate("() => { const F = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop(); return F ? [...F.querySelectorAll('.ds-motiv-inactiv')].map(m => (m.textContent || '').trim()).filter(Boolean).join(' | ') : ''; }")
                        if not motiv:
                            rele.append("BB3 F1 Facturi primite (firmă conectată la SPV, fără drept): butonul %r e inactiv, dar fără motiv scris la vedere" % princ)
        except Exception as e:   # noqa: BLE001
            rele.append("BB9 Facturi primite: fereastra nu s-a deschis (%s)" % str(e)[:60])
        finally:
            try:
                pg.unroute("**/tenants/*/spv/stare")
            except Exception:   # noqa: BLE001
                pass
        for e in sorted(set(cu) - vazute):
            if e not in ("Prime, sporuri, ore suplimentare", "Registru încasări/plăți", "Capacitate", "Suport"):
                rele.append("BB8 %s: fereastra din hartă nu s-a găsit între cardurile F1" % e)
        # F4 Încasări/plăți cu formularul deschis și F5 Prime, sporuri: verificate pe ecran
        try:
            parcurs.firma(pg, "F4 PFA Sistem Real")
            pg.evaluate(JS_DESCHIDE_GRUPURI)
            pg.click(TOP + "button:has-text('Încasări/plăți')", timeout=10000)
            pg.wait_for_timeout(2500)
            pg.click(TOP + "button:has-text('+ Operațiune nouă')", timeout=10000)
            pg.wait_for_timeout(1500)
            m = pg.evaluate(JS_BARA) or {}
            if m.get("principal") != "Adaugă (ciornă)":
                rele.append("BB7 Încasări/plăți F4, formular deschis: butonul principal e %r, în hartă «Adaugă (ciornă)»" % m.get("principal"))
        except Exception as e:   # noqa: BLE001
            rele.append("BB7 Încasări/plăți F4: nu s-a putut deschide formularul (%s)" % str(e)[:80])
    finally:
        b.close()
    assert not rele, "păzirea barei de jos: %d abateri:\n  " % len(rele) + "\n  ".join(rele)
