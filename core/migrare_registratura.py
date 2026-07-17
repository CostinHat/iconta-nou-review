"""
core/migrare_registratura.py — schema F146 (registratura documente).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent:
CREATE TABLE IF NOT EXISTS. Se aplica pe:
  - tenanti NOI: prin tenant_template.sql (la provisionare);
  - tenanti EXISTENTI: `python3 -m core.migrare_registratura`.

Ce adauga: tabel registratura — REGISTRU UNIC de intrare-iesire (un singur numar
secvential per an, coloana `directie` marcheaza sensul). Numarul se aloca din MAX(an)+1
la inregistrare (resetare anuala naturala), nu dintr-un contor separat. Izolat: nu atinge
contabilitatea. v1 = registru manual (fara hook automat la facturi/adeverinte). Vezi
DECIZII.md 17.07 "Lot 6 F146" + FUNCTIONALITATI F146.
"""
from core import db

# {s} = numele schemei (validat inainte). UNIQUE(an, numar) = fara numere duplicate pe an
# (garanteaza seria unica). CHECK pe directie = vocabular fix (intrare/iesire).
DDL = """
CREATE TABLE IF NOT EXISTS "{s}".registratura (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    directie text NOT NULL CHECK (directie IN ('intrare','iesire')),
    numar integer NOT NULL,
    an integer NOT NULL,
    data date NOT NULL,
    descriere text NOT NULL,
    partener text,
    document_ref text,
    creat_de integer,
    creat_la timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT registratura_an_numar_unic UNIQUE (an, numar)
);
"""


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".registratura",))
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
    print("Migrare registratura: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
