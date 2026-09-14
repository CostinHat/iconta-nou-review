# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/firme_scoase`.

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

from core import db
from core import repo_utilizatori
import psycopg2.extras as _E_audit


def firme_scoase(ctx):
    """[P7 · use-case] Corpul rutei `/firme-scoase`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn, conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
        return {"firme": [dict(r) for r in repo_utilizatori.firme_scoase_din_portofoliu(cur, ctx["firm"])]}
