"""
core/migrare_partener_linie.py — `inregistrari_linii.partener_cui` / `partener_nume` pe fiecare firmă (deficiența 381, comanda Costin 8.2,
18.10.2026, verbatim în DECIZII „Comanda 8.2”: „Nota pe 401/4111 cere partenerul la introducere, iar D406 semnalează liniile de terți fără
partener.”).

Coloane noi, goale: notele existente rămân cum sunt (partenerul lor vine, ca până acum, din factura legată sau din operațiunea de casă).
Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent (ADD COLUMN IF NOT EXISTS). Se aplică: firmele NOI prin template;
cele EXISTENTE prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_partener_linie.py`.
"""
from core import db

_DDL = [
    "ALTER TABLE \"{s}\".inregistrari_linii ADD COLUMN IF NOT EXISTS partener_cui text;",
    "ALTER TABLE \"{s}\".inregistrari_linii ADD COLUMN IF NOT EXISTS partener_nume text;",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='inregistrari_linii' "
                    "AND column_name IN ('partener_cui', 'partener_nume')", (schema,))
        return cur.fetchone()[0] == 2


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
    print("migrare_partener_linie: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
