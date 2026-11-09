# -*- coding: utf-8 -*-
"""ACȚIUNEA PRINCIPALĂ — lotul 17.5-D (rândurile A09, A19, A20, A22, A32 din auditul de ecrane). Scris de arhitect; Code nu îl modifică.

Pe F1 Comert Stoc, la 1366×768, ceas înghețat 03.11.2026, butonul principal din bara de jos a ferestrei (`.fj-butoane .fj-principal`) este:
Bancă -> „Importă extras”; Mișcări, fișe de magazie (din Stocuri) -> „Descarcă PDF”; Rapoarte comerciale -> „Descarcă PDF”;
Import date › Solduri inițiale -> „Încarcă balanța”; Import date (meniul straturilor) -> niciun buton principal.
Nu salvează nimic; nu alege niciun fișier. Un singur test."""
import importlib.util
import os
import sys

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
TOP = ".fereastra-overlay:not(.fundal) "
PRINCIPAL = TOP + ".fereastra .fj-butoane .fj-principal"
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


def _card(pg, parcurs, sel):
    parcurs.firma(pg, F1)
    if pg.evaluate(JS_DESCHIDE_CARD, sel) != "ok":
        return False
    pg.click(TOP + sel, timeout=10000)
    try:
        pg.wait_for_selector(TOP + "#fa-facturi", state="detached", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(2000)
    return True


def _principal(pg):
    loc = pg.locator(PRINCIPAL)
    n = loc.count()
    return n, (" ".join(loc.first.inner_text().split()) if n else "")


def test_actiune_principala_17_5_D(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        asteptat = []
        # Bancă
        _card(pg, parcurs, "#fa-banca")
        asteptat.append(("Bancă", _principal(pg), (1, "Importă extras")))
        # Mișcări, fișe de magazie (din Stocuri)
        if _card(pg, parcurs, "#fa-stocuri"):
            try:
                pg.click(TOP + "#cv-toggle", timeout=10000)
                pg.wait_for_timeout(2000)
            except Exception:   # noqa: BLE001
                pass
        asteptat.append(("Mișcări, fișe de magazie", _principal(pg), (1, "Descarcă PDF")))
        # Rapoarte comerciale
        _card(pg, parcurs, "#fa-rapoarte")
        asteptat.append(("Rapoarte comerciale", _principal(pg), (1, "Descarcă PDF")))
        # Import date (meniul) și Solduri inițiale
        _card(pg, parcurs, "#fa-import")
        try:
            pg.wait_for_selector(TOP + "#mig-pasi", timeout=20000)
            pg.wait_for_timeout(1000)
        except Exception:   # noqa: BLE001
            pass
        asteptat.append(("Import date (meniul)", _principal(pg), (0, "")))
        try:
            pg.locator(TOP + "#mig-pasi >> text=Solduri inițiale").first.click(timeout=10000)
            pg.wait_for_selector(TOP + "#mig-drop", state="attached", timeout=20000)
            pg.wait_for_timeout(1500)
        except Exception:   # noqa: BLE001
            pass
        asteptat.append(("Import date › Solduri inițiale", _principal(pg), (1, "Încarcă balanța")))
        for nume, (n, text), (n_ok, text_ok) in asteptat:
            if n != n_ok or (n_ok and text != text_ok):
                rele.append("%s: %d buton(e) principal(e) «%s», așteptat %d «%s»" % (nume, n, text, n_ok, text_ok))
    finally:
        b.close()
    assert not rele, "acțiunea principală 17.5-D: %s" % "; ".join(rele)
