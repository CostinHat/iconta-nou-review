"""
core/asistenti_api.py — managementul actorilor de cabinet (cardul Asistenți).

Un actor = user din public.users cu accounting_firm_id = cabinetul curent
și rol in ('admin_firma','angajat'). Clienții și superadmin NU sunt actori aici.

Ce face:
  - listă actori (cu permisiuni + nr firme atribuite)
  - editare permisiuni (poate_pregati / poate_valida / poate_depune)
  - atribuire / eliminare firme (populează user_tenants — calea de vizibilitate
    RBAC pentru angajat; admin_firma vede tot portofoliul prin rol, nu prin asta)
  - dezactivare (activ=false; rămâne în istoricul cozii)
  - Vizualizează: activitatea actorului din coadă + semnal "patru ochi"

Controlul intern "patru ochi": pe o declarație, pregătitorul (creat_de) nu are
voie să fie și aprobatorul (aprobat_de). Aici doar RAPORTĂM (read-only); blocarea
efectivă la aprobare se face în fluxul De validat (main).

Toate funcțiile primesc conn (RealDictCursor). RBAC-ul (admin_firma) se verifică
în main. Fiecare funcție mai verifică o dată că actorul-țintă aparține cabinetului
apelantului — apărare în adâncime contra manipulării cross-cabinet.
"""
from __future__ import annotations

import psycopg2.extras as _E

REGULI = "2026.1"
MODUL = "asistenti_api"

# ── Constante de adaptat dacă numele diferă în build (o singură linie fiecare) ──
TABEL_LEGATURA_FIRME = "public.user_tenants"   # firme atribuite per user
COL_USER = "user_id"                            # coloana user în tabelul de mai sus
COL_TENANT = "tenant_id"                         # coloana tenant în tabelul de mai sus
# creat_de/aprobat_de/depus_de din declaratii_coada stochează un identificator de
# actor (email sau nume). Pentru Vizualizează căutăm pe AMBELE variante, deci
# merge indiferent de convenție.
# ────────────────────────────────────────────────────────────────────────────

ROLURI_ACTOR = ("admin_firma", "angajat")


