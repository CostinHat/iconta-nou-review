# -*- coding: utf-8 -*-
"""Proba uneltei `_la_luna` (17.5-C0, pct.6.3) în ambele direcții, pe Casă (#c-prev), Registru jurnal (#j-prev) și Stocuri (#s-prev), pe F1 Comert Stoc, cu ceasul înghețat
(MOMENT_REF) și sesiunea ADMIN ca în e2e_pilot_x09_C0.py. Țintele sunt relative la luna L afișată la deschidere: L-1, apoi L (înainte, prin „-next”), apoi L-2.
După fiecare chemare se citește antetul „Luna LL/AAAA” al ferestrei (regexp propriu, nu ajutorul probat). Ieșirea: proba_la_luna.txt (ecran | țintă | antet citit | verde/roșu)."""
import importlib.util
import os
import re
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
E2E = os.path.join(RAD, "frontend_test", "e2e")
for cale in (E2E, RAD, os.path.join(RAD, "scripts")):
    if cale not in sys.path:
        sys.path.insert(0, cale)

# conftest.py din rădăcină (încărcat de pytest) ascunde conftest.py din frontend_test/e2e, pe care îl importă `x09_C0` și e2e_bloc_e; proba îl pune pe cel din e2e
_spec = importlib.util.spec_from_file_location("conftest", os.path.join(E2E, "conftest.py"))
_conf = importlib.util.module_from_spec(_spec)
sys.modules["conftest"] = _conf
_spec.loader.exec_module(_conf)
from conftest import BAZA, LAT, INALT, Ecran, browser, sesiune  # noqa: E402,F401  (`browser` e fixtura sesiunii)
from e2e_bloc_e import _la_luna  # noqa: E402

ADMIN = "dovada.71507@sesiuneab.test"
IESIRE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proba_la_luna.txt")
TOP = ".fereastra-overlay:not(.fundal) "
JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""
JS_ANTET = "() => { const f = [...document.querySelectorAll('.fereastra')].pop(); const m = f && f.innerText.match(/Luna (\\d{2})\\/(\\d{4})/); return m ? m[0] : null; }"
ECRANE = (("Casă", "#fa-casa", "#c-prev"), ("Registru jurnal", "#fa-jurnal", "#j-prev"), ("Stocuri", "#fa-stocuri", "#s-prev"))
RANDURI = []


def _parcurs():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _antet(c):
    return "Luna %02d/%d" % (c % 12 + 1, c // 12)


@pytest.mark.parametrize("nume,card,prev", ECRANE, ids=[e[0] for e in ECRANE])
def test_proba_la_luna(browser, nume, card, prev):
    from core import ceas_proba
    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
    ctx.clock.set_fixed_time(ceas_proba.MOMENT_REF)
    ctx.add_init_script(sesiune(ADMIN))
    ecran = Ecran(ctx.new_page(), "proba_la_luna")
    pg = ecran.pg
    rele = []
    try:
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        _parcurs().firma(pg, "F1 Comert Stoc")
        assert pg.evaluate(JS_DESCHIDE_CARD, card) == "ok"
        pg.click(TOP + card, timeout=10000)
        pg.wait_for_function(JS_ANTET, timeout=30000)
        m = re.match(r"Luna (\d{2})/(\d{4})", pg.evaluate(JS_ANTET))
        L = int(m.group(2)) * 12 + int(m.group(1)) - 1
        for eticheta, tinta in (("L-1", L - 1), ("L", L), ("L-2", L - 2)):
            verde, citit = True, None
            try:
                _la_luna(ecran, prev, tinta // 12, tinta % 12 + 1)
                citit = pg.evaluate(JS_ANTET)
                verde = citit == _antet(tinta)
            except Exception as e:  # noqa: BLE001 — rândul devine roșu, cu motivul
                verde, citit = False, "excepție: %s" % str(e)[:120].replace("\n", " ")
            RANDURI.append("%s | %s (%s) | %s | %s" % (nume, _antet(tinta), eticheta, citit, "verde" if verde else "roșu"))
            if not verde:
                rele.append(RANDURI[-1])
    finally:
        ctx.close()
        with open(IESIRE, "a", encoding="utf-8") as f:
            f.write("\n".join(RANDURI) + "\n")
        RANDURI.clear()
    assert not rele, "; ".join(rele)
