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

# Sărbători legale RO. Cele Paște-dependente (Vinerea Mare, Paște, Rusalii) se
# CALCULEAZĂ din data Paștelui ortodox (Legea 220/2016), NU se hardcodează per an -
# altfel calendarul devine incomplet in tacere peste cativa ani (istoric: 2025 lipsea
# COMPLET, iar Vinerea Mare lipsea din 2026 -> proratare CM gresita). Fixe = art. 139
# Codul muncii. Sursa unica: sarbatori_legale(an).
_SARB_FIXE = [(1, 1), (1, 2), (1, 6), (1, 7), (1, 24), (5, 1), (6, 1),
              (8, 15), (11, 30), (12, 1), (12, 25), (12, 26)]
_AN_MIN, _AN_MAX = 2024, 2099   # set fix (cu 6-7 ian) valabil din 2024; offset iulian +13 pana 2099
_cache_sarb = {}

# ziua nominală a scadenței per tip (în luna următoare perioadei)
_ZIUA = {"d394": 30}          # restul: 25 ; d406: ultima zi (tratat separat)
_ULTIMA_ZI = {"d406"}          # scadența = ultima zi a lunii


def paste_ortodox(an):
    """Data Paștelui ortodox (gregorian) — algoritmul Meeus pe calendarul iulian,
    convertit la gregorian (+13 zile, valabil 1900-2099). Verificat: 2025=20.04,
    2026=12.04, 2027=02.05."""
    a, b, c = an % 19, an % 4, an % 7
    d = (19 * a + 15) % 30
    e = (2 * b + 4 * c + 6 * d + 6) % 7
    zi = 22 + d + e
    iul = date(an, 3, zi) if zi <= 31 else date(an, 4, d + e - 9)
    return iul + timedelta(days=13)


def sarbatori_legale(an):
    """set de (lună, zi) — sărbătorile legale RO pentru an. Fixe (art. 139 Codul muncii)
    + Paște-dependente: Vinerea Mare (Paște−2), Paște (duminică+luni), Rusalii (Paște+49
    duminică, +50 luni). EȘUEAZĂ ZGOMOTOS in afara [2024, 2099] — un an neacoperit trebuie
    sa dea eroare vizibila, nu rezultat gresit TACUT (cazul 2025)."""
    if not (_AN_MIN <= an <= _AN_MAX):
        raise ValueError("sarbatori_legale: an %d neacoperit (valabil %d-%d). Extinde explicit."
                         % (an, _AN_MIN, _AN_MAX))
    if an not in _cache_sarb:
        p = paste_ortodox(an)
        mob = [p - timedelta(days=2), p, p + timedelta(days=1),
               p + timedelta(days=49), p + timedelta(days=50)]
        _cache_sarb[an] = set(_SARB_FIXE) | {(d.month, d.day) for d in mob}
    return _cache_sarb[an]


def _e_sarbatoare(d):
    return (d.month, d.day) in sarbatori_legale(d.year)


def e_zi_lucratoare(d):
    """True dacă d nu e weekend și nu e sărbătoare legală. Pură."""
    return d.weekday() < 5 and not _e_sarbatoare(d)


def zile_lucratoare_luna(an, luna):
    """Nr. de zile lucrătoare (L-V, FĂRĂ sărbători legale) dintr-o lună. SURSA UNICĂ —
    inlocuieste calculele ad-hoc weekday<5 (ignorau sarbatorile -> proratare CM gresita,
    OUG 158/2005 art.10) si tabelele hardcodate _D112_NZL."""
    return sum(1 for z in range(1, calendar.monthrange(an, luna)[1] + 1)
               if e_zi_lucratoare(date(an, luna, z)))


def zile_lucratoare_interval(start, end):
    """Nr. de zile lucrătoare (L-V, FĂRĂ sărbători legale) între start și end inclusiv.
    Folosit la auto-calcul zilelor de CM (numărătorul proratării, OUG 158/2005 art.10)."""
    if end < start:
        return 0
    n, d = 0, start
    while d <= end:
        if e_zi_lucratoare(d):
            n += 1
        d += timedelta(days=1)
    return n


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
