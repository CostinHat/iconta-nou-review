"""
core/migrare_cod_urgenta_cm.py — camp D_11 (cod urgenta medico-chirurgicala) pe concediile medicale.

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Adauga `cod_urgenta integer` (NULL = ne-aplicabil;
obligatoriu DOAR la cod 06 - urgenta medico-chirurgicala). D112 cere campul D_11 (structura oficiala, C(3),
nomenclator HG 423/2020): daca D_9=06 atunci D_11 nu poate fi null, altfel DUK respinge cu "Nu s-a completat
codul de urgenta medico-chirurgicala". Restul codurilor nu-l folosesc.

Idempotent (ADD COLUMN IF NOT EXISTS). Se aplica: tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_cod_urgenta_cm`.
"""
from core import db

DDL = 'ALTER TABLE "{s}".concedii_medicale ADD COLUMN IF NOT EXISTS cod_urgenta integer;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='concedii_medicale' AND column_name='cod_urgenta'", (schema,))
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
    print("Migrare cod_urgenta_cm: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
