#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_coada_user_id.py  —  PATCH 1 (fundatia modulului management echipa)

Leaga coada de validare de users.id (integer + FK), nu de text.
Idempotent: marker + .bak + py_compile. DDL = ADD COLUMN IF NOT EXISTS.

RULARE (ca 'costin', NU sudo — fisierele sunt in home):
  set -a && source ~/.iconta/db.env && set +a
  python3 patch_coada_user_id.py
Apoi: restart uvicorn 8010 + retest patru-ochi cu curl (vezi finalul).

Ce face:
  A. DB: 4 coloane integer (creat_de_id/aprobat_de_id/respins_de_id/depus_de_id)
     cu FK -> users(id) + index pe creat_de_id.
  B. coada_api.py: cele 4 functii scriu si *_id (langa textul existent);
     patru-ochi comuta pe comparatie de ID (fallback pe text).
  C. main.py: cele 4 rute paseaza int(ctx["uid"]).
"""
import os, re, shutil, sys, py_compile

BASE = "/home/costin/iconta_nou"
COADA = os.path.join(BASE, "core", "coada_api.py")
MAIN  = os.path.join(BASE, "main.py")
MARKER = "# [patch_coada_user_id]"

DDL = """
ALTER TABLE public.declaratii_coada
  ADD COLUMN IF NOT EXISTS creat_de_id   integer REFERENCES public.users(id),
  ADD COLUMN IF NOT EXISTS aprobat_de_id integer REFERENCES public.users(id),
  ADD COLUMN IF NOT EXISTS respins_de_id integer REFERENCES public.users(id),
  ADD COLUMN IF NOT EXISTS depus_de_id   integer REFERENCES public.users(id);
CREATE INDEX IF NOT EXISTS ix_coada_creat_de_id
  ON public.declaratii_coada (creat_de_id);
