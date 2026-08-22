# -*- coding: utf-8 -*-
"""Codurile de concediu medical PENTRU ECRAN: denumirea din nomenclator + procentul din registru.

DE CE EXISTĂ (22.08.2026, prag 1, decizia D3 a lui Costin). `static/js/ecrane/flux_concediu.js` avea
lista scrisă de mână — 18 coduri, cu procentele lipite în etichetă („01 — Boală obișnuită (55/65/75%)").
Consecințe măsurate: ecranul **nu oferea** codurile `11`, `91`, `92`, care există în nomenclator cu
temei și pe care aplicația le acceptă — deci **bloca un contabil să introducă un cod legal**. Iar
procentele erau o valoare fiscală scrisă în JS, adică în afara registrului (interdicția 1).

DECIZIA (Costin, 22.08.2026): *„Procentele rămân pe ecran, dar nu scrise de mână. Vin din registru, cu
propria lor dată de valabilitate. Eticheta se compune la randare: denumirea din nomenclator, procentul
din registru, pe data certificatului. Niciuna din cele două nu se scrie în JS."*

CELE DOUĂ SURSE, fiecare la locul ei, fiindcă **îmbătrânesc din motive diferite**:
  - denumirea  -> `core/nomenclator_cm.py`  (Nomenclatorul 9, structura ANAF)
  - procentul  -> `core/salarizare.procent_cm(cod, zile, la_data)`, care are DOUĂ variante datate ale
                  art. 17(1) din OUG 158/2005 (pre-Legea 141/2025 = 75% uniform; de la 01.08.2025 =
                  55/65/75 progresiv), fiecare cu `Temei` verificat la MO.

CUM SE COMPUNE SCARA lui 01, fără s-o scriu nicăieri: se INTEROGHEAZĂ registrul pe duratele care
schimbă rezultatul (7 / 14 / 15 zile) și se păstrează valorile distincte, în ordine. Dacă legea se
schimbă, eticheta se schimbă singură — asta e diferența față de „55/65/75" scris în JS.

CE NU FACE: nu decide nimic despre cod 10 (reducere de timp de muncă), care n-are procent, ci formula
art. 19 — pentru el se întoarce `procent = None`, iar ecranul nu afișează paranteza.
"""
from core import nomenclator_cm

# Duratele care pot schimba procentul la codul progresiv. NU sunt praguri de lege scrise aici — sunt
# puncte de SONDARE a registrului; dacă legea capătă alt prag, se adaugă o durată, nu un procent.
_DURATE_SONDA = (7, 14, 15, 30)


def _procente_distincte(cod, la_data):
    from core import salarizare
    vazute = []
    for zile in _DURATE_SONDA:
        try:
            p = salarizare.procent_cm(cod, zile, la_data=la_data)
        except ValueError:
            return None            # cod fără procent (10 — formula art. 19)
        except Exception:
            return None
        v = int(round(float(p) * 100))
        if v not in vazute:
            vazute.append(v)
    return vazute or None


def optiuni(la_data=None):
    """[{cod, denumire, procent_text}] pentru ecran, pe data certificatului.

    `procent_text` e None când codul n-are procent. Eticheta NU se compune aici: ecranul o compune,
    ca să se vadă în interfață că sunt două lucruri, nu un șir."""
    out = []
    for cod, _et in nomenclator_cm.optiuni():
        p = _procente_distincte(cod, la_data)
        out.append({
            "cod": cod,
            "denumire": nomenclator_cm.eticheta(cod),
            "procent_text": ("/".join(str(x) for x in p) + "%") if p else None,
        })
    return out
