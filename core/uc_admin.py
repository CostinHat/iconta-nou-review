# -*- coding: utf-8 -*-
"""USE_CASE — rutele `/admin`.

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
from core import repo_admin
from core import repo_tenants
from core.mesaje import DOAR_ADMIN_ICONTA
import psycopg2.extras as _E_audit
from core import erori as _erori
from core.mesaje import (DOAR_ADMIN_ICONTA)
from core import db, observare as _obs
from core import uc_comun as _uc_comun
from core.common import cate as _cate


#: [lotul 13, 646 a] anexa comenzii 13.1, decis de Costin 24.10.2026: „bifă explicită «Toate cabinetele» sus; fără nicio bifă trimiterea e
#: refuzată; înainte de trimitere confirmarea spune la câte cabinete pleacă.” Destinatarii se aleg EXPLICIT: `segment = "toate"` (bifa) sau
#: `segment = "cabinete"` cu lista. Până azi „nimic bifat = anunțul merge la toți”: o bifă uitată trimitea la toate cabinetele.
MESAJ_FARA_DESTINATARI = "Alege destinatarii: bifează «Toate cabinetele» sau cabinetele cărora le trimiți anunțul."


def admin_anunt_creeaza(date, ctx):
    """[P7 · use-case] Corpul rutei `/admin/anunturi`; docstringul ei a ramas in stratul HTTP.
    [646] Destinatarii explicit (`segment` = `toate` | `cabinete` + `cabinet_ids`); rândurile trimiterii primesc același `lot` (lista
    trimiterilor, retragerea) și pe cel care a trimis."""
    if not (date.mesaj or "").strip():
        raise _erori.DateInvalide({"mesaj": "Scrie mesajul anunțului.", "camp": "mesaj"})
    mesaj = date.mesaj.strip()
    data_af = (date.data_afisare or "").strip() or None
    segment = (date.segment or "").strip()
    alese = sorted({int(c) for c in (date.cabinet_ids or [])})
    if segment not in ("toate", "cabinete") or (segment == "cabinete" and not alese):
        raise _erori.DateInvalide({"mesaj": MESAJ_FARA_DESTINATARI, "camp": "destinatari"})
    ids = []
    with db.get_conn() as conn, conn.cursor() as cur:
        tinte = [cid for (cid,) in repo_tenants.cabinete_active(cur)] if segment == "toate" else alese
        for cid in tinte:
            ids.append(repo_admin.adauga_anunt(cur, int(cid), mesaj, data_af, ctx["uid"]))
        repo_admin.leaga_trimiterea(cur, ids)
        conn.commit()
    return {"ok": True, "trimise": len(ids), "lot": min(ids) if ids else None}


def admin_anunturi_lista(ctx):
    """[646 c] Corpul rutei `GET /admin/anunturi`: trimiterile, cu destinatarii fiecăreia (citit sau nu) și retragerea."""
    out = []
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            for (lot, mesaj, creat_la, data_af, retras_la, _tid, trimis_de, n, citite) in repo_admin.anunturi_trimise(cur):
                dest = [{"cabinet": nume or "(cabinet șters)", "citit_la": c.isoformat() if c else None}
                        for (nume, c) in repo_admin.destinatarii_trimiterii(cur, lot)]
                out.append({"lot": lot, "mesaj": mesaj, "creat_la": creat_la.isoformat() if creat_la else None,
                            "data_afisare": data_af.isoformat() if data_af else None,
                            "retras_la": retras_la.isoformat() if retras_la else None, "trimis_de": trimis_de,
                            "destinatari": int(n), "citite": int(citite), "cabinete": dest})
        conn.rollback()
    return {"trimiteri": out}


def admin_anunt_retrage(lot, ctx):
    """[646 c] Corpul rutei `POST /admin/anunturi/{lot}/retrage`: anunțul nu se mai arată cabinetelor care nu l-au citit."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            n = repo_admin.retrage_trimiterea(cur, lot)
    if not n:
        raise _erori.Conflict("Anunțul nu există sau a fost retras deja.")
    return {"ok": True, "retrase": n}


