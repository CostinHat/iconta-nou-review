"""
core/migrare_cont_linie_primita.py — `factura_linii.cont_cheltuiala`: contul pe care se contează linia unei facturi PRIMITE (deficiența
418b, comanda Costin 9.3, 19.10.2026, verbatim în DECIZII „Comanda 9.3”: „Un singur cont pentru toată factura: liniile de natură diferită
(marfă + carte de birou) merg toate pe 371. Fiecare linie trebuie să se poată conta pe contul ei.”).

Coloană nouă, goală: liniile existente rămân pe contul facturii (`efactura_primite.cont_cheltuiala`), exact ca până acum.
Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent (ADD COLUMN IF NOT EXISTS). Se aplică: firmele NOI prin template;
cele EXISTENTE prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_cont_linie_primita.py`.
"""
from core import db

_DDL = [
    "ALTER TABLE \"{s}\".factura_linii ADD COLUMN IF NOT EXISTS cont_cheltuiala text;",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='factura_linii' "
                    "AND column_name = 'cont_cheltuiala'", (schema,))
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
    print("migrare_cont_linie_primita: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
