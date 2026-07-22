# -*- coding: utf-8 -*-
"""Teste pure pentru helper-ele F180 (regim TVA vs ANAF) din firma_profil_api.
Apara contractul: comparatie apples-to-apples platitor_tva(local, bool) vs
platitor_tva_anaf(scpTVA snapshot, bool); fara snapshot / local necompletat -> 'gri'
(nu rosu). Vezi DECIZII.md 22.07 F180."""
from core import firma_profil_api as fp


# --- stare_tva_anaf: verde / rosu / gri ---
def test_stare_coincid_verde():
    assert fp.stare_tva_anaf(True, True) == "verde"
    assert fp.stare_tva_anaf(False, False) == "verde"


def test_stare_difera_rosu():
    assert fp.stare_tva_anaf(True, False) == "rosu"
    assert fp.stare_tva_anaf(False, True) == "rosu"


def test_stare_fara_snapshot_gri():
    # anaf None (fara snapshot / ANAF necunoscut) -> gri, indiferent de local
    assert fp.stare_tva_anaf(True, None) == "gri"
    assert fp.stare_tva_anaf(False, None) == "gri"


def test_stare_local_necompletat_gri():
    # local None (vector necompletat) -> gri, nu comparam
    assert fp.stare_tva_anaf(None, True) == "gri"
    assert fp.stare_tva_anaf(None, None) == "gri"


# --- avertisment_tva_anaf (signal-not-block la salvare) ---
def test_avertisment_doar_la_divergenta():
    # coincid -> fara avertisment
    assert fp.avertisment_tva_anaf(True, True) is None
    assert fp.avertisment_tva_anaf(False, False) is None
    # ANAF necunoscut -> fara avertisment (nu avertizam pe necunoscut)
    assert fp.avertisment_tva_anaf(True, None) is None


def test_avertisment_divergenta_are_camp_si_valori():
    a = fp.avertisment_tva_anaf(True, False)
    assert a is not None
    assert a["camp"] == "platitor_tva"
    assert a["local"] is True and a["anaf"] is False
    assert "ANAF" in a["mesaj"] and "salva oricum" in a["mesaj"]
