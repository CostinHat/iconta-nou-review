"""
core/scadente.py — calculează data scadenței unei declarații (format zz/ll/aaaa),
mutată la prima zi lucrătoare dacă pică în weekend/sărbătoare. PUR, fără DB.

Verificat la sursa oficială (calendar ANAF 2026):
  D100, D112, D300, D301, D390 -> 25 ale lunii următoare
  D394                          -> 30 ale lunii următoare
  D406 (SAF-T)                  -> ultima zi a lunii următoare
  trimestrial (D100/D300/...)   -> 25 (sau 30/ultima zi) ale lunii următoare trim.
  D205                          -> ultima zi februarie an următor
  D101                          -> 25 martie an următor  (PROVIZORIU — de confirmat)
Toate se mută la prima zi lucrătoare dacă pică în weekend/sărbătoare legală.

Sărbătorile sunt într-un dict EDITABIL per an (Paște/Rusalii variază anual).
"""
from __future__ import annotations
import calendar
from datetime import date, timedelta

REGULI = "2026.1"
MODUL = "scadente"

# Sărbători legale RO (zile nelucrătoare), per an. (lună, zi).
# Editabil: când se schimbă/adaugă un an, modifici aici. Paște/Rusalii = variabile.
SARBATORI = {
    2026: [(1, 1), (1, 2), (1, 6), (1, 7), (1, 24),
           (4, 12), (4, 13),            # Paște ortodox 2026
           (5, 1), (5, 31), (6, 1),      # Rusalii 2026 (31 mai), Ziua Copilului
           (8, 15), (11, 30), (12, 1), (12, 25), (12, 26)],
    2027: [(1, 1), (1, 2), (1, 6), (1, 7), (1, 24),
           (5, 1), (5, 2), (5, 3),       # Paște ortodox 2027 (2 mai)
           (6, 1), (6, 20), (6, 21),     # Rusalii 2027 (20 iun)
           (8, 15), (11, 30), (12, 1), (12, 25), (12, 26)],
}

# ziua nominală a scadenței per tip (în luna următoare perioadei)
_ZIUA = {"d394": 30}          # restul: 25 ; d406: ultima zi (tratat separat)
_ULTIMA_ZI = {"d406"}          # scadența = ultima zi a lunii


def _e_sarbatoare(d):
    return (d.month, d.day) in SARBATORI.get(d.year, [])


def e_zi_lucratoare(d):
    """True dacă d nu e weekend și nu e sărbătoare legală. Pură."""
    return d.weekday() < 5 and not _e_sarbatoare(d)


def urmatoarea_zi_lucratoare(d):
    """Prima zi lucrătoare ≥ d. Pură."""
    while not e_zi_lucratoare(d):
        d += timedelta(days=1)
    return d


def _ultima_zi_luna(an, luna):
    return calendar.monthrange(an, luna)[1]


def _luna_urmatoare(an, luna):
    return (an + 1, 1) if luna == 12 else (an, luna + 1)


def _data_nominala(tip, an, luna=None, trim=None):
    """Data scadenței nominală (înainte de mutarea la zi lucrătoare)."""
    tip = tip.lower()
    if tip == "d205":
        # ultima zi februarie an următor
        a = an + 1
        return date(a, 2, _ultima_zi_luna(a, 2))
    if tip == "d101":
        # 25 martie an următor (PROVIZORIU)
        return date(an + 1, 3, 25)

    if trim is not None:
        # luna următoare trimestrului: T1->4, T2->7, T3->10, T4->1(an+1)
        if trim == 4:
            an_s, luna_s = an + 1, 1
        else:
            an_s, luna_s = an, trim * 3 + 1
    elif luna is not None:
        an_s, luna_s = _luna_urmatoare(an, luna)
    else:
        raise ValueError("scadenta: lipsește luna sau trim pentru %r" % tip)

    if tip in _ULTIMA_ZI:
        zi = _ultima_zi_luna(an_s, luna_s)
    else:
        zi = _ZIUA.get(tip, 25)
    return date(an_s, luna_s, zi)


def scadenta_data(tip, an, luna=None, trim=None):
    """Scadența ca obiect date (mutată la zi lucrătoare). Pură."""
    nominala = _data_nominala(tip, an, luna=luna, trim=trim)
    return urmatoarea_zi_lucratoare(nominala)


def scadenta(tip, an, luna=None, trim=None):
    """Scadența ca string 'zz/ll/aaaa' (mutată la zi lucrătoare). Pură."""
    d = scadenta_data(tip, an, luna=luna, trim=trim)
    return d.strftime("%d/%m/%Y")
