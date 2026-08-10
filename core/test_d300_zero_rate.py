# -*- coding: utf-8 -*-
"""Gard Task1 (10.08.2026): liniile cu cotă 0% NU mai dispar tacit din D300.

Confruntat cu sursa oficiala (anaf_surse/d300_struct_anaf.txt):
  - rd.26 (R26_1) = "Achizitii de bunuri si servicii scutite de taxa sau neimpozabile" (nr.crt.99).
  - rd.14 (R14_1) = livrari scutite CU drept de deducere; rd.15 (R15_1) = scutite FARA drept.

NECONFORMITATE (HEAD 6cd0054): achizitiile 0% CURATE nu ajungeau in R26 (doar un avertisment
agregat) -> operatiunea disparea din decont. Livrarile 0% nu erau nici clasificate nici numite
per-linie. Nu exista camp de natura a scutirii in factura, deci livrarile NU se pot clasifica
automat (R14 vs R15) - se semnaleaza per-linie, fara sa se inventeze clasificarea.

POST-FIX: achizitie 0% curata -> R26_1 (apare in decont); livrare 0% -> avertisment per-linie
care NUMESTE suma; forfait agricol (TVA orfan) si art.331 (categorie_331) NU merg la R26.
"""
from decimal import Decimal
from core.common import Perioada
from core.d300 import calcul_d300


def _prof():
    return {"cui": "14399840", "nume": "X", "banca": "BCR", "iban": "RO1", "caen": "4711",
            "tip_decont": "L", "pro_rata": 100}


def test_achizitie_0_scutita_deriva_R26():
    """MUTATIE (RED pe HEAD: R26_1 lipsea): achizitie 0% curata -> R26_1 = baza."""
    f = {"directie": "primita", "linii": [(1, 1500, 0)]}
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [f])
    assert res.R.get("R26_1") == 1500, "achizitia 0% scutita trebuie declarata la R26_1 (nu dispare tacit)"
    # R26 e informativ: NU intra in deductibila (R27) si nu afecteaza TVA de plata.
    assert res.R.get("R27_2", 0) == 0
    assert res.tva_de_plata == 0 and res.tva_de_recuperat == 0


def test_livrare_0_nu_se_inventeaza_clasificarea_dar_se_numeste():
    """Livrare 0%: natura scutirii (R14 cu drept vs R15 fara drept) NU e capturata -> NU se
    inventeaza; se semnaleaza per-linie NUMIND suma. Doua livrari 0% distincte -> doua avertismente."""
    facturi = [
        {"directie": "emisa", "linii": [(1, 2000, 0)]},
        {"directie": "emisa", "linii": [(1, 3000, 0)]},
    ]
    res = calcul_d300(_prof(), Perioada(2026, luna=8), facturi)
    assert "R14_1" not in res.R and "R15_1" not in res.R, "livrarea 0% NU se clasifica automat"
    assert "R26_1" not in res.R, "livrarea (nu achizitie) NU merge la R26"
    liv = [a for a in res.avertismente if "Livrare cu cotă 0%" in a]
    assert len(liv) == 2, "asteptam avertisment PER-LINIE (HEAD: unul agregat); got %r" % res.avertismente
    assert any("2.000 lei" in a for a in liv) and any("3.000 lei" in a for a in liv), \
        "fiecare avertisment trebuie sa NUMEASCA suma liniei"


def test_achizitie_331_zero_NU_merge_la_R26():
    """Achizitie 0% cu categorie_331 (art.331 taxare inversa, rata pierduta) NU e scutita/neimpozabila
    -> NU merge la R26; avertisment dedicat care cere declararea la R12/R25."""
    f = {"directie": "primita", "categorie_331": "cereale", "linii": [(1, 300, 0)]}
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [f])
    assert res.R.get("R26_1", 0) == 0, "art.331 nu e scutit -> nu R26"
    assert any("art.331" in a and "300 lei" in a for a in res.avertismente)


def test_forfait_orfan_zero_NU_merge_la_R26():
    """Achizitie 0% cu TVA orfan in antet (forfait agricol) NU e scutita -> NU merge la R26."""
    f = {"directie": "primita", "total": 27000, "tva": 2000, "linii": [(1, 25000, 0)]}
    res = calcul_d300(_prof(), Perioada(2026, luna=8), [f])
    assert res.R.get("R26_1", 0) == 0, "forfait (TVA orfan) nu e scutit -> nu R26 (semnalat de avert orfan)"
