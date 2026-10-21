# -*- coding: utf-8 -*-
"""[lotul 10, găsit de uneltele vizuale (axe `empty-table-header`) pe Date firmă și Clienți] Coloana butoanelor de pe rând avea antetul
gol (`<th></th>`): un cititor de ecran anunța o coloană fără nume. Clasa (șapte locuri, în cinci ecrane) primește antetul „Acțiune”.
GARD: niciun șablon din `static/js` nu scrie un `<th>` gol. MUTAȚIE: un antet readus la `<th></th>` -> pică."""
import glob
import io
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_GOL = re.compile(r"<th(?:\s[^>]*)?>\s*</th>")


def test_niciun_antet_de_tabel_gol():
    rele = []
    for f in sorted(glob.glob(os.path.join(_RAD, "static", "js", "**", "*.js"), recursive=True)):
        for i, ln in enumerate(io.open(f, encoding="utf-8"), 1):
            if _GOL.search(ln):
                rele.append("%s:%d" % (os.path.relpath(f, _RAD), i))
    assert rele == [], rele


def test_scanul_vede_antetul_gol():
    """Anti-vacuu."""
    assert _GOL.search('<th class="cap-num">Rată</th><th></th>') and _GOL.search("<th >  </th>")
    assert not _GOL.search("<th>Acțiune</th>")
