"""
core/migrare_balanta_rulaje_an.py — balanța de deschidere cu soldurile inițiale ale anului și rulajele lui (deficiența 425, comanda Costin
10.1, verbatim în DECIZII „Comanda 10.1”): „Când fișierul are soldurile inițiale ale anului și rulajele, ele intră ca sold inițial și
sume precedente, cu toate conturile care au rulaj.” `solduri_initiale.si_an_debit` / `si_an_credit` = soldul la 1 ianuarie al anului
datei de referință; `rulaj_an_debit` / `rulaj_an_credit` = rulajele cumulate de la 1 ianuarie până la data de referință, FĂRĂ soldul
inițial (sumele precedente ale balanței SAGA minus soldul inițial). NULL = fișierul avea numai solduri finale (comportamentul de până
acum). `sold_debitor` / `sold_creditor` rămân soldurile finale.

Coloane / tabele noi, goale: datele existente nu se ating. Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent
(IF NOT EXISTS). Firmele existente: `python -m core.migrari_registru ruleaza [--productie] core/migrare_balanta_rulaje_an.py`.
"""
from core import db

_DDL = [
    "ALTER TABLE \"{s}\".solduri_initiale ADD COLUMN IF NOT EXISTS si_an_debit numeric(15,2);",
    "ALTER TABLE \"{s}\".solduri_initiale ADD COLUMN IF NOT EXISTS si_an_credit numeric(15,2);",
    "ALTER TABLE \"{s}\".solduri_initiale ADD COLUMN IF NOT EXISTS rulaj_an_debit numeric(15,2);",
    "ALTER TABLE \"{s}\".solduri_initiale ADD COLUMN IF NOT EXISTS rulaj_an_credit numeric(15,2);",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='solduri_initiale' "
                    "AND column_name IN ('si_an_debit', 'si_an_credit', 'rulaj_an_debit', 'rulaj_an_credit')", (schema,))
        return cur.fetchone()[0] == 4


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
    print("migrare_balanta_rulaje_an: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
