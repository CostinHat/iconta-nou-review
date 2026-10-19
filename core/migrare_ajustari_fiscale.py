"""
core/migrare_ajustari_fiscale.py — tabelul `ajustari_fiscale` pe fiecare firmă (deficiența 378, comanda Costin 8.2, 18.10.2026, verbatim în
DECIZII „Comanda 8.2”: „D100 trimestrial pornește de la rezultatul fiscal cumulat din Registrul de evidență fiscală [...]”).

Ajustările fiscale ale rezultatului, pe rândul oficial D101, scrise de contabil pe trimestrul lor: sursa unică pentru D100 (cumulat de la
01.01) și D101 (`core/ajustari_fiscale.py`). Tabel nou, gol — nicio dată existentă nu se atinge. Sursa UNICĂ a structurii = mirror în
tenant_template.sql. Idempotent (IF NOT EXISTS). Se aplică: firmele NOI prin template; cele EXISTENTE prin
`python -m core.migrari_registru ruleaza [--productie] core/migrare_ajustari_fiscale.py`.
"""
from core import db

_DDL = [
    "CREATE TABLE IF NOT EXISTS \"{s}\".ajustari_fiscale (id serial PRIMARY KEY, an integer NOT NULL, "
    "trim smallint CHECK (trim BETWEEN 1 AND 4), rand text NOT NULL, suma numeric(15,2) NOT NULL CHECK (suma > 0), descriere text, "
    "document text, creat_de integer, creat_la timestamptz NOT NULL DEFAULT now());",
    "CREATE INDEX IF NOT EXISTS ajustari_fiscale_an ON \"{s}\".ajustari_fiscale (an);",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='ajustari_fiscale'", (schema,))
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
    print("migrare_ajustari_fiscale: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
