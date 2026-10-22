# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.1 (Costin 21.10.2026, verbatim în DECIZII „Comanda 11.1”) — subagentul w5: deficiența 440 pe D212, pct.16
(verbatim): „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp. Fără «motivul e mai sus». Pe toată aplicația.”

W3b a adunat refuzurile D212 ÎNTRE secțiuni; în INTERIORUL unui venit (I.1.1) și al unui venit din străinătate (cap14) serverul se oprea
încă la prima greșeală: contabilul vedea un motiv pe venit, îl corecta, genera din nou și afla de următorul. Pașii contabilului pe
aplicația din index, pe baza de TEST, pe o PFA NOUĂ (`firma_noua("pfa")`, ca în `e2e_lot93d`); niciun INSERT — venitul și venitul din
străinătate se adaugă din formularul D212, generarea e butonul „Regenerează D212”.

Lângă câmp: rândurile adăugate sunt liste fără câmpuri (formularul de adăugare se golește la „+ adaugă”), deci motivele serverului stau în
caseta generării, fiecare cu venitul lui în față. Mutațiile: frontend_test/e2e/mut_lot11_w5.json."""
import pytest

from conftest import firma_noua


@pytest.fixture()
def pfa_w5():
    for f in firma_noua("pfa"):
        yield f


def _alege(pg, sel, val):
    pg.select_option(sel, val)
    pg.dispatch_event(sel, "change")


def test_def_440_d212_toate_greselile_din_venit_deodata(patron, pfa_w5):
    """440 (D212, în interiorul secțiunii). Pașii: PFA nouă -> Declarații -> D212 pe 2025 -> CNP / nume / adresă -> fără venit din
    registru, nicio excepție CASS -> venitul 1: drepturi de proprietate intelectuală, cote forfetare, cu patru greșeli independente
    (zile scutite 400, data începerii în 2024, cheltuieli 100 — le stabilește cota, pierderi reportate 50 — nu există la cote forfetare)
    -> venitul din străinătate 1: pensie din „XX”, 0 luni, 2 luni cu CASS în România (trei greșeli) -> Regenerează D212: caseta spune
    „7 motive”, numerotate, patru pe „Venitul 1”, trei pe „Venitul din străinătate 1”, fiecare cu textul lui.
    Înainte: „2 motive” (câte unul pe secțiune).
    MUTAȚIA 1: în core/d212.py zilele scutite în afara anului `motive.append(` -> `raise ValueError(` -> ROȘU (venitul 1 un singur motiv).
    MUTAȚIA 2: în core/d212.py țara din străinătate `motive.append(` -> `raise ValueError(` -> ROȘU (venitul din străinătate un motiv).
    MUTAȚIA 3: în static/stil.css `.dec-eroare` `white-space: pre-line` -> `normal` -> ROȘU (caseta pe un singur rând: motivele nu se
    mai despart, DS cap.6 v2.89 „o listă, rând cu rând”)."""
    from conftest import alege_perioada, alege_tipul
    from e2e_bloc_a import _card, pregateste_firma
    f = pfa_w5
    pregateste_firma(patron, f, forma=False, regim_fiscal=None)   # PFA: fără regim micro / profit (serverul îl refuză)
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "declaratii", "#dec-tip")
    alege_tipul(pg, "d212")
    alege_perioada(pg, 2025)
    pg.wait_for_selector("#dec-continua:not([disabled])", timeout=8000)
    pg.click("#dec-continua")
    pg.wait_for_selector("#d212-cnp", timeout=30000)
    for sel, v in (("#d212-cnp", "1800101221144"), ("#d212-nume", "POPESCU ION"), ("#d212-adr", "Bucuresti Sector 1")):   # CNP: cifra de control verificată
        pg.fill(sel, v)
        pg.dispatch_event(sel, "change")
    _alege(pg, "#d212-rip", "false")
    pg.select_option("#d212-exccass", label="nicio excepție — CASS cel puțin la baza de 6 salarii minime")
    pg.dispatch_event("#d212-exccass", "change")
    # venitul 1 — DPI, cote forfetare, patru greșeli independente
    _alege(pg, "#d212-v-cat", "1003")
    _alege(pg, "#d212-v-det", "2")
    _alege(pg, "#d212-v-faracota", "false")
    _alege(pg, "#d212-v-forma", "1")
    for sel, v in (("#d212-v-brut", "12000"), ("#d212-v-chelt", "100"), ("#d212-v-pp", "50"), ("#d212-v-scut", "400"),
                   ("#d212-v-inc", "2024-06-01")):
        pg.fill(sel, v)
    pg.click("#d212-v-add")
    pg.wait_for_selector(".d212-v-del", timeout=8000)
    # venitul din străinătate 1 — pensie, trei greșeli independente
    _alege(pg, "#d212-s-cat", "2020")
    _alege(pg, "#d212-s-faracontrib", "false")
    for sel, v in (("#d212-s-tara", "XX"), ("#d212-s-brut", "40000"), ("#d212-s-luni", "0"), ("#d212-s-lunicass", "2")):
        pg.fill(sel, v)
    pg.click("#d212-s-add")
    pg.wait_for_selector(".d212-s-del", timeout=8000)
    pg.click("#d212-regen")
    pg.wait_for_selector(".dec-eroare", timeout=90000)
    txt = pg.inner_text(".dec-eroare")
    patron.captura()
    assert "D212 nu se poate genera — 7 motive" in txt, txt                  # 440: toate deodată (înainte: 2 motive)
    # rând cu rând (DS cap.6 v2.89): `innerText` păstrează rândurile numai dacă caseta le păstrează (`white-space: pre-line`)
    randuri = [r.strip() for r in txt.split("\n") if r.strip()[:2].rstrip(".").isdigit()]
    assert [r.split(" — ")[0] for r in randuri] == ["%d. Venitul 1" % i for i in range(1, 5)] + \
        ["%d. Venitul din străinătate 1" % i for i in range(5, 8)], txt
    for t in ("zilele scutite trebuie să fie între 0", "data începerii (2024-06-01) nu e în anul 2025",
              "la cote forfetare nu se reportează pierderi", "la cote forfetare cheltuielile se calculează",
              "țara 'XX' nu e în nomenclatorul ANAF", "numărul lunilor cu pensie în an (1-12) e obligatoriu",
              "CASS datorată în România pe pensia din străinătate"):
        assert t in txt, (t, txt)                                            # fiecare cu textul lui
