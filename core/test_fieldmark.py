# -*- coding: utf-8 -*-
"""[Regula 13 + Regula 6] GARDA: marcajul vizual al campului cu eroare de validare (Regula 14 pct.4).

Bug (audit tenant_006, 18.08.2026): la salvarea unui formular cu camp obligatoriu gol, `eroareCamp` (api.js)
ancora mesajul rosu LANGA camp DAR nu marca inputul insusi (fara contur rosu) -> la un formular lung nu vezi
CARE input e problema. In plus, o regula globala contrast_ferestre_v1 forteaza `border ... !important` pe toate
inputurile (specificitate input:not(...)x6 = 0,6,1), deci un `.camp-invalid` simplu (0,1,0) nu invinge conturul.
Fix: eroareCamp adauga clasa `camp-invalid` (+ aria-invalid), curataEroriCamp o scoate, iar stil.css are un
override `input.camp-invalid:not(...)` cu specificitate mai mare pe border-color rosu. App-wide (7 ecrane folosesc
eroareCamp). Acest gard cade daca marcajul e scos din helper sau overrideul CSS dispare.
"""
import os
import re
import pytest


def _read(p):
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def test_eroareCamp_marcheaza_inputul():
    api = _read("static/js/api.js")
    if not api:
        pytest.skip("api.js absent")
    m = re.search(r"export function eroareCamp\(.*?\n\}", api, re.S)
    assert m, "eroareCamp negasit in api.js"
    corp = m.group(0)
    assert 'classList.add("camp-invalid")' in corp, \
        "eroareCamp nu marcheaza VIZUAL campul (lipseste classList.add('camp-invalid')) - Regula 14 pct.4"
    assert 'aria-invalid' in corp, "eroareCamp nu seteaza aria-invalid (a11y)"


def test_curataEroriCamp_scoate_marcajul():
    api = _read("static/js/api.js")
    if not api:
        pytest.skip("api.js absent")
    m = re.search(r"export function curataEroriCamp\(.*?\n\}", api, re.S)
    assert m, "curataEroriCamp negasit"
    assert "camp-invalid" in m.group(0), \
        "curataEroriCamp nu scoate marcajul camp-invalid -> campurile raman rosii dupa corectare"


def test_css_camp_invalid_invinge_bordura_globala():
    css = _read("static/stil.css")
    if not css:
        pytest.skip("stil.css absent")
    # override pe input cu clasa camp-invalid (specificitate > regula globala input:not(...)x6 !important)
    assert re.search(r"input\.camp-invalid[^{]*:not\([^{]*\{[^}]*border-color:\s*#a3231c", css, re.S), \
        "lipseste overrideul input.camp-invalid (border rosu) care invinge contrast_ferestre_v1 !important"
