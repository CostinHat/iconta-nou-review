"""
core/banca.py — contabilizare extras de cont. Calcul PUR, fără DB.
Generație nouă: import common, note cu urmă, o singură copie (fără dublarea din producție).

Surse oficiale (verificate):
- Conturi + monografii extras: OMFP 1802/2014 (plan de conturi, cap. trezorerie)

Direcția pe extras de cont:
  - 'credit' pe extras = bani INTRĂ (încasare)
  - 'debit'  pe extras = bani IES   (plată)
"""
from __future__ import annotations
import re
from decimal import Decimal

from core import common as c
from core.common import _dec, _q

REGULI = "2026.1"
MODUL = "banca"

# cuvinte-cheie din descrierea extrasului -> tip operațiune
CHEI = {
    "comision": ["comision", "taxa adm", "speze", "serviciu bancar"],
    "dobanda": ["dobanda", "dobânda"],
    "credit": ["credit", "imprumut", "împrumut", "rambursare", "rata credit"],
    "salarii": ["salar", "avans salar"],
    "impozit_profit": ["impozit profit", "impozit pe profit"],
    "tva": ["tva", "t.v.a"],
    "numerar": ["retragere", "atm", "ridicare numerar", "depunere numerar", "alimentare"],
}

# tip -> (cont la plată/debit-extras, cont la încasare/credit-extras)
# None = nu se aplică în acel sens
MONOGRAFIE = {
    "client":         (None,   "4111"),   # credit extras: 5121 = 4111
    "furnizor":       ("401",  None),      # debit extras:  401  = 5121
    "comision":       ("627",  None),      # 627 = 5121
    "dobanda":        ("666",  "766"),     # plată 666=5121 / încasare 5121=766
    "credit":         ("5191", "5191"),    # rambursare 5191=5121 / primit 5121=5191
    "salarii":        ("421",  None),      # 421 = 5121
    "impozit_profit": ("4411", None),      # 4411 = 5121 (corectat: NU 441)
    "tva":            ("4423", None),      # 4423 = 5121
    "numerar":        ("581",  "581"),     # viramente interne
}


def _nota(debit, credit, suma, temei=None):
    n = {"debit": debit, "credit": credit, "suma": _q(suma),
         "modul": MODUL, "reguli": REGULI}
    if temei:
        n["temei"] = temei
    return n


def detecteaza_tip(descriere):
    """Detectează tipul operațiunii din descrierea liniei de extras. Default: client/furnizor."""
    d = (descriere or "").lower()
    for tip, chei in CHEI.items():
        if any(k in d for k in chei):
            return tip
    return None   # necunoscut -> tratat ca client/furnizor după sens


def extrage_cui(text):
    """Extrage CUI/CIF din descriere (RO opțional + 2-10 cifre). Întoarce str sau None."""
    if not text:
        return None
    m = re.search(r'\bRO\s?(\d{2,10})\b', text, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r'\b(?:CUI|CIF)[:\s]*(\d{2,10})\b', text, re.IGNORECASE)
    return m.group(1) if m else None


def regula_cont(linie):
    """
    linie: {sens: 'debit'|'credit', suma, descriere?}
    Întoarce {nota, tip, cui}. Contul de bancă: 5124 dacă valuta=True, altfel 5121.
    """
    sens = linie["sens"]
    suma = _q(linie["suma"])
    banca = "5124" if linie.get("valuta") else "5121"
    tip = detecteaza_tip(linie.get("descriere"))
    cui = extrage_cui(linie.get("descriere"))

    if tip is None:
        tip = "client" if sens == "credit" else "furnizor"

    cont_plata, cont_incasare = MONOGRAFIE[tip]
    if sens == "credit":          # bani intră: 5121 = cont
        cont = cont_incasare
        if cont is None:
            raise ValueError(f"tip {tip!r} nu apare ca încasare (credit extras)")
        nota = _nota(banca, cont, suma)
    elif sens == "debit":          # bani ies: cont = 5121
        cont = cont_plata
        if cont is None:
            raise ValueError(f"tip {tip!r} nu apare ca plată (debit extras)")
        nota = _nota(cont, banca, suma)
    else:
        raise ValueError(f"sens necunoscut: {sens!r}")

    return {"nota": nota, "tip": tip, "cui": cui}


def contabilizeaza_extras(linii):
    """Aplică regula_cont pe toate liniile. Întoarce listă de rezultate."""
    return [regula_cont(l) for l in linii]
