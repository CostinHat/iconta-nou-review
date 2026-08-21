# -*- coding: utf-8 -*-
"""core/migrare_stat_emis.py — statul de plata devine DOCUMENT EMIS (21.08.2026).

Sursa UNICA a DDL-ului e `stat_plata_emis.DDL` (mirror in tenant_template.sql). Idempotent.
Se aplica: tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_stat_emis`.

Adauga pe state_plata: exemplar, amprenta, date, emis_de, emis_la, corectie_la, motiv, motiv_de,
motiv_la. RIDICA vechea UNIQUE (salariat_id, luna) - ea interzicea STRUCTURAL al doilea exemplar,
adica schema codifica statul ca VEDERE, nu ca document care se poate corecta printr-un act nou.
"""
from core import db, stat_plata_emis


def aplica(conn, schema):
    stat_plata_emis.aplica(conn, schema)


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='state_plata' AND column_name IN "
                    "('exemplar','amprenta','date','emis_de','emis_la','corectie_la','motiv',"
                    "'motiv_de','motiv_la')", (schema,))
        return cur.fetchone()[0] == 9


def main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
        for s in scheme:
            aplica(conn, s)
            print("  %-14s %s" % (s, "ok" if verifica(conn, s) else "INCOMPLET"))
    print("tenanti migrati: %d" % len(scheme))


if __name__ == "__main__":
    main()
