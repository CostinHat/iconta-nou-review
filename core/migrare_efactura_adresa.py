"""
core/migrare_efactura_adresa.py — adresa STRUCTURATA a cumparatorului pe facturi (e-Factura, F126/F160).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent (ADD COLUMN IF NOT EXISTS).
Se aplica: tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_efactura_adresa`.

DE CE (verificat la SURSA, nu speculativ): validatorul oficial ANAF (webservicesp.anaf.ro/.../
validare/FACT1) a respins prima factura cu BR-RO-110: daca tara cumparatorului e RO, judetul
(BT-54) e OBLIGATORIU (cod ISO 3166-2:RO). Schema avea doar tert_adresa (text liber). Adaug:
  - facturi.tert_oras  -> BT-52 (localitate cumparator; pt Bucuresti = SECTOR1..6, BR-RO-100)
  - facturi.tert_judet -> BT-54 (judet cumparator, ex. 'B' / 'Cluj' -> RO-B / RO-CJ)
Ambele NULL-able (nu ating facturile vechi). Vezi DECIZII.md 18.07 "e-Factura structura BR-RO".
"""
from core import db

DDL = """
ALTER TABLE "{s}".facturi ADD COLUMN IF NOT EXISTS tert_oras  text;
ALTER TABLE "{s}".facturi ADD COLUMN IF NOT EXISTS tert_judet text;
"""


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='facturi' AND column_name IN ('tert_oras','tert_judet')", (schema,))
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
    print("Migrare efactura_adresa: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