def admin_alerte_fiscale(ctx):
    """[P7 · use-case] Corpul rutei `/admin/alerte-fiscale`; docstringul ei a ramas in stratul HTTP."""
    with db.get_conn() as conn, conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
        rows = [dict(r) for r in repo_admin.alerte_fiscale(cur)]
    for r in rows:
        r["creat_la"] = str(r["creat_la"])
        for k in ("data_publicarii", "data_vigoare"):   # [646 b] datele actului; None = nu apare în sursă
            r[k] = r[k].isoformat() if r.get(k) else None
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
    for r in rows:   # [645] motivul suspendării, cum îl citește omul (cheia din bază nu ajunge pe ecran)
        r["motiv_suspendare"] = MOTIVE_SUSPENDARE.get(r.get("motiv_suspendare") or "") or None
    return {"cabinete": rows}


# ── [lotul 13, deficiența 645] SUSPENDAREA UNUI CABINET: motivul, nota internă, emailul, jurnalul ───────────────────────────────────
# Anexa comenzii 13.1 (decizia Costin + arhitect, 24.10.2026, verbatim): „Suspendarea nu cere motiv, iar cabinetul vede doar «Contactați
# furnizorul». Decis: motiv obligatoriu din listă fixă — neplată, la cererea cabinetului, încălcarea termenilor, acces suspect / securitate,
# la cererea unei autorități — plus notă internă opțională. La logare apare motivul ales, transparent, fără linie de contact (Costin, 24.10);
# nota internă nu se arată. Fără excepții și fără bifă de confidențialitate. Email către administratorul cabinetului la suspendare, cu
# același motiv. Cine, când, motivul și reactivarea rămân în jurnal.”
#: motivul (cheia din bază, CHECK-ul din `core/migrare_suspendari_cabinet.py`) -> cum îl citește cabinetul. Mulțime ÎNCHISĂ, în ordinea anexei.
MOTIVE_SUSPENDARE = {
    "neplata": "neplată",
    "cerere_cabinet": "la cererea cabinetului",
    "incalcare_termeni": "încălcarea termenilor și condițiilor",
    "securitate": "acces suspect / securitate",
    "autoritate": "la cererea unei autorități",
}
NOTA_INTERNA_MAX = 1000
TEXT_SUSPENDAT = "Cabinetul este suspendat."


def text_suspendare(motiv):
    """PURĂ. Ce vede omul cabinetului suspendat (la logare, pe linkul fără parolă, pe o sesiune deschisă): motivul ales, fără linie de
    contact; fără motiv cunoscut (suspendat înainte de jurnal) — numai faptul."""
    m = MOTIVE_SUSPENDARE.get(motiv or "")
    return ("%s Motivul: %s." % (TEXT_SUSPENDAT, m)) if m else TEXT_SUSPENDAT


def text_suspendare_cabinet(cur, cabinet_id):
    """Textul suspendării pentru cabinetul `cabinet_id`, din jurnal (cursorul apelantului, simplu)."""
    r = repo_admin.suspendarea_deschisa(cur, cabinet_id) if cabinet_id else None
    return text_suspendare(r[0] if r else None)


def mesaj_suspendare(cabinet_id):
    """`text_suspendare_cabinet` cu o conexiune proprie (logarea, linkul fără parolă)."""
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            t = text_suspendare_cabinet(cur, cabinet_id)
        conn.rollback()
    return t


def _email_suspendare(nume_cabinet, motiv, cand):
    from core import pdf_util as _pu
    from core.common import esc as _esc
    subiect = "iConta.eu — accesul cabinetului %s a fost suspendat" % nume_cabinet
    html = ("<p>Bună,</p><p>Accesul cabinetului <b>%s</b> în iConta.eu a fost suspendat pe %s.</p><p>Motivul: <b>%s</b>.</p>"
            "<p>Datele cabinetului rămân păstrate; până la reactivare nu se mai poate intra în cont, nici cu parola, nici cu linkul "
            "de logare.</p>") % (_esc(nume_cabinet), _esc(_pu.data_ro(cand, "cu_ora")), _esc(MOTIVE_SUSPENDARE[motiv]))
    return subiect, html


