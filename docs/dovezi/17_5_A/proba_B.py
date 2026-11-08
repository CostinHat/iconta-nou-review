# -*- coding: utf-8 -*-
"""Proba lui B (17.5-A pct.5 (e)) pe COPIA jurnalului (~/verif_17_5_A/jurnal_copie.log), niciodată pe jurnalul real. Rulare: ./venv/bin/python docs/dovezi/17_5_A/proba_B.py <jurnal_real_copiat>"""
import contextlib, datetime, filecmp, io, os, shutil, subprocess, sys
RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
SRC = sys.argv[1]
COPIE = os.path.expanduser("~/verif_17_5_A/jurnal_copie.log")
shutil.copy(SRC, COPIE)
os.environ["LOT_JURNAL"] = COPIE
import jurnal_lot as JL, publica_lot as PL  # noqa: E402
LOTURI = ("17.1", "17.2", "17.2-B")
VECHI = ("pornire", "hook", "verificator", "poarta_verificator", "poarta_pytest", "poarta_plasa", "pytest", "publicare", "proba_contract", "restart", "parcurs_code")

def cititori(lot):
    """Ieșirile cititorilor, filtrate pe fazele vechi."""
    o = {}
    def cap(f, *a):
        b = io.StringIO()
        with contextlib.redirect_stdout(b):
            f(*a)
        return b.getvalue()
    def vechi(text):
        return "\n".join(l for l in text.splitlines() if l.split()[:1] and l.split()[0] not in JL.FAZE_LUCRU and not l.startswith("--- total"))
    o["rezumat"] = vechi(cap(lambda l: [print("%-20s %-10s %s -> %s  %ss" % (f, r, b, s, sec)) for f, i, b, s, r, sec in JL.durate(l)], lot))
    o["durate(faze vechi)"] = repr([x for x in JL.durate(lot) if x[0] not in JL.FAZE_LUCRU])
    o["jurnal_lot.py rezumat (subproces)"] = vechi(subprocess.run([sys.executable, os.path.join(RAD, "scripts", "jurnal_lot.py"), "rezumat", lot], capture_output=True, text=True).stdout)
    o["defalcare.py"] = vechi(subprocess.run([sys.executable, os.path.join(RAD, "scripts", "defalcare.py"), lot], capture_output=True, text=True).stdout)
    rows = [r for r in JL._citeste(COPIE) if r[0] == lot]
    rv = [r for r in rows if r[1] in JL.FAZE_OBLIGATORII]
    o["faze_stop(unelte)"] = repr(PL.faze_stop(rv, True))
    o["faze_stop(produs)"] = repr(PL.faze_stop(rv, False))
    sint = ["unelte", "lot: x", "max hook 90", "max poarta_plasa 1000", "max poarta_pytest 600", "max poarta_verificator 80"]
    o["depasiri_praguri(sintetic)"] = repr(PL.depasiri_praguri([x for x in JL.durate(lot) if x[0] not in JL.FAZE_LUCRU], sint))
    return o

rez, ok = [], True
inainte = {l: cititori(l) for l in LOTURI}
vechi_octeti = open(COPIE, "rb").read()
for lot in LOTURI:
    n = JL.lucru(lot, COPIE)
    rez.append("lucru %s: %d rânduri noi" % (lot, n))
rez.append("a doua chemare: " + ", ".join("%s %d rânduri noi" % (l, JL.lucru(l, COPIE)) for l in LOTURI))
nou = open(COPIE, "rb").read()
b = nou.startswith(vechi_octeti) and vechi_octeti == open(SRC, "rb").read()
rez.append("(iv) rândurile vechi identice octet cu octet cu jurnalul real: %s (copia = vechi + %d octeți)" % ("DA" if b else "NU", len(nou) - len(vechi_octeti))); ok &= b
rows = JL._citeste(COPIE)
def suma(lot, faza):
    return sum(x["secunde"] for x in JL.rulari(rows, lot) if x["faza"] == faza and x["complet"])
for lot in LOTURI:
    prim = min(JL._t(r[3]) for r in rows if r[0] == lot and len(r) > 6 and r[1] not in JL.FAZE_LUCRU)
    pub = next(JL._t(r[3]) for r in rows if r[0] == lot and r[1] == "publicare" and r[2] == "inceput")
    tinta = round((pub - prim).total_seconds())
    s = sum(suma(lot, f) for f in ("lucru_pana_la_commit", "lucru_pana_la_poarta", "asteptare_poarta", "reparatie_dupa_rosu", "dupa_verde", "pana_la_publicare"))
    nr = sum(1 for x in JL.rulari(rows, lot) if x["faza"] == "reparatie_dupa_rosu")
    rez.append("(i) %s: suma fazelor %d s; până la începutul publicării %d s; diferență %d s; (ii) reparatie_dupa_rosu = %d" % (lot, s, tinta, s - tinta, nr))
    ok &= (s - tinta == 0) and nr == (1 if lot == "17.1" else 0)
dupa = {l: cititori(l) for l in LOTURI}
for lot in LOTURI:
    for k in inainte[lot]:
        egal = inainte[lot][k] == dupa[lot][k]
        ok &= egal
        rez.append("(v) %s %-36s identic înainte/după lucru: %s" % (lot, k, "DA" if egal else "NU"))
print("\n".join(rez))
print("REZULTAT:", "TOATE VERZI" if ok else "ABATERE")
sys.exit(0 if ok else 1)
