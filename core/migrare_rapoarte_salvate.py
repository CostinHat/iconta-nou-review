"""
core/migrare_rapoarte_salvate.py — schema F145 (rapoarte configurabile salvabile).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent:
CREATE TABLE IF NOT EXISTS. Se aplica pe:
  - tenanti NOI: prin tenant_template.sql (la provisionare);
  - tenanti EXISTENTI: `python3 -m core.migrare_rapoarte_salvate`.

Ce adauga: tabel rapoarte_salvate — variante de raport ale FIRMEI (partajate intre
utilizatorii cu acces la firma), generice prin (tip_raport, filtru jsonb). Izolat:
nu atinge nicio tabela contabila. v1 il foloseste ecranul Rapoarte comerciale
(tip_raport='comercial', filtru={an, cui?}); orice raport filtrabil viitor
refoloseste acelasi tabel fara alta schema. Vezi DECIZII.md / FUNCTIONALITATI F145.
"""
from core import db

# DDL parametrizat pe schema. {s} = numele schemei (validat inainte).
# {{}} = acolade literale (default JSON gol), scapate pentru .format().
# tip_raport: vocabular FIX prin CHECK (previne variante orfane la o litera gresita);
# dublat de constanta TIPURI_RAPORT in rapoarte_comerciale_api, verificata la scriere.
# UNIQUE(tip_raport, nume): fara doua variante cu acelasi nume care deruteaza omul.
DDL = """
CREATE TABLE IF NOT EXISTS "{s}".rapoarte_salvate (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tip_raport text NOT NULL CHECK (tip_raport IN ('comercial')),
    nume text NOT NULL,
    filtru jsonb NOT NULL DEFAULT '{{}}'::jsonb,
    creat_de integer,
    creat_la timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT rapoarte_salvate_tip_nume_unic UNIQUE (tip_raport, nume)
);
"""


def aplica(conn, schema):
    """Aplica DDL-ul idempotent pe o schema. Ridica daca numele e invalid."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    """True daca schema are tabelul rapoarte_salvate."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".rapoarte_salvate",))
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
    print("Migrare rapoarte_salvate: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
