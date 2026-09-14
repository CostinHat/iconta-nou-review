# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/notificari`.

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

from core import db
import core.notificari_api as _notif


def notificari_lista(doar_necitite, ctx):
    """[P7 · use-case] Corpul rutei `/notificari`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        return _notif.lista(conn, ctx["uid"], doar_necitite=doar_necitite)


def notificari_contor(ctx):
    """[P7 · use-case] Corpul rutei `/notificari/contor`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        return _notif.contor(conn, ctx["uid"])


def notificari_sumar(ctx):
    """[P7 · use-case] Corpul rutei `/notificari/sumar`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        return _notif.sumar(conn, ctx["uid"])


def notificari_citit_toate(ctx):
    """[P7 · use-case] Corpul rutei `/notificari/citit`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        return _notif.marcheaza_citit(conn, ctx["uid"])


def notificari_citit_una(nid, ctx):
    """[P7 · use-case] Corpul rutei `/notificari/{nid}/citit`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        return _notif.marcheaza_citit(conn, ctx["uid"], notif_id=nid)
