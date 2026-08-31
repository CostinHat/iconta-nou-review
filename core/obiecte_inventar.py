# -*- coding: utf-8 -*-
"""Obiecte de inventar (303) - motor PUR (OMFP 1802/2014).
Prag mijloc fix: 5.000 lei din 25.02.2026 (OUG 8/2026 art. 28(2)b; anterior
2.500 lei HG 276/2013). MF existente la 31.12.2025 cu valoare 2.500-5.000 se
amortizeaza pe durata ramasa (art. 45(21^3)) - NU se reclasifica.
Sub prag sau durata <1 an -> obiect de inventar:
- achizitie: 303 + 4426 = 401;
- dare in folosinta: 603 = 303 (integral pe cheltuiala) + evidenta
  extracontabila D8035 pana la scoaterea din uz (C8035)."""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date

B = Decimal("0.01")

# PRAGUL NU MAI E SCRIS AICI (01.09.2026, R108). Statea in trei locuri: `COTE["plafon_mijloc_fix"]`
# (canonic, dar cu data GRESITA si necitit de nimeni), aici (data corecta), si ca literal fara data
# in `mijloace_fixe_import_api`. O lege aplicata in trei locuri produce, la urmatoarea modificare,
# cifra valida si falsa: doua se actualizeaza, a treia nu, si nimic nu se aprinde.
#
# Sursa unica e acum REGISTRUL. Data lui a fost corectata pe 31.08 dupa marcajul din forma
# consolidata a Codului fiscal — `(la 25-02-2026, Litera b), Alineatul (2), Articolul 28 ... a fost
# modificata de Punctul 7., Articolul 6 din OUG 8/2026)`.


def prag_mf(la_data=None):
    """Pragul de incadrare ca mijloc fix, la data ceruta. CITIT din registrul de cote.

    PENTRU DATE ANTERIOARE PRIMEI VALORI DIN REGISTRU (01.01.2015) se intoarce cea mai veche valoare
    cunoscuta — exact ce facea si forma dinainte. Diferenta e ca acum necunoasterea se poate NUMI:
    `prag_mf_cunoscut()` spune daca raspunsul e verificat la sursa pentru data aia sau doar mostenit.
    Un mijloc fix intrat in 2008 avea alt prag (1.800 lei, HG 105/2007), care nu e in registru — v.
    interdictia 57, o valoare fara temei nu se inventeaza aici.
    """
    from core.common import PerioadaIndisponibila, cota
    ref = la_data or date.today()
    try:
        val, _t = cota("plafon_mijloc_fix", la_data=ref)
    except PerioadaIndisponibila:
        val = _cea_mai_veche()
    return Decimal(str(val))


def prag_mf_cunoscut(la_data=None):
    """`True` daca registrul are un prag VERIFICAT LA SURSA pentru data ceruta; `False` daca
    raspunsul lui `prag_mf` e cea mai veche valoare cunoscuta, mostenita in lipsa alteia."""
    from core.common import PerioadaIndisponibila, cota
    try:
        cota("plafon_mijloc_fix", la_data=la_data or date.today())
        return True
    except PerioadaIndisponibila:
        return False


def _cea_mai_veche():
    from core.common import COTE
    return sorted(COTE["plafon_mijloc_fix"], key=lambda r: r[0])[0][1]

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def e_obiect_inventar(valoare, la_data=None, durata_sub_1_an=False):
    """Sub pragul MF sau durata <1 an -> obiect de inventar."""
    return durata_sub_1_an or _d(valoare) < prag_mf(la_data)

def nota_achizitie(valoare, cota_tva=None):
    if cota_tva is None:
        raise ValueError("Cota de TVA nu s-a dat. Nu se folosește o valoare implicită: o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi. Declară cota operațiunii.")
    v = _d(valoare)
    if v <= 0:
        raise ValueError("Valoarea introdusă e invalidă (trebuie un număr pozitiv).")
    tva = (v * Decimal(str(cota_tva)) / 100).quantize(B, rounding=ROUND_HALF_UP)
    linii = [("303", "401", v)]
    if tva > 0:
        linii.append(("4426", "401", tva))
    return {"linii": linii, "tva": tva}

def nota_dare_folosinta(valoare):
    """603=303 + D8035 extracontabil (contrapartida tehnica 891)."""
    v = _d(valoare)
    if v <= 0:
        raise ValueError("Valoarea introdusă e invalidă (trebuie un număr pozitiv).")
    return {"linii": [("603", "303", v), ("8035", "891", v)]}

def nota_scoatere_uz(valoare):
    """C8035 la casare/scoatere din uz (proces-verbal)."""
    v = _d(valoare)
    if v <= 0:
        raise ValueError("Valoarea introdusă e invalidă (trebuie un număr pozitiv).")
    return {"linii": [("891", "8035", v)]}
