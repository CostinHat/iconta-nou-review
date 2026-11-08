#!/bin/sh
# Control independent (17.5-A pct.5): citește același .lot_jurnal.log cu awk/python de sine stătător; NU importă scripts/jurnal_lot.py.
# Utilizare: sh control_independent.sh <jurnal> praguri <lot-în-lucru|-> <lot...>   (loturile date explicit, sau "--inainte-de <lot>" ca prim argument după "praguri")
#            sh control_independent.sh <jurnal> timp <lot>
J="$1"; CMD="$2"; shift 2
python3 -I - "$J" "$CMD" "$@" <<'PY'
import sys, datetime as D
J, CMD, A = sys.argv[1], sys.argv[2], sys.argv[3:]
rows = [l.rstrip("\n").split("\t") for l in open(J, encoding="utf-8") if l.strip()]
T = D.datetime.fromisoformat
def cicluri(lot):
    """-> lista (faza, id, inceput, sfarsit|None, rezultat) cu ultimul rând sfarsit pe id"""
    ini = [r for r in rows if r[0] == lot and r[2] == "inceput"]
    fin = {}
    for r in rows:
        if r[0] == lot and r[2] == "sfarsit":
            fin[r[6]] = r
    return [(r[1], r[6], r[3], fin[r[6]][3] if r[6] in fin else None, fin[r[6]][5] if r[6] in fin else "fara") for r in ini]
def secunde(a, b):
    return round((T(b) - T(a)).total_seconds())
if CMD == "praguri":
    if A[0] == "--inainte-de":
        L = A[1]
        prim = min(T(r[3]) for r in rows if r[0] == L)
        pub = {}
        for r in rows:
            if r[1] == "publicare" and r[2] == "sfarsit" and r[5] == "publicat":
                pub[r[0]] = max(pub.get(r[0], T(r[3])), T(r[3]))
        lots = [l for l, m in sorted(pub.items(), key=lambda x: x[1]) if l != L and m < prim][-3:]
        faze = A[2:] or ["hook", "poarta_verificator", "poarta_pytest", "poarta_plasa"]
    else:
        lots = A[:1] if False else [a for a in A if not a.startswith("faza=")]
        faze = [a[5:] for a in A if a.startswith("faza=")] or ["hook", "poarta_verificator", "poarta_pytest", "poarta_plasa"]
    print("loturi:", ",".join(lots))
    for f in faze:
        d = [secunde(i, s) for l in lots for (ff, _, i, s, rez) in cicluri(l) if ff == f and s and rez != "intrerupt"]
        n_int = sum(1 for l in lots for (ff, _, i, s, rez) in cicluri(l) if ff == f and rez == "intrerupt")
        mx = max(d)
        print("%s maxim=%d prag=%d complete=%d intrerupte=%d" % (f, mx, -(-mx * 12 // 10), len(d), n_int))
elif CMD == "timp":
    lot = A[0]
    ore = [T(r[3]) for r in rows if r[0] == lot]
    print("timp_total_min=%.1f" % ((max(ore) - min(ore)).total_seconds() / 60))
    cic = cicluri(lot)
    ps = [(i, s) for (f, _, i, s, rez) in cic if f == "pytest" and s]
    print("pytest_toate=%d min=%.1f" % (len(ps), sum(secunde(i, s) for i, s in ps) / 60))
    for f in ("hook", "poarta_verificator", "poarta_pytest", "poarta_plasa"):
        c = [secunde(i, s) for (ff, _, i, s, rez) in cic if ff == f and s and rez != "intrerupt"]
        n_int = sum(1 for (ff, _, i, s, rez) in cic if ff == f and rez == "intrerupt")
        print("%s complete=%d min=%.1f intrerupte=%d" % (f, len(c), sum(c) / 60, n_int))
PY
