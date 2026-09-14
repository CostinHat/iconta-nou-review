# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/admin`.

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
from core import repo_admin
from core import repo_tenants
from core.mesaje import DOAR_ADMIN_ICONTA
import psycopg2.extras as _E_audit
from core import erori as _erori
from core.mesaje import (DOAR_ADMIN_ICONTA)
from core import db, observare as _obs
from core import uc_comun as _uc_comun


def admin_anunt_creeaza(date, ctx):
    """[P7 · use-case] Corpul rutei `/admin/anunturi`; docstringul ei a ramas in stratul HTTP."""
    if not (date.mesaj or "").strip():
        raise _erori.DateInvalide("mesaj gol")
    mesaj = date.mesaj.strip()
    data_af = (date.data_afisare or "").strip() or None
    n = 0
    with db.get_conn() as conn, conn.cursor() as cur:
        if date.cabinet_ids:  # [anunturi_alese_v1] cabinete alese cu bife
            for cid in date.cabinet_ids:
                repo_admin.adauga_anunt(cur, int(cid), mesaj, data_af)
                n += 1
        elif date.cabinet_id:
            repo_admin.adauga_anunt(cur, date.cabinet_id, mesaj, data_af)
            n = 1
        else:
            for (cid,) in repo_tenants.cabinete_active(cur):
                repo_admin.adauga_anunt(cur, cid, mesaj, data_af)
                n += 1
        conn.commit()
    return {"ok": True, "trimise": n}


def admin_alerte_fiscale(ctx):
    """[P7 · use-case] Corpul rutei `/admin/alerte-fiscale`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn, conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
        rows = [dict(r) for r in repo_admin.alerte_fiscale(cur)]
    for r in rows:
        r["creat_la"] = str(r["creat_la"])
    return {"alerte": rows}


def admin_alerta_tratata(aid, ctx):
    """[P7 · use-case] Corpul rutei `/admin/alerte-fiscale/{aid}/tratat`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn, conn.cursor() as cur:
        r = repo_admin.marcheaza_alerta_vazuta(cur, aid)
        conn.commit()
    if not r:
        raise _erori.Inexistent("alertă inexistentă")
    return {"ok": True}


def admin_activitate_cabinete(ctx):
    """[P7 · use-case] Corpul rutei `/admin/activitate/cabinete`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] != "superadmin":
        raise _erori.FaraDrept(DOAR_ADMIN_ICONTA)
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            rows = repo_admin.activitate_pe_cabinete(cur)
    return {"cabinete": rows}


def admin_cabinet_suspenda(firm_id, ctx):
    """[P7 · use-case] Corpul rutei `/admin/cabinete/{firm_id}/suspenda`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] != "superadmin":
        raise _erori.FaraDrept(DOAR_ADMIN_ICONTA)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            repo_tenants.suspenda_cabinetul(cur, firm_id)
    return {"ok": True}


def admin_cabinet_reactiveaza(firm_id, ctx):
    """[P7 · use-case] Corpul rutei `/admin/cabinete/{firm_id}/reactiveaza`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] != "superadmin":
        raise _erori.FaraDrept(DOAR_ADMIN_ICONTA)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            repo_tenants.reactiveaza_cabinetul(cur, firm_id)
    return {"ok": True}


def admin_sanatate_istoric(ore, ctx):
    """[P7 · use-case] Corpul rutei `/admin/sanatate/istoric`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] != "superadmin":
        raise _erori.FaraDrept(DOAR_ADMIN_ICONTA)
    ore = _uc_comun._interval_cerut(ore, "Numărul de ore de istoric", 1, 168, "ore")   # [R150]
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            rows = repo_admin.istoric_sanatate(cur, ore)
    return {"istoric": rows}



