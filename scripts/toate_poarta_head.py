# -*- coding: utf-8 -*-
"""Bratul four-way REDEFINIT: toate procesele care servesc poarta HEAD?

  ./venv/bin/python scripts/toate_poarta_head.py <sha>

Iese 0 daca DA, 1 daca NU, 2 daca nu se poate sti (baza inaccesibila). Tiparit oricum: cate procese
si care e ratacit — un brat care spune doar «nu» obliga pe cineva sa caute singur.

DE CE EXISTA. Pana azi bratul citea `ActiveEnterTimestamp > data commitului`: un PROXY care spunea
«unitatea a repornit dupa commit», si din care se deducea «procesul viu poarta HEAD». Cu un singur
proces, deductia era buna. Cu mai multe, proxy-ul afirma despre UNITATE ce trebuie afirmat despre
FIECARE PROCES — exact ce cere `PLAN_HARDENING.md:718-720` sa se schimbe.

ASTEAPTA, si de-aia. Hook-ul cheama scriptul imediat dupa `systemctl restart`, iar systemd raspunde
cand unitatea e activa, nu cand fiecare worker si-a terminat verificarea de pornire. Inregistrarea
se face la CAPATUL acelei verificari (deliberat: un proces care n-a trecut-o n-are voie sa apara ca
viu). Deci se reincearca un timp marginit; ce nu apare in fereastra aia chiar e o problema.
"""
import os
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)

#: Cat se asteapta ca workerii sa se inregistreze, si cat de des se intreaba.
RABDARE_SEC = 60
PAS_SEC = 2


def main(argv):
    if not argv:
        print("folosire: toate_poarta_head.py <sha>")
        return 2
    head = argv[0].strip()

    try:
        from core import db, instante
        db.init_pool()
    except Exception as e:
        print("[four-way] NU SE POATE STI: baza inaccesibila (%s)" % e)
        return 2

    limita = time.time() + RABDARE_SEC
    da, total, rataciti = False, 0, []
    while True:
        try:
            with db.get_conn() as conn:
                da, total, rataciti = instante.toate_poarta(conn, head)
        except Exception as e:
            print("[four-way] NU SE POATE STI: %s" % e)
            return 2
        if da or time.time() >= limita:
            break
        time.sleep(PAS_SEC)

    if da:
        print("[four-way] TOATE procesele poarta HEAD: %d din %d" % (total, total))
        return 0

    if total == 0:
        print("[four-way] NICIUN proces inregistrat dupa %d s. Bratul NU se inchide pe o multime "
              "vida: «toate poarta HEAD» n-ar insemna nimic daca nu traieste niciunul." % RABDARE_SEC)
        return 1

    print("[four-way] %d din %d procese NU poarta HEAD (%s):" % (len(rataciti), total, head[:8]))
    for gazda, pid, sha, pornit in rataciti:
        print("    %s pid=%-7d commit=%s  pornit %s" % (gazda, pid, (sha or "?")[:8], pornit))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
