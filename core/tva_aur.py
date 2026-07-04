# -*- coding: utf-8 -*-
"""Regim special aur de investitii (art. 313 CF) - motor PUR.
- alin. 1: lingouri/plachete >=995 la mie; monede >=900 la mie, emise dupa 1800,
  pret <= valoarea aurului +80%;
- alin. 3: livrari scutite (inclusiv intermediere in numele mandantului);
- alin. 4-6: optiune taxare (doar catre persoana impozabila) -> taxare inversa
  (art. 331 al. 2 lit. h): factura fara TVA, mentiune obligatorie;
- alin. 10: identificarea clientului obligatorie, evidenta 5 ani."""
from decimal import Decimal

def _d(x):
    return Decimal(str(x))

def este_aur_investitii(tip, puritate, an_emisie=None, pret=None, valoare_aur=None):
    """tip: 'lingou'|'plancheta'|'moneda'. Returneaza (bool, motiv)."""
    p = _d(puritate)
    if tip in ("lingou", "plancheta"):
        if p >= 995:
            return True, None
        return False, "puritate sub 995 la mie (art. 313 al. 1 lit. a)"
    if tip == "moneda":
        if p < 900:
            return False, "puritate sub 900 la mie (art. 313 al. 1 lit. b)"
        if an_emisie is None or int(an_emisie) <= 1800:
            return False, "moneda emisa pana in 1800 inclusiv (art. 313 al. 1 lit. b)"
        if pret is None or valoare_aur is None:
            return False, "pret si valoare aur obligatorii pentru moneda"
        if _d(pret) > _d(valoare_aur) * Decimal("1.8"):
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
