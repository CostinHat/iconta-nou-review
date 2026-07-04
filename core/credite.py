# -*- coding: utf-8 -*-
"""Credite bancare, dobanzi, garantii - motor PUR (OMFP 1802/2014 pct. 360-364,
functiunea conturilor 162/168/519/801).
- termen LUNG (>12 luni): primire 5121=1621; dobanda angajata 666=1682,
  plata 1682=5121; rata 1621=5121; restanta 1621=1622;
- termen SCURT: primire 5121=5191; dobanda 666=5198, plata 5198=5121
  (sau direct 666=5121); rata 5191=5121; restanta 5191=5192;
- OVERDRAFT (descoperire de cont): nu se inregistreaza primirea, doar 666=5121;
- comision acordare esalonat: 471=5121 apoi lunar 628=471; comision lunar 627=5121;
- garantii NUMAI extracontabil: acordate D8011, primite D8021 (contrapartida
  tehnica 891); la eliberare se crediteaza."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")
CONTURI = {"lung": {"credit": "1621", "dobanda": "1682", "restant": "1622"},
           "scurt": {"credit": "5191", "dobanda": "5198", "restant": "5192"}}

def _d(x):
    v = Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)
    return v

def _tip(tip):
    if tip not in CONTURI:
        raise ValueError("tip: lung|scurt")
    return CONTURI[tip]

def nota_primire(suma, tip="lung", cont_banca="5121"):
    s = _d(suma)
    if s <= 0:
        raise ValueError("suma invalida")
    return {"linii": [(cont_banca, _tip(tip)["credit"], s)]}

def nota_dobanda_angajata(dobanda, tip="lung"):
    """Sfarsit de luna: 666 = 1682/5198 (dobanda datorata, neplatita inca)."""
    d = _d(dobanda)
    if d <= 0:
        raise ValueError("dobanda invalida")
    return {"linii": [("666", _tip(tip)["dobanda"], d)]}

def nota_plata(rata=0, dobanda=0, comision=0, tip="lung", cont_banca="5121",
               dobanda_angajata=True):
    """Plata rata+dobanda+comision. dobanda_angajata=True -> 1682/5198=5121
    (dobanda fusese deja pe 666); False -> 666=5121 direct."""
    r, d, co = _d(rata), _d(dobanda), _d(comision)
    if r < 0 or d < 0 or co < 0 or (r + d + co) <= 0:
        raise ValueError("valori invalide")
    c = _tip(tip)
    linii = []
    if r > 0:
        linii.append((c["credit"], cont_banca, r))
    if d > 0:
        linii.append((c["dobanda"] if dobanda_angajata else "666", cont_banca, d))
    if co > 0:
        linii.append(("627", cont_banca, co))
    return {"linii": linii}

def nota_restanta(suma, tip="lung"):
    """Rata nerambursata la scadenta: 1621=1622 / 5191=5192."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("suma invalida")
    c = _tip(tip)
    return {"linii": [(c["credit"], c["restant"], s)]}

def nota_garantie(suma, fel="primita", actiune="inregistrare"):
    """Extracontabil: primita D8021 / acordata D8011; eliberare = credit."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("suma invalida")
    if fel not in ("primita", "acordata"):
        raise ValueError("fel: primita|acordata")
    cont = "8021" if fel == "primita" else "8011"
    if actiune == "inregistrare":
        return {"linii": [(cont, "891", s)]}
    if actiune == "eliberare":
        return {"linii": [("891", cont, s)]}
    raise ValueError("actiune: inregistrare|eliberare")
