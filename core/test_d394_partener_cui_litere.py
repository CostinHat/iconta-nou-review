# -*- coding: utf-8 -*-
"""GARD neconformitate T3/G-d1 (CATALOG_INVALIDITATE.md - cea mai grava D394): un CUI de partener
cu LITERE (prefix alfabetic care NU e cod de tara real, ex. 'ABC123') era clasificat TACIT ca
partener STRAIN (tip 3/4) -> rutat pe livrare scutita cota 0 (LS) -> DUK trecea cu DATE GRESITE.

FIX (core/d394.py): clasifica_partener recunoaste partener strain DOAR pentru prefixe de tara
reale (_TARI_UE / _TARI_NONUE); un prefix alfabetic necunoscut -> sentinel P_INVALID, iar
calcul_d394 BLOCHEAZA cu motivul exact ("CUI RO invalid, nu partener strain"), numind partenerul.

Pe HEAD (8b74ccb) 'ABC123' -> tip 4 (P_NONUE) tacit, factura acceptata: acest test PICA.
Dupa fix: clasificarea nu mai e strain, iar generarea blocheaza cu motiv exact: TRECE.
"""
import pytest

from core.common import Perioada
from core import d394

_PROF = {"cui": "RO14399840", "caen": "4690", "nume": "TEST SRL",
         "adresa": "str X", "telefon": "0700", "tip_decont": "L"}
_PER = Perioada(2026, luna=8)


def _calc(facturi, manual=None):
    return d394.calcul_d394(_PROF, _PER, {"facturi": facturi, "serii": {}}, manual)


def test_cui_litere_nu_devine_partener_strain_tacit():
    tp, _ = d394.clasifica_partener("ABC123")
    assert tp not in (d394.P_UE, d394.P_NONUE), \
        "CUI RO garbage cu litere clasificat TACIT ca partener strain (tip 3/4) - G-d1"


def test_factura_cui_litere_blocheaza_cu_motiv_exact():
    facturi = [{"cui": "ABC123", "nume": "PARTENER GRESIT SRL", "directie": "emisa",
                "taxare_inversa": False, "cota": 0, "baza": 1000, "tva": 0,
                "platitor_tva": True}]
    with pytest.raises(ValueError) as ei:
        _calc(facturi)
    msg = str(ei.value)
    assert "nu partener strain" in msg.lower(), "motivul exact lipseste din blocaj"
    assert "PARTENER GRESIT SRL" in msg, "partenerul nu e numit in mesaj"
    assert "ABC123" in msg, "CUI-ul gresit nu apare in mesaj"


def test_partener_strain_genuin_ramane_clasificat():
    # regresie: partenerii straini reali (prefix de tara valid) raman corect clasificati
    assert d394.clasifica_partener("DE811569869")[0] == d394.P_UE
    assert d394.clasifica_partener("CH123456")[0] == d394.P_NONUE
    assert d394.clasifica_partener("IE6388047V")[0] == d394.P_UE