# ============================================================
#  LISTĂ ACTORI — DB
# ============================================================
def lista_actori(conn, cabinet_id):
    """Actorii cabinetului, cu permisiuni și nr firme atribuite."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            f"""
            SELECT u.id, u.nume, u.prenume, u.email, u.rol, u.functie, u.activ,
                   u.poate_pregati, u.poate_valida, u.poate_depune,
                   COALESCE(f.nr, 0) AS nr_firme
              FROM public.users u
              LEFT JOIN (
                   SELECT {COL_USER} AS uid, COUNT(*) AS nr
                     FROM {TABEL_LEGATURA_FIRME}
                    GROUP BY {COL_USER}
              ) f ON f.uid = u.id
             WHERE u.accounting_firm_id = %s
               AND u.rol = ANY(%s)
             ORDER BY (u.rol = 'admin_firma') DESC, u.activ DESC, u.id
            """,
            (cabinet_id, list(ROLURI_ACTOR)),
        )
        return [dict(r) for r in cur.fetchall()]


# [p16_activitate_cabinet]
def _interval_sql(de, pana, prefix=""):
    """Construieste fragmentul WHERE pe creat_la + parametrii. de/pana = ISO date.
    prefix = alias tabel (ex 'c.') pentru query-uri cu JOIN, ca sa nu fie ambiguu."""
    cond, par = [], []
    if de:
        cond.append(prefix + "creat_la >= %s"); par.append(de)
    if pana:
        cond.append(prefix + "creat_la < (%s::date + 1)"); par.append(pana)
    return cond, par


def centralizator(conn, cabinet_id, de=None, pana=None):
    """Numere agregate pe cabinet, in intervalul [de, pana] dupa creat_la.
    Returneaza totaluri, defalcare pe tip si pe asistent, rata respingeri."""
    cond, par = _interval_sql(de, pana)
    w = "cabinet_id = %s" + (" AND " + " AND ".join(cond) if cond else "")
    args = [cabinet_id] + par
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        # totaluri pe actiuni (in interval, dupa creat_la pentru toate)
        cur.execute(
            "SELECT "
            "COUNT(*) AS create_, "
            "COUNT(aprobat_la) AS aprobate, "
            "COUNT(respins_la) AS respinse, "
            "COUNT(depus_la) AS depuse, "
            "COUNT(*) FILTER (WHERE stare = 'la_senior') AS in_asteptare "
            "FROM public.declaratii_coada WHERE " + w,
            tuple(args),
        )
        tot = dict(cur.fetchone() or {})
        # defalcare pe tip
        cur.execute(
            "SELECT tip, COUNT(*) AS nr FROM public.declaratii_coada WHERE " + w +
            " GROUP BY tip ORDER BY nr DESC",
            tuple(args),
        )
        pe_tip = [dict(r) for r in cur.fetchall()]
        # defalcare pe asistent (creator) — nume din users prin creat_de_id, fallback creat_de
        cond_c, par_c = _interval_sql(de, pana, prefix="c.")
        w_c = "c.cabinet_id = %s" + (" AND " + " AND ".join(cond_c) if cond_c else "")
        cur.execute(
            "SELECT COALESCE(NULLIF(TRIM(CONCAT_WS(' ', u.prenume, u.nume)), ''), "
            "       c.creat_de, '(necunoscut)') AS nume, "
            "       COUNT(*) AS create_, "
            "       COUNT(c.respins_la) AS respinse "
            "  FROM public.declaratii_coada c "
            "  LEFT JOIN public.users u ON u.id = c.creat_de_id "
            " WHERE " + w_c +
            " GROUP BY 1 ORDER BY create_ DESC",
            tuple([cabinet_id] + par_c),
        )
        pe_asistent = [dict(r) for r in cur.fetchall()]
    cre = int(tot.get("create_", 0) or 0)
    resp = int(tot.get("respinse", 0) or 0)
    rata = round(resp / cre, 3) if cre else 0.0
    return {
        "ok": True,
        "interval": {"de": de, "pana": pana},
        "totaluri": {
            "create": cre,
            "aprobate": int(tot.get("aprobate", 0) or 0),
            "respinse": resp,
            "depuse": int(tot.get("depuse", 0) or 0),
            "in_asteptare": int(tot.get("in_asteptare", 0) or 0),
            "rata_respins": rata,
        },
        "pe_tip": pe_tip,
        "pe_asistent": pe_asistent,
    }


def jurnal(conn, cabinet_id, de=None, pana=None, limit=200):
    """Evenimente cronologice (flat) derivate din timestamp-urile cozii.
    Fiecare declaratie produce 1-4 evenimente: pregatit/aprobat/respins/depus.
    Sortare descrescatoare pe momentul evenimentului."""
    cond, par = _interval_sql(de, pana, prefix="c.")
    w = "c.cabinet_id = %s" + (" AND " + " AND ".join(cond) if cond else "")
    args = [cabinet_id] + par
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT c.id, c.tip, c.perioada, c.tenant_id, "
            "       t.nume AS firma, "
            "       c.creat_de, c.creat_la, c.creat_de_id, "
            "       c.aprobat_de, c.aprobat_la, c.aprobat_de_id, "
            "       c.respins_de, c.respins_la, c.respins_de_id, c.motiv_respingere, "
            "       c.depus_de, c.depus_la, c.depus_de_id, "
            "       cu.prenume AS cre_pre, cu.nume AS cre_num, "
            "       au.prenume AS apr_pre, au.nume AS apr_num, "
            "       ru.prenume AS res_pre, ru.nume AS res_num, "
            "       du.prenume AS dep_pre, du.nume AS dep_num "
            "  FROM public.declaratii_coada c "
            "  LEFT JOIN public.tenants t ON t.id = c.tenant_id "
            "  LEFT JOIN public.users cu ON cu.id = c.creat_de_id "
            "  LEFT JOIN public.users au ON au.id = c.aprobat_de_id "
            "  LEFT JOIN public.users ru ON ru.id = c.respins_de_id "
            "  LEFT JOIN public.users du ON du.id = c.depus_de_id "
            " WHERE " + w,
            tuple(args),
        )
        randuri = [dict(r) for r in cur.fetchall()]

    def _nume(pre, num, fallback):
        n = " ".join(x for x in [pre, num] if x).strip()
        return n or fallback or "(necunoscut)"

    ev = []
    for r in randuri:
        firma = r.get("firma") or ("firma #%s" % r["tenant_id"])
        baza = {"coada_id": r["id"], "tip": r["tip"],
                "perioada": r["perioada"], "firma": firma}
        if r.get("creat_la"):
            ev.append({**baza, "actiune": "pregatit", "culoare": "verde",
                       "cine": _nume(r.get("cre_pre"), r.get("cre_num"), r.get("creat_de")),
                       "cand": r["creat_la"].isoformat(), "motiv": None})
        if r.get("aprobat_la"):
            ev.append({**baza, "actiune": "aprobat", "culoare": "verde",
                       "cine": _nume(r.get("apr_pre"), r.get("apr_num"), r.get("aprobat_de")),
                       "cand": r["aprobat_la"].isoformat(), "motiv": None})
        if r.get("respins_la"):
            ev.append({**baza, "actiune": "respins", "culoare": "rosu",
                       "cine": _nume(r.get("res_pre"), r.get("res_num"), r.get("respins_de")),
                       "cand": r["respins_la"].isoformat(),
                       "motiv": r.get("motiv_respingere")})
        if r.get("depus_la"):
            ev.append({**baza, "actiune": "depus", "culoare": "verde",
                       "cine": _nume(r.get("dep_pre"), r.get("dep_num"), r.get("depus_de")),
                       "cand": r["depus_la"].isoformat(), "motiv": None})
    ev.sort(key=lambda x: x["cand"], reverse=True)
    return {"ok": True, "interval": {"de": de, "pana": pana},
            "evenimente": ev[:int(limit)], "total": len(ev)}


def sumar(conn, cabinet_id):
    """Pentru nivelul 1 (card): total actori + câți activi."""
    actori = lista_actori(conn, cabinet_id)
    activi = sum(1 for a in actori if a["activ"])
    return {"total": len(actori), "activi": activi}


# ============================================================
#  DETALII ACTOR (nivel 3) — permisiuni + firme portofoliu
# ============================================================
def _actor_din_cabinet(conn, cabinet_id, user_id):
    """Întoarce rândul actorului dacă aparține cabinetului, altfel None."""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT id, nume, prenume, email, rol, functie, activ,
                   poate_pregati, poate_valida, poate_depune
              FROM public.users
             WHERE id = %s AND accounting_firm_id = %s AND rol = ANY(%s)
            """,
            (user_id, cabinet_id, list(ROLURI_ACTOR)),
        )
        r = cur.fetchone()
        return dict(r) if r else None


