"""
core/migrare_profil_c69.py — câmpurile firmei cerute de bilanț și de D406, care până acum se inventau (C69, lotul 10, deciziile Costin
20.10.2026, verbatim în DECIZII „Lotul 10, C69”): `firma_profil.mare_contribuabil` (bilanțul: „bifaMC=1 pt. Mari contribuabili …
bifaMC=0 pt.restul entitatilor”; NULL = nedeclarat -> bilanțul se oprește), `firma_profil.forma_proprietate` (codul din nomenclatorul
ANAF al formelor de proprietate; NULL -> bilanțul se oprește), `firma_profil.fara_cont_bancar` (D406 S.BA.2: „Pentru companiile care nu
detin cont bancar se va inscrie … "Fara cont bancar"”; cu rulaj / sold pe 512x în perioadă, D406 se oprește — contradicția).

Coloane noi, goale: datele existente nu se ating. Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent
(IF NOT EXISTS). Firmele existente: `python -m core.migrari_registru ruleaza [--productie] core/migrare_profil_c69.py`.
"""
from core import db

_DDL = [
    "ALTER TABLE \"{s}\".firma_profil ADD COLUMN IF NOT EXISTS mare_contribuabil boolean;",
    "ALTER TABLE \"{s}\".firma_profil ADD COLUMN IF NOT EXISTS forma_proprietate text;",
    "ALTER TABLE \"{s}\".firma_profil ADD COLUMN IF NOT EXISTS fara_cont_bancar boolean NOT NULL DEFAULT false;",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='firma_profil' "
                    "AND column_name IN ('mare_contribuabil', 'forma_proprietate', 'fara_cont_bancar')", (schema,))
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
    print("migrare_profil_c69: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
