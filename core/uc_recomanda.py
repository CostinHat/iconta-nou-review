# -*- coding: utf-8 -*-
"""USE_CASE — corpurile rutelor `/recomanda`.

[P7 · valul use-case, 13.09.2026] Corpurile au plecat din `main.py` VERBATIM, cu tranzactiile lor
cu tot: `with db.get_conn()` se deschide aici, in stratul care detine unitatea de lucru, nu in
stratul HTTP. `HTTPException(cod, mesaj)` a devenit `_erori.<Clasa>(mesaj)`; codul se pune la loc
in invelisul din `main.py`, dintr-o harta fixa. Mesajul si ordinea efectelor sunt neatinse.
"""
from core import db, auth_api
from core import uc_comun as _uc_comun


def recomanda_preview(ctx):
    """[P7 · use-case] Corpul rutei `/recomanda/preview`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        r = auth_api.get_cabinet(conn, ctx["firm"])
    nume_cabinet = (r.get("cabinet") or {}).get("nume", "") if r.get("ok") else ""
    return {"ok": True, "html": _uc_comun._mesaj_promo_html(nume_cabinet),
            "subiect": "O recomandare pentru cabinetul tau: iConta.eu"}



def trimite_recomandari(date, ctx):
    """[P7 · use-case] Corpul rutei `/recomanda`; docstringul ei a ramas in stratul HTTP."""
    emails = [e.strip() for e in (date.emails or []) if e and e.strip()]
    with db.get_conn() as conn:
        r = auth_api.get_cabinet(conn, ctx["firm"])
    nume_cabinet = (r.get("cabinet") or {}).get("nume", "") if r.get("ok") else ""
    html = _uc_comun._mesaj_promo_html(nume_cabinet)
    rezultate = _uc_comun._trimite_recomandari(emails, html, "O recomandare pentru cabinetul tau: iConta.eu")
    return {"ok": True, "rezultate": rezultate}
