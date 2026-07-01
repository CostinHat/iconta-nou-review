#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch9_semafor_backend.py — backend Card Echipa: semafor agregat + drill erori."""
import os, shutil, py_compile

BASE = "/home/costin/iconta_nou"
ASIST = os.path.join(BASE, "core", "asistenti_api.py")
MAIN  = os.path.join(BASE, "main.py")
M_ASIST = "# [patch9_semafor_erori]"
M_MAIN  = "# [patch9_semafor_rute]"
NL = chr(10)


def backup(p, suf):
    b = p + suf
    if not os.path.exists(b):
        shutil.copy2(p, b); print("  .bak ->", b)


def once(t, old, new, label):
    if old not in t: raise SystemExit("ANCORA LIPSA: " + label)
    if t.count(old) != 1: raise SystemExit("ANCORA NEUNICA: " + label)
    return t.replace(old, new)


HELPERS = '''

''' + M_ASIST + '''
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

'''

# ancora: inserez inainte de blocul DEZACTIVARE (acelasi loc sigur ca patch7)
A_ASIST = ("# ============================================================" + NL +
           "#  DEZACTIVARE \u2014 DB")

RUTE = '''
''' + M_MAIN + '''
@app.get("/asistenti/echipa/semafor")
def asistenti_semafor(zile: int = 30, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return _asist.semafor_echipa(conn, cabinet_id, zile)


@app.get("/asistenti/echipa/erori")
def asistenti_erori(zile: int = 30, ctx=Depends(cere_cabinet)):
    cabinet_id = _cer_admin_cabinet(ctx)
    with db.get_conn() as conn:
        return _asist.erori_echipa(conn, cabinet_id, zile)

'''
A_MAIN = "# [patch_asistenti_calitate]"


def main():
    for p in (ASIST, MAIN):
        if not os.path.exists(p): raise SystemExit("Lipseste: " + p)

    s = open(ASIST, encoding="utf-8").read()
    if M_ASIST in s:
        print("asistenti_api.py deja patch-at — sar.")
    else:
        backup(ASIST, ".bak_p9")
        s = once(s, A_ASIST, HELPERS.rstrip(NL) + NL + NL + NL + A_ASIST, "helperi semafor")
        open(ASIST, "w", encoding="utf-8").write(s)
        py_compile.compile(ASIST, doraise=True)
        print("  asistenti_api.py: semafor_echipa + erori_echipa")

    s = open(MAIN, encoding="utf-8").read()
    if M_MAIN in s:
        print("main.py deja patch-at — sar.")
    else:
        backup(MAIN, ".bak_p9")
        s = once(s, A_MAIN, RUTE.rstrip(NL) + NL + NL + NL + A_MAIN, "rute semafor")
        open(MAIN, "w", encoding="utf-8").write(s)
        py_compile.compile(MAIN, doraise=True)
        print("  main.py: GET /asistenti/echipa/semafor + /erori")

    print(NL + "GATA. Restart 8010. Rollback: .bak_p9")


if __name__ == "__main__":
    main()
