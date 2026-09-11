# -*- coding: utf-8 -*-
"""conftest.py (radacina) — MECANISM UNIC de mediu, si FRONTIERA fata de productie.

[R68, 11.09.2026] Pana azi, fisierul asta sursa `~/.iconta/db.env` — adica DSN-ul de PRODUCTIE —
in `os.environ`, inaintea colectarii. Suita rula pe baza reala, iar izolarea era o CONVENTIE:
fiecare test trebuia sa-si faca `rollback`. Conventia s-a rupt pe 10.09: un rand a ramas in
`tenant_001.salariu_istoric` si a facut poarta rosie la rularea urmatoare. *O frontiera care
depinde de disciplina fiecarui test nu e o frontiera.*

Acum se sursaza `~/.iconta/test.env`, iar `core.mediu_test` verifica mediul INAINTE de colectare.
Verificarea e **fail-closed in intelesul tare**: lipsa informatiei nu e permisiune. Fara
`ICONTA_MEDIU=test`, fara un DSN citibil, sau cu o configuratie ambigua, suita nu porneste — nu
fiindca a gasit productia, ci fiindca *nu poate dovedi ca nu e pe ea*.

**Nu exista cadere pe productie.** Daca `test.env` lipseste, suita refuza. Varianta «baza de test
indisponibila -> folosim productia» nu e implementata nicaieri si nu trebuie sa fie: exact acolo
s-ar pierde tot ce apara fisierul asta.

A doua incuietoare, cea tare, e la PostgreSQL: rolul `iconta_test_user` nu are `CONNECT` pe
`iconta_v2`, deci refuzul vine de la server chiar daca cineva ocoleste codul de aici.
"""
import os

CALE_TEST_ENV = os.path.expanduser("~/.iconta/test.env")


def _incarca(cale):
    """Sourceaza un fisier de mediu in `os.environ` (setdefault). Intoarce numarul de variabile
    incarcate, sau `None` daca fisierul lipseste.

    `setdefault`, nu suprascriere: ce e deja in mediu are prioritate (systemd / CI / override
    manual). Asta inseamna si ca un mediu deja incarcat cu valori de PRODUCTIE **nu** e corectat
    tacit de fisierul asta — e prins de verificarea de mai jos si refuzat vizibil.
    """
    if not os.path.isfile(cale):
        return None
    n = 0
    with open(cale, encoding="utf-8") as f:
        for linie in f:
            s = linie.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            cheie, val = s.split("=", 1)
            cheie = cheie.strip()
            if cheie and cheie not in os.environ:
                os.environ[cheie] = val.strip().strip('"').strip("'")
                n += 1
    return n


_TEST_ENV = _incarca(CALE_TEST_ENV)

# Verificarea, la INCARCAREA conftest-ului: inainte de colectare, deci inainte ca vreun test sa
# apuce sa deschida vreo conexiune. Ridica `MediuNedovedit`, cu motivele scrise.
from core import mediu_test as _mediu  # noqa: E402  (dupa incarcarea mediului, intentionat)

if _TEST_ENV is None and not os.environ.get(_mediu.CHEIE_MEDIU):
    raise _mediu.MediuNedovedit(
        "suita NU porneste: nu exista %s si mediul nu declara nimic.\n"
        "  Nu se cade pe baza de productie — asta ar anula tot ce apara fisierul asta.\n"
        "  Mediul izolat se construieste o singura data (R68); vezi masuratori/r68/."
        % CALE_TEST_ENV)

_mediu.verifica(os.environ)


def pytest_configure(config):
    # skip-urile raman VIZIBILE ca semnal, indiferent de flag-urile de pornire (echiv. -rs)
    rc = getattr(config.option, "reportchars", "") or ""
    if "s" not in rc:
        config.option.reportchars = rc + "s"
    config.addinivalue_line("markers", "izolare: probele de acceptanta ale frontierei R68")


def pytest_sessionstart(session):
    """Monteaza sonda de scrieri cand e ceruta (`ICONTA_SONDA_SCRIERI=1`).

    Sonda refuza singura sa se monteze pe un mediu nedovedit de test — un jurnal de scrieri scris
    in productie ar adauga exact felul de reziduu pe care il investigheaza."""
    from core import sonda_scrieri
    if not sonda_scrieri.ACTIVA:
        return
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        montate = sonda_scrieri.instaleaza(conn)
    print("sonda de scrieri: montata pe %d tabele" % len(montate))


def pytest_runtest_setup(item):
    """Identitatea testului ajunge la PostgreSQL prin `application_name`, de unde o citeste
    declansatorul din `core/sonda_scrieri.py`. Fara asta, jurnalul sondei ar spune CE s-a scris,
    dar nu de catre cine — iar «cine» e chiar intrebarea din incidentul randului 53."""
    os.environ["PGAPPNAME"] = item.nodeid[-63:]


def pytest_report_header(config):
    st = _mediu.descrie(os.environ)
    return ("mediu: %s · baza: %s · rol: %s  (frontiera R68: rolul asta nu are CONNECT pe %s)"
            % (st["mediu"], st["dbname"], st["user"], _mediu.PRODUCTIE_DBNAME))
