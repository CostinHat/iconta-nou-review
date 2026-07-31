# -*- coding: utf-8 -*-
"""Temei fiscal STRUCTURAT (act/nr/an/art/alin/lit/data_in/data_out/url) + garda de EXPIRARE.

DE CE (31.07.2026): temeiul era string liber. Structurat = grep-abil la o schimbare de lege
(gasesti TOATE locurile afectate) + poarta data_out, deci cota() RIDICA la expirare in loc sa
intoarca tacit valoarea veche. Nu exista API legislativ RO fiabil (dovedit): garda de EXPIRARE
(data_out) e mecanismul PRINCIPAL de deriva, nu un proxy. Se comporta ca string peste tot unde
codul vechi asteapta un string (afisare, JSON, operatorul `in`)."""
from datetime import date

import pytest

from core.common import Temei, cota, COTE


def test_temei_se_comporta_ca_string_citare_canonica():
    t = Temei("HG", 146, 2026, data_in="2026-07-01", data_out="2027-07-01",
              url="https://legislatie.just.ro/x", estimat=True)
    assert str(t) == "HG 146/2026"
    assert "HG 146/2026" in ("temei: " + t)     # concatenare (compat calleri vechi)
    assert t in "citat: HG 146/2026 aici"        # operatorul `in` pe string
    assert t.data_in == date(2026, 7, 1)
    assert t.data_out == date(2027, 7, 1)
    assert t.estimat is True and t.url.endswith("/x")


def test_temei_coduri_fara_nr_an():
    assert str(Temei("CF", art="146", alin="5^6")) == "CF art.146 alin.(5^6)"
    assert str(Temei("Legea", 141, 2025)) == "Legea 141/2025"
    assert str(Temei("OUG", 89, 2025, art="III", alin="4", lit="b")) == "OUG 89/2025 art.III alin.(4) lit.b"


def test_cota_cu_data_out_expirat_ridica(monkeypatch):
    """O cota al carei Temei poarta data_out in trecut -> cota() RIDICA dupa data_out, nu
    intoarce tacit valoarea veche. (azi: fara data_out, cota() ar intoarce 5 oricand)."""
    t = Temei("HG", 1, 2020, data_in="2020-01-01", data_out="2020-12-31")
    monkeypatch.setitem(COTE, "_proba_expira", [(date(2020, 1, 1), 5, t)])
    assert cota("_proba_expira", date(2020, 6, 1))[0] == 5      # inainte de data_out: ok
    with pytest.raises(ValueError) as e:
        cota("_proba_expira", date(2021, 6, 1))                 # dupa data_out: RIDICA
    assert "2020-12-31" in str(e.value), "mesajul nu spune data_out expirata"


def test_cota_data_out_None_nu_expira(monkeypatch):
    """data_out=None (inca in vigoare) + fara EXPIRA_DUPA_LUNI -> nu expira."""
    t = Temei("Legea", 227, 2015, data_in="2017-01-01", data_out=None)
    monkeypatch.setitem(COTE, "_proba_fara_out", [(date(2017, 1, 1), 9, t)])
    assert cota("_proba_fara_out", date(2099, 1, 1))[0] == 9
