# -*- coding: utf-8 -*-
"""Plan de conturi OMFP 1802/2014 - denumiri (fallback cand planul tenantului e gol, conturile de venit din Date firmă).

[deficiența 387, comanda Costin 9.1, 19.10.2026] Denumirile vin din `core.plan_conturi_omfp.PLAN` — GENERAT din textul ordinului (pct.594,
forma consolidată; `scripts/plan_conturi_omfp.py`). Aici era o copie scrisă de mână (188 de conturi, 13 denumiri prescurtate), a doua sursă
a aceluiași plan. Rămân numai conturile grupei 73 din planul entităților fără scop patrimonial (OMFP 3103/2017), care nu sunt în 1802."""
from core.plan_conturi_omfp import PLAN as _PLAN_1802

PLAN_OMFP = {c: d for c, (d, _f) in _PLAN_1802.items()}
PLAN_OMFP.update({
    # OMFP 3103/2017 - persoane juridice fara scop patrimonial (grupa 73, verificat la sursa)
    "731": "Venituri din cotizațiile membrilor, contribuțiile bănești sau în natură ale membrilor și simpatizanților, din cote-părți primite potrivit statutului",
    "732": "Venituri din taxele de înregistrare stabilite potrivit legislației în vigoare",
    "733": "Venituri din donații, sume sau bunuri primite prin sponsorizare și ajutoare",
    "734": "Venituri financiare rezultate din activitățile fără scop patrimonial",
    "736": "Venituri din subvenții de exploatare",
    "738": "Alte venituri din activitățile fără scop patrimonial",
})


def denumire_omfp(cont):
    """Denumirea OMFP pentru un simbol de cont; cadere pe sinteticul de 3 cifre; '' daca necunoscut."""
    c = str(cont or "").strip()
    if c in PLAN_OMFP:
        return PLAN_OMFP[c]
    if len(c) > 3 and c[:4] in PLAN_OMFP:
        return PLAN_OMFP[c[:4]]
    if len(c) >= 3 and c[:3] in PLAN_OMFP:
        return PLAN_OMFP[c[:3]]
    return ""
