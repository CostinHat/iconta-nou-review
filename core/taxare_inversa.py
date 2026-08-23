# -*- coding: utf-8 -*-
"""Taxare inversa interna (art. 331 CF + norme pct. 109) - motor PUR.
- conditie: furnizor SI beneficiar inregistrati in scopuri TVA (art. 316);
  doar livrari/prestari in interiorul tarii (alin. 5);
- beneficiar: 4426 = 4427 (norme pct. 109 al. 1); furnizor factureaza FARA TVA,
  mentiune obligatorie "taxare inversa";
- prag 22.500 lei/factura (fara TVA) pt. telefoane/circuite/console-tablete-laptopuri;
- lit. c)-f), i)-l): valabile pana la 31.12.2026 (OUG 85/2022 + prelungiri);
- neaplicare corecta -> beneficiarul PIERDE dreptul de deducere (norme 109 al. 4)."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from core.pdf_util import bani

B = Decimal("0.01")
PRAG_ELECTRONICE = Decimal("22500")
EXPIRA_2026 = date(2026, 12, 31)

CATEGORII = {
    "deseuri":            {"lit": "a", "expira": None,        "prag": None},
    "masa_lemnoasa":      {"lit": "b", "expira": None,        "prag": None},
    "cereale":            {"lit": "c", "expira": EXPIRA_2026, "prag": None},
    "certificate_emisii": {"lit": "d", "expira": EXPIRA_2026, "prag": None},
    "energie_electrica":  {"lit": "e", "expira": EXPIRA_2026, "prag": None},
    "certificate_verzi":  {"lit": "f", "expira": EXPIRA_2026, "prag": None},
    "cladiri_terenuri":   {"lit": "g", "expira": None,        "prag": None},
    "aur_investitii":     {"lit": "h", "expira": None,        "prag": None},
    "telefoane":          {"lit": "i", "expira": EXPIRA_2026, "prag": PRAG_ELECTRONICE},
    "circuite_integrate": {"lit": "j", "expira": EXPIRA_2026, "prag": PRAG_ELECTRONICE},
    "console_tablete":    {"lit": "k", "expira": EXPIRA_2026, "prag": PRAG_ELECTRONICE},
    "gaze_naturale":      {"lit": "l", "expira": EXPIRA_2026, "prag": None},
}

def se_aplica(categorie, valoare_fara_tva, furnizor_tva, beneficiar_tva, la_data=None):
    """Returneaza (True, mentiune_factura) sau ridica ValueError cu motivul."""
    ref = la_data or date.today()
    c = CATEGORII.get(categorie)
    if not c:
        raise ValueError(f"categorie necunoscuta ({'|'.join(CATEGORII)})")
    if not furnizor_tva or not beneficiar_tva:
        raise ValueError("taxare inversa doar intre persoane inregistrate in scopuri "
                         "de TVA (art. 331 al. 1) - regim normal cu TVA")
    if c["expira"] and ref > c["expira"]:
        raise ValueError(f"taxarea inversa pt. lit. {c['lit']}) a expirat la {c['expira']} - regim normal")
    if c["prag"] and Decimal(str(valoare_fara_tva)) < c["prag"]:
        raise ValueError(f"sub pragul de {bani(c['prag'], 'lei')}/factura (lit. {c['lit']}) - regim normal cu TVA")
    return True, f"taxare inversa - art. 331 alin. (2) lit. {c['lit']}) Cod fiscal"

def tva_beneficiar(valoare_fara_tva, cota=None):
    """TVA simultan colectata si deductibila la beneficiar: 4426 = 4427."""
    if cota is None:
        raise ValueError("Cota de TVA nu s-a dat. Nu se folosește o valoare implicită: o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi. Declară cota operațiunii.")
    v = Decimal(str(valoare_fara_tva))
    if v <= 0:
        raise ValueError("Valoarea introdusă e invalidă (trebuie un număr pozitiv).")
    return (v * Decimal(str(cota)) / 100).quantize(B, rounding=ROUND_HALF_UP)
