# -*- coding: utf-8 -*-
"""core/migrare_cont_venit_linie.py - contul de venit stabilit PE LINIE de factura.

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Adauga `cont_venit text` (nullable)
pe factura_linii: contul de venit al fiecarei linii, dedus din denumire (marfa->707,
produse->701, serviciu->704, OMFP 1802/2014) si editabil de contabil. Inainte contul de
venit era unic pe firma (COALESCE(cont_venit_implicit,'707')) si ignora ce contine linia,
asa ca o factura de servicii primea 707 in loc de 704. La contabilizare nota se grupeaza
acum pe (cont_venit, cota) -> o factura mixta produce mai multe conturi de venit.
Nullable intentionat: linie fara cont -> contabilizarea decide (cont_venit_implicit / legacy 707).
Idempotent (ADD COLUMN IF NOT EXISTS). Se aplica: tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_cont_venit_linie`. Obiectiv #11 (auto din denumire + confirmabil)."""
from core import db

DDL = 'ALTER TABLE "{s}".factura_linii ADD COLUMN IF NOT EXISTS cont_venit text;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='factura_linii' AND column_name='cont_venit'", (schema,))
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
    print("cont_venit_linie: %d ok, %d esec" % (ok, len(esec)))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
