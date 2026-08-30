# -*- coding: utf-8 -*-
"""[Regula 13 PERIMETRU + #3 din roadmap] GARD: harta ecranelor nu crește TĂCUT. Fiecare ecran de firmă
(`#fa-*` în static/js) trebuie să fie în inventarul cunoscut; un ecran NOU neînregistrat PICĂ → forțează o
decizie conștientă: fie îl adaugi în `frontend_test/vizual/nav_ecrane.ECRANE` (scanat vizual/comportamental
de `test_acoperire_vizuala`), fie îl adaugi aici în baseline ca DATORIE de scanat.

v1 (19.08, campania gardare #3): baseline = cele 27 ecrane existente. Doar 6 sunt în ECRANE (scanate); restul
= datorie de scanat, se mută din baseline în ECRANE incremental. Scopul acum: niciun ecran NOU nu scapă.
"""
import os
import re
import glob
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Inventarul ecranelor de firmă la 19.08.2026. Un ecran nou => se adaugă AICI (conștient) + de preferat în ECRANE.
_BASELINE = {
    "fa-acces", "fa-balanta", "fa-banca", "fa-bilant", "fa-bonuri", "fa-casa", "fa-centrecost", "fa-contracte",
    "fa-control", "fa-datefirma", "fa-declaratii", "fa-etransport", "fa-facturi",
    # [lista 3, 30.08.2026] doua artefacte care aveau producator si nu ajungeau la om:
    # Cartea mare (fisa de cont 14-6-22) si jurnalul special de regim marja (normele CF, pct. 86).
    "fa-fisacont", "fa-marja",
    "fa-import", "fa-jurnal",
    "fa-magazin", "fa-mijloace", "fa-operatiuni", "fa-produse", "fa-rapoarte", "fa-raportz", "fa-registratura",
    "fa-rip", "fa-salariati", "fa-solicitari", "fa-stocuri", "fa-verificari",
}


def _ecrane_din_cod():
    ids = set()
    for f in glob.glob(os.path.join(_RAD, "static", "js", "**", "*.js"), recursive=True):
        ids |= set(re.findall(r"\bfa-[a-z]+\b", open(f, encoding="utf-8").read()))
    return ids


def test_harta_ecrane_nu_creste_tacut():
    noi = _ecrane_din_cod() - _BASELINE
    assert not noi, ("ecran(e) `#fa-*` NOU neînregistrat: %s. Adaugă-l în frontend_test/vizual/nav_ecrane.ECRANE "
                     "(ca să fie scanat de test_acoperire_vizuala) SAU în _BASELINE aici (datorie de scanat, conștientă)."
                     % sorted(noi))


def test_baseline_nu_are_ecrane_disparute():
    """Un ecran din baseline care nu mai există în cod = baseline stătut (curăță-l)."""
    disparute = _BASELINE - _ecrane_din_cod()
    assert not disparute, "ecrane în _BASELINE care nu mai există în cod (curăță baseline): %s" % sorted(disparute)
