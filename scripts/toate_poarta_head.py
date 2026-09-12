# -*- coding: utf-8 -*-
"""Bratul four-way REDEFINIT: toate procesele care servesc poarta HEAD?

  ./venv/bin/python scripts/toate_poarta_head.py <sha>

Iese 0 daca DA, 1 daca NU, 2 daca nu se poate sti. Tiparit oricum: cate procese se asteptau, cate
s-au gasit, si care e ratacit — un brat care spune doar «nu» obliga pe cineva sa caute singur.

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

## CARDINALITATEA (13.09.2026) — a doua jumatate a aceleiasi intrebari

MASURAT, la publicarea lui `a9566af0`: bratul a tiparit «TOATE procesele de productie poarta HEAD:
1 din 1» pe o productie cu DOI workeri. N-a mintit despre ce a vazut — a vazut un singur proces
inregistrat, fiindca cei doi se inregistreaza la ~0,8 s distanta si intrebarea a nimerit fereastra
dintre ele. A mintit prin ce NU s-a intrebat: *cati ar fi trebuit sa fie.*

E aceeasi clasa cu `all([])`, cu un pas mai departe: acolo multimea era VIDA, aici e INCOMPLETA.
Un brat care se inchide pe o submultime afirma despre «toate» ce a verificat despre «cateva».

DECI VERDICTUL ARE ACUM DOUA CONDITII, amandoua necesare:

    FOUR_WAY_PASS = cardinalitatea e completa  SI  fiecare proces inregistrat poarta HEAD

Numarul asteptat NU e scris aici: se citeste din configuratia canonica efectiva a serviciului —
`WEB_CONCURRENCY`, aceeasi variabila pe care o citeste `uvicorn` pentru `--workers` si `main.py`
pentru pragul de conexiuni. Un numar scris in doua locuri ar putea diverge; asta e chiar defectul
pe care valul 3 l-a inchis la prag.

SI NU EXISTA CALE PRIN CARE «NU STIU» SA DEVINA «DA». Daca unitatea nu se poate citi, bratul iese
cu 2 (necunoscut), nu cu 0. Singurul caz in care absenta variabilei da un numar e absenta EI din
configuratie, si nici acela nu e o presupunere: `uvicorn/config.py:339` citeste `WEB_CONCURRENCY`
numai daca `--workers` lipseste, iar fara niciuna porneste UN proces. Absenta e determinata, nu
necunoscuta — si se tipareste ca atare.
"""
import collections
import io
import os
import subprocess
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)

from core import mediu_test as _mediu  # noqa: E402

#: Unde sta acreditarea de productie. Aceeasi conventie ca `mediu_test.CALE_TEST_ENV`.
CALE_DB_ENV = os.path.expanduser("~/.iconta/db.env")

#: Unitatea care serveste. Numele ei e singurul lucru scris aici despre infrastructura; numarul de
#: procese se CITESTE din ea, nu se scrie a doua oara.
UNITATE = "iconta-nou"

#: Cat se asteapta ca procesele sa se inregistreze, si cat de des se intreaba. Masurat pe
#: 12.09.2026: de la `ActiveEnterTimestamp` pana la inregistrare au trecut 2 s, iar intre primul si
#: al doilea worker inca 0,8 s. Cu `--workers N` pornirile se SERIALIZEAZA pe blocajul de pornire,
#: deci marja e pentru ele.
RABDARE_SEC = 90
PAS_SEC = 2

PASS, INCOMPLET, PREA_MULTE, RATACITI = "PASS", "INCOMPLET", "PREA_MULTE", "RATACITI"

Verdict = collections.namedtuple("Verdict", "stare total asteptate rataciti")

#: DE UNDE vine numarul asteptat — multime INCHISA, nu proza. `detaliu` e pentru om si pentru
#: tiparire; `fel` e ce intreaba o proba, ca sa nu ajunga sa caute un cuvant intr-o propozitie.
UNITATE_ENV, FISIER_ENV, IMPLICIT, NECUNOSCUT = "unitate", "fisier", "implicit", "necunoscut"

Sursa = collections.namedtuple("Sursa", "fel detaliu")


