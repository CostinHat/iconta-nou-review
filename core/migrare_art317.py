# -*- coding: utf-8 -*-
"""core/migrare_art317.py — inregistrarea speciala in scopuri de TVA (art. 317 CF, fost 153^1).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Adauga `inreg_art317` boolean pe firma_profil:
decide pers_inreg in D301 (1 vs 2, core/d301.py) si face verdictul D390 la neplatitorul cu operatiuni IC
SATISFIABIL (inainte era permanent-gri "nu avem inregistrata calitatea art.317", fara camp de completat).
Idempotent (ADD COLUMN IF NOT EXISTS, DEFAULT false NOT NULL). Se aplica: tenanti NOI prin template;
EXISTENTI prin `python3 -m core.migrare_art317`. Plimbarea vizuala 14.08.2026, constatarea 4."""
from core import db

DDL = 'ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS inreg_art317 boolean DEFAULT false NOT NULL;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='firma_profil' AND column_name='inreg_art317'", (schema,))
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
    print("art317: %d ok, %d esec" % (ok, len(esec)))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
