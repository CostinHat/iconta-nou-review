# -*- coding: utf-8 -*-
"""BUTOANE LA LOCUL LOR — lotul 17.5-F (rândurile A04, A15, A34, A43 din auditul de ecrane; decizii_17_5_F.txt cu SUPRASCRIS). Scris de arhitect; Code nu îl modifică.

La 1366×768, ceas înghețat 03.11.2026, fără a salva nimic (fiecare fereastră trebuie întâi să existe, altfel pică — nimic nu trece „în gol”):
(2) F1 › Facturi › Facturi primite (firma nu e conectată la SPV): „Verifică acum în SPV” (#fp-verifica) e inactiv și rămâne singurul buton principal al ferestrei.
(3) F5 SRL Salariati › Salariați › Ionescu Vasile › Prime, sporuri, ore suplimentare: nu mai are „Închide” în corp (#el-renunta).
(4) Cabinet › Capacitate (3 asistenți pe snapshot): butonul principal e „Adaugă asistenți”.
(5) F4 PFA Sistem Real › Încasări/plăți › „+ Operațiune nouă”: cu formularul deschis butonul principal e „Adaugă (ciornă)”.
Un singur test."""
import importlib.util
import os
import sys

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
TOP = ".fereastra-overlay:not(.fundal) "
JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _card(pg, parcurs, firma, sel):
    parcurs.firma(pg, firma)
    if pg.evaluate(JS_DESCHIDE_CARD, sel) != "ok":
        return False
    pg.click(TOP + sel, timeout=10000)
    try:
        pg.wait_for_selector(TOP + "#fa-facturi", state="detached", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(2000)
    return True


def test_butoane_la_loc_17_5_F(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        # (2)
        if _card(pg, parcurs, "F1 Comert Stoc", "#fa-facturi"):
            try:
                pg.click(TOP + "#fac-primite", timeout=10000)
                pg.wait_for_selector(TOP + "#fp-actiuni", state="attached", timeout=20000)
                pg.wait_for_timeout(2500)
            except Exception:   # noqa: BLE001
                pass
        if not pg.locator(TOP + "#fp-actiuni").count():
            rele.append("(2) fereastra Facturi primite nu s-a deschis")
        v = pg.locator(TOP + "#fp-verifica, " + TOP + ".fj-butoane button:has-text('Verifică acum în SPV')")
        activ = [i for i in range(v.count()) if v.nth(i).is_enabled()]
        if activ:
            rele.append("(2) „Verifică acum în SPV” e activ pe o firmă neconectată la SPV")
        pr = pg.locator(TOP + ".fereastra .fj-butoane .fj-principal")
        if pr.count() != 1 or "Verifică acum în SPV" not in pr.first.inner_text():
            rele.append("(2) butonul principal al ferestrei nu e singurul „Verifică acum în SPV” (inactiv): %d butoane principale" % pr.count())
        # (3)
        if _card(pg, parcurs, "F5 SRL Salariati", "#fa-salariati"):
            try:
                pg.locator(TOP + "button, " + TOP + "tr, " + TOP + "td", has_text="Ionescu Vasile").first.click(timeout=10000)
                pg.wait_for_timeout(2000)
                pg.locator(TOP + "button", has_text="Prime, sporuri").first.click(timeout=10000)
                pg.wait_for_selector(TOP + "#el-formular", state="attached", timeout=20000)
                pg.wait_for_timeout(1500)
                if pg.locator(TOP + "#el-renunta").count():
                    rele.append("(3) Prime, sporuri are încă „Închide” în corp (#el-renunta)")
            except Exception as e:   # noqa: BLE001
                rele.append("(3) fereastra Prime, sporuri nu s-a deschis: %s" % str(e)[:100])
        # (4)
        PR = TOP + ".fereastra .fj-butoane .fj-principal"
        try:
            pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
            pg.goto(BAZA + "/", wait_until="load", timeout=30000)
            pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
            if pg.get_attribute("#fg-sef button.firme-grup-btn", "aria-expanded") != "true":   # Capacitate stă în „Pentru șeful de cabinet”, pliată la încărcare
                pg.click("#fg-sef button.firme-grup-btn", timeout=10000)
                pg.wait_for_timeout(500)
            pg.click("button.cab-card:has([data-cheie='capacitate'])", timeout=10000)
            pg.wait_for_timeout(3000)
            t = pg.locator(PR).first.inner_text() if pg.locator(PR).count() else ""
            if "Adaugă asistenți" not in t:
                rele.append("(4) Capacitate: butonul principal e «%s», nu „Adaugă asistenți”" % " ".join(t.split()))
        except Exception as e:   # noqa: BLE001
            rele.append("(4) Capacitate nu s-a deschis: %s" % str(e)[:100])
        # (5)
        if _card(pg, parcurs, "F4 PFA Sistem Real", "#fa-rip"):
            try:
                pg.click(TOP + "#r-toggle", timeout=10000)
                pg.wait_for_timeout(2000)
                t = pg.locator(PR).first.inner_text() if pg.locator(PR).count() else ""
                if "Adaugă (ciornă)" not in t:
                    rele.append("(5) Încasări/plăți cu formularul deschis: butonul principal e «%s»" % " ".join(t.split()))
            except Exception as e:   # noqa: BLE001
                rele.append("(5) formularul Încasări/plăți nu s-a deschis: %s" % str(e)[:100])
        else:
            rele.append("(5) cardul Încasări/plăți lipsește pe F4")
    finally:
        b.close()
    assert not rele, "butoane la loc 17.5-F: %s" % "; ".join(rele)
