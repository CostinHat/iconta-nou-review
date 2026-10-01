# -*- coding: utf-8 -*-
"""GARD: căsuța unei bife cu etichetă (`.set-bifa`, DS v2.11) nu se strivește sub dimensiunea ei (02.10.2026).

DE CE. `.set-bifa` e flex; fără `flex-shrink: 0`, o etichetă lungă care se rupe pe două rânduri comprimă căsuța
(măsurat: 13px în loc de 16px, pe telefon, la bifa D212 „Include venitul din registrul RIP"). Instanța s-a văzut
într-o probă; clasa e regula CSS — deci gardul stă pe regulă, nu pe ecran.

CE NU VEDE: un `style` inline care ar suprascrie (interzis de DS v2.11 pe `.set-bifa`, păzit de verificator).
"""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _regula(css):
    m = re.search(r"\.set-bifa input\s*\{([^}]*)\}", css)
    return m.group(1) if m else None


def test_casuta_set_bifa_nu_se_comprima():
    r = _regula(open(os.path.join(RAD, "static", "stil.css"), encoding="utf-8").read())
    assert r is not None, "regula `.set-bifa input` lipsește din stil.css"
    assert re.search(r"flex-shrink\s*:\s*0", r), "`.set-bifa input` fără flex-shrink:0 — eticheta lungă strivește căsuța"


def test_CALIBRARE():
    assert re.search(r"flex-shrink\s*:\s*0", _regula(".set-bifa input { width: 16px; flex-shrink: 0; }"))
    assert not re.search(r"flex-shrink\s*:\s*0", _regula(".set-bifa input { width: 16px; }"))
