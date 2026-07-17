"""
core/migrare_stoc_lot4.py — coloane aditive Lot 4 Stoc (17.07.2026).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent (ADD COLUMN
IF NOT EXISTS + CREATE INDEX IF NOT EXISTS). PUR ADITIV — nu atinge date existente,
nu atinge valorizarea/CMP/D406.

Coloane (autorizate 17.07, DECIZII.md "Lot 4 Stoc"):
  - miscari_stoc.locatie   -> F138 Tier 1: eticheta descriptiva unde sta fizic stocul.
                              CMP ramane GLOBAL (nu segmenteaza valorizarea). Tier 3
                              (CMP separat per depozit) AMANAT pana la testare.
  - articole.barcode       -> F141: cod de bare/EAN, unic (index partial WHERE NOT NULL).
  - articole.nivel_minim   -> F140: prag pentru stoc critic / necesar aprovizionare.
  - nir.transport, nir.taxe -> F139: cost accesoriu (landed cost), repartizat in
                              costul de achizitie (OMFP 1802/2014).

Aplicare: tenanti noi prin tenant_template.sql; tenanti existenti prin
`python3 -m core.migrare_stoc_lot4` (ruleaza pe toate schemele tenant_% si verifica).
"""
from core import db

DDL = """
ALTER TABLE "{s}".miscari_stoc ADD COLUMN IF NOT EXISTS locatie varchar(100);
ALTER TABLE "{s}".articole ADD COLUMN IF NOT EXISTS barcode varchar(50);
ALTER TABLE "{s}".articole ADD COLUMN IF NOT EXISTS nivel_minim numeric(12,3);
CREATE UNIQUE INDEX IF NOT EXISTS articole_barcode_uq
    ON "{s}".articole (barcode) WHERE barcode IS NOT NULL;
ALTER TABLE "{s}".nir ADD COLUMN IF NOT EXISTS transport numeric(12,2) NOT NULL DEFAULT 0;
ALTER TABLE "{s}".nir ADD COLUMN IF NOT EXISTS taxe numeric(12,2) NOT NULL DEFAULT 0;
"""

# coloanele asteptate dupa migrare, pentru verificare
COLOANE = [("miscari_stoc", "locatie"), ("articole", "barcode"),
           ("articole", "nivel_minim"), ("nir", "transport"), ("nir", "taxe")]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        for tabel, coloana in COLOANE:
            cur.execute("SELECT 1 FROM information_schema.columns "
                        "WHERE table_schema=%s AND table_name=%s AND column_name=%s",
                        (schema, tabel, coloana))
            if cur.fetchone() is None:
                return False
    return True


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
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1; print("  OK  %s" % s)
                else:
                    esec.append(s); print("  ESEC (verificare)  %s" % s)
        except Exception as e:
            esec.append(s); print("  ESEC %s: %s" % (s, e))
    print("Migrare stoc Lot 4: %d/%d scheme OK%s" % (ok, len(scheme),
          ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
