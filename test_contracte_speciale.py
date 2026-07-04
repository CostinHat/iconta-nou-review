# -*- coding: utf-8 -*-
from decimal import Decimal
import pytest
from core import contracte_speciale as m

def test_zilier():
    c = m.calcul_zilier(2500)
    assert c["cas"] == Decimal("625.00")
    assert c["impozit"] == Decimal("187.50")
    assert c["cass"] == Decimal("0.00")
    assert c["net"] == Decimal("1687.50")

def test_mandat():
    c = m.calcul_mandat(5000)
    assert c["cas"] == Decimal("1250.00")
    assert c["cass"] == Decimal("500.00")
    assert c["impozit"] == Decimal("325.00")
    assert c["net"] == Decimal("2925.00")

def test_remuneratie_minima():
    r = m.remuneratie_minima_zilier(4050)
    assert r["orar_minim"] == Decimal("24.50")
    assert r["zi_minima"] == Decimal("196.00")

def test_nota_zilier():
    r = m.nota(2500, "zilier")
    assert ("641", "421", Decimal("2500.00")) in r["linii"]
    assert ("421", "4315", Decimal("625.00")) in r["linii"]
    assert ("421", "444", Decimal("187.50")) in r["linii"]
    assert ("421", "5311", Decimal("1687.50")) in r["linii"]
    assert not any(l[1] == "4316" for l in r["linii"])

def test_nota_cenzor():
    r = m.nota(5000, "cenzor", "banca")
    assert ("621", "421", Decimal("5000.00")) in r["linii"]
    assert ("421", "4316", Decimal("500.00")) in r["linii"]
    assert ("421", "5121", Decimal("2925.00")) in r["linii"]

def test_invalid():
    with pytest.raises(ValueError):
        m.nota(0)
