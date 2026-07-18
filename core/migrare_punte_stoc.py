"""
core/migrare_punte_stoc.py — schema punte factura->stoc (F172).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent:
ADD COLUMN IF NOT EXISTS + FK adaugat conditional. Se aplica pe:
  - tenanti NOI: prin tenant_template.sql;
  - tenanti EXISTENTI: `python3 -m core.migrare_punte_stoc`.

Ce adauga (ambele NULL-able - nu ating datele existente):
  - factura_linii.articol_id -> cheia care lipsea intre vanzare si stoc. NULL = linie de
    serviciu (fara articol). FK spre articole ON DELETE SET NULL (stergerea unui articol nu
    rupe factura). Serveste si factura si aviz (aceeasi tabela).
  - miscari_stoc.factura_id -> cheia de intoarcere pentru profit-pe-produs. NULL = miscare
    manuala (iesire/intrare/inventar/transfer), neschimbata. FK spre facturi ON DELETE SET NULL.
Vezi DECIZII.md 18.07 "Punte factura -> stoc".
"""
from core import db

DDL = """
ALTER TABLE "{s}".factura_linii ADD COLUMN IF NOT EXISTS articol_id integer;
ALTER TABLE "{s}".miscari_stoc  ADD COLUMN IF NOT EXISTS factura_id integer;
DO $mig$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'factura_linii_articol_fk'
                   AND connamespace = '"{s}"'::regnamespace) THEN
        ALTER TABLE "{s}".factura_linii ADD CONSTRAINT factura_linii_articol_fk
            FOREIGN KEY (articol_id) REFERENCES "{s}".articole(id) ON DELETE SET NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'miscari_stoc_factura_fk'
                   AND connamespace = '"{s}"'::regnamespace) THEN
        ALTER TABLE "{s}".miscari_stoc ADD CONSTRAINT miscari_stoc_factura_fk
            FOREIGN KEY (factura_id) REFERENCES "{s}".facturi(id) ON DELETE SET NULL;
    END IF;
END $mig$;
"""


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND "
                    "((table_name='factura_linii' AND column_name='articol_id') OR "
                    " (table_name='miscari_stoc' AND column_name='factura_id'))", (schema,))
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
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1
                    print("  OK  %s" % s)
                else:
                    esec.append(s)
                    print("  ESEC (verificare)  %s" % s)
        except Exception as e:
            esec.append(s)
            print("  ESEC %s: %s" % (s, e))
    print("Migrare punte_stoc: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
