"""
core/migrare_pontaj.py — schema F135 (pontaj informativ).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent. Tabelul stocheaza
DOAR EXCEPTIILE (zilele care NU sunt "prezent"); prezenta = absenta unui rand pe o zi
lucratoare. NU alimenteaza calculul salarial (evidenta pura, DECIZII.md 17.07 F135).

Aplicare: tenanti noi prin tenant_template.sql; tenanti existenti prin
`python3 -m core.migrare_pontaj` (ruleaza pe toate schemele tenant_% si verifica).
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS "{s}".pontaj (
    salariat_id integer NOT NULL,
    zi date NOT NULL,
    stare text NOT NULL,
    nota text,
    CONSTRAINT pontaj_pkey PRIMARY KEY (salariat_id, zi)
);
"""

# starile valide (excepatii de la "prezent"). Pur informativ.
STARI = ("absent_motivat", "absent_nemotivat", "concediu_odihna",
         "concediu_medical", "invoire", "delegatie")


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".pontaj",))
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
                    ok += 1; print("  OK  %s" % s)
                else:
                    esec.append(s); print("  ESEC (verificare)  %s" % s)
        except Exception as e:
            esec.append(s); print("  ESEC %s: %s" % (s, e))
    print("Migrare pontaj: %d/%d scheme OK%s" % (ok, len(scheme),
          ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
