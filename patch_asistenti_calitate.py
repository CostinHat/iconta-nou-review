#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_asistenti_calitate.py  —  PATCH 2 (prima piesa vizibila a modulului)

Adauga endpoint GET /asistenti/{uid}/calitate?de=&pana=
Read-only. Deriva totul din coada, grupand pe creat_de_id (fundatia Patch 1).
  pregatite / aprobate / respinse / rata (= respinse / evaluate) / timp mediu /
  acoperire (tipuri) / top motive de respingere.
Idempotent: marker + .bak + py_compile. ZERO DDL.

RULARE (ca 'costin'):
  cd ~/iconta_nou
  /opt/iconta/venv/bin/python3 patch_asistenti_calitate.py
Apoi restart 8010 + test cu curl (vezi finalul).
"""
import os, shutil, py_compile

BASE = "/home/costin/iconta_nou"
ASIST = os.path.join(BASE, "core", "asistenti_api.py")
MAIN  = os.path.join(BASE, "main.py")
MARKER = "# [patch_asistenti_calitate]"


def backup(path):
    bak = path + ".bak_calitate"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print("  .bak ->", bak)


FUNCTIE = '''

# [patch_asistenti_calitate]
def calitate(conn, cabinet_id, user_id, de=None, pana=None):
    """
    Read-only. Indicatori de calitate pentru un asistent, derivati din coada
    (grupare pe creat_de_id). Rata = respinse / evaluate (aprobate + respinse);
    ce e inca 'la_senior' (nedecis) NU intra in rata.
    de/pana = 'YYYY-MM-DD' optional (filtru pe creat_la::date).
    """
    import psycopg2.extras as _E
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
            "SELECT motiv_respingere AS motiv, COUNT(*) AS nr "
            "FROM public.declaratii_coada WHERE " + w + " "
            "  AND stare = 'respinsa' AND motiv_respingere IS NOT NULL "
            "GROUP BY motiv_respingere ORDER BY nr DESC LIMIT 5",
            val)
        motive = [dict(r) for r in cur.fetchall()]

    pregatite = int(a.get("pregatite") or 0)
    aprobate = int(a.get("aprobate") or 0)
    respinse = int(a.get("respinse") or 0)
    evaluate = aprobate + respinse
    rata = round(respinse * 100 / evaluate) if evaluate else 0
    zile = a.get("zile_mediu")
    zile_mediu = round(float(zile), 1) if zile is not None else None
    tipuri = [t for t in (a.get("tipuri") or []) if t]

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
        "motive": [{"motiv": m["motiv"], "nr": int(m["nr"])} for m in motive],
    }
'''

RUTA_OLD = '@app.get("/asistenti/{uid}/activitate")'
RUTA_NEW = '''@app.get("/asistenti/{uid}/calitate")
def asistenti_calitate(uid: int, de: Optional[str] = None,
                       pana: Optional[str] = None, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        r = _asist.calitate(conn, cabinet_id, uid, de=de, pana=pana)
        if not r.get("ok"):
            raise HTTPException(404, r.get("cod", "eroare"))
        return r


@app.get("/asistenti/{uid}/activitate")'''


def patch_asist():
    src = open(ASIST, encoding="utf-8").read()
    if MARKER in src:
        print("asistenti_api.py deja patch-at — sar.")
        return
    backup(ASIST)
    open(ASIST, "w", encoding="utf-8").write(src.rstrip() + "\n" + FUNCTIE)
    print("  asistenti_api.py: functia calitate() adaugata")


def patch_main():
    src = open(MAIN, encoding="utf-8").read()
    if MARKER in src:
        print("main.py deja patch-at — sar.")
        return
    if RUTA_OLD not in src:
        raise SystemExit("ANCORA LIPSA (ruta activitate) — opresc, nu ghicesc.")
    if src.count(RUTA_OLD) != 1:
        raise SystemExit("ANCORA NEUNICA (ruta activitate) — opresc.")
    backup(MAIN)
    src = src.replace(RUTA_OLD, "# [patch_asistenti_calitate]\n" + RUTA_NEW, 1)
    open(MAIN, "w", encoding="utf-8").write(src)
    print("  main.py: ruta /asistenti/{uid}/calitate adaugata")


def main():
    for p in (ASIST, MAIN):
        if not os.path.exists(p):
            raise SystemExit("Lipseste: " + p)
    patch_asist()
    patch_main()
    print("py_compile...")
    for p in (ASIST, MAIN):
        py_compile.compile(p, doraise=True)
        print("  OK", p)
    print("\\nGATA. Urmeaza:")
    print("  1) restart 8010")
    print("  2) test: curl .../asistenti/2/calitate (Nistor) cu Bearer token")
    print("  Rollback: muta .bak_calitate peste fisiere.")


if __name__ == "__main__":
    main()
