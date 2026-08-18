# -*- coding: utf-8 -*-
"""core/migrare_d301_partener.py - furnizorul UE pe operatiunea D301 (pt auto-derivarea D390 cod A).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Adauga pe d301_operatiuni identitatea
FURNIZORULUI intracomunitar: `partener_tara` (cod ISO tara, ex. DE), `partener_cod` (codul de TVA
al furnizorului, FARA prefix tara; poate fi gol = NOTA 1, furnizor fara cod valid) si `partener_den`
(denumire). Inainte d301_operatiuni avea doar (tip, nr_doc, data_doc, val_valuta, curs, tva) - suficient
pentru D301 (care nu cere furnizorul), dar NU pentru D390 cod A (care cere codT/codO furnizor). Cu aceste
coloane, o achizitie IC inregistrata o SINGURA data in ecranul D301 alimenteaza si D390 (auto-derivare
d301->cod A/S), fara dubla introducere. Decizia Costin 18.08.2026 (peste recomandarea executorului).
Nullable/DEFAULT '' intentionat: operatiunile D301 vechi n-au furnizor -> raman NOTA 1 la D390 pana la
completare. Idempotent (ADD COLUMN IF NOT EXISTS). Se aplica: tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_d301_partener`."""
from core import db

DDL = (
    'ALTER TABLE "{s}".d301_operatiuni '
    "ADD COLUMN IF NOT EXISTS partener_tara varchar(2) DEFAULT '', "
    "ADD COLUMN IF NOT EXISTS partener_cod  varchar(20) DEFAULT '', "
    "ADD COLUMN IF NOT EXISTS partener_den  text DEFAULT '';"
)

_COLOANE = ("partener_tara", "partener_cod", "partener_den")


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='d301_operatiuni' AND column_name = ANY(%s)", (schema, list(_COLOANE)))
        return cur.fetchone()[0] == len(_COLOANE)


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
                else:
                    esec.append(s)
        except Exception as e:
            esec.append("%s (%s)" % (s, e))
    print("migrare_d301_partener: %d/%d OK" % (ok, len(scheme)))
    if esec:
        print("ESEC:", esec)
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
