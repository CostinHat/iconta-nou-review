# -*- coding: utf-8 -*-
"""core/mediu_test.py — FRONTIERA dintre suita de teste si baza de PRODUCTIE (R68, 11.09.2026).

**De ce exista.** Pana azi, `conftest.py` sursa `~/.iconta/db.env` in `os.environ` inaintea
colectarii, deci suita primea DSN-ul de PRODUCTIE si scria in el. Izolarea era o CONVENTIE:
fiecare test trebuia sa-si faca `rollback`. Pe 10.09.2026 conventia s-a rupt — un rand a ramas in
`tenant_001.salariu_istoric` (salariat 53, `2026-06-01`, `7000.0`, scris la `23:54:38`) si a facut
poarta rosie la rularea urmatoare. Producatorul exact NU e cunoscut, si tocmai asta e argumentul:
*o frontiera care depinde de disciplina fiecarui test nu e o frontiera.*

**Ce NU e modulul asta.** Nu e bariera. Bariera adevarata e la PostgreSQL: rolul cu care ruleaza
suita nu are `CONNECT` pe baza de productie, deci refuzul vine de la server, nu din Python. Modulul
asta e a DOUA incuietoare — cea care opreste suita *inainte* sa incerce, si care spune limpede de
ce. Daca vreodata cele doua nu sunt de acord, cea de la PostgreSQL are dreptate.

**Fail-closed, in intelesul tare.** Lipsa unei informatii NU e permisiune. Fara `ICONTA_MEDIU=test`
suita refuza sa porneasca — nu pentru ca a gasit productia, ci pentru ca *nu poate dovedi ca nu e
pe ea*. Tacerea nu trece.
"""
from __future__ import annotations

import collections
import os

MODUL = "mediu_test"

#: Identitatea bazei de PRODUCTIE. Scrisa aici, EXPLICIT, fiindca o frontiera care nu stie ce
#: aparara nu apara nimic. Daca productia se muta, se schimba aici si garda cade pana se schimba.
PRODUCTIE_DBNAME = "iconta_v2"
PRODUCTIE_USER = "iconta_user"

#: Valoarea pe care mediul de test trebuie s-o declare EXPLICIT.
MEDIU_TEST = "test"

CHEIE_MEDIU = "ICONTA_MEDIU"

#: Calea mediului izolat. Se intoarce pe exceptie ca `cale_remediu`, deci se poate verifica pe
#: camp — un refuz fara iesire scrisa se ocoleste, nu se respecta.
CALE_TEST_ENV = os.path.expanduser("~/.iconta/test.env")


#: Un motiv de refuz e un OBIECT cu campuri, nu o propozitie. Asa se poate asserta pe COD —
#: structural —, nu cautand un subsir in proza refuzului. (METODA §23; si decizia din DS cap.25:
#: afirmatiile sunt obiecte cu atribute, nu siruri.) Namedtuple, nu dictionar: un dict cu cheia
#: `motiv` ar fi citit de garda afirmatiilor tipate drept afirmatie despre datele unei firme.
Motiv = collections.namedtuple("Motiv", "cod detaliu")

COD_MEDIU_NEDECLARAT = "MEDIU_NEDECLARAT"
COD_BAZA_PRODUCTIE = "BAZA_PRODUCTIE"
COD_UTILIZATOR_PRODUCTIE = "UTILIZATOR_PRODUCTIE"
COD_BAZA_NECITIBILA = "BAZA_NECITIBILA"
COD_UTILIZATOR_NECITIBIL = "UTILIZATOR_NECITIBIL"
COD_CONFIGURATIE_AMBIGUA = "CONFIGURATIE_AMBIGUA"


class MediuNedovedit(RuntimeError):
    """Suita a fost pornita fara sa se poata dovedi ca NU e pe baza de productie.

    Poarta `coduri` (multimea codurilor de refuz) si `cale_remediu` — ca cine o prinde sa poata
    decide pe structura, nu pe textul mesajului.
    """

    def __init__(self, mesaj, coduri=(), cale_remediu=None):
        RuntimeError.__init__(self, mesaj)
        self.coduri = frozenset(coduri)
        self.cale_remediu = cale_remediu


def desface_dsn(url):
    """Componentele unui DSN `postgresql://user:parola@host:port/dbname`, FARA parola.

    Intoarce dict cu `user`, `host`, `port`, `dbname` — si `None` pe ce nu se poate citi. Nu
    foloseste `urlparse` pe orbeste: un DSN cu parola care contine `@` sau `/` ar da un raspuns
    gresit cu incredere, iar aici raspunsul gresit cu incredere e exact felul de esec care ne-a
    adus in situatia asta. Se taie de la DREAPTA pe `@` (ultimul), si de la STANGA pe primul `/`
    de dupa el.
    """
    d = {"user": None, "host": None, "port": None, "dbname": None}
    if not url or "://" not in url:
        return d
    _schema, rest = url.split("://", 1)
    if "@" in rest:
        acreditare, adresa = rest.rsplit("@", 1)
        d["user"] = acreditare.split(":", 1)[0] or None
    else:
        adresa = rest
    if "/" in adresa:
        gazda, cale = adresa.split("/", 1)
        d["dbname"] = (cale.split("?", 1)[0] or None)
    else:
        gazda = adresa
    if ":" in gazda:
        d["host"], _, port = gazda.rpartition(":")
        d["port"] = port or None
    else:
        d["host"] = gazda or None
    return d


