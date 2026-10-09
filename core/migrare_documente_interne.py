# -*- coding: utf-8 -*-
"""core/migrare_documente_interne.py — contorul documentelor interne pe tip și an (comanda Costin 06.10.2026 §6.2).

Sursa UNICĂ a DDL-ului (mirror în tenant_template.sql). Idempotent. Pe ORICE schemă care are `inregistrari`.
Tenanți NOI prin template; EXISTENȚI prin `python3 -m core.migrare_documente_interne`. Notele vechi nu se ating.
"""
from core import db

DDL = ('CREATE TABLE IF NOT EXISTS "{s}".documente_interne_contor ('
       ' tip text NOT NULL,'
       ' an integer NOT NULL,'
       ' ultim integer NOT NULL,'
       ' PRIMARY KEY (tip, an));')


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ('"%s".documente_interne_contor' % schema,))
        return cur.fetchone()[0] is not None


def scheme_cu_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables "
                    "WHERE table_name='inregistrari' ORDER BY 1")
        return [r[0] for r in cur.fetchall()]


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        scheme = scheme_cu_tabela(conn)
        ok, esec = 0, []
        for s in scheme:
            try:
                aplica(conn, s)
                conn.commit()
                ok += 1 if verifica(conn, s) else 0
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, str(e)))
        print("migrare documente_interne_contor: %d/%d ok" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
