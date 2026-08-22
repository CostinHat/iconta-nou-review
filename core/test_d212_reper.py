# -*- coding: utf-8 -*-
"""D212: salariul minim REPER vine din cota() (nu literal 4050) -> dependenta D212->salariu_minim VIZIBILA
in graf (inchide blind-spot-ul V2). Valoare neschimbata (4050 = sm la 1 ian, fix pe an fiscal)."""

# [R17 23.08.2026] Cheile grafului sunt CALIFICATE ("fisier.py::nume") de cand `graf_temei` nu mai
# conflateaza functii omonime din fisiere diferite. Afirmatiile de mai jos numesc acum si FISIERUL:
# inainte treceau daca ORICE functie din core/ cu numele cerut aparea in graf.
from core import d212_engine as d
from core.graf_temei import depinde_de


def test_d212_reper_din_cota_nu_literal():
    assert d._sm_reper(2025) == 4050        # din cota("salariu_minim", 1 ian 2025), nu hardcodat
    assert d._sm_reper(2026) == 4050        # 1 ian 2026 = 4050 (majorarea 4325 din iulie NU atinge reperul)
    assert d.PLAFOANE_VENIT_2025.salariu_minim == 4050
    assert d.PLAFOANE_VENIT_2026.salariu_minim == 4050 and d.PLAFOANE_VENIT_2026.cass_prag_max_sm == 72


def test_d212_apare_in_graful_salariu_minim():
    """Dupa reroute: graful vede D212 depinzand de salariu_minim (V2 blind-spot inchis)."""
    dep = depinde_de("salariu_minim")
    d212 = [n for n in dep if n.split("::")[-1] in ("_sm_reper", "plafoane_an")]
    assert d212, "d212_engine NU apare in graful salariu_minim dupa reroute prin cota()"
