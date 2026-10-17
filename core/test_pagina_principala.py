# -*- coding: utf-8 -*-
"""GARD (12.10.2026) — pagina principală are aceeași structură la ambele roluri; „Recomandă” și „Suport” sunt benzile de deasupra
cardurilor; cardul Control fiscal e un rând cu patru buline și numerele lor, la înălțimea celorlalte carduri.

Comanda Costin 12.10.2026, verbatim în DECIZII: 224 „Cardul arată doar un rând cu 4 buline colorate și numărul fiecăreia, fără text, iar
înălțimea lui e la fel cu a celorlalte carduri.” · 225 „«Recomandă» și «Suport» sunt două benzi înguste, una lângă alta, deasupra
cardurilor, la ambele roluri, ca la Cabinet.” · 231 „la Ana, scoate meniul din stânga care repetă cardurile. Pagina principală are aceeași
structură la ambele roluri.” Supersedează garda arborelui asistentului (R175, `test_asistent_arbore`, 06.09.2026).

Așezarea nu se probează citind sursa: se MĂSOARĂ în browser, pe arborele de randare — `frontend_test/proba_pagina_principala.py`, la
contabilul-șef și la asistent. Garda ține proba VIE: artefactul poartă `ui_hash` (ca `test_acoperire_vizuala`), deci un `cabinet.js` /
`asistent.js` / `salut.js` / `stil.css` schimbat după probă face garda roșie până la reprobare. ANTI-VACUU: se cer ambele roluri, ambele
benzi, cardurile și luminile — un artefact gol nu trece.
"""
import json
import os
import re
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "frontend_test", "vizual"))
from acoperire_hash import ui_hash  # noqa: E402

ARTEFACT = os.path.join(_RAD, "frontend_test", "proba_pagina_principala.json")
ROLURI = ("cabinet", "asistent")


def _proba():
    if not os.path.exists(ARTEFACT):
        pytest.fail("proba paginii principale lipsește — rulează frontend_test/proba_pagina_principala.py pe instanța de probă")
    return json.load(open(ARTEFACT, encoding="utf-8"))


def test_proba_e_proaspata():
    """UI-ul nu s-a schimbat de la ultima probare a paginii principale."""
    assert _proba().get("ui_hash") == ui_hash(), (
        "UI-ul s-a schimbat de la ultima probare a paginii principale — rulează frontend_test/proba_pagina_principala.py și comite artefactul")


@pytest.mark.parametrize("rol", ROLURI)
def test_aceeasi_structura_fara_meniu_lateral(rol):
    """231: sub conținutul paginii, exact banda de salut și grila de carduri, la ambele roluri; niciun meniu lateral.
    MUTAȚIE: arborele asistentului readus -> structura are trei elemente și meniul lateral apare -> pică."""
    m = _proba()["roluri"][rol]
    # [319 + 320] zona cardurilor de început (`inceput`) stă între banda de salut și grilă, cât timp are carduri nefăcute (DS cap.12b)
    assert [x for x in m["structura"] if x != "inceput"] == ["cab-salut", "cab-grila"], m["structura"]
    assert m["meniu_lateral"] == 0, m["meniu_lateral"]


@pytest.mark.parametrize("rol", ROLURI)
def test_recomanda_si_suport_benzi_deasupra_cardurilor(rol):
    """225: două benzi, „Recomandă” apoi „Suport”, pe același rând, deasupra grilei, mai scunde decât un card.
    MUTAȚIE: „Suport” înapoi card în grilă -> o singură bandă -> pică."""
    m = _proba()["roluri"][rol]
    b = m["benzi"]
    assert [x["titlu"] for x in b] == ["Recomandă", "Suport"], b
    assert abs(b[0]["top"] - b[1]["top"]) <= 1, b                              # una lângă alta
    assert max(x["bottom"] for x in b) <= m["grila_top"], (b, m["grila_top"])   # deasupra cardurilor
    assert max(x["h"] for x in b) < min(m["inaltimi_carduri"]), (b, m["inaltimi_carduri"])   # înguste


@pytest.mark.parametrize("rol", ROLURI)
def test_cardul_control_un_rand_de_buline_fara_text(rol):
    """224: patru lumini în ordinea roșu, galben, verde, gri, pe un rând, numai numere; înălțimea cardului = a celorlalte.
    MUTAȚIE: cardul întors pe semaforul ferestrei (listă cu text) -> textul și cele patru rânduri -> pică."""
    m = _proba()["roluri"][rol]
    c = m["control"]
    assert c and c["lumini"] == ["rosu", "galben", "verde", "gri"], c
    assert c["randuri"] == 1, c
    assert re.fullmatch(r"\d+( \d+){3}", c["text"]), c["text"]                  # numai numerele, fără nume de stare
    # înălțimea NATURALĂ (fără întinderea pe rând): rândul de lumini e cu ~2 px peste un rând de text; o listă adaugă un rând (~27 px)
    h = sorted(m["inaltimi_naturale"])
    assert abs(c["h"] - h[len(h) // 2]) <= 12, (c["h"], m["inaltimi_naturale"])   # înălțimea celorlalte carduri


@pytest.mark.parametrize("rol", ROLURI)
def test_pagina_e_curata_la_privire(rol):
    """axe (desktop), fără title-only, iar pe telefon nimic nu iese din ecran și benzile rămân ținte de atins."""
    m = _proba()["roluri"][rol]
    assert m["axe"]["violari"] == [], m["axe"]["violari"]
    to = m["axe"]["title_only"]
    assert sum(len(v) for v in to.values()) == 0, to
    assert m["mobil"] == {"revarsare_x": False, "benzi_sub_24": 0}, m["mobil"]
