"""
core/migrare_avans_nir_ajustare_nota.py — două legături noi, numai DDL (lotul 9, închiderea lotului, deciziile Costin 19.10.2026, verbatim în
DECIZII „Închiderea lotului 9”):

  · `casa_operatiuni.nir_id` (405, „Avans 409x = 5311”): plata în numerar a unui NIR a cărui factură n-a sosit (marfa pe 408) e avans acordat
    furnizorului, 4091 = 5311 (`casa_api.adauga`, `niruri`), legat de NIR. Din legătură se știe cât s-a plătit din NIR (NIR-ul plătit nu se
    mai oferă) și cât se compensează la sosirea facturii (401 = 4091, `casa_api.compensare_avans_nir`).
  · `ajustari_fiscale.inregistrare_id` (404, „Da, automat”): ajustarea fiscală scrisă AUTOMAT din lipsa neimputabilă de la inventar
    (`stocuri_cv_api.inventar`, CF art.25 alin.(4) lit.c) e legată de nota inventarului: intră în D100 / D101 numai cu nota validată
    (`repo_ajustari_fiscale.cumulat`), iar ștergerea notei o șterge și pe ea (ON DELETE CASCADE) — nu rămâne orfană.

Coloane noi, goale — nicio dată existentă nu se atinge. Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent (ADD COLUMN IF NOT
EXISTS). Se aplică: firmele NOI prin template; cele EXISTENTE prin
`python -m core.migrari_registru ruleaza [--productie] core/migrare_avans_nir_ajustare_nota.py` (după `core/migrare_ajustari_fiscale.py`).
"""
from core import db

_DDL = [
    'ALTER TABLE "{s}".casa_operatiuni ADD COLUMN IF NOT EXISTS nir_id integer REFERENCES "{s}".nir(id);',
    'ALTER TABLE "{s}".ajustari_fiscale ADD COLUMN IF NOT EXISTS inregistrare_id integer REFERENCES "{s}".inregistrari(id) ON DELETE CASCADE;',
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 2 FROM information_schema.columns WHERE table_schema=%s AND ((table_name='casa_operatiuni' "
                    "AND column_name='nir_id') OR (table_name='ajustari_fiscale' AND column_name='inregistrare_id'))", (schema,))
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
    print("migrare_avans_nir_ajustare_nota: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
