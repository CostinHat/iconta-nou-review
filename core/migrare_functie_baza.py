# -*- coding: utf-8 -*-
"""core/migrare_functie_baza.py — coloana `functie_baza` pe salariati (CF art.77 alin.(1)).

Deducerea personala se acorda NUMAI la locul unde e functia de baza. Default TRUE = cazul obisnuit
(unic angajator); se seteaza FALSE cand salariatul si-a declarat functia de baza la alt angajator.
Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent (ADD COLUMN IF NOT EXISTS).
Tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_functie_baza`.
"""
from core import db

DDL = 'ALTER TABLE "{s}".salariati ADD COLUMN IF NOT EXISTS functie_baza boolean NOT NULL DEFAULT true;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='salariati' AND column_name='functie_baza'", (schema,))
        return cur.fetchone()[0] == 1


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
        ok, esec = 0, []
        for s in scheme:
            try:
                aplica(conn, s)
                conn.commit()
                ok += 1 if verifica(conn, s) else 0
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, str(e)))
        print("migrare functie_baza: %d/%d ok" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
