"""
core/migrare_produse_categorie_tva.py — categoria cotei 0% a produsului din nomenclator (lotul 11, deficiența 449, comanda Costin 11.1
pct.10, verbatim: „la cota TVA a produsului lipsesc taxarea inversă (art. 331), scutit cu drept de deducere (art. 294) și neimpozabil.”).

`produse.categorie_tva` = categoria cotei 0% care ține de produs (`core/produse_api.CATEGORII_PRODUS`, un subset din `core/categorii_tva`:
taxare inversă, scutit cu drept de deducere, scutit fără drept de deducere, în afara sferei / bazei TVA); `produse.categorie_331` = bunul
cu taxare inversă, codul din D394 (`core/d394.CODPR`: deșeuri, masă lemnoasă ...; cerealele pe subcodul NC, ca în D394). Factura le propune pe linie și pe document,
de unde ajung în XML-ul e-Factura (AE / E), în D300 (rd.13 / rd.14 / rd.15) și în D394.

Datele existente NU se schimbă: un produs vechi cu cota 0 rămâne fără categorie (natura scutirii nu e pe el; factura o cere pe linie, ca
până acum — 274b). Valorile admise sunt SCRISE aici (o categorie nouă schimbă fișierul, deci amprenta lui din registrul migrărilor);
`core/test_lot11_b_449_produse_categorie.py` cere egalitatea cu `produse_api.CATEGORII_PRODUS` și cu `d394.CODPR`.
Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent. Firmele existente:
`python -m core.migrari_registru ruleaza [--productie] core/migrare_produse_categorie_tva.py`.
"""
from core import db

CATEGORII = ("taxare_inversa", "scutit_cu_drept", "scutit_fara_drept", "in_afara_sferei")
#: categoriile D394 (`d394.CODPR`), cu cerealele pe subcodul NC (HG 1/2016 pct.109 alin.(7)) în locul centralizatorului — `produse_api.coduri_331`
CODURI_331 = ("1001", "1002", "1003", "1004", "1005", "10086000", "1201", "120400", "1205", "120600", "121291", "deseuri", "masa_lemnoasa",
              "certificate_emisii", "energie_electrica", "certificate_verzi", "cladiri_terenuri", "aur_investitii", "telefoane",
              "circuite_integrate", "console_tablete", "gaze_naturale")

_DDL = [
    'ALTER TABLE "{s}".produse ADD COLUMN IF NOT EXISTS categorie_tva text;',
    'ALTER TABLE "{s}".produse ADD COLUMN IF NOT EXISTS categorie_331 text;',
    'ALTER TABLE "{s}".produse DROP CONSTRAINT IF EXISTS produse_categorie_tva_check;',
    'ALTER TABLE "{s}".produse ADD CONSTRAINT produse_categorie_tva_check CHECK ((categorie_tva IS NULL OR (cota_tva = 0 AND categorie_tva IN ('
    + ", ".join("'%s'" % v for v in CATEGORII) + '))) AND (categorie_331 IS NULL OR (categorie_tva = \'taxare_inversa\' AND categorie_331 IN ('
    + ", ".join("'%s'" % v for v in CODURI_331) + '))));',
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 2 FROM information_schema.columns WHERE table_schema = %s AND table_name = 'produse' "
                    "AND column_name IN ('categorie_tva', 'categorie_331')", (schema,))
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
    print("migrare_produse_categorie_tva: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
