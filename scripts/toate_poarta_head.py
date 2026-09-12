# -*- coding: utf-8 -*-
"""Bratul four-way REDEFINIT: toate procesele care servesc poarta HEAD?

  ./venv/bin/python scripts/toate_poarta_head.py <sha>

Iese 0 daca DA, 1 daca NU, 2 daca nu se poate sti. Tiparit oricum: cate procese si care e ratacit
— un brat care spune doar «nu» obliga pe cineva sa caute singur.

DE CE EXISTA. Pana la 12.09.2026 bratul citea `ActiveEnterTimestamp > data commitului`: un PROXY
care spunea «unitatea a repornit dupa commit», si din care se deducea «procesul viu poarta HEAD».
Cu un singur proces, deductia era buna. Cu mai multe, proxy-ul afirma despre UNITATE ce trebuie
afirmat despre FIECARE PROCES — exact ce cere `PLAN_HARDENING.md:718-720` sa se schimbe.

DE CE ISI CITESTE SINGUR ACREDITAREA DE PRODUCTIE, in loc s-o mosteneasca din mediu. Prima forma
folosea `DATABASE_URL` din mediu. Hook-ul `post-commit` mosteneste insa mediul scriptului de
commit, iar acela sursează `test.env` — fiindca asa cere R68, ca poarta sa ruleze suita in baza
IZOLATA. Deci o afirmatie despre procesele de PRODUCTIE se facea, in tacere, pe `iconta_test`:
prima rulare pe viu a raportat un proces «ratacit» care era de fapt un proces de TEST (`TestClient`
ruleaza `lifespan`, deci se inregistreaza), iar a doua a raportat «niciun proces» acolo unde
productia avea unul corect. *Aceeasi clasa cu verificarea gazdei gresite din P5: patru raspunsuri
verzi despre o lume la care nu ma uitam.*

Deci intrebarea «toate procesele de productie poarta HEAD?» isi cere ea baza de productie, si
REFUZA sa raspunda daca nu e acolo. E oglinda lui R68: acela refuza sa porneasca peste productie,
asta refuza sa raspunda despre altceva decat productia.
"""
import io
import os
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)

from core import mediu_test as _mediu  # noqa: E402

#: Unde sta acreditarea de productie. Aceeasi conventie ca `mediu_test.CALE_TEST_ENV`.
CALE_DB_ENV = os.path.expanduser("~/.iconta/db.env")

#: Cat se asteapta ca procesele sa se inregistreze, si cat de des se intreaba. Masurat pe
#: 12.09.2026: de la `ActiveEnterTimestamp` pana la inregistrare au trecut 2 s. Cu `--workers N`
#: pornirile se SERIALIZEAZA pe blocajul de pornire, deci marja e pentru ele.
RABDARE_SEC = 90
PAS_SEC = 2


def dsn_productie():
    """DSN-ul de productie, citit din fisierul lui. `None` daca nu se poate."""
    try:
        for linie in io.open(CALE_DB_ENV, encoding="utf-8"):
            linie = linie.strip()
            if linie.startswith("export "):
                linie = linie[len("export "):]
            if linie.startswith("DATABASE_URL="):
                return linie.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception:
        return None
    return None


def main(argv):
    if not argv:
        print("folosire: toate_poarta_head.py <sha>")
        return 2
    head = argv[0].strip()

    url = dsn_productie()
    if not url:
        print("[four-way] NU SE POATE STI: %s n-are DATABASE_URL" % CALE_DB_ENV)
        return 2
    componente = _mediu.desface_dsn(url)
    if componente["dbname"] != _mediu.PRODUCTIE_DBNAME:
        print("[four-way] REFUZ: intrebarea e despre procesele de PRODUCTIE, iar acreditarea "
              "citita duce la baza %r, nu la %r."
              % (componente["dbname"], _mediu.PRODUCTIE_DBNAME))
        return 2

    try:
        import psycopg2
    except Exception as e:
        print("[four-way] NU SE POATE STI: psycopg2 lipseste (%s)" % e)
        return 2

    from core import instante

    limita = time.time() + RABDARE_SEC
    da, total, rataciti = False, 0, []
    while True:
        try:
            conn = psycopg2.connect(url, connect_timeout=10)
            try:
                conn.set_session(readonly=True, autocommit=True)
                da, total, rataciti = instante.toate_poarta(conn, head)
            finally:
                conn.close()
        except Exception as e:
            print("[four-way] NU SE POATE STI: %s" % str(e).strip().splitlines()[0])
            return 2
        if da or time.time() >= limita:
            break
        time.sleep(PAS_SEC)

    if da:
        print("[four-way] TOATE procesele de productie poarta HEAD: %d din %d" % (total, total))
        return 0

    if total == 0:
        print("[four-way] NICIUN proces inregistrat in %s dupa %d s. Bratul NU se inchide pe o "
              "multime vida: «toate poarta HEAD» n-ar insemna nimic daca nu traieste niciunul."
              % (_mediu.PRODUCTIE_DBNAME, RABDARE_SEC))
        return 1

    print("[four-way] %d din %d procese NU poarta HEAD (%s):" % (len(rataciti), total, head[:8]))
    for gazda, pid, sha, pornit in rataciti:
        print("    %s pid=%-7d commit=%s  pornit %s" % (gazda, pid, (sha or "?")[:8], pornit))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
