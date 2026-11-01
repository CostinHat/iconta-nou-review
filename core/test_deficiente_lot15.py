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
