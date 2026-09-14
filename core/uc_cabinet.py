# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/cabinet`.

[P7 · valul use-case, 13.09.2026] Corpurile astea stateau in `main.py`, adica in stratul HTTP, si
isi deschideau singure tranzactia. Textul canonic (`PLAN_HARDENING.md:827`) spune ca use-case-ul e
cel care **detine tranzactia si orchestreaza**; aici e mutarea, nu o rescriere.

CE S-A PASTRAT, literă cu literă: corpul, cu tot cu blocurile `with db.get_conn()`, in aceeasi
ordine, cu aceleasi efecte. CE S-A TRADUS: `HTTPException(cod, mesaj)` a devenit
`_erori.<Clasa>(mesaj)` — acelasi mesaj, iar codul se pune la loc in stratul HTTP, dintr-o singura
harta. Se poate face fiindca `HTTPException` **nu e prinsa nicaieri** in aplicatie.

CE A RAMAS IN `main.py`: semnatura rutei (FastAPI valideaza pe ea), docstringul ei, si o linie care
cheama functia de aici prin adaptorul `_http`.
"""

from core import db, documente_api
from core import repo_tenants
from core import erori as _erori
from core import uc_comun as _uc_comun


def api_cheie_creeaza(corp, ctx):
    """[P7 · use-case] Corpul rutei `/cabinet/api-chei`; docstringul ei a ramas in stratul HTTP."""
    from core import api_public as _ap
    # [lotul 9] Corpul gol crea o cheie **fara nume** — iar cheia se arata O SINGURA DATA, la
    # creare. Una fara nume nu se mai poate recunoaste in lista ca s-o revoci: ramane activa, si
    # nimeni nu stie ce deschide.
    _nume = str((corp or {}).get("nume") or "").strip()
    if not _nume:
        raise _erori.DateInvalide("Cheia de API are nevoie de un nume. Ea se arată o singură dată, "
                                     "la creare; una fără nume nu se mai poate recunoaște în listă ca "
                                     "s-o revoci.")
    with db.get_conn() as conn:
        return _ap.genereaza(conn, ctx["firm"], _nume)


def api_chei_lista(ctx):
    """[P7 · use-case] Corpul rutei `/cabinet/api-chei`; docstringul ei a ramas in stratul HTTP."""
    from core import api_public as _ap
    with db.get_conn() as conn:
        return {"chei": _ap.lista(conn, ctx["firm"])}


def api_cheie_revoca(kid, ctx):
    """[P7 · use-case] Corpul rutei `/cabinet/api-chei/{kid}`; docstringul ei a ramas in stratul HTTP."""
    from core import api_public as _ap
    with db.get_conn() as conn:
        r = _ap.revoca(conn, ctx["firm"], kid)
    if r.get("eroare"):
        raise _erori.Inexistent(r["eroare"])
    return r


def cabinet_consolidare(an, luna, ctx):
    """[P7 · use-case] Corpul rutei `/cabinet/consolidare`; docstringul ei a ramas in stratul HTTP."""
    _uc_comun._cere_perioada(an, luna)
    from datetime import date as _d
    from core import kpi_client as _kpi
    azi = _d.today()
    an = an or azi.year
    luna = luna or azi.month
    with db.get_conn() as conn, conn.cursor() as cur:
        tenanti = repo_tenants.firme_cu_schema(cur, ctx["firm"])
    firme = []
    total = {"venituri": 0, "cheltuieli": 0, "profit": 0,
             "cash": 0, "de_incasat": 0, "de_platit": 0}
    with db.get_conn() as conn:
        for tid, nume, schema in tenanti:
            try:
                k = _kpi.kpi_din_balanta(documente_api.balanta(conn, schema, an, luna))
            except Exception:
                k = None
            firme.append({"tenant_id": tid, "nume": nume, "kpi": k})
            if k:
                for c in total:
                    total[c] = round(total[c] + k[c], 2)
    return {"an": an, "luna": luna, "firme": firme, "total": total}
