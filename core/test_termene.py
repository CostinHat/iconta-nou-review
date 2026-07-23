"""
core/test_termene.py — plasa de regresie pentru scadentele viitoare (termene_api).
Pana la 23.07.2026 modulul avea ZERO teste; ecranul Termene reimplementa maparea
"cine ce datoreaza" fara acoperire (vezi CHECKLIST_BROWSER poz. 3). Aici o construim.
"""
import datetime
from core import termene_api


# ---------- T1: firma neevaluata NU dispare tacut (gri cu temei) ----------

def test_portofoliu_propaga_neevaluate():
    """portofoliu returneaza canalul `neevaluate` intact (gri cu temei, doctrina 23.07)."""
    neeval = [{"tenant_id": 7, "nume": "ACME SRL",
               "cauza": "Nu am putut evalua această firmă (OperationalError)."}]
    r = termene_api.portofoliu([], azi=datetime.date(2026, 7, 23), neevaluate=neeval)
    assert r["neevaluate"] == neeval
    assert r["grupuri"] == []           # nicio scadenta reala
    assert r["urmatoarea"] is None


def test_portofoliu_neevaluate_lipsa_default_gol():
    """Fara neevaluate -> lista goala, nu None (shape stabil pentru UI)."""
    r = termene_api.portofoliu([], azi=datetime.date(2026, 7, 23))
    assert r["neevaluate"] == []
