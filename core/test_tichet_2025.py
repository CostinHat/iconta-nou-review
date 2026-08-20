# -*- coding: utf-8 -*-
"""GARD B1/tichet 2025: valorile nominale ale tichetului de masa in 2025, verificate VERBATIM la sursa.
40,04 (ian-mar, Ordinul MF 4.679/2024), 40,18 (apr-sep, Ordinul MF 484/2025), 45 (de la noiembrie 2025,
Legea 201/2025). OCTOMBRIE 2025 = GOL MOTIVAT (fara sursa): data_out explicit 30 septembrie pe Ordinul 484
impiedica propagarea TACITA a lui 40,18 peste octombrie. Corectie: 45 de la 1 noiembrie 2025 (era @2026-01)."""
from datetime import date
from decimal import Decimal

import pytest

from core.common import cota


def test_valorile_tichet_2025_verbatim():
    for m, v in [(2, "40.04"), (3, "40.04"), (4, "40.18"), (8, "40.18"), (9, "40.18"), (11, "45"), (12, "45")]:
        val, _ = cota("tichet_masa_plafon", date(2025, m, 1))
        assert val == Decimal(v), "tichet 2025-%02d trebuie %s, e %s" % (m, v, val)
    assert cota("tichet_masa_plafon", date(2026, 7, 1))[0] == Decimal("45"), "2026 ramane 45"


def test_octombrie_2025_gol_motivat_nu_valoare_tacuta():
    """Punctul critic: octombrie 2025 e GOL (fara sursa), NU 40,18 propagat tacit. data_out explicit 30 sep
    pe Ordinul 484/2025 opreste derivarea din succesorul @noiembrie -> gol motivat."""
    with pytest.raises(ValueError) as ei:
        cota("tichet_masa_plafon", date(2025, 10, 1))
    # [20.08.2026] Aserțiunea se lega de FORMULAREA mesajului („gol in registru"), care a trebuit
    # rescrisă când mesajul a intrat în canalul publicat contabilului (diacritice, F5). Un test legat
    # de cuvinte pică la fiecare rescriere corectă și împinge spre a NU repara mesajul. Se leagă acum
    # de FAPTELE pe care mesajul trebuie să le poarte ca să fie „motivat", indiferent de formulare:
    # numele cotei și data cerută.
    _msg = str(ei.value)
    assert "tichet_masa_plafon" in _msg and "2025-10-01" in _msg,         "octombrie 2025 trebuie gol MOTIVAT (mesajul numește cota și data cerută), nu 40,18 tacit: %s" % _msg
    assert cota("tichet_masa_plafon", date(2025, 9, 1))[0] == Decimal("40.18"), "septembrie ramane 40,18"


def test_45_de_la_noiembrie_nu_ianuarie_2026():
    """REPARATIE: Legea 201/2025 art.II alin.(1) se aplica de la drepturile lunii NOIEMBRIE 2025 -> nov si
    dec 2025 = 45 (erau tratate gresit inainte de corectia data_in @2026-01 -> @2025-11)."""
    assert cota("tichet_masa_plafon", date(2025, 11, 1))[0] == Decimal("45")
    assert cota("tichet_masa_plafon", date(2025, 12, 1))[0] == Decimal("45")
