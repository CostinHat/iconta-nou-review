# -*- coding: utf-8 -*-
"""core/migrare_d301_confirmat.py - confirmarea ca o operatiune D301 tip 4 NU e serviciu IC.

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Adauga `d390_confirmat_local` (boolean, default false)
pe d301_operatiuni. Rezolva fals-pozitivul benign al indiciului de mis-clasificare: o operatiune tip 4 (art.307
alin.(3)(5)(6), taxare inversa locala - nu intra in D390) cu cod TVA furnizor primeste indiciul "poate e serviciu
IC -> tip 5". Pentru gaz/energie/bunuri (alin.3/5) de la furnizor INregistrat, indiciul e un fals-pozitiv:
contabilul apasa "confirma (nu e serviciu)" -> d390_confirmat_local=true -> indiciul se stinge pentru acea
operatiune. Idempotent (ADD COLUMN IF NOT EXISTS). Se aplica: tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_d301_confirmat`. Decizia Costin 18.08.2026."""
from core import db

DDL = 'ALTER TABLE "{s}".d301_operatiuni ADD COLUMN IF NOT EXISTS d390_confirmat_local boolean DEFAULT false;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='d301_operatiuni' AND column_name='d390_confirmat_local'", (schema,))
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
                    ok += 1
                else:
                    esec.append(s)
        except Exception as e:
            esec.append("%s (%s)" % (s, e))
    print("migrare_d301_confirmat: %d/%d OK" % (ok, len(scheme)))
    if esec:
        print("ESEC:", esec)
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
