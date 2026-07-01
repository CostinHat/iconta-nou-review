#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch4_calitate_tipare_nivel.py  —  PATCH 4 (backend pentru fereastra completa)

Extinde calitate() din core/asistenti_api.py cu:
  - nivel (1/2/3 derivat din poate_pregati/valida/depune pe users)
  - tipare: fiecare motiv clasificat sistematic (>=2x) vs accident (1x)
  - drift: flag 'nou' daca motivul a aparut prima data in ultimele 30 zile
Read-only, zero DDL. Alimenteaza piesele din macheta ferestrei (Patch 5).
Idempotent: marker + .bak + py_compile.

RULARE (ca 'costin'):
  cd ~/iconta_nou
  /opt/iconta/venv/bin/python3 patch4_calitate_tipare_nivel.py
Apoi restart 8010 + test curl.
"""
import os, shutil, py_compile

BASE = "/home/costin/iconta_nou"
ASIST = os.path.join(BASE, "core", "asistenti_api.py")
MARKER = "# [patch4_tipare_nivel]"


def backup(path):
    bak = path + ".bak_tipare"
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
        print("  .bak ->", bak)


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit("ANCORA LIPSA (%s) — opresc, nu ghicesc." % label)
    if text.count(old) != 1:
        raise SystemExit("ANCORA NEUNICA (%s) — opresc." % label)
    return text.replace(old, new)


# 1) import datetime in calitate()
IMP_OLD = (
    "    import psycopg2.extras as _E\n"
    "    actor = _actor_din_cabinet(conn, cabinet_id, user_id)"
)
IMP_NEW = (
    "    import psycopg2.extras as _E\n"
    "    import datetime as _dt\n"
    "    actor = _actor_din_cabinet(conn, cabinet_id, user_id)"
)

# 2) query motive extins (+ MIN(prima)) + query permisiuni
MOT_OLD = (
    '        cur.execute(\n'
    '            "SELECT motiv_respingere AS motiv, COUNT(*) AS nr "\n'
    '            "FROM public.declaratii_coada WHERE " + w + " "\n'
    '            "  AND stare = \'respinsa\' AND motiv_respingere IS NOT NULL "\n'
    '            "GROUP BY motiv_respingere ORDER BY nr DESC LIMIT 5",\n'
    '            val)\n'
    '        motive = [dict(r) for r in cur.fetchall()]'
)
MOT_NEW = (
    '        cur.execute(\n'
    '            "SELECT motiv_respingere AS motiv, COUNT(*) AS nr, MIN(respins_la) AS prima "\n'
    '            "FROM public.declaratii_coada WHERE " + w + " "\n'
    '            "  AND stare = \'respinsa\' AND motiv_respingere IS NOT NULL "\n'
    '            "GROUP BY motiv_respingere ORDER BY nr DESC",\n'
    '            val)\n'
    '        _motive_raw = [dict(r) for r in cur.fetchall()]\n'
    '\n'
    '        cur.execute(\n'
    '            "SELECT poate_pregati, poate_valida, poate_depune "\n'
    '            "FROM public.users WHERE id = %s", (user_id,))\n'
    '        _perm = cur.fetchone() or {}'
)

# 3) calcul nivel + tipare inainte de return
CALC_OLD = (
    "    tipuri = [t for t in (a.get(\"tipuri\") or []) if t]\n"
    "\n"
    "    return {"
)
CALC_NEW = (
    "    tipuri = [t for t in (a.get(\"tipuri\") or []) if t]\n"
    "\n"
    "    " + MARKER + "\n"
    "    nivel = 3 if _perm.get(\"poate_depune\") else (2 if _perm.get(\"poate_valida\") else 1)\n"
    "    _prag = 2\n"
    "    _limita_nou = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=30)\n"
    "    tipare = []\n"
    "    for _m in _motive_raw:\n"
    "        _nr = int(_m[\"nr\"]); _prima = _m.get(\"prima\")\n"
    "        tipare.append({\n"
    "            \"motiv\": _m[\"motiv\"], \"nr\": _nr,\n"
    "            \"tip\": \"sistematic\" if _nr >= _prag else \"accident\",\n"
    "            \"nou\": bool(_prima and _prima >= _limita_nou),\n"
    "        })\n"
    "\n"
    "    return {"
)

# 4) return: adauga nivel + tipare, motive devine top5 din tipare
RET_OLD = (
    '        "motive": [{"motiv": m["motiv"], "nr": int(m["nr"])} for m in motive],\n'
    '    }'
)
RET_NEW = (
    '        "nivel": nivel,\n'
    '        "tipare": tipare,\n'
    '        "motive": [{"motiv": t["motiv"], "nr": t["nr"]} for t in tipare[:5]],\n'
    '    }'
)


def main():
    if not os.path.exists(ASIST):
        raise SystemExit("Lipseste: " + ASIST)
    src = open(ASIST, encoding="utf-8").read()
    if MARKER in src:
        print("asistenti_api.py deja patch-at (tipare/nivel) — sar.")
        return
    backup(ASIST)
    src = replace_once(src, IMP_OLD, IMP_NEW, "import datetime")
    src = replace_once(src, MOT_OLD, MOT_NEW, "query motive+permisiuni")
    src = replace_once(src, CALC_OLD, CALC_NEW, "calcul nivel+tipare")
    src = replace_once(src, RET_OLD, RET_NEW, "return")
    open(ASIST, "w", encoding="utf-8").write(src)
    print("  asistenti_api.py: calitate() extins (nivel + tipare + drift)")
    py_compile.compile(ASIST, doraise=True)
    print("  py_compile OK")
    print("\nGATA. Restart 8010 + test:")
    print("  curl .../asistenti/2/calitate -> apar 'nivel', 'tipare' (cu tip+nou)")
    print("  Rollback: muta .bak_tipare peste asistenti_api.py")


if __name__ == "__main__":
    main()
