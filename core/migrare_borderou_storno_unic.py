"""
core/migrare_borderou_storno_unic.py — un borderou de achiziție se stornează o singură dată (lotul 11, decizia Costin 10.3 pct.4, verbatim:
„Borderoul se corectează prin stornare, ca factura.”).

Stornarea borderoului (`uc_tenants.borderou_storneaza`) scrie un document de stornare legat (`facturi.storno_din_id`, tip `borderou`,
cantitățile și valoarea cu minus) și nota inversă. Aplicația refuză a doua stornare și stornarea unei stornări (CF art.330 alin.(1)
lit.b), ca la factură — lotul 10, C74); indexul unic o face IMPOSIBILĂ și la două cereri simultane.

Datele existente NU se schimbă (până azi borderoul nu se putea storna: `facturi_api.storneaza` primea numai facturi emise), deci nu există
dubluri. Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent (IF NOT EXISTS).
Firmele existente: `python -m core.migrari_registru ruleaza [--productie] core/migrare_borderou_storno_unic.py`.
"""
from core import db

_INDEX = ("CREATE UNIQUE INDEX IF NOT EXISTS facturi_borderou_storno_uniq ON \"{s}\".facturi (storno_din_id) "
          "WHERE tip = 'borderou' AND storno_din_id IS NOT NULL;")


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(_INDEX.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM pg_indexes WHERE schemaname = %s AND indexname = 'facturi_borderou_storno_uniq'", (schema,))
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
                conn.commit()
            ok += 1
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_borderou_storno_unic: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
