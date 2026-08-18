# -*- coding: utf-8 -*-
"""[Regula 14.4 pct.4] GARD: formularul 'Adauga cont' (plan_conturi) semnaleaza obligativitatea INAINTE de
buton (asterisc) SI marcheaza campul gol la submit (contur rosu + aria-invalid), nu doar mesaj generic dupa
apasare. Provocat live pe tenant_006 in perimetrul stratului plan_conturi (Regula 13: se repara pe instanta).
"""
import os
import re
import pytest


def _js():
    p = "static/js/ecrane/migrare.js"
    if not os.path.exists(p):
        pytest.skip("migrare.js absent")
    return open(p, encoding="utf-8").read()


def _handler():
    m = re.search(r'#pc-adauga"\)\.addEventListener.*?\n  \}\);', _js(), re.DOTALL)
    return m.group(0) if m else ""


def test_obligativitate_inainte_de_buton():
    assert re.search(r'cont nou <span class="oblig">\*</span>', _js()), \
        "lipseste asteriscul de obligativitate pe eticheta 'Adauga cont nou' (semnalat abia dupa buton)"


def test_marcheaza_campul_gol():
    h = _handler()
    assert h, "handler #pc-adauga negasit"
    assert 'inpS.classList.add("camp-invalid")' in h and 'inpD.classList.add("camp-invalid")' in h, \
        "campul gol nu e marcat vizual (camp-invalid pe #pc-simbol/#pc-denumire)"


def test_mesajul_numeste_campul_lipsa():
    h = _handler()
    assert "simbolul contului" in h and "denumirea contului" in h, \
        "mesajul nu mai numeste exact campul lipsa (simbol vs denumire)"


def test_nu_mai_e_mesajul_generic():
    h = _handler()
    assert "Simbol \\u0219i denumire sunt obligatorii" not in h and "Simbol și denumire sunt obligatorii" not in h, \
        "inca foloseste mesajul generic care nu marcheaza campul vinovat"
