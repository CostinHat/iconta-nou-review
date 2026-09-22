# -*- coding: utf-8 -*-
"""core/migrare_d301_op_factura.py — leaga operatiunea D301 de factura care a produs-o.

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Adauga `factura_id integer` (nullable) pe
d301_operatiuni: operatiunile scrise de `achizitie_ic` (intrarea unica a achizitiei IC, DECIZII 66)
poarta id-ul facturii. Consecinta: D390 ia acea achizitie din FACTURA (nu din op — calea D390-din-op
filtreaza factura_id IS NULL), iar D301 o ia din op (citeste toate operatiunile). Fara dubla numarare
in D390. Operatiunile introduse manual pe ecranul D301 raman cu factura_id=NULL (alimenteaza D390).
Nullable + idempotent (ADD COLUMN IF NOT EXISTS). Tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_d301_op_factura`."""
from core import db

DDL = 'ALTER TABLE "{s}".d301_operatiuni ADD COLUMN IF NOT EXISTS factura_id integer;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='d301_operatiuni' AND column_name='factura_id'", (schema,))
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
            with db.get_conn() as conn:
                aplica(conn, s)
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1; print("  OK  %s" % s)
                else:
                    esec.append(s); print("  ESEC (verificare)  %s" % s)
        except Exception as e:
            esec.append(s); print("  ESEC %s: %s" % (s, e))
    print("d301_op_factura: %d ok, %d esec" % (ok, len(esec)))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
