# -*- coding: utf-8 -*-
"""Teste gardian pentru F134 (plata salariilor pe card, SEPA pain.001).

Apara partile pure critice:
  - iban_valid: cifra de control mod-97 (ISO 13616). Un IBAN gresit trimite banii altcuiva ->
    orice regresie aici = pierdere reala de bani. Verificat pe exemplul standard ISO pt Romania.
  - _sepa_text: charset SEPA (banca respinge diacritice/caractere in afara setului Latin restrans).
  - _q2: rotunjire aritmetica HALF_UP a sumelor (nu bancara).
"""
from decimal import Decimal
from core.salariati_api import iban_valid
from core.plata_salarii import _sepa_text, _q2


# IBAN valid de referinta: exemplul standard ISO 13616 pentru Romania.
IBAN_OK = "RO49AAAA1B31007593840000"


def test_iban_valid_exemplu_standard():
    assert iban_valid(IBAN_OK) is True


def test_iban_normalizeaza_spatii_si_minuscule():
    assert iban_valid("ro49 aaaa 1b31 0075 9384 0000") is True


def test_iban_cifra_control_gresita():
    # o singura cifra schimbata rupe mod-97
    assert iban_valid("RO49AAAA1B31007593840001") is False


def test_iban_lungime_gresita():
    assert iban_valid("RO49AAAA1B3100759384") is False       # prea scurt
    assert iban_valid("RO49AAAA1B310075938400001") is False  # prea lung


def test_iban_doar_romanesc():
    # IBAN german valid ca format international, dar respins: acceptam doar RON domestic (RO)
    assert iban_valid("DE89370400440532013000") is False


def test_iban_gol_sau_none():
    assert iban_valid("") is False
    assert iban_valid(None) is False


def test_sepa_text_transliterare_diacritice():
    assert _sepa_text("Ștefănescu Ioană") == "Stefanescu Ioana"
    assert _sepa_text("ȚĂNDĂRĂ") == "TANDARA"


def test_sepa_text_elimina_caractere_interzise():
    # caracterele in afara setului SEPA devin spatiu, spatiile se colapseaza
    out = _sepa_text("Firma @#% SRL")
    assert "@" not in out and "#" not in out and "%" not in out
    assert out == "Firma SRL"


def test_sepa_text_gol_devine_placeholder():
    assert _sepa_text("") == "NA"
    assert _sepa_text(None) == "NA"


def test_sepa_text_trunchiaza():
    assert len(_sepa_text("A" * 200, maxlen=140)) == 140


def test_q2_rotunjire_aritmetica_half_up():
    # HALF_UP, nu bancara (half-to-even): 2.5 -> 2.50 exact, 0.005 -> 0.01
    assert _q2(Decimal("0.005")) == "0.01"
    assert _q2(Decimal("2.345")) == "2.35"
    assert _q2(2968) == "2968.00"
    assert _q2(0) == "0.00"


if __name__ == "__main__":
    import sys
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn(); print("OK", fn.__name__)
    print("\n%d teste PASS" % len(fns))
    sys.exit(0)
