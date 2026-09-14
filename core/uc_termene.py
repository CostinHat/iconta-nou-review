# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/termene`.

[P7 · valul use-case, 13.09.2026] Corpurile astea stateau in `main.py`, adica in stratul HTTP, si
isi deschideau singure tranzactia. Textul canonic (`PLAN_HARDENING.md:840`) spune ca use-case-ul e
cel care **detine tranzactia si orchestreaza**; aici e mutarea, nu o rescriere.

CE S-A PASTRAT, literă cu literă: corpul, cu tot cu blocurile `with db.get_conn()`, in aceeasi
ordine, cu aceleasi efecte. CE S-A TRADUS: `HTTPException(cod, mesaj)` a devenit
`_erori.<Clasa>(mesaj)` — acelasi mesaj, iar codul se pune la loc in stratul HTTP, dintr-o singura
harta. Se poate face fiindca `HTTPException` **nu e prinsa nicaieri** in aplicatie.

CE A RAMAS IN `main.py`: semnatura rutei (FastAPI valideaza pe ea), docstringul ei, si o linie care
cheama functia de aici prin adaptorul `_http`.
"""

from core import afirmatii as _af
from core import db, auth_api, termene_api
from core.common import azi_ro


def termene_portofoliu(ctx):
    """[P7 · use-case] Corpul rutei `/termene`; docstringul ei a ramas in stratul HTTP."""
    from core import firma_rezumat as _fr
    azi = azi_ro()   # [fus] fereastra scadentelor = verdict (ce vede contabilul), zi RO
    with db.get_conn() as conn:
        firme = auth_api.tenantii_userului(conn, ctx["uid"])
        model = _fr.citeste(conn, [f.get("id") for f in firme], ["termene"])
    firme_eval = []
    neevaluate = []
    for f in firme:
        st = (model.get(f.get("id")) or {}).get("termene") or {}
        d = st.get("date") or {}
        if st.get("stare") == _fr.CURENT and d.get("eval"):
            firme_eval.append(d["eval"])
            continue
        if d.get("neevaluat"):
            neevaluate.append(d["neevaluat"])
            continue
        _n = _af.afirmatie(
            "necunoastere", "obligații fiscale",
            "Termenele acestei firme nu sunt încă recalculate — se actualizează în fundal.",
            domeniu_de=azi.isoformat(), domeniu_pana=azi.isoformat())
        _n["tenant_id"] = f.get("id")
        _n["nume"] = f.get("nume")
        _n["cauza"] = _n["motiv"]
        _n["prospetime"] = st.get("stare") or _fr.LIPSESTE
        neevaluate.append(_n)
    return termene_api.portofoliu(firme_eval, azi, neevaluate)
