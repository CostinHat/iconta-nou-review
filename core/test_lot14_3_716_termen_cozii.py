"""[716, comanda 14.3] „Depășită” numai după termen: coada dă termenul legal și `termen_depasit`; o perioadă neîncheiată nu e depășită."""
import datetime as _dt

from core import coada_api as CA, common


def _el(**k):
    return dict({"fel": "declaratie", "tip": "d300", "p_an": 2026, "p_luna": 10, "p_trim": None}, **k)


def test_perioada_neincheiata_nu_e_depasita_si_are_termenul_25_11(monkeypatch):
    monkeypatch.setattr(common, "azi_ro", lambda: _dt.date(2026, 10, 29))
    assert CA._termen_cozii(_el(), activa=True) == ("2026-11-25", False)


def test_dupa_termen_si_nedepusa_e_depasita_iar_depusa_sau_nota_nu(monkeypatch):
    monkeypatch.setattr(common, "azi_ro", lambda: _dt.date(2026, 11, 26))
    assert CA._termen_cozii(_el(), activa=True) == ("2026-11-25", True)
    assert CA._termen_cozii(_el(), activa=False) == ("2026-11-25", False), "depusă / respinsă: nu mai e în coadă activă"
    assert CA._termen_cozii(_el(fel="nota"), activa=True) == (None, False)
    assert CA._termen_cozii(_el(p_an=None), activa=True) == (None, False)
