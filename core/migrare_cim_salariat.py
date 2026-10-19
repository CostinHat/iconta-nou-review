"""
core/migrare_cim_salariat.py — contractul individual de muncă pe fișa salariatului: `salariati.tip_contract` (durata: nedeterminată /
determinată), `salariati.nr_cim`, `salariati.data_cim` (deficiența 412, decizia Costin 19.10.2026, verbatim în DECIZII „Închiderea
lotului 9”: „Da, în fișa salariatului” — „Adeverință: Funcția, Tipul contractului, Nr./Data CIM se precompletează din fișă.”).

Temei: Legea 53/2003 art.12 alin.(1)–(2) (durata: nedeterminată, prin excepție determinată — de aici cele două valori ale CHECK-ului),
art.16 alin.(1) (contractul se încheie în formă scrisă — are număr și dată), art.34 alin.(3) (registrul de evidență cuprinde „tipul
contractului individual de muncă”).

Coloane noi, goale: salariații existenți rămân fără ele până le completează contabilul; adeverința le cere atunci în formularul ei, ca
până acum. Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent (ADD COLUMN IF NOT EXISTS). Firmele existente:
`python -m core.migrari_registru ruleaza [--productie] core/migrare_cim_salariat.py`.
"""
from core import db

_DDL = [
    "ALTER TABLE \"{s}\".salariati ADD COLUMN IF NOT EXISTS tip_contract text CONSTRAINT salariati_tip_contract_valid "
    "CHECK (tip_contract IS NULL OR tip_contract IN ('nedeterminata', 'determinata'));",
    "ALTER TABLE \"{s}\".salariati ADD COLUMN IF NOT EXISTS nr_cim text;",
    "ALTER TABLE \"{s}\".salariati ADD COLUMN IF NOT EXISTS data_cim date;",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='salariati' "
                    "AND column_name IN ('tip_contract', 'nr_cim', 'data_cim')", (schema,))
        return cur.fetchone()[0] == 3


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
    print("migrare_cim_salariat: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