def admin_cabinet_suspenda(firm_id, date, ctx):
    """[P7 · use-case] Corpul rutei `/admin/cabinete/{firm_id}/suspenda`; docstringul ei a ramas in stratul HTTP.

    [645] `date.motiv` din `MOTIVE_SUSPENDARE` (obligatoriu), `date.nota_interna` opțională. Flagul cabinetului, jurnalul — în aceeași
    tranzacție; emailul către administratorii cabinetului pleacă după commit (o suspendare anulată nu anunță nimic), iar câte au plecat se
    scrie pe rândul jurnalului. Întoarce `{ok, motiv, emailuri_trimise, destinatari}`."""
    if ctx["rol"] != "superadmin":
        raise _erori.FaraDrept(DOAR_ADMIN_ICONTA)
    motiv = str(getattr(date, "motiv", None) or "").strip()
    if motiv not in MOTIVE_SUSPENDARE:
        raise _erori.DateInvalide({"mesaj": "Alege motivul suspendării: %s." % ", ".join(MOTIVE_SUSPENDARE.values()), "camp": "motiv"})
    nota = str(getattr(date, "nota_interna", None) or "").strip() or None
    if nota and len(nota) > NOTA_INTERNA_MAX:
        raise _erori.DateInvalide({"mesaj": "Nota internă are %s; încap cel mult %s." % (_cate(len(nota), "caracter", "caractere"),
                                                                                            _cate(NOTA_INTERNA_MAX, "caracter", "caractere")),
                                   "camp": "nota_interna"})
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            nume = repo_admin.numele_cabinetului(cur, firm_id)
            if nume is None:
                raise _erori.Inexistent("Nu există niciun cabinet cu numărul %d." % firm_id)
            if repo_admin.suspendarea_deschisa(cur, firm_id):
                raise _erori.Conflict("Cabinetul %s e deja suspendat." % nume)
            repo_tenants.suspenda_cabinetul(cur, firm_id)
            rand = repo_admin.deschide_suspendarea(cur, firm_id, motiv, nota, ctx["uid"])
            if rand is None:   # suspendat între verificare și scriere (două suspendări simultane)
                raise _erori.Conflict("Cabinetul %s e deja suspendat." % nume)
            sid, cand = rand
            admini = repo_admin.adminii_cabinetului(cur, firm_id)
    subiect, html = _email_suspendare(nume, motiv, cand)
    trimise = sum(1 for (email, _p, _n) in admini
                  if _obs.trimite_email_html_sau_semnaleaza("email suspendare cabinet", email, subiect, html))
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            repo_admin.scrie_emailurile_suspendarii(cur, sid, trimise)
    return {"ok": True, "motiv": MOTIVE_SUSPENDARE[motiv], "emailuri_trimise": trimise, "destinatari": len(admini)}


def admin_cabinet_reactiveaza(firm_id, ctx):
    """[P7 · use-case] Corpul rutei `/admin/cabinete/{firm_id}/reactiveaza`; docstringul ei a ramas in stratul HTTP.
    [645] Reactivarea închide suspendarea deschisă din jurnal (cine, când), în aceeași tranzacție cu flagul cabinetului."""
    if ctx["rol"] != "superadmin":
        raise _erori.FaraDrept(DOAR_ADMIN_ICONTA)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            if repo_admin.numele_cabinetului(cur, firm_id) is None:
                raise _erori.Inexistent("Nu există niciun cabinet cu numărul %d." % firm_id)
            repo_tenants.reactiveaza_cabinetul(cur, firm_id)
            repo_admin.inchide_suspendarea(cur, firm_id, ctx["uid"])
    return {"ok": True}


