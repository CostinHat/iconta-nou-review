# -*- coding: utf-8 -*-
"""core/migrare_extras_import.py — [C5] tabel `extras_import`: registrul importurilor de extras bancar.

DE CE. Reimportul aceluiasi extras (dublu-click / raspuns pierdut dupa commit) insera TOATE liniile a
doua oara in `extras_linii` (fara cheie de dedup) -> contarile pe 5121 dublate. C5 din auditul
independent 2026-09-17. Fix (decizia Costin 20.09, varianta A): idempotenta la nivel de FISIER, pe
hash de continut. Un tabel dedicat (nu o coloana pe extras_linii): registrul importurilor e o entitate
proprie (un import = un fisier, N linii), iar cheia UNIQUE pe hash e gardul care face reimportul un
no-op de INSERT chiar sub cursa dublu-click.

DE CE HASH DE FISIER, nu cheie de continut per linie: parserul CSV da doar (data, detalii, suma), fara
referinta bancara unica. O cheie de continut ar arunca tacit doua tranzactii REALE identice in acelasi
extras (ex. doua comisioane egale in aceeasi zi). Hash-ul de fisier distinge re-submit al ACELUIASI
fisier (de eliminat) de linii legitim identice in acelasi fisier (de pastrat).

Sursa UNICA a DDL-ului = mirror in tenant_template.sql (CREATE TABLE extras_import). Idempotent
(CREATE TABLE IF NOT EXISTS). Se aplica: tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_extras_import`.
"""
from core import db

_DDL = """
CREATE TABLE IF NOT EXISTS "{s}".extras_import (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fisier_hash text NOT NULL,
    fisier_nume character varying(255),
    nr_linii integer NOT NULL DEFAULT 0,
    creat_la timestamp with time zone NOT NULL DEFAULT now(),
    CONSTRAINT extras_import_hash_uniq UNIQUE (fisier_hash)
);
"""
# OWNER: in productie tabelul apartine iconta_user (ca restul). Best-effort: pe baza de TEST userul
# poate sa nu poata SET ROLE iconta_user, iar owner-ul nu conteaza pentru conformitatea de schema
# (auditul compara coloane/tipuri, nu owner). Deci CREATE e obligatoriu, OWNER e tolerant.
_DDL_OWNER = 'ALTER TABLE "{s}".extras_import OWNER TO iconta_user;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    import psycopg2 as _pg
    with conn.cursor() as cur:
        cur.execute(_DDL.format(s=schema))
    conn.commit()  # tabelul e persistat INAINTE de a incerca owner-ul (altfel rollback l-ar sterge)
    try:
        with conn.cursor() as cur:
            cur.execute(_DDL_OWNER.format(s=schema))
        conn.commit()
    except _pg.errors.InsufficientPrivilege:
        conn.rollback()  # doar owner-ul cade; tabelul ramane (deja comis)


def toate_schemele(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM information_schema.schemata "
                    "WHERE schema_name LIKE 'tenant_%' ORDER BY 1")
        return [r[0] for r in cur.fetchall()]


def main():
    db.init_pool()
    with db.get_conn() as conn:
        scheme = toate_schemele(conn)
        for s in scheme:
            aplica(conn, s)
        conn.commit()
        print("extras_import aplicat pe %d scheme: %s" % (len(scheme), ", ".join(scheme)))


if __name__ == "__main__":
    main()
