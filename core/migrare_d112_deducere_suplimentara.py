# -*- coding: utf-8 -*-
"""core/migrare_d112_deducere_suplimentara.py — coloane pt DEDUCEREA PERSONALA SUPLIMENTARA (D112, CF art.77
alin.(10)): tineri <26 (15% x salariu minim) + copii <=18 scolarizati (100 lei/copil, pe baza declaratiei
parintelui art.77 alin.(12)-(13)).

Formula exista in salarizare.deducere_personala (sub_26/copii_scoala/declaratie_copii) DAR era necablata -
niciun apelant de productie trecea input-ul -> impozit SUPRA-declarat pt tineri<26 si parinti cu copii
scolarizati. Acum d112.pull + stat_plata_api paseaza:
  - sub_26 = derivat din data_nastere (varsta < 26 la luna venitului);
  - copii_scoala = copii_scolarizati (numar copii <=18 in invatamant);
  - declaratie_copii = flag declaratia parintelui (fara ea deducerea de 100 lei NU se acorda - art.77 alin.12-13).

Sursa UNICA a DDL-ului = mirror in tenant_template.sql. Idempotent (ADD COLUMN IF NOT EXISTS).
Se aplica: tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_d112_deducere_suplimentara`.
"""
from core import db

_DDL = [
    'ALTER TABLE "{s}".salariati ADD COLUMN IF NOT EXISTS data_nastere date;',
    'ALTER TABLE "{s}".salariati ADD COLUMN IF NOT EXISTS copii_scolarizati integer NOT NULL DEFAULT 0;',
    'ALTER TABLE "{s}".salariati ADD COLUMN IF NOT EXISTS declaratie_copii boolean NOT NULL DEFAULT false;',
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='salariati' AND column_name IN "
                    "('data_nastere','copii_scolarizati','declaratie_copii')", (schema,))
        return cur.fetchone()[0] == 3


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
        for s in scheme:
            aplica(conn, s)
            conn.commit()
            print("  migrat: %s (deducere suplimentara) -> %s" % (s, verifica(conn, s)))
    print("gata: %d scheme" % len(scheme))


if __name__ == "__main__":
    _main()
