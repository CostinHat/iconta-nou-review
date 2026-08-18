# -*- coding: utf-8 -*-
"""[a11y WCAG 2.1.1 / Regula 14] GARD: corpul modal .fereastra-corp e focusabil din tastatura.

axe (mobil_scan + axe pe Pixel 5, audit tenant_006 strat solduri_parteneri) a scos 'scrollable-region-focusable'
pe .fereastra-corp: pe ecran ingust (393px) continutul ferestrei se deruleaza dar nu se putea focusa din
tastatura. .fereastra-corp e shell-ul modal PARTAJAT (navigator.js) -> fix o data = app-wide (toate ecranele).
"""
import os
import re
import pytest


def test_fereastra_corp_focusabila_din_tastatura():
    p = "static/js/navigator.js"
    if not os.path.exists(p):
        pytest.skip("navigator.js absent")
    s = open(p, encoding="utf-8").read()
    corps = re.findall(r'<div class="fereastra-corp"[^>]*>', s)
    assert corps, "fereastra-corp negasit in navigator.js"
    fara = [c for c in corps if "tabindex" not in c]
    assert not fara, "corp modal scrollabil nefocusabil (axe scrollable-region-focusable): %s" % fara