def admin_sanatate(ctx):
    """[P7 · use-case] Corpul rutei `/admin/sanatate`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] != "superadmin":
        raise _erori.FaraDrept(DOAR_ADMIN_ICONTA)
    import time as _time
    import shutil as _shutil
    import os as _os

    # --- server: load average, RAM, disk ---
    try:
        load1, load5, load15 = _os.getloadavg()
    except Exception:
        load1 = load5 = load15 = None

    ram = {"total_mb": None, "disponibil_mb": None, "folosit_procent": None}
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for linie in f:
                k, v = linie.split(":", 1)
                info[k.strip()] = int(v.strip().split()[0])  # kB
        total_kb = info.get("MemTotal", 0)
        disp_kb = info.get("MemAvailable", 0)
        if total_kb:
            ram = {
                "total_mb": round(total_kb / 1024, 1),
                "disponibil_mb": round(disp_kb / 1024, 1),
                "folosit_procent": round(100 * (1 - disp_kb / total_kb), 1),
            }
    except Exception:
        pass

    disc = {"total_gb": None, "liber_gb": None, "folosit_procent": None}
    try:
        total, folosit, liber = _shutil.disk_usage("/")
        disc = {
            "total_gb": round(total / (1024 ** 3), 1),
            "liber_gb": round(liber / (1024 ** 3), 1),
            "folosit_procent": round(100 * folosit / total, 1),
        }
    except Exception:
        pass

    uptime_sec = round(_time.time() - _uc_comun._APP_PORNIT_LA)

    # --- baza de date ---
    db_info = {"conexiuni": None, "marime": None}
    try:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                db_info["conexiuni"] = repo_admin.conexiuni_active(cur)[0]
                db_info["marime"] = repo_admin.marimea_bazei(cur)[0]
    except Exception as _e:
        _obs.esec_secundar("admin sanatate: info DB", _e)  # inghitit, dar nu tacut (27.07.2026)

    # --- erori recente (status >= 500 in ultimele 24h) ---
    erori_24h = 0
    lista_erori = []
    try:
        with db.get_conn() as conn:
            with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
                rows = repo_admin.ultimele_actiuni(cur)
                erori_24h = len(rows)
                lista_erori = rows[:50]
    except Exception as _e:
        _obs.esec_secundar("admin sanatate: erori 24h", _e)  # inghitit, dar nu tacut (27.07.2026)

    # [POST-P2 HARDENING] Starea infrastructurii P2, din INSTANTANEUL buclei de sănătate — nu
    # recalculată aici. Ruta e de administrare, dar tot o cerere: verificarea stă în afara ei.
    # `ok = None` înseamnă „încă neverificat", și NU se rotunjește la `true`.
    from core import firma_rezumat as _fr_s
    _p2 = _fr_s.stare_infrastructura()
    return {
        "server": {"load1": load1, "load5": load5, "load15": load15, "ram": ram, "disc": disc},
        "aplicatie": {"uptime_secunde": uptime_sec},
        "baza_date": db_info,
        "erori_24h": erori_24h,
        "erori_lista": lista_erori,
        "p2_infrastructure_ok": _p2["ok"],
        "p2_infrastructure_last_checked_at": (_p2["verificat_la"].isoformat()
                                              if _p2["verificat_la"] else None),
        "p2_infrastructure_probleme": [p["cod"] for p in _p2["probleme"]],
    }



def admin_activitate_cabinet(firm_id, limita, ctx):
    """[P7 · use-case] Corpul rutei `/admin/activitate/cabinet/{firm_id}`; docstringul ei a ramas in stratul HTTP."""
    if ctx["rol"] != "superadmin":
        raise _erori.FaraDrept(DOAR_ADMIN_ICONTA)
    limita = _uc_comun._interval_cerut(limita, "Numărul de înregistrări", 1, 2000, "înregistrări")
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
            # [R150] Pana azi, un cabinet INEXISTENT primea `{"activitate": []}` — adica raspunsul
            # „cabinetul asta n-a facut nimic" la o intrebare despre un cabinet care nu exista.
            # Gasit apasand, in lotul 14: `GET /admin/activitate/cabinet/999999` -> `200`.
            # *Absenta inregistrarilor si inexistenta subiectului sunt doua lucruri diferite, iar
            # primul e o afirmatie despre cabinet.* Clasa e chiar cea pazita de
            # `core/test_absenta_nu_e_neaplicabil.py`, pe alt obiect.
            if not repo_tenants.cabinetul_exista(cur, firm_id):
                raise _erori.Inexistent("Nu există niciun cabinet cu numărul %d. "
                                         "Verifică numărul: un cabinet fără activitate ar fi "
                                         "răspuns cu o listă goală, nu cu asta." % firm_id)
            rows = repo_admin.actiunile_cabinetului(cur, firm_id, limita)
    return {"activitate": rows}



def admin_analytics(zile, ctx):
    """[P7 · use-case] Corpul rutei `/admin/analytics`; docstringul ei a ramas in stratul HTTP."""
    zile = _uc_comun._interval_cerut(zile if zile is not None else 30, "Numărul de zile", 1, 365, "zile")  # [R150]
    with db.get_conn() as conn, conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
        pe_eveniment = repo_admin.evenimente_pe_tip(cur, zile)
        pe_zi = repo_admin.evenimente_pe_zi(cur, zile)
        pe_pagina = repo_admin.evenimente_pe_pagina(cur, zile)
        total = repo_admin.cate_evenimente(cur, zile)["n"]
    return {"zile": zile, "total": total, "pe_eveniment": pe_eveniment, "pe_zi": pe_zi, "pe_pagina": pe_pagina}

