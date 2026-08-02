"""
core/migrare_tichet_cultural.py — tichete culturale in beneficii_lunare (Legea 165/2018 cap.V).

Extinde CHECK-urile tabelei beneficii_lunare: tip accepta 'cultural' (pe langa 'vacanta'/'cadou');
eveniment accepta 'ocazional' (pe langa gol/cadou), pentru tichetul cultural pe eveniment (art.21(1)).

Sursa UNICA a DDL-ului = mirror in tenant_template.sql. Idempotent (DROP CONSTRAINT IF EXISTS + ADD).
Se aplica: tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_tichet_cultural`.
"""
from core import db

_DDL = [
    'ALTER TABLE "{s}".beneficii_lunare DROP CONSTRAINT IF EXISTS beneficii_lunare_tip_ck;',
    "ALTER TABLE \"{s}\".beneficii_lunare ADD CONSTRAINT beneficii_lunare_tip_ck "
    "CHECK (tip IN ('vacanta','cadou','cultural'));",
    'ALTER TABLE "{s}".beneficii_lunare DROP CONSTRAINT IF EXISTS beneficii_lunare_eveniment_ck;',
    "ALTER TABLE \"{s}\".beneficii_lunare ADD CONSTRAINT beneficii_lunare_eveniment_ck "
    "CHECK (eveniment IN ('','paste','craciun','8martie','1iunie','altul','ocazional'));",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT pg_get_constraintdef(c.oid) FROM pg_constraint c "
            "JOIN pg_class t ON t.oid = c.conrelid "
            "JOIN pg_namespace n ON n.oid = t.relnamespace "
            "WHERE n.nspname=%s AND t.relname='beneficii_lunare' AND c.conname='beneficii_lunare_tip_ck'",
            (schema,))
        row = cur.fetchone()
        return bool(row) and "cultural" in row[0]


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
    print("migrare_tichet_cultural: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))


if __name__ == "__main__":
    _main()
