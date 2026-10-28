# -*- coding: utf-8 -*-
"""Lotul 14, 687 — Balanță: după ce contabilul deschide un card-rezumat (ex. «Ciorne nevalidate») și apasă „înapoi”, balanța rămâne pe
LUNA aleasă de el. DEFECT DE PRODUS găsit la repararea testelor (agentA): azi revine pe luna curentă (probat: 07/2026 -> 10/2026), deci
contabilul își pierde luna și citește cifrele altei luni. Testul e ROȘU până se repară produsul."""
from e2e_bloc_e import _balanta, _nota, firma  # noqa: F401


def test_def_lot14_balanta_ramane_pe_luna_aleasa_dupa_inapoi(patron, firma):
    v = _nota(firma, "2026-07-05", [{"debit": "5311", "credit": "1012", "suma": "1000.00"}], "Aport capital", valideaza=True)
    c = _nota(firma, "2026-07-06", [{"debit": "5311", "credit": "1012", "suma": "250.00"}], "Aport capital — ciornă")
    pg = patron.pg
    _balanta(patron, firma, 2026, 7)
    inainte = " ".join(pg.inner_text(".fereastra:last-of-type").split())[:260]
    n_f = pg.locator(".fereastra").count()
    pg.click("[data-card='ciorne']")
    pg.wait_for_selector("#b-ciorne", timeout=30000)
    n_f2 = pg.locator(".fereastra").count()
    pg.click(".fereastra:last-of-type .nav-sageata.nav-inapoi")
    pg.wait_for_timeout(2000)
    dupa = " ".join(pg.inner_text(".fereastra:last-of-type").split())[:260]
    n_f3 = pg.locator(".fereastra").count()
    patron.captura("dupa_inapoi")
    assert inainte == dupa, ("INAINTE", n_f, inainte, "DUPA", n_f3, n_f2, dupa)