def descrie(env=None):
    """Ce baza si ce utilizator sunt in mediu, dupa aceleasi reguli ca `db.config_din_env`:
    `DATABASE_URL` are prioritate, altfel `DB_NAME`/`DB_USER`. Pura (primeste env)."""
    env = env if env is not None else os.environ
    url = env.get("DATABASE_URL")
    if url:
        d = desface_dsn(url)
        return {
            "mediu": env.get(CHEIE_MEDIU),
            "sursa": "DATABASE_URL",
            "dbname": d["dbname"],
            "user": d["user"],
            "host": d["host"],
            "port": d["port"],
        }
    return {
        "mediu": env.get(CHEIE_MEDIU),
        "sursa": "DB_*",
        "dbname": env.get("DB_NAME"),
        "user": env.get("DB_USER"),
        "host": env.get("DB_HOST"),
        "port": env.get("DB_PORT"),
    }


def motive(env=None):
    """Lista motivelor pentru care mediul NU poate fi acceptat ca fiind de test. Goala = acceptat.

    Intoarce motive, nu un bool, fiindca un refuz care nu spune CE anume l-a declansat se
    dezactiveaza a doua zi de cine nu-l intelege.
    """
    env = env if env is not None else os.environ
    st = descrie(env)
    m = []

    if st["mediu"] != MEDIU_TEST:
        m.append(Motiv(COD_MEDIU_NEDECLARAT,
                       "%s nu e '%s' (e %r) — tacerea nu trece: mediul trebuie sa se DECLARE, "
                       "fiindca lipsa declaratiei nu dovedeste ca nu suntem pe productie"
                       % (CHEIE_MEDIU, MEDIU_TEST, st["mediu"])))

    if st["dbname"] is None:
        m.append(Motiv(COD_BAZA_NECITIBILA,
                       "nu se poate citi numele bazei din %s — o baza necunoscuta se trateaza ca "
                       "productie" % st["sursa"]))
    elif st["dbname"] == PRODUCTIE_DBNAME:
        m.append(Motiv(COD_BAZA_PRODUCTIE, "baza e chiar cea de PRODUCTIE (%s)" % PRODUCTIE_DBNAME))

    if st["user"] is None:
        m.append(Motiv(COD_UTILIZATOR_NECITIBIL,
                       "nu se poate citi utilizatorul din %s — un utilizator necunoscut se "
                       "trateaza ca cel de productie" % st["sursa"]))
    elif st["user"] == PRODUCTIE_USER:
        m.append(Motiv(COD_UTILIZATOR_PRODUCTIE,
                       "utilizatorul e chiar cel de PRODUCTIE (%s) — chiar daca baza difera, "
                       "rolul asta are drepturi pe productie" % PRODUCTIE_USER))

    # Ambiguitatea e un motiv de refuz, nu o preferinta de rezolvat tacut: daca DATABASE_URL si
    # DB_NAME spun lucruri diferite, nu se stie care a ajuns la psycopg2 in fiecare cale de cod.
    if env.get("DATABASE_URL") and env.get("DB_NAME"):
        d = desface_dsn(env["DATABASE_URL"])
        if d["dbname"] and d["dbname"] != env["DB_NAME"]:
            m.append(Motiv(COD_CONFIGURATIE_AMBIGUA,
                           "DATABASE_URL spune baza %r, DB_NAME spune %r — cat timp nu sunt de "
                           "acord, nu se stie care ajunge la conexiune"
                           % (d["dbname"], env["DB_NAME"])))
    return m


def coduri(env=None):
    """Multimea codurilor de refuz. Asta e forma pe care se asserteaza — nu textul."""
    return frozenset(x.cod for x in motive(env))


def verifica(env=None):
    """Ridica `MediuNedovedit` daca mediul nu se poate dovedi a fi de test. Altfel, tace.

    Se cheama din `conftest.py`, la incarcare — deci INAINTE de colectare, deci inainte ca vreun
    test sa apuce sa deschida vreo conexiune.
    """
    m = motive(env)
    if m:
        st = descrie(env)
        raise MediuNedovedit(
            "suita NU porneste: nu se poate dovedi ca mediul e de test.\n"
            "  baza=%r utilizator=%r gazda=%r (din %s)\n"
            "  motive:\n%s\n"
            "  Cum se porneste corect: cu ~/.iconta/test.env in mediu (ICONTA_MEDIU=test si DSN-ul "
            "bazei izolate). Frontiera adevarata e la PostgreSQL — rolul de test nu are CONNECT pe "
            "%s —, iar mesajul asta e doar prima incuietoare."
            % (st["dbname"], st["user"], st["host"], st["sursa"],
               "\n".join("    - " + x.detaliu for x in m), PRODUCTIE_DBNAME),
            coduri=[x.cod for x in m], cale_remediu=CALE_TEST_ENV)
    return True
