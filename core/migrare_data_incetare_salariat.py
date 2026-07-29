"""
core/migrare_data_incetare_salariat.py — dimensiune temporala pe contractul salariatului (PASUL 1).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Adauga `data_incetare` (NULL = contract activ)
si RETRAGE `activ` (boolean): sub Optiunea A, data_incetare e sursa unica pentru "a plecat" - un boolean
nu poate spune CAND, iar doua campuri pt acelasi fapt diverg (tiparul care ne-a costat de doua ori).
Idempotent (ADD/DROP IF EXISTS + CHECK conditionat). Se aplica: tenanti NOI prin template; EXISTENTI
prin `python3 -m core.migrare_data_incetare_salariat`. Acum sunt ZERO tenanti -> zero migrare reala de
date, dar migrarea trebuie sa existe pentru viitor.
"""
from core import db

DDL = """
ALTER TABLE "{s}".salariati ADD COLUMN IF NOT EXISTS data_incetare date;
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'salariati_incetare_dupa_angajare'
                 AND conrelid = ('"{s}".salariati')::regclass) THEN
    ALTER TABLE "{s}".salariati ADD CONSTRAINT salariati_incetare_dupa_angajare
      CHECK (data_incetare IS NULL OR data_incetare >= data_angajare);
  END IF;
END $$;
ALTER TABLE "{s}".salariati DROP COLUMN IF EXISTS activ;
"""


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='salariati' AND column_name='data_incetare'", (schema,))
        are_col = cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='salariati' AND column_name='activ'", (schema,))
        fara_activ = cur.fetchone()[0] == 0
    return are_col and fara_activ


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
    print("Migrare data_incetare_salariat: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
