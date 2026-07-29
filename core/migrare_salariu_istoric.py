"""core/migrare_salariu_istoric.py — istoricul salariului de baza (PASUL 2, forma 1).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent. Se aplica: tenanti NOI prin
template; EXISTENTI prin `python3 -m core.migrare_salariu_istoric`. Zero tenanti azi -> zero migrare
reala, dar exista pentru viitor. In 2a salariu_brut ramane in salariati (bridge); scrierile trec pe
istoric in 2b."""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS "{s}".salariu_istoric (
  id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  salariat_id   INTEGER NOT NULL,
  valabil_din   DATE NOT NULL,
  salariu_brut  NUMERIC NOT NULL CHECK (salariu_brut >= 0),
  creat_la      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_salariu_istoric_sal_data
  ON "{s}".salariu_istoric (salariat_id, valabil_din);
"""


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables "
                    "WHERE table_schema=%s AND table_name='salariu_istoric'", (schema,))
        return cur.fetchone()[0] == 1


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
    print("Migrare salariu_istoric: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
