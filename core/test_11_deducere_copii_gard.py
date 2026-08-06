# -*- coding: utf-8 -*-
"""GARD #11: deducerea de 100 lei/copil (CF art.77 alin.(10) lit.b) NU se acorda tacit — art.77 alin.(12)-(13)
o conditioneaza de declaratia parintelui. Feature NECABLAT azi (copii_scoala nu e coloana pe salariati,
apelantii reali trec 0). Gardul defensiv ridica daca cineva cere copii_scoala>0 fara flag -> la cablare
esueaza VIZIBIL, nu acorda dublu. Cablarea completa = build-new (§PRODUS)."""
from datetime import date
from decimal import Decimal

import pytest

from core.salarizare import deducere_personala

LA = date(2026, 7, 15)


def test_copii_fara_declaratie_ridica():
    """copii_scoala>0 FARA flag-ul declaratiei -> eroare explicita care citeaza art.77(12)-(13)."""
    with pytest.raises(ValueError) as ei:
        deducere_personala(6000, copii_scoala=2, la_data=LA)
    msg = str(ei.value)
    assert "77" in msg and "(12)-(13)" in msg, "eroarea trebuie sa citeze art.77 alin.(12)-(13): %s" % msg


def test_copii_cu_declaratie_acorda():
    """Cu flag-ul declaratiei -> matematica se aplica (100 lei/copil)."""
    d = deducere_personala(6000, copii_scoala=2, declaratie_copii=True, la_data=LA)
    assert d["copii"] == Decimal("200.00")


def test_fara_copii_no_op():
    """Cazul REAL (copii_scoala=0): fara eroare, fara deducere de copii -> gardul nu atinge calculul viu."""
    d = deducere_personala(6000, la_data=LA)
    assert d["copii"] == Decimal("0.00")
