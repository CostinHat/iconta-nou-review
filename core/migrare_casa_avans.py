"""
core/migrare_casa_avans.py — `casa_operatiuni.avans`: partea unei încasări (plăți) în numerar care depășește facturile alese.

Comanda Costin 16.10.2026, „Lotul 6, comanda 1” pct.3b (278), verbatim în DECIZII: „Suma care depășește facturile deschise ale clientului se
semnalează ca avans de la client; verifici la sursă tratamentul contabil și de TVA al avansului și îl aplici.” Dispoziția legată de facturi
(`casa_api.adauga`, `facturi`) se împarte într-o operațiune pe factură, cu nota legată de ea (`inregistrari.factura_id`), plus una marcată
`avans` pentru rest (5311 = 4111 / 401 = 5311, nelegată, până la factura de avans: CF art.319 alin.(16), exigibilitatea TVA la încasare:
CF art.282 alin.(2) lit.b).
[17.10.2026, poarta 1 a lotului 6] Forma dintâi mai punea `factura_id` pe nota chitanțelor de dinainte (un UPDATE pe `inregistrari`): pe copia
producției a picat la regula notelor validate (`regula_nota`: o notă validată nu se mai modifică, OMFP 1802/2014 pct.69) și ar fi atins
notele validate ale firmelor. Scos: migrarea e numai DDL, iar legătura chitanță -> factură se CITEȘTE din `chitante` la reconciliere
(`reconciliere_api.facturi_deschise`). Gard: `core/test_migrari_registru.py::test_nicio_migrare_noua_nu_scrie_in_notele_contabile`.
Sursa UNICĂ = mirror în tenant_template.sql. Idempotent (ADD COLUMN IF NOT EXISTS). Se aplică: firmele NOI prin
template; cele EXISTENTE prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_casa_avans.py`.
"""
from core import db

_DDL = [
    'ALTER TABLE "{s}".casa_operatiuni ADD COLUMN IF NOT EXISTS avans boolean NOT NULL DEFAULT false;',
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
