# -*- coding: utf-8 -*-
"""Lotul 9, închiderea (Costin 19.10.2026, verbatim în DECIZII „Închiderea lotului 9: comanda și deciziile”): 412 — „Adeverință: Funcția,
Tipul contractului, Nr./Data CIM se precompletează din fișă.” Decizia: „Da, în fișa salariatului” — tipul contractului și Nr. / Data
CIM se scriu pe fișa salariatului („Corectează datele”, la sfârșitul rândului de câmpuri), iar „Adeverință” le arată precompletate,
modificabile. (Funcția din COR: `e2e_lot92.py::test_def_412_adeverinta_precompleteaza_functia_din_fisa`.)

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firma nouă a lui `e2e_lot92` (`firma_cv`), cu salariatul probelor
411–414 (`_salariat_cu_cm`: IONESCU VASILE, CNP 1900101410011 — cifra de control verificată cu algoritmul din CLAUDE.md)."""
import re

from conftest import sql
from e2e_lot92 import _salariat_cu_cm, _stat, firma_cv, firma_cv_noua  # noqa: F401 — fixturile modulului

_RAND = "IONESCU VASILE"
_FISA = re.compile(r"/tenants/\d+/salariati/\d+$")


def _fisa_citita(pg):
    """Așteaptă răspunsul GET-ului fișei (din care se precompletează câmpurile CIM)."""
    return pg.expect_response(lambda r: r.request.method == "GET" and _FISA.search(r.url.split("?")[0]) is not None, timeout=20000)


def test_def_412_adeverinta_precompleteaza_tipul_si_cim_din_fisa(patron, firma_cv):
    """412. Pașii: Salariați -> „Corectează datele” la IONESCU VASILE -> Tip contract „determinată”, Nr. CIM „12/2023”, Dată CIM
    20.12.2023 -> „Salvează” -> fișa le păstrează (redeschisă, le arată) -> „Adeverință”: Tip contract, Nr. CIM și Dată CIM vin
    precompletate din fișă, iar câmpul rămâne modificabil."""
    s = firma_cv["schema"]
    sid = _salariat_cu_cm(firma_cv)
    sql('UPDATE "%s".salariati SET tip_contract = NULL, nr_cim = NULL, data_cim = NULL WHERE id = %%s' % s, (sid,))  # rulare repetată
    pg = _stat(patron, firma_cv)
    rand = pg.locator(".pf-frand", has_text=_RAND).first
    with _fisa_citita(pg):
        rand.locator("[data-date]").click()
    pg.select_option("#ed-tipcim", "determinata")
    pg.fill("#ed-nrcim", "12/2023")
    pg.fill("#ed-datacim", "2023-12-20")
    pg.click("#ed-save")
    pg.wait_for_function("() => !document.querySelector('#ed-save')", timeout=20000)
    assert sql('SELECT tip_contract, nr_cim, data_cim::text FROM "%s".salariati WHERE id = %%s' % s, (sid,)) == \
        [("determinata", "12/2023", "2023-12-20")]
    # fișa redeschisă arată CIM-ul salvat
    rand = pg.locator(".pf-frand", has_text=_RAND).first
    with _fisa_citita(pg):
        rand.locator("[data-date]").click()
    pg.wait_for_function("() => (document.querySelector('#ed-nrcim') || {}).value === '12/2023'", timeout=20000)
    assert (pg.input_value("#ed-tipcim"), pg.input_value("#ed-datacim")) == ("determinata", "2023-12-20")
    pg.click("#ed-cancel")
    # adeverința le ia din fișă, modificabile
    rand = pg.locator(".pf-frand", has_text=_RAND).first
    rand.locator("[data-adev]").click()
    pg.wait_for_function("() => (document.querySelector('#ad-nrcim') || {}).value === '12/2023'", timeout=20000)
    assert (pg.input_value("#ad-tip"), pg.input_value("#ad-datacim")) == ("determinata", "2023-12-20")
    assert pg.is_editable("#ad-nrcim") and pg.is_enabled("#ad-tip")
    assert pg.locator(".pf-intro", has_text="Tipul contractului și Nr. / Dată CIM vin din fișa salariatului — le poți schimba.").count() == 1
    patron.captura()
