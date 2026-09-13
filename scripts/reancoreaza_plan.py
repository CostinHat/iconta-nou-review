# -*- coding: utf-8 -*-
"""Reancorarea citarilor din `PLAN_HARDENING.md`, dupa orice editare a planului.

DE CE EXISTA (13.09.2026). Planul e citat pe LINIE din peste douazeci de module — `core/straturi.py`
o face de peste o suta de ori. Orice rand adaugat deasupra unei ancore muta toate citarile de sub
ea, tacut. `core/test_citari_plan.py` PRINDE mutarea; instrumentul asta o REPARA, ca reparatia sa nu
fie o cautare cu mana prin douazeci de fisiere — exact felul de munca in care se strecoara o cifra
gresita.

CUM: pentru fiecare ancora din tabelul gardului, se cauta fragmentul ei in planul de ACUM. Pentru o
ancora de o linie, noua ancora e linia gasita. Pentru un interval, se pastreaza INALTIMEA lui si se
muta cu aceeasi diferenta — un interval isi pastreaza intelesul numai daca ramane la fel de larg.

CE NU FACE, declarat: nu inventeaza ancore noi si nu sterge niciuna. Daca un fragment nu se mai
gaseste, sau se gaseste de doua ori, se OPRESTE si o spune — o ancora ambigua reparata automat ar
arata spre orice.
"""
import io
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

PLAN = os.path.join(RAD, "PLAN_HARDENING.md")
GARDA = os.path.join(RAD, "core", "test_p7_straturi.py")  # doar pentru mesaj
TABEL = os.path.join(RAD, "core", "test_citari_plan.py")
_CITARE = re.compile(r"PLAN_HARDENING\.md:(\d+(?:-\d+)?)")


def _ancore():
    sys.path.insert(0, os.path.join(RAD, "core"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("_tcp", TABEL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return dict(mod.ANCORE)


def _plan_la_head():
    """Planul asa cum era la `HEAD` — reperul fata de care se masoara deplasarea."""
    import subprocess
    try:
        brut = subprocess.check_output(["git", "show", "HEAD:PLAN_HARDENING.md"], cwd=RAD)
    except Exception:
        return []
    return brut.decode("utf-8").split("\n")


def _fisiere_py():
    out = []
    for rad, dirs, fis in os.walk(RAD):
        dirs[:] = [d for d in dirs if d not in ("venv", ".git", "__pycache__", "efactura_zip")]
        out += [os.path.join(rad, f) for f in fis if f.endswith(".py")]
    return sorted(out)


def calculeaza():
    """{ancora_veche: ancora_noua} — numai cele care s-au mutat."""
    linii = io.open(PLAN, encoding="utf-8").read().split("\n")
    harta = {}
    for ancora, fragment in _ancore().items():
        gasite = [i + 1 for i, l in enumerate(linii) if fragment in l]
        if not gasite:
            raise SystemExit("ancora %r: fragmentul %r nu mai exista in plan — se repara cu mana"
                             % (ancora, fragment))
        # Un fragment e ales ca sa fie unic IN INTERVALUL CITAT, nu in tot planul
        # (`**Cum se verifica.**` apare o data pentru fiecare pas P0..P7). Se ia potrivirea cea mai
        # apropiata de ancora veche; daca doua sunt la fel de aproape, ancora e ambigua si ne oprim.
        reper = int(ancora.split("-")[0])
        distante = sorted((abs(g - reper), g) for g in gasite)
        if len(distante) > 1 and distante[0][0] == distante[1][0]:
            raise SystemExit("ancora %r: doua potriviri la fel de aproape (%s) — se repara cu mana"
                             % (ancora, [g for _d, g in distante[:2]]))
        nou_start = distante[0][1]
        if "-" in ancora:
            a, b = (int(x) for x in ancora.split("-"))
            # Fragmentul poate fi oriunde in interval: se pastreaza pozitia lui RELATIVA, citita din
            # planul de DINAINTE de editare (`HEAD`) — in cel de acum ancora veche arata spre altceva.
            vechi_linii = _plan_la_head()
            offset = 0
            for k in range(a, b + 1):
                if k - 1 < len(vechi_linii) and fragment in vechi_linii[k - 1]:
                    offset = k - a
                    break
            na = nou_start - offset
            noua = "%d-%d" % (na, na + (b - a))
        else:
            noua = str(nou_start)
        if noua != ancora:
            harta[ancora] = noua
    return harta


def aplica(harta):
    if not harta:
        print("nicio ancora nu s-a mutat")
        return 0
    # de la cel mai lung tipar la cel mai scurt, ca `:748` sa nu manance `:748-751`
    perechi = sorted(harta.items(), key=lambda kv: -len(kv[0]))
    atinse = 0
    for cale in _fisiere_py():
        t = io.open(cale, encoding="utf-8").read()
        nou = t
        for vechi, noua in perechi:
            nou = nou.replace("PLAN_HARDENING.md:%s" % vechi, "PLAN_HARDENING.md:%s" % noua)
        if nou != t:
            io.open(cale, "wb").write(nou.encode("utf-8"))
            atinse += 1
    # tabelul gardului poarta ancorele ca CHEI, nu ca citari — daca nu se muta si el, garda ramane
    # rosie dupa o reparatie care a reusit. *O reparatie care repara jumatate e o reparatie care
    # arata ca un defect.*
    t = io.open(TABEL, encoding="utf-8").read()
    nou = t
    for vechi, noua in perechi:
        cheie = '    "%s": ' % vechi
        if cheie in nou:
            nou = nou.replace(cheie, '    "%s": ' % noua)
    if nou != t:
        io.open(TABEL, "wb").write(nou.encode("utf-8"))
        atinse += 1
    print("reancorate in %d fisiere: %s" % (atinse, harta))
    return atinse


def main():
    harta = calculeaza()
    if "--scrie" not in sys.argv:
        print("ancore care s-au mutat: %s" % (harta or "niciuna"))
        print("(ruleaza cu --scrie ca sa le repare; tabelul din core/test_citari_plan.py intra si el)")
        return
    aplica(harta)


if __name__ == "__main__":
    main()
