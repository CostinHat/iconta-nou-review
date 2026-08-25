# -*- coding: utf-8 -*-
"""core/prapastie_salariu.py — R49, varianta (c): prăpastia, cu cifre, calculate cu TOATE elementele.

Decizia lui Costin, 25.08.2026: *„Contabilul care mărește un salariu cu 100 de lei are nevoie
să vadă CÂT pierde salariatul, nu că pierde. «Se pierde facilitatea» e adevărat și inutil: el
știe regula, vrea suma."*

De ce (c) e posibilă, deși R28 a scos varianta veche. Blocul de atunci pasa **doi** din cei
optsprezece parametri ai lui `salarizare.calcul_salariu`; restul luau valorile implicite, deci
cifra nu putea coincide cu fluturașul de peste o lună. Ecranul de angajare colectează însă
**toate** elementele care intră în calcul: persoane în întreținere, data nașterii (sub 26),
copii școlarizați, declarația părintelui, tipul de normă, orele/zi, județul, data angajării,
scutirea de contribuția minimă, tichetul de masă. Deci nu lipsesc date — lipsea pasarea lor.

CE ÎNTOARCE, și ce NU:
  - `net_acum`      — netul la brutul introdus, cu toate elementele;
  - `prag`          — salariul minim brut la data cerută (din registru, nu din cod);
  - `net_la_prag`   — netul dacă brutul ar fi exact pragul;
  - `pierdere`      — `net_la_prag - net_acum`, POZITIVĂ când netul SCADE peste prag;
  - `brut_egal`     — cel mai mic brut la care netul redevine ≥ `net_la_prag`, căutat pe pași
                      de un leu între prag și `plafon_facilitate_salariu_minim` (registru);
                      `None` dacă nu se atinge sub plafon.
  - `cod`           — când nu se aplică: de ce, dintr-un vocabular ÎNCHIS. Textul îl compune
                      ecranul.

NU e o estimare de fluturaș și n-o înlocuiește: `functie_baza=True`, o singură funcție de bază,
fără concedii, fără corecții. Se cheamă în momentul angajării, cu ce s-a completat pe ecran.

`brut_egal` se caută, nu se rezolvă analitic: formula are praguri și rotunjiri, iar o formulă
inversă ar fi a doua implementare a aceleiași reguli — exact ce interzice P7.
"""
from datetime import date as _date

from core import common as _c
from core import salarizare as _s

# Capătul de sus al prăpastiei NU se inventează: e `plafon_facilitate_salariu_minim` din
# registru — brutul peste care facilitatea nu se mai aplică deloc. Prima formă folosea un
# `1.6` scris de mână, prins de `test_constante_nesursate`: era o valoare fiscală ghicită,
# nu o limită de căutare.
#
# Vocabular ÎNCHIS pentru motivul neaplicării. Textul îl compune ecranul (DS cap.13: textul
# nu e purtător de decizie); un `motiv` în proză într-un dicționar e o afirmație netipată.
COD_FARA_BRUT = "FARA_BRUT"
COD_SUB_PRAG = "SUB_PRAG"
COD_NETUL_NU_SCADE = "NETUL_NU_SCADE"


def _net(brut, el, la_data):
    r = _s.calcul_salariu(
        brut,
        persoane=el.get("persoane_intretinere") or 0,
        sub_26=_s.sub_26_la(el.get("data_nastere"), la_data) if el.get("data_nastere") else False,
        copii_scoala=el.get("copii_scolarizati") or 0,
        declaratie_copii=bool(el.get("declaratie_copii")),
        functie_baza=True,
        la_data=la_data,
        norma_intreaga=(el.get("tip_norma") or "intreaga") == "intreaga",
        exceptat_suprataxare=bool(el.get("scutit_contrib_minim")),
        data_angajare=el.get("data_angajare"),
    )
    return float(r["net"] if isinstance(r, dict) else getattr(r, "net"))


def prapastie(brut, elemente=None, la_data=None):
    """Ce pierde salariatul dacă brutul trece peste salariul minim. Pură (citește registrul)."""
    el = dict(elemente or {})
    la_data = la_data or _date.today()
    # `cota` intoarce (valoare, temei) — temeiul nu se arunca, se poarta mai departe.
    _val, _temei = _c.cota("salariu_minim", la_data)
    prag = float(_val)
    _plaf, _plaf_temei = _c.cota("plafon_facilitate_salariu_minim", la_data)
    plafon = float(_plaf)
    brut = float(brut or 0)
    out = {"prag": prag, "prag_temei": _temei, "plafon": plafon,
           "plafon_temei": _plaf_temei, "la_data": str(la_data), "peste_prag": brut > prag}
    if brut <= 0:
        return {**out, "aplicabil": False, "cod": COD_FARA_BRUT}
    net_acum = _net(brut, el, la_data)
    net_la_prag = _net(prag, el, la_data)
    out.update({"net_acum": round(net_acum, 2), "net_la_prag": round(net_la_prag, 2),
                "pierdere": round(net_la_prag - net_acum, 2)})
    if not out["peste_prag"] or out["pierdere"] <= 0:
        # Sub prag, sau peste prag fără scădere: nu e nicio prăpastie de arătat.
        return {**out, "aplicabil": False,
                "cod": (COD_SUB_PRAG if not out["peste_prag"] else COD_NETUL_NU_SCADE)}
    # cel mai mic brut la care netul redevine cel puțin cât la prag
    brut_egal = None
    for x in range(int(prag) + 1, int(plafon) + 1):
        if _net(float(x), el, la_data) >= net_la_prag:
            brut_egal = float(x)
            break
    return {**out, "aplicabil": True, "brut_egal": brut_egal,
            "temei": "OUG 156/2024 art. LXVI, modificat prin OUG 89/2025 art. III"}
