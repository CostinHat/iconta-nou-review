# -*- coding: utf-8 -*-
"""conftest.py (radacina) — MECANISM UNIC de mediu pentru suita de teste.

Testele de integrare cu DB (core/test_spv_poll, test_spv_receive, test_etransport_send)
sar cu "DB indisponibil" cand os.environ n-are datele de conectare. Asta se intampla ori
de cate ori pytest e pornit ALTFEL decat prin systemd (direct, IDE, CI) -> un skip TACIT
care arata verde si nu apara nimic (DE_FACUT item 6).

Aici, la incarcarea conftest-ului (INAINTE de colectare, indiferent cum e pornita suita),
sursam ~/.iconta/db.env in os.environ, ca EnvironmentFile-ul serviciului. NU suprascriem
ce e deja setat -> systemd / CI / override manual au prioritate.

NU inlocuim garda _db_ok() din teste: daca db.env LIPSESTE sau baza NU raspunde, testele
tot sar — dar VIZIBIL: antetul rularii spune starea db.env, iar motivele de skip sunt
fortate sa apara (reportchars 's'). Un skip ramane semnal, nu tacere.
"""
import os


def _incarca_db_env():
    """Sourceaza ~/.iconta/db.env in os.environ (setdefault). Intoarce nr. variabile incarcate,
    sau None daca fisierul lipseste (= semnal, nu eroare: testele de DB vor sari vizibil)."""
    cale = os.path.expanduser("~/.iconta/db.env")
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
            if cheie and cheie not in os.environ:  # ce e deja in mediu are prioritate
                os.environ[cheie] = val.strip().strip('"').strip("'")
                n += 1
    return n


_DB_ENV = _incarca_db_env()


def pytest_configure(config):
    # skip-urile raman VIZIBILE ca semnal, indiferent de flag-urile de pornire (echiv. -rs)
    rc = getattr(config.option, "reportchars", "") or ""
    if "s" not in rc:
        config.option.reportchars = rc + "s"


def pytest_report_header(config):
    if _DB_ENV is None:
        return "db.env: LIPSA la ~/.iconta/db.env -> testele de DB SAR (skip vizibil, nu tacut)"
    return "db.env: incarcat din ~/.iconta/db.env (%d variabile)" % _DB_ENV
