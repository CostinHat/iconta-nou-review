# -*- coding: utf-8 -*-
"""scripts/poarta_scurta.py — RULEAZA poarta scurta din PLAN_LUCRU regula 4.

CE ERA SI CE LIPSEA. Derivarea perimetrului exista deja, intreaga, in `scripts/perimetru.py`:
inchiderea tranzitiva pe „cine importa", plus lista `incerte` care spune cand NU se poate inchide.
Ce lipsea era un lansator — ceva care sa ia perimetrul si sa-l RULEZE, cu refuzul respectat. Asta e.
Nu rescrie derivarea: o IMPORTA. *A doua definitie a aceluiasi lucru e inceputul unei divergente
tacute* (PLAN_LUCRU, regula 5).

TREI LUCRURI PE CARE LE FACE IMPOSIBILE, si sunt chiar motivul formei:

1. **NU primeste fisiere.** `perimetru.py` accepta cai in argv — util cand PROBEZI derivarea, dar
   fatal intr-un lansator: ar insemna ca cel care a scris modificarea alege ce se ruleaza. Regula o
   interzice pe litere: *„nu-l suprascrie cu judecata ta — o exceptie luata o data face regula o
   formalitate."* Aici lista atinselor vine NUMAI din `git diff`, si nu exista argument care s-o
   schimbe.
2. **NU poate trece drept poarta.** Cand perimetrul e verde, iesirea spune raspicat ce N-A rulat.
   Un verde care nu-si declara marginile e chiar felul de verde impotriva caruia e scrisa casa asta.
3. **NU ghiceste.** Daca derivarea intoarce fie si un singur motiv de nesiguranta (sau perimetrul iese
   gol), RULEAZA TOT: suita intreaga (`SUITA_INTREAGA`, pe procesele portii), nu poarta. *Un perimetru
   ghicit e mai rau decat o rulare lunga.* [15.10.2026, comanda Costin, verbatim in DECIZII „Poarta o dată
   pe lot”: „după fiecare comandă, doar rularea țintită de azi (poarta_scurta.py / perimetru.py, cu
   «incert → rulează tot»), pe numărul de procese de acum”.] Pana pe 15.10 iesea cu 2 si cerea poarta.

CE NU RULEAZA, scris ca sa nu se creada altceva: verificatorul de conformitate, cifrele F1–F5, plasa e2e.
Poarta completa ruleaza O DATA PE LOT, la inchiderea lui (`scripts/poarta_lot.sh`), inaintea publicarii.
"""
import os
import subprocess
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))

import perimetru as P  # noqa: E402

#: „incert -> ruleaza tot”: suita intreaga, fara selectie, pe procesele portii (`scripts/githooks/poarta-suita`: -n 3, loadfile)
SUITA_INTREAGA = ["./venv/bin/python", "-m", "pytest", "-q", "-n", "3", "--dist", "loadfile"]


def _ruleaza_tot(motiv):
    print()
    print("PERIMETRUL NU SE POATE INCHIDE (%s) — se ruleaza SUITA INTREAGA:" % motiv)
    print("  " + " ".join(SUITA_INTREAGA))
    print("(«un perimetru ghicit e mai rau decat o rulare lunga» — PLAN_LUCRU, regula 4)")
    t0 = time.time()
    r = subprocess.run(SUITA_INTREAGA, cwd=RAD)
    print("suita intreaga: %.0f s, exit %d. CE N-A RULAT: verificatorul, cifrele F1–F5, plasa e2e (poarta lotului)."
          % (time.time() - t0, r.returncode))
    return r.returncode


def main(argv):
    # [1] niciun argument de fisier. Explicit, cu motivul, nu prin ignorare tacuta.
    fisiere = [a for a in argv if not a.startswith("-")]
    if fisiere:
        print("REFUZ: poarta scurta nu primeste fisiere pe linia de comanda.")
        print("  Perimetrul se DERIVA din `git diff`, nu se alege. Ai dat: %s" % " ".join(fisiere))
        print("  (PLAN_LUCRU regula 5: «o excepție luată o dată face regula o formalitate».)")
        print("  Ca sa PROBEZI derivarea pe un fisier anume: scripts/perimetru.py <cale>")
        return 3

    # [P0 07.09.2026] NIVELUL cerut. Implicit: `subsistem` — treapta de minute, cea mai des
    # folosita in bucla de lucru. `--nivel complet` nu e acceptat aici: N4 e suita intreaga, si se
    # ruleaza cu `pytest` fara lista, nu prin instrumentul de perimetru.
    nivel = "subsistem"
    for a in argv:
        if a.startswith("--nivel="):
            nivel = a.split("=", 1)[1]
    if nivel not in P.NIVELURI:
        print("REFUZ: nivel necunoscut %r. Cunoscute: %s" % (nivel, ", ".join(P.NIVELURI)))
        return 3
    if nivel == "complet":
        print("N4 (complet) NU se ruleaza de aici — e suita intreaga:")
        print("  ./venv/bin/python -m pytest -q")
        return 3

    atinse = P.atinse_din_git()
    nt = P.netracked()
    if not atinse:
        print("ATINSE: niciunul — arborele e curat fata de HEAD. Nimic de rulat.")
        if nt:
            print("(%d fisiere neurmarite si nestagiate, NEPRIVITE de instrument)" % len(nt))
        return 0

    print("ATINSE (%d):" % len(atinse))
    for a in atinse:
        print("   ", a)
    if nt:
        print("(plus %d fisiere neurmarite si nestagiate, care NU intra in perimetru)" % len(nt))

    teste, incerte = P.nivel(nivel, atinse)

    # [3] nesiguranta -> suita intreaga, cu motivele scrise
    if incerte:
        print()
        print("Motive de nesiguranta:")
        for m in incerte:
            print("   -", m)
        return _ruleaza_tot("%d motive" % len(incerte))

    if not teste:
        # «nimic de rulat» nu e un raspuns despre ce s-a schimbat
        return _ruleaza_tot("perimetru gol, desi s-au atins fisiere")

    print()
    print("NIVEL %s — %d fisiere de test." % (nivel.upper(), len(teste)))
    t0 = time.time()
    r = subprocess.run(["./venv/bin/python", "-m", "pytest", "-q", "--no-header"] + teste,
                       cwd=RAD)
    dt = time.time() - t0

    print()
    print("nivel %s: %.0f s pe %d fisiere de test" % (nivel, dt, len(teste)))
    urm = {"direct": "subsistem", "subsistem": "integrare", "integrare": "complet"}.get(nivel)
    if urm:
        print("CE N-A RULAT: tot ce e peste nivelul asta. Urmatoarea treapta: --nivel=%s" % urm)
    print("CE N-A RULAT, oricum: verificatorul de conformitate.")
    print("Poarta COMPLETA: o data pe lot, la inchiderea lui (scripts/poarta_lot.sh), inaintea publicarii.")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
