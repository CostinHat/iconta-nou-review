# -*- coding: utf-8 -*-
"""Perioada — obiect valoare pentru contractul uniform al generatoarelor (A1, 31.07.2026).

Inlocuieste params divergenti (an/trim/luna) cu un obiect. Fiecare declaratie citeste ce-i
trebuie; pull() foloseste interval() pentru fereastra de date."""
from datetime import date

from core.common import Perioada


def test_perioada_lunara_interval():
    p = Perioada(2026, luna=6)
    assert p.an == 2026 and p.luna == 6 and p.trim is None
    assert p.interval() == (date(2026, 6, 1), date(2026, 7, 1))


def test_perioada_decembrie_trece_anul():
    assert Perioada(2026, luna=12).interval() == (date(2026, 12, 1), date(2027, 1, 1))


def test_perioada_trimestriala():
    # trim 2 = apr-iun
    assert Perioada(2026, trim=2).interval() == (date(2026, 4, 1), date(2026, 7, 1))
    assert Perioada(2026, trim=4).interval() == (date(2026, 10, 1), date(2027, 1, 1))


def test_perioada_anuala():
    p = Perioada(2026)
    assert p.luna is None and p.trim is None
    assert p.interval() == (date(2026, 1, 1), date(2027, 1, 1))


def test_perioada_imutabila():
    import pytest
    p = Perioada(2026, luna=6)
    with pytest.raises(Exception):
        p.an = 2027


def test_cheie_manual_accepta_permise():
    from core.common import cheie_manual
    assert cheie_manual({"cota": "1"}, "cota") == {"cota": "1"}
    assert cheie_manual(None, "cota") == {}
    assert cheie_manual({}, "cota", "reclasificari") == {}


def test_cheie_manual_necunoscuta_ridica():
    """Typo ({kota} in loc de {cota}) NU se ignora tacut -> ridica (clasa 'or 21')."""
    import pytest
    from core.common import cheie_manual
    with pytest.raises(ValueError) as e:
        cheie_manual({"kota": "1"}, "cota")
    assert "necunoscut" in str(e.value).lower() and "kota" in str(e.value)
    with pytest.raises(ValueError):
        cheie_manual({"cotă": "1"}, "cota")   # diacritica gresita = alta cheie
