# -*- coding: utf-8 -*-
"""Regim special aur de investitii (art. 313 CF) - motor PUR.
- alin. 1: lingouri/plachete >=995 la mie; monede >=900 la mie, emise dupa 1800,
  pret <= valoarea aurului +80%;
- alin. 3: livrari scutite (inclusiv intermediere in numele mandantului);
- alin. 4-6: optiune taxare (doar catre persoana impozabila) -> taxare inversa
  (art. 331 al. 2 lit. h): factura fara TVA, mentiune obligatorie;
- alin. 10: identificarea clientului obligatorie, evidenta 5 ani."""
from decimal import Decimal, InvalidOperation

def _d(x):
    return Decimal(str(x))


# [R144, 04.09.2026] UN NUMAR CARE NU E NUMAR NU E O EROARE DE SERVER.
#
# `_d("«»@#$%")` ridica `decimal.InvalidOperation`, care e `ArithmeticError`, **nu** `ValueError` —
# iar ruta din `main.py` prinde numai `ValueError`. Deci textul tastat de un om intr-o caseta iesea
# ca **`500`**, iar contabilul citea „eroare 500" in loc sa afle ce camp e gresit.
#
# Gasit apasand, in lotul 13: din cele 32 de operatiuni speciale, **una singura** a cazut asa. Aceeasi
# clasa ca R134 („toate portile raspundeau 500, deci mesajele lor n-au ajuns niciodata la un om") —
# un refuz care iese ca eroare de server e un refuz care nu exista.
#
# Reparat AICI, in motorul pur, si nu la ruta, fiindca functia are deja contractul potrivit:
# intoarce `(False, motiv)` pentru orice nu e aur de investitii. „Puritatea nu e un numar" e un motiv
# ca oricare altul — nu o exceptie.
#
# CELE PATRU intrari numerice se verifica toate, nu doar cea care a cazut: `puritate`, `an_emisie`,
# `pret`, `valoare_aur`. *A repara doar instanta ar fi lasat trei usi deschise pe acelasi hol.*
def _numar(x, nume):
    """(valoare, None) daca `x` e un numar; (None, motiv) altfel. Motivul e pentru un om."""
    if x is None:
        return None, "%s lipsește" % nume
    try:
        return _d(x), None
    except (InvalidOperation, ValueError, TypeError):
        return None, "%s trebuie să fie un număr (am primit %r)" % (nume, x)


def este_aur_investitii(tip, puritate, an_emisie=None, pret=None, valoare_aur=None):
    """tip: 'lingou'|'plancheta'|'moneda'. Returneaza (bool, motiv)."""
    p, motiv = _numar(puritate, "Puritatea")
    if motiv:
        return False, motiv
    if tip in ("lingou", "plancheta"):
        if p >= 995:
            return True, None
        return False, "puritate sub 995 la mie (art. 313 al. 1 lit. a)"
    if tip == "moneda":
        if p < 900:
            return False, "puritate sub 900 la mie (art. 313 al. 1 lit. b)"
        an, motiv = _numar(an_emisie, "Anul de emisiune")
        if motiv:
            return False, motiv
        if an <= 1800:
            return False, "moneda emisa pana in 1800 inclusiv (art. 313 al. 1 lit. b)"
        pr, motiv = _numar(pret, "Prețul")
        if motiv:
            return False, "pret si valoare aur obligatorii pentru moneda" if pret is None else motiv
        va, motiv = _numar(valoare_aur, "Valoarea aurului")
        if motiv:
            return False, "pret si valoare aur obligatorii pentru moneda" if valoare_aur is None else motiv
        if pr > va * Decimal("1.8"):
            return False, "pret peste valoarea aurului +80% (art. 313 al. 1 lit. b)"
        return True, None
    return False, "tip necunoscut (lingou|plancheta|moneda)"

def livrare_aur(optiune_taxare, calitate_client, client_identificare):
    """Returneaza regimul livrarii: 'scutit' | 'taxare_inversa'.
    Optiunea de taxare e permisa doar catre persoana impozabila (alin. 4-5).
    Identificarea clientului e obligatorie (alin. 10)."""
    if not (client_identificare or "").strip():
        raise ValueError("identificarea clientului este obligatorie (art. 313 al. 10)")
    if optiune_taxare:
        if calitate_client != "PJ":
            raise ValueError("optiunea de taxare permisa doar catre persoana impozabila (art. 313 al. 4-5)")
        return "taxare_inversa"
    return "scutit"