def jurnal_suspendari(cur, firm_id):
    """[645] Jurnalul suspendărilor pentru fișa cabinetului: cine, când, motivul (eticheta), nota internă, reactivarea."""
    out = []
    for (sid, motiv, nota, s_la, r_la, emailuri, s_de, r_de) in repo_admin.jurnalul_suspendarilor(cur, firm_id):
        out.append({"id": sid, "motiv": MOTIVE_SUSPENDARE.get(motiv or "") or None, "nota_interna": nota,
                    "suspendat_la": s_la.isoformat() if s_la else None, "suspendat_de": s_de,
                    "reactivat_la": r_la.isoformat() if r_la else None, "reactivat_de": r_de, "emailuri_trimise": emailuri})
    return out


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
                "total_mb": round(total_kb / 1024, 1),  # round-ok: indicator (procent / durată / rație), nu sumă fiscală
                "disponibil_mb": round(disp_kb / 1024, 1),  # round-ok: indicator (procent / durată / rație), nu sumă fiscală
                "folosit_procent": round(100 * (1 - disp_kb / total_kb), 1),  # round-ok: indicator (procent / durată / rație), nu sumă fiscală
            }
    except Exception:
        pass

    disc = {"total_gb": None, "liber_gb": None, "folosit_procent": None}
    try:
        total, folosit, liber = _shutil.disk_usage("/")
        disc = {
            "total_gb": round(total / (1024 ** 3), 1),  # round-ok: indicator (procent / durată / rație), nu sumă fiscală
            "liber_gb": round(liber / (1024 ** 3), 1),  # round-ok: indicator (procent / durată / rație), nu sumă fiscală
            "folosit_procent": round(100 * folosit / total, 1),  # round-ok: indicator (procent / durată / rație), nu sumă fiscală
        }
    except Exception:
        pass

    uptime_sec = round(_time.time() - _uc_comun._APP_PORNIT_LA)  # round-ok: indicator (procent / durată / rație), nu sumă fiscală

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
    # [460] cursul BNR de care au nevoie operațiunile de azi: în cache sau lipsă (bucla de sănătate îl completează; aici doar se citește)
    curs_bnr = {"asteptat": None, "ultima_zi": None, "lipsa": None, "zile_lipsa": []}
    try:
        from core import curs_bnr as _cb_s
        with db.get_conn() as conn:
            curs_bnr = _cb_s.stare_curs_zilei(conn)
    except Exception as _e:
        _obs.esec_secundar("admin sanatate: curs BNR", _e)  # inghitit, dar nu tacut
    # [lotul 13, 643] pragurile alertelor, lângă cifre și pe grafice — aceleași cu cele ale buclei de alertă (`alerta_load`)
    from core import alerta_load as _al
    _praguri = _al.praguri(_os.cpu_count(), _os.environ.get("WEB_CONCURRENCY") or 1, db.config_din_env()["maxconn"])
    return {
        "curs_bnr": curs_bnr,
        "praguri": _praguri,
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
        with conn.cursor() as cur:
            suspendari = jurnal_suspendari(cur, firm_id)   # [645] cine, când, motivul și reactivarea, în fișa cabinetului
    return {"activitate": rows, "suspendari": suspendari}



def admin_analytics(zile, ctx):
    """[P7 · use-case] Corpul rutei `/admin/analytics`; docstringul ei a ramas in stratul HTTP."""
    zile = _uc_comun._interval_cerut(zile if zile is not None else 30, "Numărul de zile", 1, 365, "zile")  # [R150]
    with db.get_conn() as conn, conn.cursor(cursor_factory=_E_audit.RealDictCursor) as cur:
        pe_eveniment = repo_admin.evenimente_pe_tip(cur, zile)
        pe_zi = repo_admin.evenimente_pe_zi(cur, zile)
        pe_pagina = repo_admin.evenimente_pe_pagina(cur, zile)
        total = repo_admin.cate_evenimente(cur, zile)["n"]
    return {"zile": zile, "total": total, "pe_eveniment": pe_eveniment, "pe_zi": pe_zi, "pe_pagina": pe_pagina}

