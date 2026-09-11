# -*- coding: utf-8 -*-
"""core/sonda_scrieri.py — cine scrie in `salariu_istoric`, si daca scrierea a RAMAS.

Ceruta de arhitect (11.09.2026, §3) pentru incidentul randului 53. Intrebarea nu e «s-a scris?» —
asta se vede in tabel —, ci *care test, pe ce sesiune, prin ce comanda, si daca tranzactia a fost
comisa*. Un `INSERT` urmat de `rollback` e nevinovat; acelasi `INSERT` comis e producatorul cautat.

**De ce un declansator in PostgreSQL, si nu o imbracare a lui psycopg2.** Prima forma a modulului
asta imbraca `psycopg2.extensions.cursor` ca sa prinda `execute`. N-ar fi prins nimic: aplicatia
cere explicit `RealDictCursor`, deci `cursor_factory`-ul meu nu s-ar fi aplicat niciodata, iar
sonda ar fi raportat *zero scrieri* pe o rulare plina de scrieri — adica exact felul de verde care
nu apara nimic. Declansatorul nu poate fi ocolit: orice cale, orice biblioteca, orice conexiune.

**Si, mai important, discriminatorul vine pe gratis.** Randul scris de declansator traieste in
ACEEASI tranzactie cu scrierea pe care o observa. Daca testul face `rollback`, dispare si el. Daca
randul a supravietuit in jurnal, **scrierea a fost comisa** — nu se mai deduce nimic din capete de
tranzactie corelate pe id-uri de obiect Python.

Identitatea testului vine prin `application_name`, pus de `pytest` la fiecare faza (vezi
`instaleaza_carlig_pytest`). PostgreSQL il da inapoi in `current_setting('application_name')`.

**Numai in mediul izolat.** `instaleaza` refuza sa creeze declansatorul daca `core.mediu_test`
spune ca baza nu e dovedit de test.
"""
from __future__ import annotations

import os

MODUL = "sonda_scrieri"

#: Tabelele urmarite. `salariu_istoric` e cel din incident; `state_plata` e vecinul care a lasat
#: exemplarele in aceeasi noapte.
TABELE = ("salariu_istoric", "state_plata")

JURNAL = "sonda_scrieri_jurnal"

ACTIVA = os.environ.get("ICONTA_SONDA_SCRIERI") == "1"


def sql_jurnal(schema):
    """Tabela-jurnal, in schema urmarita."""
    return (
        'CREATE TABLE IF NOT EXISTS "%s".%s ('
        "  id           bigserial PRIMARY KEY,"
        "  tabela       text        NOT NULL,"
        "  operatia     text        NOT NULL,"
        "  rand_nou     jsonb,"
        "  rand_vechi   jsonb,"
        "  testul       text,"          # application_name, pus de carligul pytest
        "  utilizator   text        NOT NULL,"
        "  baza         text        NOT NULL,"
        "  schema_tinta text        NOT NULL,"
        "  backend_pid  integer     NOT NULL,"
        "  xid          bigint,"
        "  comanda      text,"
        "  momentul     timestamptz NOT NULL DEFAULT clock_timestamp()"
        ")" % (schema, JURNAL))


def sql_functie(schema):
    """Functia declansatorului. `txid_current()` e sigur AICI: tranzactia a scris deja, deci are
    oricum un xid atribuit — nu-l fortam noi."""
    return (
        'CREATE OR REPLACE FUNCTION "%s".%s_f() RETURNS trigger AS $sonda$\n'
        "BEGIN\n"
        '  INSERT INTO "%s".%s (tabela, operatia, rand_nou, rand_vechi, testul, utilizator,\n'
        "                       baza, schema_tinta, backend_pid, xid, comanda)\n"
        "  VALUES (TG_TABLE_NAME, TG_OP,\n"
        "          CASE WHEN TG_OP <> 'DELETE' THEN to_jsonb(NEW) END,\n"
        "          CASE WHEN TG_OP <> 'INSERT' THEN to_jsonb(OLD) END,\n"
        "          current_setting('application_name', true),\n"
        "          current_user, current_database(), TG_TABLE_SCHEMA,\n"
        "          pg_backend_pid(), txid_current(), current_query());\n"
        "  RETURN NULL;\n"
        "END;\n"
        "$sonda$ LANGUAGE plpgsql;" % (schema, JURNAL, schema, JURNAL))


def sql_declansator(schema, tabela):
    return (
        'DROP TRIGGER IF EXISTS %s_t ON "%s".%s;\n'
        'CREATE TRIGGER %s_t AFTER INSERT OR UPDATE OR DELETE ON "%s".%s\n'
        '  FOR EACH ROW EXECUTE FUNCTION "%s".%s_f();'
        % (JURNAL, schema, tabela, JURNAL, schema, tabela, schema, JURNAL))


def instaleaza(conn, scheme=None):
    """Monteaza sonda pe schemele date (implicit: toate `tenant_%`). Intoarce ce a montat.

    REFUZA daca mediul nu e dovedit de test — o sonda care scrie un jurnal in productie ar adauga
    exact felul de reziduu pe care il investigheaza.
    """
    from core import mediu_test as mt
    mt.verifica(os.environ)

    montate = []
    with conn.cursor() as cur:
        if scheme is None:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        " WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY 1")
            scheme = [(r["schema_name"] if isinstance(r, dict) else r[0]) for r in cur.fetchall()]
        for schema in scheme:
            cur.execute(sql_jurnal(schema))
            cur.execute(sql_functie(schema))
            for tabela in TABELE:
                cur.execute("SELECT to_regclass(%s)", ("%s.%s" % (schema, tabela),))
                r = cur.fetchone()
                exista = (r["to_regclass"] if isinstance(r, dict) else r[0]) is not None
                if exista:
                    cur.execute(sql_declansator(schema, tabela))
                    montate.append("%s.%s" % (schema, tabela))
    conn.commit()
    return montate


def citeste(conn, schema):
    """Inregistrarile ramase — adica scrierile COMISE. Cele date inapoi au disparut odata cu ele."""
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM "%s".%s ORDER BY id' % (schema, JURNAL))
        return [dict(r) for r in cur.fetchall()]


def instaleaza_carlig_pytest():
    """Codul care trebuie pus in `conftest.py` ca fiecare sesiune sa-si spuna testul.

    Se intoarce ca TEXT, nu se executa: `conftest.py` e fisier normativ, deci se modifica vazut,
    nu prin efect secundar al unui import.
    """
    return (
        "def pytest_runtest_setup(item):\n"
        "    # identitatea testului ajunge la PostgreSQL prin application_name, de unde o citeste\n"
        "    # declansatorul sondei. Fara asta, jurnalul ar spune CE s-a scris, dar nu de catre cine.\n"
        "    import os\n"
        "    os.environ['PGAPPNAME'] = item.nodeid[:63]\n")


def raport(inregistrari):
    """Rezumat: cate scrieri comise, pe ce tabele, din ce teste. Ordonat descrescator."""
    dupa_test = {}
    for inr in inregistrari:
        cheie = (inr.get("testul") or "(necunoscut)", inr.get("tabela"), inr.get("operatia"))
        dupa_test[cheie] = dupa_test.get(cheie, 0) + 1
    return sorted(dupa_test.items(), key=lambda kv: -kv[1])
