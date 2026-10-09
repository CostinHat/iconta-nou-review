# -*- coding: utf-8 -*-
"""core/migrare_metoda_stoc.py — `firma_profil.metoda_stoc` (comanda Costin 06.10.2026 §6.3): global_valoric |
cantitativ_valoric | NULL (nedeclarată — fără implicit tăcut). Sursa UNICĂ a DDL-ului (mirror în tenant_template.sql). Idempotent.
Tenanți NOI prin template; EXISTENȚI prin `python3 -m core.migrare_metoda_stoc`. Nicio valoare nu se completează din oficiu.
"""
from core import db

DDL = ('ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS metoda_stoc text '
       "CHECK (metoda_stoc IN ('global_valoric', 'cantitativ_valoric'));")


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema=%s AND table_name='firma_profil' "
                    "AND column_name='metoda_stoc'", (schema,))
        return cur.fetchone() is not None


def scheme_cu_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables WHERE table_name='firma_profil' ORDER BY 1")
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
        print("migrare metoda_stoc: %d/%d ok" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
