# -*- coding: utf-8 -*-
"""core/migrare_nir_cost.py — NIR-ul la firma cu stocul la COST (lotul 07.10 B, comanda Costin C10/C11).

  · `nir_linii.pret_vanzare` acceptă NULL: la cost (cantitativ-valoric) prețul de raft nu se cere și nu se verifică — până azi
    coloana era NOT NULL, iar ecranul trimitea golul ca 0;
  · `nir_linii.articol_id`: linia NIR e un articol ales din listă sau creat explicit (C11c) — legătura se păstrează;
  · `nir_linii.cota_tva` fără implicit (avea o cotă implicită în schemă, pe care n-o alesese nimeni; NIR-ul o cere pe fiecare linie);
  · `nir.metoda_stoc`: metoda după care s-a înregistrat NIR-ul (cost / preț de vânzare), arătată când se deschide.
Sursa UNICĂ a DDL-ului (mirror în tenant_template.sql). Idempotentă. `python3 -m core.migrare_nir_cost`.
"""
from core import db

DDL = [
    'ALTER TABLE "{s}".nir_linii ALTER COLUMN pret_vanzare DROP NOT NULL;',
    'ALTER TABLE "{s}".nir_linii ALTER COLUMN cota_tva DROP DEFAULT;',
    'ALTER TABLE "{s}".nir_linii ADD COLUMN IF NOT EXISTS articol_id integer;',
    'ALTER TABLE "{s}".nir ADD COLUMN IF NOT EXISTS metoda_stoc text;',
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='nir_linii'", (schema,))
        if not cur.fetchone():
            return False
        for d in DDL:
            cur.execute(d.format(s=schema))
    return True


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND ((table_name='nir_linii' AND "
                    "column_name='pret_vanzare' AND is_nullable='YES') OR (table_name='nir_linii' AND column_name='articol_id') "
                    "OR (table_name='nir' AND column_name='metoda_stoc'))", (schema,))
        return cur.fetchone()[0] == 3


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables WHERE table_name='nir_linii' ORDER BY 1")
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
        print("migrare nir_cost: %d/%d ok" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
