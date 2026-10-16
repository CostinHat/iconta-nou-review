"""
core/migrare_extras_miscare.py — `extras_linii.cont_extras` și `extras_linii.referinta`: contul extrasului și referința mișcării.

Comanda Costin 16.10.2026, „Lotul 6, comanda 1” pct.1a (277), verbatim în DECIZII: „o linie e duplicat numai dacă aceeași mișcare (dată,
sumă, sens, referință/descriere, cont) există deja.” Până acum duplicatul se hotăra pe hash-ul fișierului întreg (`extras_import`, C5) și
nici contul (MT940 `:25:`), nici referința (`:61:`) nu se păstrau. Coloanele rămân NULL la liniile vechi și la extrasele în tabel (xls / xlsx
/ csv), care nu le au; cheia le compară cu `IS NOT DISTINCT FROM` (un cont necunoscut nu se socotește același cu unul cunoscut).
Sursa UNICĂ = mirror în tenant_template.sql. Idempotent (ADD COLUMN IF NOT EXISTS). Se aplică: firmele NOI prin template; cele EXISTENTE
prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_extras_miscare.py`.
"""
from core import db

_DDL = [
    'ALTER TABLE "{s}".extras_linii ADD COLUMN IF NOT EXISTS cont_extras character varying(34);',
    'ALTER TABLE "{s}".extras_linii ADD COLUMN IF NOT EXISTS referinta character varying(100);',
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 2 FROM information_schema.columns WHERE table_schema=%s AND table_name='extras_linii' "
                    "AND column_name IN ('cont_extras', 'referinta')", (schema,))
        return bool(cur.fetchone()[0])


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
    print("migrare_extras_miscare: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
