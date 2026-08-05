"""
core/migrare_cnp_ingrijit.py — camp CNP persoana ingrijita (D_8/D_8a) pe concediile medicale.

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Adauga `cnp_ingrijit text` (NULL = ne-aplicabil).
D112 cere CNP-ul persoanei pentru care s-a eliberat certificatul (structura oficiala, N(13), regula DUK S97):
- cod 09/91/92 (ingrijire copil bolnav) -> D_8 = CNP/CIS copil (daca null: "trebuie sa se completeze CNP/cod
  CIS copil pentru care a fost eliberat certificatul medical");
- cod 17 (ingrijire pacient cu afectiuni oncologice) -> D_8a = CNP/CIS pacient.
Un CNP invalid nu intra (validare valideaza_cnp la salvare + hard-block la emisie). Restul codurilor nu-l folosesc.

Idempotent (ADD COLUMN IF NOT EXISTS). Se aplica: tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_cnp_ingrijit`.
"""
from core import db

DDL = 'ALTER TABLE "{s}".concedii_medicale ADD COLUMN IF NOT EXISTS cnp_ingrijit text;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='concedii_medicale' AND column_name='cnp_ingrijit'", (schema,))
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
    print("Migrare cnp_ingrijit: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
