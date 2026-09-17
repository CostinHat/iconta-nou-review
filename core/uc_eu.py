# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/eu`.

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

from core import asistenti_api as _asist
from core import db, auth_api, coada_api
from core import nucleu as _nucleu
from core import repo_admin
from core import repo_utilizatori
from core.mesaje import mesaj_din_cod, DOAR_PATRON, DOAR_ADMIN_CABINET
import psycopg2.extras as _E_audit
from core import erori as _erori


def eu_anunturi(ctx):
    """[P7 · use-case] Corpul rutei `/eu/anunturi`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn, conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
        rows = [dict(r) for r in repo_admin.anunturi_pentru_cabinet(cur, ctx.get("firm"))]
    for r in rows:
        r["creat_la"] = str(r["creat_la"])
    return {"anunturi": rows}


def eu_anunt_confirma(aid, ctx):
    """[P7 · use-case] Corpul rutei `/eu/anunturi/{aid}/confirma`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn, conn.cursor() as cur:
        r = repo_admin.confirma_anunt(cur, aid, ctx.get("firm"))
        conn.commit()
    if not r:
        raise _erori.Inexistent("anunt inexistent")
    return {"ok": True}


def eu_calitate(de, pana, ctx):
    """[P7 · use-case] Corpul rutei `/eu/calitate`; docstringul ei a ramas in stratul HTTP."""
    if de and pana and str(pana) < str(de):
        raise _erori.DateInvalide("Sfârșitul intervalului (%s) e înaintea începutului "
                                     "(%s). Raportul se cere pe un interval, iar intervalul "
                                     "are o ordine." % (pana, de))
    with db.get_conn() as conn:
        r = _asist.calitate(conn, ctx["firm"], ctx["uid"], de=de, pana=pana)
        if not r.get("ok"):
            raise _erori.Inexistent(mesaj_din_cod(r.get("cod")))
        return r


def eu_educatie(ctx):
    """[P7 · use-case] Corpul rutei `/eu/educatie`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        return {"ok": True, "educatii": []}
    with db.get_conn() as conn:
        return _asist.educatie_de_aratat(conn, ctx["firm"])


def eu_patru_ochi_stare(ctx):
    """[P7 · use-case] Corpul rutei `/eu/patru-ochi`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        return coada_api.patru_ochi_stare(conn, ctx["firm"])


def eu_patru_ochi(date, ctx):
    """[P7 · use-case] Corpul rutei `/eu/patru-ochi`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise _erori.FaraDrept(DOAR_PATRON)
    with db.get_conn() as conn:
        return _asist.patru_ochi_seteaza(conn, ctx["firm"], date.activ)


def eu_educatie_vazut(ctx):
    """[P7 · use-case] Corpul rutei `/eu/educatie/patru-ochi/vazut`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise _erori.FaraDrept(DOAR_PATRON)
    with db.get_conn() as conn:
        return _asist.educatie_marcheaza(conn, ctx["firm"])


def eu_competente_get(ctx):
    """[P7 · use-case] Corpul rutei `/eu/competente`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        return _asist.get_competente_proprii(conn, ctx["uid"])


def eu_competente_set(date, ctx):
    """[P7 · use-case] Corpul rutei `/eu/competente`; docstringul ei a ramas in stratul HTTP.

    [B2, 17.09.2026] CINE POATE ACORDA. `poate_valida`/`poate_depune` sunt privilegii de CONTROL
    INTERN (patru-ochi): le acordă administratorul cabinetului prin `/asistenti/{uid}/permisiuni`, nu
    și le acordă fiecare singur. Până azi orice angajat sub `cere_cabinet` își scria toate trei
    flagurile pe propriul rând și apoi aproba orice. Acum ruta e rezervată admin_firma/superadmin
    (care își administrează legitim propriile competențe); restul primesc competențele de la admin."""
    if ctx.get("rol") not in ("admin_firma", "superadmin"):
        raise _erori.FaraDrept(DOAR_ADMIN_CABINET)
    with db.get_conn() as conn:
        return _asist.set_competente_proprii(
            conn, ctx["uid"], date.poate_pregati, date.poate_valida, date.poate_depune)


def eu_schimba_parola(date, ctx):
    """[P7 · use-case] Corpul rutei `/eu/schimba-parola`; docstringul ei a ramas in stratul HTTP."""
    if not _nucleu.parola_ok(date.parola_noua):
        raise _erori.CerereGresita(_nucleu.PAROLA_MESAJ)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            row = repo_utilizatori.hash_parola(cur, ctx["uid"])
        if not row or not auth_api.verifica_parola_orice(date.parola_veche, row[0]):
            raise _erori.FaraDrept("Parola actuala este gresita.")
        auth_api.schimba_parola(conn, ctx["uid"], date.parola_noua)
    return {"ok": True}


def eu_profil(date, ctx):
    """[P7 · use-case] Corpul rutei `/eu/profil`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        r = auth_api.actualizeaza_profil(conn, ctx["uid"], nume=date.nume, prenume=date.prenume)
    if not r.get("ok"):
        raise _erori.DateInvalide(mesaj_din_cod(r.get("cod")))
    return r


def eu_cabinet_get(ctx):
    """[P7 · use-case] Corpul rutei `/eu/cabinet`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn:
        r = auth_api.get_cabinet(conn, ctx["firm"])
    if not r.get("ok"):
        raise _erori.Inexistent(mesaj_din_cod(r.get("cod")))
    return r


def eu_cabinet_set(date, ctx):
    """[P7 · use-case] Corpul rutei `/eu/cabinet`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] not in ("admin_firma", "superadmin"):
        raise _erori.FaraDrept("Doar administratorul cabinetului poate edita datele cabinetului.")
    with db.get_conn() as conn:
        r = auth_api.actualizeaza_cabinet(conn, ctx["firm"], nume=date.nume, cui=date.cui)
    if not r.get("ok"):
        raise _erori.DateInvalide(mesaj_din_cod(r.get("cod")))
    return r


def eu_permisiuni(ctx):
    """[P7 · use-case] Corpul rutei `/eu/permisiuni`; docstringul ei a ramas in stratul HTTP."""
    if ctx.get("rol") == "superadmin":
        return {"poate_pregati": True, "poate_valida": True, "poate_depune": True,
                "rol": "superadmin"}
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            r = repo_utilizatori.permisiuni(cur, ctx["uid"])
    if not r:
        raise _erori.Inexistent("user inexistent")
    return {"poate_pregati": bool(r[0]), "poate_valida": bool(r[1]),
            "poate_depune": bool(r[2]), "rol": r[3]}
