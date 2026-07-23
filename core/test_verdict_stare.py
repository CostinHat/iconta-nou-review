# test_verdict_stare.py — mecanismul culorii de verdict: deriva DIN nivelul motorului, nu literal.
# Reparat 23.07: _flag("galben",...) slabea un BLOCANT de trezorerie la galben. Culoarea =
# common.stare_din_nivel(nivel), mapare UNICA. Vezi DECIZII 23.07.
from decimal import Decimal

from core.common import stare_din_nivel, BLOCANT, AVERTISMENT
from core import verificatoare as vf


def test_mapare_nivel_stare():
    assert stare_din_nivel(BLOCANT) == "rosu"
    assert stare_din_nivel(AVERTISMENT) == "galben"
    assert stare_din_nivel(None) == "gri"        # nivel absent -> gri, nu inventa severitate
    assert stare_din_nivel("necunoscut") == "gri"


def test_trezorerie_negativa_e_BLOCANT_deci_rosu():
    # sold creditor pe 5121 = imposibilitate contabila certa -> BLOCANT -> rosu (NU galben).
    bal = {"5121": {"debit": Decimal(0), "credit": Decimal(100), "sold": Decimal("-100")}}
    probleme = vf.verifica_trezorerie(bal)
    assert len(probleme) == 1
    assert probleme[0]["nivel"] == BLOCANT
    assert stare_din_nivel(probleme[0]["nivel"]) == "rosu"


def test_balanta_dezechilibrata_e_BLOCANT_deci_rosu():
    bal = {"401": {"debit": Decimal(100), "credit": Decimal(0), "sold": Decimal(100)}}
    p = vf.verifica_balanta(bal)
    assert p["nivel"] == BLOCANT
    assert stare_din_nivel(p["nivel"]) == "rosu"


def test_stocuri_fara_nivel_e_gri():
    # verificare_stocuri intoarce {conturi, ok, nota} FARA nivel (cauze legitime: note ciorna
    # nevalidate) -> maparea din cheia absenta da gri. Nu se inventeaza un nivel la randare.
    rez_stocuri = {"conturi": [], "ok": False, "nota": "..."}
    assert stare_din_nivel(rez_stocuri.get("nivel")) == "gri"


def test_intrastat_fara_nivel_e_gri():
    # intrastat_praguri intoarce status (sub_prag|atentie|depasit) dar NU un `nivel` common ->
    # maparea din cheia absenta da gri. GAP semnalat (motorul ar trebui sa declare nivel).
    rez_intrastat = {"introduceri": {"status": "depasit"}, "nota": "..."}
    assert stare_din_nivel(rez_intrastat.get("nivel")) == "gri"
