# -*- coding: utf-8 -*-
"""ALEGEREA CU O SINGURĂ VARIANTĂ ȘI INTRAREA MOARTĂ — lotul 17.5-E (rândurile A25, A44 din auditul de ecrane). Scris de arhitect; Code nu îl modifică.

(1) Pe F1 Comert Stoc (un singur partener în Compensări: DANTE INTERNATIONAL SA), la deschiderea ferestrei Compensări ecranul NU mai cere „Alege partenerul”
    (#cz-alege lipsește) și arată sumele partenerului („de încasat de la partener”), fără nicio apăsare.
(2) Intrarea „Import date — Preluare F7” din core/catalog_ecrane.json caută un text care există în meniul Import date („Audit de preluare”).
Nu salvează nimic. Un singur test."""
import importlib.util
import json
import os
import sys

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
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


def test_alegere_unica_17_5_E(browser):
    from core import ceas_proba
    rele = []
    # (2) intrarea din catalog
    cat = json.load(open(os.path.join(RAD, "core", "catalog_ecrane.json"), encoding="utf-8"))
    intr = [e for e in cat if e.get("nume") == "Import date — Preluare F7"]
    texte = [p.get("text") for e in intr for p in e.get("pasi", []) if p.get("text")]
    if not intr or texte != ["Audit de preluare"]:
        rele.append("(2) intrarea „Import date — Preluare F7” caută %s, nu „Audit de preluare”" % texte)
    # (1) Compensări cu un singur partener
    parcurs = _incarca_parcurs_17_1()
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        parcurs.firma(pg, F1)
        if pg.evaluate(JS_DESCHIDE_CARD, "#fa-compensari") != "ok":
            rele.append("(1) cardul Compensări lipsește")
        else:
            pg.click(TOP + "#fa-compensari", timeout=10000)
            try:
                pg.wait_for_selector(TOP + "#cz-rezumat", timeout=25000)
            except Exception:   # noqa: BLE001
                pass
            pg.wait_for_timeout(2500)
            alege = pg.locator(TOP + "#cz-alege").count()
            total = " ".join(pg.inner_text(TOP + "#cz-total").split()) if pg.locator(TOP + "#cz-total").count() else ""
            if alege:
                rele.append("(1) Compensări cere încă „Alege partenerul” deși F1 are un singur partener")
            if "de încasat de la partener" not in total:
                rele.append("(1) Compensări nu arată sumele partenerului: «%s»" % total[:120])
    finally:
        b.close()
    assert not rele, "alegerea unică 17.5-E: %s" % "; ".join(rele)
