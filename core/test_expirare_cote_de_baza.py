# -*- coding: utf-8 -*-
"""Gard: o valoare fiscala expirata NU se foloseste tacit.

DE CE (29.07.2026): `cota()` intorcea ultima valoare cunoscuta pentru orice data viitoare.
In ianuarie 2027, D112 ar fi generat cu salariul minim din iulie 2026 - o cifra plauzibila
si gresita intr-o declaratie depusa la ANAF, fara niciun semnal.

Cotele au "de cand", n-au "pana cand". Pentru valorile actualizate periodic prin act normativ
nou (HG anuala pentru salariul minim, OUG pentru facilitati), lipsa unei valori noi NU
inseamna ca cea veche ramane - inseamna ca nimeni n-a actualizat registrul.
"""
from datetime import date

import pytest

from core.common import COTE, EXPIRA_DUPA_LUNI, cota, cote_care_expira


def test_valoarea_curenta_se_intoarce_normal():
    v, t = cota("salariu_minim", date(2026, 6, 1))
    assert int(v) == 4050 and "1506" in t   # 2026 H1: HG 1506/2024 in vigoare 01.01.2025..30.06.2026 (abrogat la 01.07.2026 de HG salariu minim 2026, ART.2)


def test_salariu_minim_2025_este_4050_hg_1506():
    """Salariul minim 2025 = 4050 lei de la 1 ian 2025 (HG 1506/2024, MO 1185/28.11.2024, abroga
    HG 598/2024=3700). Bug inchis 31.07.2026: tabelul avea 2025=3700 (valoarea VECHE, 2024 H2) ->
    calcul salariu 2025 gresit. Sursa: legislatie.just.ro Public/DetaliiDocument/291450."""
    v, t = cota("salariu_minim", date(2025, 3, 1))
    assert int(v) == 4050, "salariu minim 2025 gresit: %s (asteptat 4050, HG 1506/2024)" % v
    assert "1506" in t, "temeiul salariului minim 2025 nu citeaza HG 1506/2024: %r" % t


def test_valoarea_expirata_ridica():
    """2027 depaseste valabilitatea de 12 luni a intrarii din 01.07.2026."""
    with pytest.raises(ValueError) as e:
        cota("salariu_minim", date(2027, 9, 1))
    m = str(e.value)
    assert "2026-07-01" in m, "mesajul nu spune din cand e valoarea veche"
    assert "actualiz" in m.lower(), "mesajul nu spune ce trebuie facut"


def test_strict_false_da_valoarea_veche():
    """Rapoartele istorice si comparatiile au voie sa ceara valoarea veche, EXPLICIT."""
    v, _ = cota("salariu_minim", date(2027, 9, 1), strict=False)
    assert int(v) == 4325


def test_cotele_fara_expirare_merg_oricand():
    """TVA se schimba prin lege, nu periodic - n-are termen."""
    v, _ = cota("tva_standard", date(2030, 1, 1))
    assert v > 0


def test_fiecare_valoare_cu_expirare_exista_in_registru():
    """Altfel jobul de avertizare tace pe o valoare care nu se poate verifica."""
    lipsa = [n for n in EXPIRA_DUPA_LUNI if n not in COTE]
    assert not lipsa, "in EXPIRA_DUPA_LUNI dar nu in COTE: %s" % lipsa


def test_cote_care_expira_da_termenul_si_temeiul():
    r = cote_care_expira(400, la_data=date(2026, 7, 29))
    assert r, "nicio valoare nu expira in 400 de zile - verifica registrul"
    for x in r:
        assert x["temei"] and x["expira"] and x["zile"] >= 0
    assert any(x["nume"] == "salariu_minim" for x in r)
