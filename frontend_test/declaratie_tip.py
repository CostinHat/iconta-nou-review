# -*- coding: utf-8 -*-
"""Alegerea tipului de declarație pe ecranul Declarații — singurul loc din plasă și din unelte (garda: `core/test_e2e_perioada.py`).

[deficiența 301, comanda Costin 17.10.2026 7.2] „Alte declarații” e pliată și se deschide doar la cerere: un tip care nu e datorat
(ex. D390 la o firmă fără operațiuni intracomunitare) nu e în listă până la clicul pe „Alte declarații”. Ce alege tipul direct
(`select_option("#dec-tip", tip)`) a așteptat 30 de secunde o opțiune care nu era acolo (scanul de text, 17.10.2026). Aici, ca omul:
dacă tipul nu e în listă, deschide „Alte declarații”, apoi îl alege; dacă nici atunci nu e, pică spunând asta."""


def alege_tipul(pg, tip, zona=""):
    """Alege tipul `tip` (valoarea opțiunii, ex. „d300”) în `zona + "#dec-tip"`, deschizând „Alte declarații” dacă trebuie."""
    optiune = zona + "#dec-tip option[value='%s']" % tip
    if not pg.locator(optiune).count() and pg.locator(zona + "#dec-alte").count():
        if pg.get_attribute(zona + "#dec-alte", "aria-expanded") != "true":
            pg.click(zona + "#dec-alte")
        pg.wait_for_selector(optiune, state="attached", timeout=10000)
    assert pg.locator(optiune).count(), "tipul %s nu e în lista Declarații, nici în „Alte declarații”" % tip
    pg.select_option(zona + "#dec-tip", tip)
