# -*- coding: utf-8 -*-
"""Proba de unică folosință (17.5-C, pct.4): căderea pe lista goală. Cererea GET perioade-blocate interceptată, o dată cu răspuns `{}`, o dată cu eroare de
rețea: Balanța se deschide pe luna trecută (10/2026, ceas înghețat 03.11.2026), fără mesaj de eroare. Nu e unealtă și nu intră în poartă.
Rulare: pytest -q -p no:cacheprovider docs/dovezi/17_5_C/cadere_blocate_proba.py  (cu mediul serverului de lucru)"""
import os
import re
import sys

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "frontend_test", "e2e"))
sys.modules.pop("conftest", None)   # pytest a încărcat conftest.py din rădăcină; testul arhitectului cere pe cel din frontend_test/e2e
import e2e_luna_lucru_17_5_C as t  # noqa: E402
from conftest import BAZA, sesiune  # noqa: E402


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        yield b
        b.close()


def _ruleaza(browser, tratare, nume):
    from core import ceas_proba
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(t.ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        tid = t._tenant(pg)
        tipar = re.compile(r".*/tenants/%d/perioade-blocate(\?.*)?$" % tid)
        pg.route(tipar, tratare)
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        luna = t._luna_ecranului(pg, t._incarca_parcurs_17_1(), "#fa-balanta")
        text = pg.evaluate("() => { const f = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop(); return f ? f.innerText : ''; }")
        mesaje = re.findall(r"[^\n]*(?:eroare|nu s-a putut|nu am putut|e[șs]uat)[^\n]*", text, re.I)
        print("CADERE %s: luna=%s, mesaje=%s" % (nume, luna, mesaje))
        assert luna == "10/2026", "%s: Balanța pornește pe %s, nu pe 10/2026" % (nume, luna)
        assert not mesaje, "%s: mesaj de eroare pe ecran: %s" % (nume, mesaje)
    finally:
        b.close()


def test_raspuns_gol(browser):
    _ruleaza(browser, lambda r: r.fulfill(status=200, content_type="application/json", body="{}"), "răspuns {}")


def test_eroare_de_retea(browser):
    _ruleaza(browser, lambda r: r.abort("failed"), "eroare de rețea")