"""


def backup(path):
    bak = path + ".bak_user_id"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print("  .bak ->", bak)


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit("ANCORA LIPSA (%s) — opresc, nu ghicesc. Verifica fisierul." % label)
    if text.count(old) != 1:
        raise SystemExit("ANCORA NEUNICA (%s) — apare de %d ori. Opresc." % (label, text.count(old)))
    return text.replace(old, new)


# ----------------------------------------------------------------------
# A. DB
# ----------------------------------------------------------------------
def migreaza_db():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL lipseste. Ruleaza: set -a && source ~/.iconta/db.env && set +a")
    import psycopg2
    conn = psycopg2.connect(url)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.close()
    print("  DB: coloane _id + index OK (idempotent)")


# ----------------------------------------------------------------------
# B. coada_api.py
# ----------------------------------------------------------------------
def patch_coada():
    src = open(COADA, encoding="utf-8").read()
    if MARKER in src:
        print("coada_api.py deja patch-at — sar.")
        return
    backup(COADA)

    # B1. semnatura adauga_in_coada: adauga creat_de_id=None inainte de ):
    src = re.sub(
        r"(def adauga_in_coada\(conn, cabinet_id, tenant_id, tip, an, payload,[^)]*?)\):",
        r"\1, creat_de_id=None):",
        src, count=1,
    )
    if "creat_de_id=None" not in src:
        raise SystemExit("Nu am gasit semnatura adauga_in_coada — opresc.")

    # B2. INSERT: adauga coloana + valoare + tuplu
    src = replace_once(
        src,
        '"(cabinet_id, tenant_id, tip, perioada, stare, coerenta, payload, hash, creat_de) "\n'
        '                "VALUES (%s,%s,%s,%s,\'la_senior\',%s,%s,%s,%s) RETURNING id",\n'
        '                (cabinet_id, tenant_id, tip, perioada, coerenta,\n'
        '                 _E.Json(payload), h, creat_de))',
        '"(cabinet_id, tenant_id, tip, perioada, stare, coerenta, payload, hash, creat_de, creat_de_id) "\n'
        '                "VALUES (%s,%s,%s,%s,\'la_senior\',%s,%s,%s,%s,%s) RETURNING id",\n'
        '                (cabinet_id, tenant_id, tip, perioada, coerenta,\n'
        '                 _E.Json(payload), h, creat_de, creat_de_id))',
        "INSERT adauga_in_coada",
    )

    # B3. aproba: semnatura + SELECT (adauga creat_de_id) + patru-ochi pe ID + UPDATE
    src = replace_once(
        src,
        "def aproba(conn, coada_id, aprobat_de):",
        "def aproba(conn, coada_id, aprobat_de, aprobat_de_id=None):",
        "semnatura aproba",
    )
    src = replace_once(
        src,
        '            "SELECT stare, creat_de FROM public.declaratii_coada WHERE id = %s",\n'
        '            (coada_id,))\n'
        '        r = cur.fetchone()\n'
        '        if r is None:\n'
        '            return {"ok": False, "cod": "INEXISTENT"}\n'
        '        st, creat_de = r[0], r[1]',
        '            "SELECT stare, creat_de, creat_de_id FROM public.declaratii_coada WHERE id = %s",\n'
        '            (coada_id,))\n'
        '        r = cur.fetchone()\n'
        '        if r is None:\n'
        '            return {"ok": False, "cod": "INEXISTENT"}\n'
        '        st, creat_de, creat_de_id = r[0], r[1], r[2]',
        "SELECT aproba",
    )
    src = replace_once(
        src,
        '        if creat_de is not None and str(creat_de) == str(aprobat_de):\n'
        '            return {"ok": False, "cod": "PATRU_OCHI",',
        '        ' + MARKER + ' patru-ochi pe ID (fallback pe text)\n'
        '        _vinovat = (\n'
        '            (creat_de_id is not None and aprobat_de_id is not None\n'
        '             and creat_de_id == aprobat_de_id)\n'
        '            or (creat_de_id is None and creat_de is not None\n'
        '                and str(creat_de) == str(aprobat_de))\n'
        '        )\n'
        '        if _vinovat:\n'
        '            return {"ok": False, "cod": "PATRU_OCHI",',
        "patru-ochi aproba",
    )
    src = replace_once(
        src,
        '            "UPDATE public.declaratii_coada SET stare=\'aprobata\', "\n'
        '            "aprobat_de=%s, aprobat_la=now() WHERE id=%s", (aprobat_de, coada_id))',
        '            "UPDATE public.declaratii_coada SET stare=\'aprobata\', "\n'
        '            "aprobat_de=%s, aprobat_de_id=%s, aprobat_la=now() WHERE id=%s",\n'
        '            (aprobat_de, aprobat_de_id, coada_id))',
        "UPDATE aproba",
    )

    # B4. respinge: semnatura + UPDATE
    src = replace_once(
        src,
        "def respinge(conn, coada_id, respins_de, motiv):",
        "def respinge(conn, coada_id, respins_de, motiv, respins_de_id=None):",
        "semnatura respinge",
    )
    src = replace_once(
        src,
        '            "UPDATE public.declaratii_coada SET stare=\'respinsa\', "\n'
        '            "respins_de=%s, respins_la=now(), motiv_respingere=%s WHERE id=%s",\n'
        '            (respins_de, motiv, coada_id))',
        '            "UPDATE public.declaratii_coada SET stare=\'respinsa\', "\n'
        '            "respins_de=%s, respins_de_id=%s, respins_la=now(), motiv_respingere=%s WHERE id=%s",\n'
        '            (respins_de, respins_de_id, motiv, coada_id))',
        "UPDATE respinge",
    )

    # B5. marcheaza_depusa: semnatura (autor nou) + UPDATE
    src = replace_once(
        src,
        "def marcheaza_depusa(conn, coada_id, spv_index=None):",
        "def marcheaza_depusa(conn, coada_id, spv_index=None, depus_de=None, depus_de_id=None):",
        "semnatura marcheaza_depusa",
    )
    src = replace_once(
        src,
        '            "UPDATE public.declaratii_coada SET stare=\'depusa\', depus_la=now(), "\n'
        '            "spv_index=%s WHERE id=%s", (spv_index, coada_id))',
        '            "UPDATE public.declaratii_coada SET stare=\'depusa\', depus_la=now(), "\n'
        '            "spv_index=%s, depus_de=%s, depus_de_id=%s WHERE id=%s",\n'
        '            (spv_index, depus_de, depus_de_id, coada_id))',
        "UPDATE marcheaza_depusa",
    )

    src = MARKER + " fundatie user_id\n" + src
    open(COADA, "w", encoding="utf-8").write(src)
    print("  coada_api.py: 4 functii patch-ate")


# ----------------------------------------------------------------------
# C. main.py (rute paseaza int(ctx["uid"]))
# ----------------------------------------------------------------------
def patch_main():
    src = open(MAIN, encoding="utf-8").read()
    if MARKER in src:
        print("main.py deja patch-at — sar.")
        return
    backup(MAIN)

    src = replace_once(
        src,
        '            creat_de=str(ctx["uid"]), luna=date.luna, trim=date.trim)',
        '            creat_de=str(ctx["uid"]), creat_de_id=int(ctx["uid"]), luna=date.luna, trim=date.trim)',
        "ruta adauga_in_coada",
    )
    src = replace_once(
        src,
        'r = coada_api.aproba(conn, coada_id, str(ctx["uid"]))',
        'r = coada_api.aproba(conn, coada_id, str(ctx["uid"]), aprobat_de_id=int(ctx["uid"]))',
        "ruta aproba",
    )
    src = replace_once(
        src,
        'r = coada_api.respinge(conn, coada_id, str(ctx["uid"]), date.motiv)',
        'r = coada_api.respinge(conn, coada_id, str(ctx["uid"]), date.motiv, respins_de_id=int(ctx["uid"]))',
        "ruta respinge",
    )
    src = replace_once(
        src,
        'r = coada_api.marcheaza_depusa(conn, coada_id, date.spv_index)',
        'r = coada_api.marcheaza_depusa(conn, coada_id, date.spv_index, '
        'depus_de=str(ctx["uid"]), depus_de_id=int(ctx["uid"]))',
        "ruta depune",
    )

    src = MARKER + " rute paseaza int(uid)\n" + src
    open(MAIN, "w", encoding="utf-8").write(src)
    print("  main.py: 4 rute patch-ate")


def main():
    for p in (COADA, MAIN):
        if not os.path.exists(p):
            raise SystemExit("Lipseste: " + p)
    print("A. DB... SARIT (rulat manual)")
    print("B. coada_api..."); patch_coada()
    print("C. main.py...");   patch_main()
    print("py_compile...")
    for p in (COADA, MAIN):
        py_compile.compile(p, doraise=True)
        print("  OK", p)
    print("\nGATA. Urmeaza:")
    print("  1) restart 8010 (env + uvicorn, ca de obicei)")
    print("  2) RETEST patru-ochi cu curl: cine a pregatit NU poate aproba (403 PATRU_OCHI)")
    print("  Rollback: muta .bak_user_id peste fisiere; coloanele _id raman (inofensive).")


if __name__ == "__main__":
    main()
