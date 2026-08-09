"""
core/migrare_program_national_cm.py — marcaj "pacient inclus in program national de sanatate" (D112 D_9a).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Adauga `program_national boolean DEFAULT false`
pe concedii_medicale. D112 structura_D112_0726_030826.pdf: D_9a N(1), "9.1 - se bifeaza pentru CM acordate
pacientilor inclusi in programele nationale de sanatate" (se aplica din 07/2026). Marcajul e o BIFA per
certificat; cand e 1, D112 emite D_9a="1", iar CM e exceptat de la diminuarea de 1 zi (Ordin 506/1030/2026
art.78^4 alin.(2^1): "concediilor medicale acordate bolnavilor inclusi in programele nationale de sanatate").

Idempotent (ADD COLUMN IF NOT EXISTS). Tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_program_national_cm`.
"""
from core import db

DDL = 'ALTER TABLE "{s}".concedii_medicale ADD COLUMN IF NOT EXISTS program_national boolean DEFAULT false;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='concedii_medicale' AND column_name='program_national'", (schema,))
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
    print("Migrare program_national: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
