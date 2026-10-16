"""
core/migrare_casa_avans.py — `casa_operatiuni.avans`: partea unei încasări (plăți) în numerar care depășește facturile alese.

Comanda Costin 16.10.2026, „Lotul 6, comanda 1” pct.3b (278), verbatim în DECIZII: „Suma care depășește facturile deschise ale clientului se
semnalează ca avans de la client; verifici la sursă tratamentul contabil și de TVA al avansului și îl aplici.” Dispoziția legată de facturi
(`casa_api.adauga`, `facturi`) se împarte într-o operațiune pe factură, cu nota legată de ea (`inregistrari.factura_id`), plus una marcată
`avans` pentru rest (5311 = 4111 / 401 = 5311, nelegată, până la factura de avans: CF art.319 alin.(16), exigibilitatea TVA la încasare:
CF art.282 alin.(2) lit.b). Plus: nota chitanțelor neanulate de dinainte primește factura chitanței (date, idempotent: numai unde lipsește).
Sursa UNICĂ = mirror în tenant_template.sql. Idempotent (ADD COLUMN IF NOT EXISTS). Se aplică: firmele NOI prin
template; cele EXISTENTE prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_casa_avans.py`.
"""
from core import db

_DDL = [
    'ALTER TABLE "{s}".casa_operatiuni ADD COLUMN IF NOT EXISTS avans boolean NOT NULL DEFAULT false;',
    # Chitanțele emise / primite pe o factură, de dinainte: nota lor n-avea `factura_id`, deci factura rămânea „deschisă” la
    # reconcilierea bancară (`reconciliere_api.facturi_deschise`). Nota fiecărei chitanțe neanulate primește factura chitanței.
    'UPDATE "{s}".inregistrari i SET factura_id = c.factura_id FROM "{s}".chitante c '
    'WHERE c.inregistrare_id = i.id AND c.factura_id IS NOT NULL AND NOT c.anulata AND i.factura_id IS NULL;',
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 1 FROM information_schema.columns WHERE table_schema=%s AND table_name='casa_operatiuni' "
                    "AND column_name = 'avans'", (schema,))
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
    print("migrare_casa_avans: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
