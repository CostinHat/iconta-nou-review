# -*- coding: utf-8 -*-
"""Gard pe validatorul de identitate PARTAJAT (core/identitate.py, LANT legislatie TURA 3, 10.08.2026).
Ancorat pe valorile pe care DUKIntegrator le ACCEPTA/RESPINGE (verificat live in tura 29):
  CUI valide: 301111003, 143000000, 145000006 (+ prefix RO acceptat).
  CUI invalide: 301111004, 143000009, 111111111 (cifra de control), gol, litere.
  CNP valide: 1900101410011, 1800101221144, 1700510400076.
  CNP invalide: 1700510400077 (control), 123456789012 (12 cifre), 9900101410011 (control).
Un validator care nu pica pe valorile DUK-invalide nu e validator - de-aici ancora dubla (valid + invalid)."""
from core.identitate import valideaza_cui, valideaza_cnp, valideaza_cif


def test_cui_valide_conform_duk():
    for c in ("301111003", "143000000", "145000006", "RO 301111003"):
        v, m = valideaza_cui(c)
        assert v, "CUI %s trebuia valid (DUK il accepta): %s" % (c, m)


def test_cui_invalide_conform_duk():
    for c, motiv_asteptat in (("301111004", "cifra de control"), ("143000009", "cifra de control"),
                              ("111111111", "cifra de control"), ("", "lipsa")):
        v, m = valideaza_cui(c)
        assert not v, "CUI %s trebuia invalid (DUK il respinge)" % c
        assert motiv_asteptat in m, "motiv CUI %s: %r (asteptat %r)" % (c, m, motiv_asteptat)


def test_cui_lungime():
    v, m = valideaza_cui("12345678901")   # 11 cifre > 10
    assert not v and "lungime" in m, m


def test_cnp_valide_conform_duk():
    for c in ("1900101410011", "1800101221144", "1700510400076"):
        v, m = valideaza_cnp(c)
        assert v, "CNP %s trebuia valid: %s" % (c, m)


def test_cnp_invalide_conform_duk():
    for c, motiv in (("1700510400077", "cifra de control"), ("123456789012", "format"),
                     ("0123456789012", "prima cifra"), ("9900101410011", "cifra de control")):
        v, m = valideaza_cnp(c)
        assert not v, "CNP %s trebuia invalid" % c
        assert motiv in m, "motiv CNP %s: %r (asteptat %r)" % (c, m, motiv)


def test_cif_alege_cnp_sau_cui():
    v, tip, m = valideaza_cif("1900101410011")   # 13 cifre prima 1-9 -> CNP
    assert v and tip == "cnp", (v, tip, m)
    v, tip, m = valideaza_cif("301111003")        # CUI
    assert v and tip == "cui", (v, tip, m)
    v, tip, m = valideaza_cif("")
    assert not v and tip == "?", (v, tip, m)
