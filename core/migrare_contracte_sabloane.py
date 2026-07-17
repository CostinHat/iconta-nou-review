"""
core/migrare_contracte_sabloane.py — schema F147 (generare contracte din sabloane).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent:
CREATE TABLE IF NOT EXISTS. Se aplica pe:
  - tenanti NOI: prin tenant_template.sql (la provisionare);
  - tenanti EXISTENTI: `python3 -m core.migrare_contracte_sabloane`.

Ce adauga: tabel contracte_sabloane — sabloane de contract EDITABILE DE FIRMA (mail-merge):
firma isi scrie textul cu marcaje {{partener_nume}} etc., iar generarea completeaza datele
din clienti + firma_profil si scoate PDF. NU autoram continut legal (v. DECIZII.md 17.07
"Lot 6 F147" + lectia F136). Contractul generat NU se stocheaza (doar descarcare). Izolat.
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS "{s}".contracte_sabloane (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nume text NOT NULL,
    continut text NOT NULL,
    creat_de integer,
    creat_la timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT contracte_sabloane_nume_unic UNIQUE (nume)
);
"""


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".contracte_sabloane",))
        return cur.fetchone()[0] is not None


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
    print("Migrare contracte_sabloane: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
