# -*- coding: utf-8 -*-
"""core/migrare_destinatie_tva.py — [A12] coloana `destinatie_tva` pe factura_linii.

Clasificarea destinatiei achizitiei pentru dreptul de deducere (art.300 CF, persoana cu regim mixt):
  - 'taxabil' (DEFAULT) : achizitie destinata EXCLUSIV operatiunilor cu drept de deducere
                          (art.300 alin.3) -> se deduce integral, fara pro-rata.
  - 'scutit'            : achizitie destinata EXCLUSIV operatiunilor FARA drept (art.300 alin.4)
                          -> NU se deduce.
  - 'mixt'             : destinatie mixta/necunoscuta (art.300 alin.5) -> se deduce pe baza de pro-rata.

DEFAULT 'taxabil': randurile existente/seed raman valide si isi pastreaza comportamentul (deducere
integrala), iar contabilul marcheaza explicit doar liniile scutite/mixte. Coloana e PER LINIE (decizia
Costin 19.09): o factura poate avea linii cu destinatii diferite.

Sursa UNICA a DDL-ului = mirror in tenant_template.sql (CREATE TABLE factura_linii). Idempotent
(ADD COLUMN IF NOT EXISTS). Se aplica: tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_destinatie_tva`.
"""
from core import db

_DDL = "ALTER TABLE \"{s}\".factura_linii ADD COLUMN IF NOT EXISTS destinatie_tva text NOT NULL DEFAULT 'taxabil';"
DESTINATII = ("taxabil", "scutit", "mixt")


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(_DDL.format(s=schema))


def toate_schemele(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM information_schema.schemata "
                    "WHERE schema_name LIKE 'tenant_%' ORDER BY 1")
        return [r[0] for r in cur.fetchall()]


def main():
    db.init_pool()
    with db.get_conn() as conn:
        scheme = toate_schemele(conn)
        for s in scheme:
            aplica(conn, s)
        print("destinatie_tva aplicata pe %d scheme: %s" % (len(scheme), ", ".join(scheme)))


if __name__ == "__main__":
    main()
