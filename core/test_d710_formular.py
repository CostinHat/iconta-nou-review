# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 6] GARDA: formularul D710 gol NU produce declaratie.

D710 (rectificativa D100) e produsa din obligatiile introduse de contabil in formularul manual (ecran nou
18.08.2026, scos din _DOAR_API). Un formular GOL (nicio obligatie corectata, sau toate cu ambele sume 0 ->
filtrate in calcul) e structural invalid la DUK (sectiunea <obligatie> obligatoria). genereaza refuza PRE-DUK
cu mesaj de CONTABIL (ce lipseste, in limba lui), nu numele intern al campului si nu un XML respins de validator.
"""
import pytest
from core import d710
from core.common import Perioada


def _fake_pull(monkeypatch, prof):
    # profil valid (CUI/nume/adresa) -> nu pica pe erori_generare; date=() (D710 nu foloseste D100 real la gol)
    monkeypatch.setattr(d710, "pull", lambda conn, schema, per: (prof, {}))


_PROF = {"cui": "14399840", "nume": "T SRL", "adresa": "Str. Testului nr. 1"}


def test_d710_formular_gol_refuza():
    """Lista de obligatii GOALA -> ValueError cu mesaj de contabil, nu XML."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m, _PROF)
        with pytest.raises(ValueError) as e:
            d710.genereaza(None, "x", Perioada(2026, trim=2), {"obligatii": []})
    finally:
        m.undo()
    msg = str(e.value)
    assert "nicio obligație" in msg.lower() or "cel puțin o obligație" in msg.lower(), msg
    # limbaj de contabil: NU expune numele interne ale campurilor
    for intern in ("obligatii", "suma_dat_i", "suma_dat_c", "cod_oblig", "res.obligatii"):
        assert intern not in msg, "mesajul expune numele intern %r: %s" % (intern, msg)


def test_d710_toate_sumele_zero_refuza():
    """O obligatie cu ambele sume 0 (filtrata in calcul) -> tot GOL -> refuz."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m, _PROF)
        with pytest.raises(ValueError) as e:
            d710.genereaza(None, "x", Perioada(2026, trim=2),
                           {"obligatii": [{"cod_oblig": "121", "suma_dat_i": 0, "suma_dat_c": 0, "cota": "1"}]})
    finally:
        m.undo()
    assert "obligație" in str(e.value).lower()


def test_d710_cu_o_obligatie_valida_genereaza():
    """Regresie: o obligatie reala (cod 103 profit) -> NU refuza (produce XML)."""
    import _pytest.monkeypatch as _mp
    m = _mp.MonkeyPatch()
    try:
        _fake_pull(m, _PROF)
        xml, res = d710.genereaza(None, "x", Perioada(2026, trim=2),
                                  {"obligatii": [{"cod_oblig": "103", "suma_dat_i": 1000, "suma_dat_c": 1500}]})
    finally:
        m.undo()
    assert xml and res.obligatii, "o obligatie valida trebuie sa produca declaratie"
