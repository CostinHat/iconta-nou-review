"""
core/migrare_categorie_tva_linie.py — `factura_linii.categorie_tva`: categoria de TVA a liniei cu cota 0% (274b).

Decizia Costin 16.10.2026 (răspunsul la raportul lotului 6 pct.1, verbatim în DECIZII): „Categoria e obligatorie pe orice linie cu 0%”.
Valorile = `core/categorii_tva.VALORI` (sursa unică: codul UBL, motivul, rândul D300). NULL = linie taxabilă, sau factură de dinainte
(D300 o semnalează ca până acum: „nu se clasifică automat”). Nicio valoare nu se deduce pentru facturile vechi — natura scutirii nu e pe
ele. Sursa UNICĂ = mirror în tenant_template.sql. Idempotent. Se aplică: firmele NOI prin template; cele EXISTENTE prin
`python -m core.migrari_registru ruleaza [--productie] core/migrare_categorie_tva_linie.py`.
"""
from core import db

#: valorile admise, SCRISE aici (nu citite din `core/categorii_tva.VALORI` la rulare): o categorie nouă schimbă fișierul, deci amprenta lui
#: din registrul migrărilor, deci migrarea se rulează din nou. `core/test_274b_categorii_tva.py` cere egalitatea cu `VALORI`.
VALORI = ('taxare_inversa', 'scutit_cu_drept', 'scutit_fara_drept', 'livrare_ic', 'serviciu_extern', 'export', 'in_afara_sferei', 'neplatitor')

_DDL = [
    'ALTER TABLE "{s}".factura_linii ADD COLUMN IF NOT EXISTS categorie_tva text;',
    'ALTER TABLE "{s}".factura_linii DROP CONSTRAINT IF EXISTS factura_linii_categorie_tva_check;',
    'ALTER TABLE "{s}".factura_linii ADD CONSTRAINT factura_linii_categorie_tva_check CHECK (categorie_tva IS NULL OR categorie_tva IN ('
    + ", ".join("\'%s\'" % v for v in VALORI) + '));',
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 1 FROM information_schema.columns WHERE table_schema=%s AND table_name='factura_linii' "
                    "AND column_name = 'categorie_tva'", (schema,))
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
    print("migrare_categorie_tva_linie: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
