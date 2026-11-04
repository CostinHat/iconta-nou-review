# -*- coding: utf-8 -*-
"""scripts/poarta_clasifica.py — clasificarea picăturilor porții față de baza.json (comanda 16.1, pct.1a; extinde scăderea restanțelor numerotate din 16.0).
Clase, pe fiecare test al rulării candidatului:
  regresie        verde pe bază, roșu pe candidat; sau test din baza verde care a dispărut din rulare (numai la rularea completă)
  restanta        roșu pe ambele și numerotat (a/b/c) în scripts/poarta_e2e_restante.txt
  baza_mutata     roșu pe ambele și nenumerotat în inventar — oprirea lotului
  nou_regresie    test absent din bază, fișierul lui în diff-ul lotului, roșu
  invalid         test absent din bază cu fișierul în afara diff-ului lotului; sau test nou fără aserțiuni; sau fișier de test din diff fără teste
  infra           eroare de infrastructură (conexiune, server căzut, sesiune fără raport) — reluată o singură dată, apoi oprire
  asertiuni_scazute  număr de aserțiuni statice mai mic decât în bază, într-un test comun
Curat = nicio regresie, nicio nou_regresie, nicio baza_mutata, niciun invalid, nicio infra, nicio asertiuni_scazute."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventar_restante as INV  # noqa: E402
import poarta_lib as L  # noqa: E402


def _inventar():
    """{(fișier, test fără parametri): ID} pentru rândurile a/b/c — restanțele numerotate."""
    rez = {}
    for _, p in INV.citeste():
        if p[2] in ("a", "b", "c"):
            f, t = p[1].split("::")[0], p[1].split("::")[-1].split("[")[0]
            rez[(f, t)] = p[0]
    return rez


def _numarat(nume, inv):
    f, t = os.path.basename(nume.split("::")[0]), nume.split("::")[-1].split("[")[0]
    return inv.get((f, t))


def clasifica(cand, baza, fisiere_lot, rad, complet=True, inv=None):
    """cand, baza: liste de {nume, rezultat, infra?, asertiuni?}; fisiere_lot: fișierele din diff-ul lotului. -> dict clasă -> [nume]."""
    inv = _inventar() if inv is None else inv
    b = {t["nume"]: t for t in baza}
    rez = {k: [] for k in ("regresie", "restanta", "baza_mutata", "nou_regresie", "invalid", "infra", "asertiuni_scazute", "reparat", "noi_verzi")}
    cache = {}
    vazute = set()
    for t in cand:
        n = t["nume"]
        vazute.add(n)
        if t["rezultat"] == "sarit":
            continue
        fisier, cheie = L.cheie_asertiuni(n)
        ca = cache.setdefault(fisier, L.asertiuni(rad, fisier))
        bt = b.get(n)
        if t["rezultat"] == "pica" and t.get("infra"):
            rez["infra"].append(n)
            continue
        if bt is None:
            if fisier not in fisiere_lot:
                rez["invalid"].append("%s (test nou în afara diff-ului lotului)" % n)
            elif ca.get(cheie, 0) == 0 and not n.startswith("verificator::"):
                rez["invalid"].append("%s (test nou fără aserțiuni)" % n)
            elif t["rezultat"] == "pica":
                rez["nou_regresie"].append(n)
            else:
                rez["noi_verzi"].append(n)
            continue
        if t["rezultat"] == "pica":
            if bt["rezultat"] == "trece":
                rez["regresie"].append(n)
            else:
                id_ = _numarat(n, inv)
                (rez["restanta"] if id_ else rez["baza_mutata"]).append("%s %s" % (id_ or "NENUMEROTAT", n) if id_ else n)
        elif bt["rezultat"] == "pica":
            rez["reparat"].append(n)
        if not n.startswith("verificator::") and ca.get(cheie, 0) < bt.get("asertiuni", 0):
            rez["asertiuni_scazute"].append("%s (%d < %d în bază)" % (n, ca.get(cheie, 0), bt.get("asertiuni", 0)))
    if complet:
        rez["regresie"] += ["%s (a dispărut din rulare)" % n for n, t in b.items() if t["rezultat"] == "trece" and n not in vazute]
    # fișier de test din diff fără niciun test colectat
    for f in sorted(fisiere_lot):
        if not f.startswith("scripts/") and re.search(r"(^|/)(test_|e2e_)[^/]*\.py$", f) and os.path.exists(os.path.join(rad, f)) and not L.asertiuni(rad, f) \
                and not any(n.startswith(f + "::") for n in vazute):
            rez["invalid"].append("%s (fișier de test fără teste)" % f)
    return rez


CURAT = ("regresie", "nou_regresie", "baza_mutata", "invalid", "infra", "asertiuni_scazute")


def este_curat(rez):
    return not any(rez[k] for k in CURAT)


def rezumat(rez):
    return " · ".join("%s %d" % (k, len(v)) for k, v in rez.items())
