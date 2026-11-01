"""Lotul 15, 634.2 — titlul notei scris înainte de reparația 634 (c) se arată fără mențiunea veche; nota din bază rămâne neschimbată."""
import pytest

from core.nir_legare import MENTIUNE_ALTA_LIVRARE_VECHE
from core.jurnal_api import note_fara_serie_lipita


class _Cur:
    def __init__(self, rows):
        self.rows, self._ultim = rows, []

    def execute(self, sql, params=None):
        self._ultim = self.rows if "LIKE" in sql else []

    def fetchall(self):
        return self._ultim


def test_def_634_2_titlul_notei_fara_mentiunea_veche(monkeypatch):
    monkeypatch.setattr("core.jurnal_api.note_cu_serie_lipita", lambda cur, schema, ids: [])
    descr = "Contare factura DNT-UBL-083" + MENTIUNE_ALTA_LIVRARE_VECHE
    out = note_fara_serie_lipita(_Cur([{"id": 5, "descriere": descr}]), "t_x", [5])
    assert out[5]["descriere"] == "Contare factura DNT-UBL-083"


def test_d3_nimic_nu_se_datoreaza_inainte_de_infiintare():
    """D3 (3f/3k): o perioadă dinaintea lunii înființării (D101 pe 2025 la o firmă înființată în 03.2026) nu se datorează; trimestrul și luna care cuprind
    data înființării se datorează."""
    from core import luna_preluare as lp
    infiintare = (2026, 3)
    assert lp.inainte(2025, None, infiintare)          # D101/2025: anuală, ancora 12/2025
    assert lp.inainte(2026, 2, infiintare)             # luna 02/2026
    assert not lp.inainte(2026, 3, infiintare)         # luna înființării
    assert not lp.inainte(2026, 3, infiintare) and not lp.inainte(2026, 6, infiintare)   # trimestrul 1 (ancora 3) și al doilea (6)
