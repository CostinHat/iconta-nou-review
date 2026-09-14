# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/gdpr`.

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
from core.mesaje import FARA_CABINET
from core import erori as _erori
from core.mesaje import (FARA_CABINET)
from core import db, observare as _obs
from core import repo_admin
import json as _json_audit


def gdpr_sterge_previzualizare(cabinet_id, ctx):
    """[P7 · use-case] Corpul rutei `/gdpr/sterge-cabinet/{cabinet_id}/previzualizare`; docstringul ei a ramas in stratul HTTP."""
    from core import gdpr_sterge as _gs
    with db.get_conn() as conn:
        try:
            return _gs.previzualizare(conn, cabinet_id)
        except ValueError as e:
            raise _erori.Inexistent(str(e))


def gdpr_sterge_executa(cabinet_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/gdpr/sterge-cabinet/{cabinet_id}/executa`; docstringul ei a ramas in stratul HTTP."""
    from core import gdpr_sterge as _gs
    with db.get_conn() as conn:
        try:
            return _gs.executa(conn, cabinet_id, date.confirmare, ctx.get("uid"))
        except ValueError as e:
            raise _erori.DateInvalide(str(e))


def gdpr_cerere_stergere(date, ctx):
    """[P7 · use-case] Corpul rutei `/gdpr/cerere-stergere`; docstringul ei a ramas in stratul HTTP."""
    from core import gdpr_cerere as _gc
    cab = ctx.get("firm")
    if not cab:
        raise _erori.CerereGresita(FARA_CABINET)
    with db.get_conn() as conn:
        try:
            r = _gc.depune_cerere(conn, cab, ctx.get("uid"), date.confirmare_nume, date.motiv)
            conn.commit()
        except ValueError as e:
            raise _erori.DateInvalide(str(e))
    # [P5 val 3] AICI, nu înăuntru: cererea e comisă și conexiunea s-a întors în pool. Efectul
    # ireversibil vine ultimul, iar apelul la Brevo (termen 10 s) nu mai ține nimic din pool.
    _gc.anunta_echipa(r.pop("anunt", None))
    return r


def gdpr_export_cabinet(cabinet_id, ctx):
    """[P7 · use-case] Corpul rutei `/gdpr/export-cabinet`; docstringul ei a ramas in stratul HTTP."""
    from core import gdpr_export as _ge
    if ctx["rol"] == "superadmin":
        cab = cabinet_id
        if not cab:
            raise _erori.DateInvalide("Alegeți cabinetul (obligatoriu pentru superadmin).")
    else:
        # [lotul 9] `cabinet_id` era IGNORAT tacut pentru cine nu e superadmin: cereai exportul
        # cabinetului X si primeai, cu `200`, arhiva cabinetului TAU. Nu e o scurgere — dar pe o
        # rutà GDPR, „am exportat" despre alt cabinet decat cel cerut e cea mai proasta forma de
        # tacere: arhiva pleaca mai departe cu numele gresit in minte.
        if cabinet_id is not None and cabinet_id != ctx.get("firm"):
            raise _erori.FaraDrept("Poți exporta numai cabinetul tău. Cererea a numit "
                                     "cabinetul %s, iar al tău e %s — arhiva n-a fost produsă."
                                     % (cabinet_id, ctx.get("firm")))
        cab = ctx.get("firm")
    if not cab:
        raise _erori.CerereGresita(FARA_CABINET)
    with db.get_conn() as conn:
        _zip = _ge.export_cabinet(conn, cab)
        try:  # [F199] jurnalizare export (cine/cand, FARA continut)
            with conn.cursor() as _cur:
                repo_admin.scrie_audit_cu_detalii(_cur, ctx.get("uid"), "cabinet", cab, _json_audit.dumps({"octeti": len(_zip)}))
            conn.commit()
        except Exception as _e:
            _obs.esec_secundar("audit_log export GDPR", _e, alerta=True)  # inghitit, dar nu tacut (27.07.2026)
    return _zip, cab