def detalii_actor(conn, cabinet_id, user_id):
    """Actor + lista întregului portofoliu cu flag 'atribuit' (pentru bife)."""
    actor = _actor_din_cabinet(conn, cabinet_id, user_id)
    if not actor:
        return {"ok": False, "cod": "actor_inexistent"}

    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            f"""
            SELECT t.id, t.nume, t.cui,
                   (l.{COL_USER} IS NOT NULL) AS atribuit
              FROM public.tenants t
              LEFT JOIN {TABEL_LEGATURA_FIRME} l
                     ON l.{COL_TENANT} = t.id AND l.{COL_USER} = %s
             WHERE t.accounting_firm_id = %s
             ORDER BY t.nume
            """,
            (user_id, cabinet_id),
        )
        firme = [dict(r) for r in cur.fetchall()]

    # admin_firma are tot portofoliul prin rol — atribuirea per-firmă e irelevantă
    actor["atribuire_relevanta"] = actor["rol"] == "angajat"
    return {"ok": True, "actor": actor, "firme": firme}


# ============================================================
#  EDITARE PERMISIUNI — DB
# ============================================================
def _nr_validatori(conn, cabinet_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM public.users "
            " WHERE accounting_firm_id = %s AND poate_valida = true AND activ = true",
            (cabinet_id,))
        return int(cur.fetchone()[0])


def _po_posibil(conn, cabinet_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FILTER (WHERE poate_pregati), "
            "       COUNT(*) FILTER (WHERE poate_valida), COUNT(*) "
            "  FROM public.users "
            " WHERE accounting_firm_id = %s AND activ = true AND (poate_pregati OR poate_valida)",
            (cabinet_id,))
        r = cur.fetchone()
    return int(r[0]) >= 1 and int(r[1]) >= 1 and int(r[2]) >= 2


def _po_activ(conn, cabinet_id):
    with conn.cursor() as cur:
        cur.execute("SELECT patru_ochi_activ FROM public.accounting_firms WHERE id = %s", (cabinet_id,))
        r = cur.fetchone()
    return bool(r[0]) if r and r[0] is not None else False


