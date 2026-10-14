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


def test_tabelele_cu_derulare_proprie_sunt_focusabile():
    """[14.10.2026, importul din SAGA — axe mobil pe previzualizarea istoricului] `.mig-sold-tabel` are derulare proprie
    (`max-height` + `overflow-y: auto`, static/stil.css): pe telefon, cu rânduri lungi, se derulează și trebuie să poată fi atins
    din tastatură (WCAG 2.1.1, axe `scrollable-region-focusable`). Aceeași clasă ca `.fereastra-corp` de mai sus, pe toate cele 7
    tabele (6 previzualizări de import + jurnalul de activitate). MUTAȚIA: `tabindex` scos de pe unul -> ROȘU."""
    import glob
    rele = []
    for p in glob.glob("static/js/**/*.js", recursive=True):
        for m in re.finditer(r'<div class="mig-sold-tabel[^"]*"[^>]*>', open(p, encoding="utf-8").read()):
            if 'tabindex="0"' not in m.group(0):
                rele.append("%s: %s" % (p, m.group(0)))
    assert not rele, "tabel cu derulare proprie nefocusabil:\n" + "\n".join(rele)
