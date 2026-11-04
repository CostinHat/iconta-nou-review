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
Maparea claselor inventarului (scripts/poarta_e2e_restante.txt) la clasele porții — scrisă de arhitect (16.1-C3, pct.5), în CLASE_INVENTAR de mai jos, în antetul inventarului și în CLAUDE.md:
  a (test prost) -> restanță; b (stare/dată) -> restanță; c (defect numerotat) -> restanță; d (șters) -> nu există în poartă; e (verde fără aserțiuni) -> invalid;
  f (inexistent) -> nu există în poartă. Un test cu rând „e” care rulează = invalid; un manifest care conține un fișier cu rând „e” e refuzat (`manifest_invalide`).
Curat = nicio regresie, nicio nou_regresie, nicio baza_mutata, niciun invalid, nicio infra, nicio asertiuni_scazute."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventar_restante as INV  # noqa: E402
import poarta_lib as L  # noqa: E402


#: clasa inventarului -> clasa porții (None = nu există în poartă)
CLASE_INVENTAR = {"a": "restanta", "b": "restanta", "c": "restanta", "d": None, "e": "invalid", "f": None}


def _inventar_e():
    """{(fișier, test fără parametri): ID} pentru rândurile „e” — verde fără aserțiuni, deci invalide."""
    rez = {}
    for _, p in INV.citeste():
        if CLASE_INVENTAR.get(p[2]) == "invalid":
            rez[(p[1].split("::")[0], p[1].split("::")[-1].split("[")[0])] = p[0]
    return rez


def manifest_invalide(cale_manifest, randuri=None):
    """Refuzul mecanic (16.1-C3, pct.5): un fișier al manifestului care are rânduri „e” în inventar. -> mesajele (goală = manifestul e curat). Un test invalid în afara manifestului
    nu rulează și nu refuză. `randuri` = rândurile inventarului ([(n, câmpuri)]; implicit cel din repo; calibrarea dă un inventar de probă)."""
    e = {}
    for _, p in (INV.citeste() if randuri is None else randuri):
        if CLASE_INVENTAR.get(p[2]) == "invalid":
            e.setdefault(p[1].split("::")[0], []).append(p[0])
    ref = []
    for ln in open(cale_manifest, encoding="utf-8"):
        if ln.strip() and not ln.startswith("#"):
            f = os.path.basename(ln.split("\t")[0])
            if f in e:
                ref.append("%s: în manifest, dar inventarul îl numește invalid (clasa e: %s)" % (f, ", ".join(e[f])))
    return ref


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


def clasifica(cand, baza, fisiere_lot, rad, complet=True, inv=None, inv_e=None):
    """cand, baza: liste de {nume, rezultat, infra?, asertiuni?}; fisiere_lot: fișierele din diff-ul lotului. -> dict clasă -> [nume]."""
    inv = _inventar() if inv is None else inv
    inv_e = _inventar_e() if inv_e is None else inv_e
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
        if (os.path.basename(fisier), cheie.split("::")[-1]) in inv_e:   # clasa e (verde fără aserțiuni) = invalid (16.1-C3, pct.5)
            rez["invalid"].append("%s (clasa e din inventar: %s)" % (n, inv_e[(os.path.basename(fisier), cheie.split("::")[-1])]))
            continue
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
