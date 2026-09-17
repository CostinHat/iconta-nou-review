# -*- coding: utf-8 -*-
"""[A5, 17.09.2026] Partener non-UE: serviciile se rutează pe rd.3 / rd.7+rd.20, nu pe rd.14 / rd.26.

Constatarea A5: rutarea `strain and not ue` ignora `axa_ic` — orice emisă non-UE → rd.14 (export
bunuri), orice primită non-UE 0% → rd.26 (neimpozabil). Serviciile prestate au locul în afara RO
(rd.3); serviciile primite se autolichidează (rd.7 colectat + rd.20 deductibil). PICĂ pe codul de
dinainte (`{'R14_1': 1000}` / `{'R26_1': 1000}`), TRECE după.
"""
from collections import namedtuple

from core import d300

P = namedtuple("P", "an luna")


def test_servicii_emise_non_ue_rd3_nu_rd14():
    f = {"directie": "emisa", "tert_tara": "US", "axa_ic": "servicii",
         "moneda": "RON", "linii": [(1, 1000, 0)]}
    res = d300.calcul_d300({}, P(2026, 8), [f])
    assert res.R.get("R3_1") == 1000, "R3_1=%r (prestări servicii cu locul în afara RO)" % res.R.get("R3_1")
    assert res.R.get("R14_1", 0) == 0, "R14_1=%r — serviciile non-UE NU sunt export de bunuri" % res.R.get("R14_1")


def test_bunuri_emise_non_ue_raman_export_rd14():
    """Regresie: bunurile non-UE rămân export (rd.14) — reparația nu mută bunurile."""
    f = {"directie": "emisa", "tert_tara": "US", "axa_ic": "bunuri",
         "moneda": "RON", "linii": [(1, 1000, 0)]}
    res = d300.calcul_d300({}, P(2026, 8), [f])
    assert res.R.get("R14_1") == 1000
    assert res.R.get("R3_1", 0) == 0


def test_servicii_primite_non_ue_rd7_si_rd20_nu_rd26():
    f = {"directie": "primita", "tert_tara": "US", "axa_ic": "servicii",
         "moneda": "RON", "linii": [(1, 1000, 0)]}
    res = d300.calcul_d300({}, P(2026, 8), [f])
    # autolichidare: rd.7 colectat (bază 1000) + rd.20 deductibil (oglindă), NU rd.26
    assert res.R.get("R7_1") == 1000, "R7_1=%r (autolichidare servicii non-UE)" % res.R.get("R7_1")
    assert res.R.get("R26_1", 0) == 0, "R26_1=%r — serviciile primite non-UE se autolichidează" % res.R.get("R26_1")
