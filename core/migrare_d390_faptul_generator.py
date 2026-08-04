# -*- coding: utf-8 -*-
"""core/migrare_d390_faptul_generator.py — camp OPTIONAL data_faptului_generator pe facturi (D390, art.284).

Art.284 CF: exigibilitatea operatiunilor IC intervine la data emiterii facturii, dar nu mai tarziu de a 15-a zi
a lunii urmatoare celei in care a avut loc faptul generator (ziua 15). Cand data_faptului_generator e completata,
D390 incadreaza operatiunea pe exigibilitate = MIN(data_emitere, ziua 15 a lunii urmatoare faptului). Camp NULL
(default) -> comportamentul actual (incadrare pe data_emitere) NESCHIMBAT (backward-compat).

Sursa UNICA a DDL-ului = mirror in tenant_template.sql. Idempotent (ADD COLUMN IF NOT EXISTS).
Se aplica: tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_d390_faptul_generator`.
"""
from core import db

_DDL = [
    'ALTER TABLE "{s}".facturi ADD COLUMN IF NOT EXISTS data_faptului_generator date;',
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='facturi' AND column_name='data_faptului_generator'", (schema,))
        return cur.fetchone() is not None


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
            with db.get_conn() as conn:
                aplica(conn, s)
                conn.commit()
            ok += 1
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_d390_faptul_generator: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))


if __name__ == "__main__":
    _main()