def patru_ochi_seteaza(conn, cabinet_id, activ):
    """Patronul decide ON/OFF. La activare/respingere memoram si nr de validatori (sa nu reapara imediat)."""
    nr = _nr_validatori(conn, cabinet_id)
    with conn.cursor() as cur:
        cur.execute("UPDATE public.accounting_firms SET patru_ochi_activ = %s, educatie_4ochi_la_nr = %s WHERE id = %s",
                    (bool(activ), nr, cabinet_id))
    return {"ok": True, "patru_ochi_activ": bool(activ), "nr_validatori": nr}


def educatie_de_aratat(conn, cabinet_id):
    """Intoarce lista de educatii de aratat patronului. Acum: patru-ochi.
    Apare cand nr validatori >=2 si a crescut peste valoarea memorata."""
    nr = _nr_validatori(conn, cabinet_id)
    posibil = _po_posibil(conn, cabinet_id)  # [p54_4ochi]
    activ = _po_activ(conn, cabinet_id)
    with conn.cursor() as cur:
        cur.execute("SELECT educatie_4ochi_la_nr FROM public.accounting_firms WHERE id = %s",
                    (cabinet_id,))
        r = cur.fetchone()
        vazut_la = int(r[0]) if r and r[0] is not None else 0
    educatii = []
    # propune doar daca e posibil, NU e deja activat, si nr de validatori a crescut peste ultima propunere
    if posibil and not activ and nr > vazut_la:
        educatii.append({
            "cheie": "patru-ochi",
            "titlu": "Validare in doi (patru ochi)",
            "nr_validatori": nr,
        })
    return {"ok": True, "educatii": educatii}


def educatie_marcheaza(conn, cabinet_id):
    """Memoreaza nr curent de validatori ca 'educatie vazuta' (nu mai revine pana creste)."""
    nr = _nr_validatori(conn, cabinet_id)
    with conn.cursor() as cur:
        cur.execute("UPDATE public.accounting_firms SET educatie_4ochi_la_nr = %s WHERE id = %s",
                    (nr, cabinet_id))
    return {"ok": True, "nr_validatori": nr}


def get_competente_proprii(conn, user_id):
    """Competentele userului logat (oricine, inclusiv patronul)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT poate_pregati, poate_valida, poate_depune "
            "  FROM public.users WHERE id = %s", (user_id,))
        r = cur.fetchone()
    if not r:
        return {"ok": False, "cod": "inexistent"}
    return {"ok": True,
            "poate_pregati": bool(r[0]),
            "poate_valida": bool(r[1]),
            "poate_depune": bool(r[2])}


def set_competente_proprii(conn, user_id, preg, val, dep):
    """Userul isi seteaza propriile competente. Fara restrictii (zero e valid)."""
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE public.users SET poate_pregati=%s, poate_valida=%s, poate_depune=%s "
            " WHERE id = %s",
            (bool(preg), bool(val), bool(dep), user_id))
    return {"ok": True,
            "poate_pregati": bool(preg),
            "poate_valida": bool(val),
            "poate_depune": bool(dep)}


def set_permisiuni(conn, cabinet_id, user_id, preg, val, dep):
    """Setează cele 3 flaguri pe un actor al cabinetului."""
    if not _actor_din_cabinet(conn, cabinet_id, user_id):
        return {"ok": False, "cod": "actor_inexistent"}
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE public.users
               SET poate_pregati = %s, poate_valida = %s, poate_depune = %s
             WHERE id = %s AND accounting_firm_id = %s
            """,
            (bool(preg), bool(val), bool(dep), user_id, cabinet_id),
        )
    return {"ok": True}