# ============================================================
#  1. CATI AR TREBUI SA FIE — citit din unitate, nu presupus
# ============================================================
def _campuri_unitate(unitate=UNITATE):
    r = subprocess.run(["systemctl", "show", unitate,
                        "-p", "LoadState", "-p", "Environment", "-p", "EnvironmentFiles"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None
    out = {}
    for linie in r.stdout.splitlines():
        if "=" in linie:
            k, v = linie.split("=", 1)
            out.setdefault(k, []).append(v)
    return out


def _din_text(text):
    """Numarul din `WEB_CONCURRENCY=<n>`, oriunde ar fi in sirul asta. `None` daca nu-i, si
    ridica daca e acolo dar nu e numar — o valoare stricata nu are voie sa treaca drept absenta."""
    for bucata in text.split():
        if bucata.startswith("WEB_CONCURRENCY="):
            return int(bucata.split("=", 1)[1])
    return None


#: „nu mi s-a dat nimic", deosebit de `None`, care inseamna „unitatea nu s-a putut citi". Prima
#: forma le confunda: `numar_asteptat(campuri=None)` mergea si citea unitatea REALA, deci proba care
#: voia sa arate ca necunoscutul nu devine PASS n-avea cum sa exprime necunoscutul.
_NECITIT = object()


def numar_asteptat(unitate=UNITATE, campuri=_NECITIT):
    """(n, `Sursa`) — cate procese ar trebui sa serveasca, si DE UNDE se stie.

    `(None, Sursa(NECUNOSCUT, motiv))` cand nu se poate sti — si atunci bratul iese cu 2, nu cu 0.

    Ordinea surselor e a lui systemd: `Environment=` din unitate, apoi fisierele `EnvironmentFile`.
    """
    campuri = _campuri_unitate(unitate) if campuri is _NECITIT else campuri
    if campuri is None:
        return None, Sursa(NECUNOSCUT, "`systemctl show %s` n-a raspuns" % unitate)
    stare = (campuri.get("LoadState") or [""])[0]
    if stare != "loaded":
        return None, Sursa(NECUNOSCUT, "unitatea %s are LoadState=%r" % (unitate, stare))

    try:
        for valoare in campuri.get("Environment", []):
            n = _din_text(valoare)
            if n is not None:
                return n, Sursa(UNITATE_ENV, "Environment= din unitatea %s" % unitate)
        for rand in campuri.get("EnvironmentFiles", []):
            cale = rand.split(" (")[0].strip()
            try:
                text = io.open(cale, encoding="utf-8").read()
            except OSError:
                continue
            for linie in text.splitlines():
                linie = linie.strip()
                if linie.startswith("#"):
                    continue
                if linie.startswith("export "):
                    linie = linie[len("export "):]
                n = _din_text(linie)
                if n is not None:
                    return n, Sursa(FISIER_ENV, "EnvironmentFile %s" % cale)
    except ValueError as e:
        return None, Sursa(NECUNOSCUT, "WEB_CONCURRENCY nu e un numar (%s)" % e)

    return 1, Sursa(IMPLICIT,
                    "nicio valoare scrisa: `uvicorn` porneste un singur proces cand nici "
                    "`--workers`, nici `WEB_CONCURRENCY` nu exista (uvicorn/config.py:339)")


# ============================================================
#  2. VERDICTUL — functie pura, ca sa poata fi probata fara baza
# ============================================================
def judeca(total, rataciti, asteptate):
    """Cele doua conditii, in ordinea in care se pot afirma.

    Cardinalitatea se judeca INAINTEA commiturilor: «toti cei gasiti poarta HEAD» nu spune nimic
    daca nu s-au gasit toti. Iar mai multi decat se asteptau nu e o veste buna — e un registru
    despre care nu se stie ce contine (un rand ramas de la un proces mort, alta gazda, un proces
    strain), deci nu poate inchide bratul.
    """
    if total < asteptate:
        return Verdict(INCOMPLET, total, asteptate, list(rataciti))
    if total > asteptate:
        return Verdict(PREA_MULTE, total, asteptate, list(rataciti))
    if rataciti:
        return Verdict(RATACITI, total, asteptate, list(rataciti))
    return Verdict(PASS, total, asteptate, [])


def asteapta_si_judeca(citeste, asteptate, rabdare_sec=RABDARE_SEC, pas_sec=PAS_SEC,
                       ceas=time.time, dormi=time.sleep):
    """Reia intrebarea pana cand verdictul e PASS sau pana expira rabdarea.

    `citeste()` intoarce `(total, rataciti)`. Ceasul si somnul se pot injecta, ca probele sa poata
    trece prin expirare fara sa astepte cu adevarat.
    """
    limita = ceas() + rabdare_sec
    while True:
        v = judeca(*citeste(), asteptate=asteptate)
        if v.stare == PASS or ceas() >= limita:
            return v
        dormi(pas_sec)


# ============================================================
#  3. Baza de productie
# ============================================================
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

    asteptate, sursa = numar_asteptat()
    if asteptate is None:
        print("[four-way] NU SE POATE STI cati workeri ar trebui sa serveasca: %s" % sursa.detaliu)
        return 2

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

    def citeste():
        conn = psycopg2.connect(url, connect_timeout=10)
        try:
            conn.set_session(readonly=True, autocommit=True)
            _da, total, rataciti = instante.toate_poarta(conn, head)
            return total, rataciti
        finally:
            conn.close()

    try:
        v = asteapta_si_judeca(citeste, asteptate)
    except Exception as e:
        print("[four-way] NU SE POATE STI: %s" % str(e).strip().splitlines()[0])
        return 2

    print("[four-way] asteptati %d (%s) · gasiti %d" % (v.asteptate, sursa.detaliu, v.total))
    if v.stare == PASS:
        print("[four-way] TOATE procesele de productie poarta HEAD: %d din %d"
              % (v.total, v.asteptate))
        return 0

    if v.stare == INCOMPLET:
        print("[four-way] INCOMPLET: %d din %d procese inregistrate in %s dupa %d s. Bratul NU se "
              "inchide pe o submultime: «toate poarta HEAD» ar afirma despre TOATE ce s-a "
              "verificat despre cateva."
              % (v.total, v.asteptate, _mediu.PRODUCTIE_DBNAME, RABDARE_SEC))
    elif v.stare == PREA_MULTE:
        print("[four-way] PREA MULTE: %d procese inregistrate, %d asteptate. Registrul contine "
              "ceva ce nu se stie ce e — un rand ramas, alta gazda, un proces strain."
              % (v.total, v.asteptate))
    else:
        print("[four-way] %d din %d procese NU poarta HEAD (%s):"
              % (len(v.rataciti), v.total, head[:8]))
    for gazda, pid, sha, pornit in v.rataciti:
        print("    %s pid=%-7d commit=%s  pornit %s" % (gazda, pid, (sha or "?")[:8], pornit))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