# ============================================================
#  ATRIBUIRE / ELIMINARE FIRME — DB (populează user_tenants)
# ============================================================
def atribuie_firma(conn, cabinet_id, user_id, tenant_id):
    """Adaugă firma în portofoliul actorului (idempotent)."""
    if not _actor_din_cabinet(conn, cabinet_id, user_id):
        return {"ok": False, "cod": "actor_inexistent"}
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        # firma trebuie să fie a cabinetului
        cur.execute(
            "SELECT 1 FROM public.tenants WHERE id = %s AND accounting_firm_id = %s",
            (tenant_id, cabinet_id),
        )
        if not cur.fetchone():
            return {"ok": False, "cod": "firma_alt_cabinet"}
        cur.execute(
            f"""
            INSERT INTO {TABEL_LEGATURA_FIRME} ({COL_USER}, {COL_TENANT})
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (user_id, tenant_id),
        )
    return {"ok": True}


def elimina_firma(conn, cabinet_id, user_id, tenant_id):
    """Scoate firma din portofoliul actorului."""
    if not _actor_din_cabinet(conn, cabinet_id, user_id):
        return {"ok": False, "cod": "actor_inexistent"}
    with conn.cursor() as cur:
        cur.execute(
            f"DELETE FROM {TABEL_LEGATURA_FIRME} "
            f"WHERE {COL_USER} = %s AND {COL_TENANT} = %s",
            (user_id, tenant_id),
        )
    return {"ok": True}



# [patch7_zero_firme]
def _numara_firme(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT COUNT(*) FROM {TABEL_LEGATURA_FIRME} WHERE {COL_USER} = %s",
            (user_id,),
        )
        return int(cur.fetchone()[0])


def aplica_regula_zero_firme(conn, cabinet_id, user_id):
    """La ZERO firme: competentele se golesc.
    angajat -> cont dezactivat (ramane in istoric).
    admin_firma -> contul ramane intact (iese doar din procesatori)."""
    actor = _actor_din_cabinet(conn, cabinet_id, user_id)
    if not actor:
        return {"ok": False, "cod": "actor_inexistent"}
    if _numara_firme(conn, user_id) > 0:
        return {"ok": True, "aplicat": False}
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE public.users SET poate_pregati=false, poate_valida=false, "
            "poate_depune=false WHERE id=%s AND accounting_firm_id=%s",
            (user_id, cabinet_id),
        )
        dezactivat = False
        if actor["rol"] == "angajat":
            cur.execute(
                "UPDATE public.users SET activ=false "
                "WHERE id=%s AND accounting_firm_id=%s",
                (user_id, cabinet_id),
            )
            dezactivat = True
    return {"ok": True, "aplicat": True, "dezactivat": dezactivat,
            "rol": actor["rol"]}




# [patch9_semafor_erori]
def _culoare_asistent(cal):
    """rosu daca tipar sistematic; galben daca drift(nou); altfel verde."""
    tip = cal.get("tipare") or []
    if any(t.get("tip") == "sistematic" for t in tip):
        return "rosu"
    if any(t.get("nou") for t in tip):
        return "galben"
    return "verde"


def semafor_echipa(conn, cabinet_id, zile=30):
    """Agregat pe asistentii ACTIVI care au procesat, ultimele `zile`.
    Culoarea cea mai grava + numaratoare per culoare."""
    import datetime as _dt
    de = (_dt.date.today() - _dt.timedelta(days=int(zile))).isoformat()
    actori = [a for a in lista_actori(conn, cabinet_id) if a["activ"]]
    counts = {"rosu": 0, "galben": 0, "verde": 0}
    detaliu = []
    for a in actori:
        cal = calitate(conn, cabinet_id, a["id"], de=de)
        if not cal.get("ok"):
            continue
        if cal.get("evaluate", 0) == 0 and not cal.get("tipare"):
            continue
        cul = _culoare_asistent(cal)
        counts[cul] += 1
        detaliu.append({
            "id": a["id"],
            "nume": " ".join(x for x in [a.get("prenume"), a.get("nume")] if x) or a.get("email"),
            "culoare": cul,
            "respinse": cal.get("respinse", 0),
            "rata": cal.get("rata_respins", 0),
        })
    glob = "rosu" if counts["rosu"] else ("galben" if counts["galben"] else "verde")
    return {"ok": True, "culoare": glob, "counts": counts,
            "zile": int(zile), "asistenti": detaliu}


def erori_echipa(conn, cabinet_id, zile=30):
    """Drill: cine a produs respingeri, sortat descrescator dupa nr respinse,
    cu tiparele lor. Ultimele `zile`."""
    import datetime as _dt
    de = (_dt.date.today() - _dt.timedelta(days=int(zile))).isoformat()
    actori = [a for a in lista_actori(conn, cabinet_id) if a["activ"]]
    rez = []
    for a in actori:
        cal = calitate(conn, cabinet_id, a["id"], de=de)
        if not cal.get("ok") or cal.get("respinse", 0) == 0:
            continue
        rez.append({
            "id": a["id"],
            "nume": " ".join(x for x in [a.get("prenume"), a.get("nume")] if x) or a.get("email"),
            "respinse": cal.get("respinse", 0),
            "evaluate": cal.get("evaluate", 0),
            "rata": cal.get("rata_respins", 0),
            "culoare": _culoare_asistent(cal),
            "tipare": cal.get("tipare") or [],
        })
    rez.sort(key=lambda x: x["respinse"], reverse=True)
    return {"ok": True, "zile": int(zile), "asistenti": rez}


# ============================================================
#  DEZACTIVARE — DB (nu ștergem; rămâne în istoricul cozii)
# ============================================================
def dezactiveaza(conn, cabinet_id, user_id, apelant_id):
    """Pune activ=false. Nu te poți dezactiva pe tine; nu dezactivezi un admin."""
    if user_id == apelant_id:
        return {"ok": False, "cod": "auto_dezactivare"}
    actor = _actor_din_cabinet(conn, cabinet_id, user_id)
    if not actor:
        return {"ok": False, "cod": "actor_inexistent"}
    if actor["rol"] == "admin_firma":
        return {"ok": False, "cod": "nu_dezactivezi_admin"}
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE public.users SET activ = false "
            "WHERE id = %s AND accounting_firm_id = %s",
            (user_id, cabinet_id),
        )
    return {"ok": True}


def reactiveaza(conn, cabinet_id, user_id):
    """Repune activ=true (simetric cu dezactivarea)."""
    if not _actor_din_cabinet(conn, cabinet_id, user_id):
        return {"ok": False, "cod": "actor_inexistent"}
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE public.users SET activ = true "
            "WHERE id = %s AND accounting_firm_id = %s",
            (user_id, cabinet_id),
        )
    return {"ok": True}


# ============================================================
#  VIZUALIZEAZĂ — activitatea actorului + semnal "patru ochi"
# ============================================================
def _identificatori(actor):
    """Variantele sub care actorul poate apărea în creat_de/aprobat_de."""
    vals = []
    if actor.get("email"):
        vals.append(actor["email"])
    nume_intreg = " ".join(
        x for x in [actor.get("prenume"), actor.get("nume")] if x
    ).strip()
    if actor.get("nume"):
        vals.append(actor["nume"])
    if nume_intreg and nume_intreg not in vals:
        vals.append(nume_intreg)
    return list(dict.fromkeys(vals)) or [""]


def activitate(conn, cabinet_id, user_id):
    """
    Read-only. Declarațiile prin care a trecut actorul (pregătit/aprobat/respins),
    limitate la cabinetul lui. Plus semnalul patru-ochi: declarații unde
    creat_de == aprobat_de (același actor și-a aprobat propria muncă).
    """
    actor = _actor_din_cabinet(conn, cabinet_id, user_id)
    if not actor:
        return {"ok": False, "cod": "actor_inexistent"}
    idents = _identificatori(actor)

    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            """
            SELECT id, tenant_id, tip, perioada, stare,
                   creat_de, creat_la, aprobat_de, aprobat_la,
                   respins_de, respins_la
              FROM public.declaratii_coada
             WHERE cabinet_id = %s
               AND (creat_de = ANY(%s) OR aprobat_de = ANY(%s)
                    OR respins_de = ANY(%s))
             ORDER BY COALESCE(aprobat_la, respins_la, creat_la) DESC
             LIMIT 200
            """,
            (cabinet_id, idents, idents, idents),
        )
        randuri = [dict(r) for r in cur.fetchall()]

    for r in randuri:
        r["a_pregatit"] = r["creat_de"] in idents
        r["a_aprobat"] = r["aprobat_de"] in idents if r["aprobat_de"] else False
        r["a_respins"] = r["respins_de"] in idents if r["respins_de"] else False
        # patru ochi încălcat dacă pe ACEEAȘI declarație e și pregătitor și aprobator
        r["self_approval"] = bool(
            r["aprobat_de"] and r["creat_de"]
            and r["creat_de"] == r["aprobat_de"]
            and r["a_pregatit"] and r["a_aprobat"]
        )

    incalcari = [r for r in randuri if r["self_approval"]]
    return {
        "ok": True,
        "actor": {
            "id": actor["id"], "nume": actor["nume"],
            "prenume": actor.get("prenume"), "rol": actor["rol"],
        },
        "activitate": randuri,
        "nr_self_approval": len(incalcari),
    }


# [patch_asistenti_calitate]
def calitate(conn, cabinet_id, user_id, de=None, pana=None):
    """
    Read-only. Indicatori de calitate pentru un asistent, derivati din coada
    (grupare pe creat_de_id). Rata = respinse / evaluate (aprobate + respinse);
    ce e inca 'la_senior' (nedecis) NU intra in rata.
    de/pana = 'YYYY-MM-DD' optional (filtru pe creat_la::date).
    """
    import psycopg2.extras as _E
    import datetime as _dt
    actor = _actor_din_cabinet(conn, cabinet_id, user_id)
    if not actor:
        return {"ok": False, "cod": "actor_inexistent"}

    cond = ["cabinet_id = %s", "creat_de_id = %s"]
    val = [cabinet_id, user_id]
    if de:
        cond.append("creat_la::date >= %s"); val.append(de)
    if pana:
        cond.append("creat_la::date <= %s"); val.append(pana)
    w = " AND ".join(cond)

    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT "
            "  COUNT(*) AS pregatite, "
            "  COUNT(*) FILTER (WHERE stare IN ('aprobata','depusa')) AS aprobate, "
            "  COUNT(*) FILTER (WHERE stare = 'respinsa') AS respinse, "
            "  EXTRACT(EPOCH FROM AVG(aprobat_la - creat_la) "
            "    FILTER (WHERE stare IN ('aprobata','depusa') AND aprobat_la IS NOT NULL)) "
            "    / 86400.0 AS zile_mediu, "
            "  array_agg(DISTINCT tip) AS tipuri "
            "FROM public.declaratii_coada WHERE " + w,
            val)
        a = cur.fetchone() or {}

        cur.execute(
            "SELECT motiv_respingere AS motiv, COUNT(*) AS nr, MIN(respins_la) AS prima "
            "FROM public.declaratii_coada WHERE " + w + " "
            "  AND stare = 'respinsa' AND motiv_respingere IS NOT NULL "
            "GROUP BY motiv_respingere ORDER BY nr DESC",
            val)
        _motive_raw = [dict(r) for r in cur.fetchall()]

        cur.execute(
            "SELECT poate_pregati, poate_valida, poate_depune "
            "FROM public.users WHERE id = %s", (user_id,))
        _perm = cur.fetchone() or {}

    pregatite = int(a.get("pregatite") or 0)
    aprobate = int(a.get("aprobate") or 0)
    respinse = int(a.get("respinse") or 0)
    evaluate = aprobate + respinse
    rata = round(respinse * 100 / evaluate) if evaluate else 0
    zile = a.get("zile_mediu")
    zile_mediu = round(float(zile), 1) if zile is not None else None
    tipuri = [t for t in (a.get("tipuri") or []) if t]

    # [patch4_tipare_nivel]
    nivel = 3 if _perm.get("poate_depune") else (2 if _perm.get("poate_valida") else 1)
    _prag = 2
    _limita_nou = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=30)
    tipare = []
    for _m in _motive_raw:
        _nr = int(_m["nr"]); _prima = _m.get("prima")
        tipare.append({
            "motiv": _m["motiv"], "nr": _nr,
            "tip": "sistematic" if _nr >= _prag else "accident",
            "nou": bool(_prima and _prima >= _limita_nou),
        })

    return {
        "ok": True,
        "actor": {"id": actor["id"], "nume": actor["nume"],
                  "prenume": actor.get("prenume"), "rol": actor["rol"]},
        "perioada": {"de": de, "pana": pana},
        "pregatite": pregatite,
        "aprobate": aprobate,
        "respinse": respinse,
        "evaluate": evaluate,
        "rata_respins": rata,
        "zile_mediu": zile_mediu,
        "tipuri": tipuri,
        "nivel": nivel,
        "tipare": tipare,
        "motive": [{"motiv": t["motiv"], "nr": t["nr"]} for t in tipare[:5]],
        # [p26_motivationale] lista metrici motivationale (POZITIVE). Frontend le afiseaza
        # pe toate, oricate. Adaugi una noua aici -> apare automat in bara 3.
        "motivationale": [
            {"cheie": "pregatite", "eticheta": "pregătite luna aceasta",
             "valoare": pregatite},
            {"cheie": "acceptate", "eticheta": "acceptate din prima",
             "valoare": (str(round(aprobate * 100 / evaluate)) + "%") if evaluate else "100%"},
        ],
    }
