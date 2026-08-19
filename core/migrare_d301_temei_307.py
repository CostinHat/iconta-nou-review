# -*- coding: utf-8 -*-
"""core/migrare_d301_temei_307.py - temeiul art. 307 per operatiune D301 tip 4.

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). O operatiune tip 4 (Sectiunea 4 = art. 307
alin. (3)/(5)/(6), NU intra in D390) trebuie sa poarte CARE alineat se aplica, ca excluderea din D390
sa fie AUDITABILA (motiv numit + temei citat), nu dedusa din denumire sau din prezenta codului.

Adauga `temei_307` (text, NULL = NECONFIRMAT) si SCOATE `d390_confirmat_local` (boolean) impreuna cu
euristica "tip 4 + cod -> poate serviciu" pe care o inlocuieste: temeiul explicit e mai tare decat un
indiciu soft. Op-urile tip 4 existente raman cu temei_307 NULL -> semnal, nu verde (nu se deduce temeiul).

Valori acceptate (d301_operatiuni_api.TEMEI_307): gaz_energie (alin.3), suspensiv (alin.5), nestabilit (alin.6).
Idempotent. Tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_d301_temei_307`.
"""
from core import db

DDL_ADD = 'ALTER TABLE "{s}".d301_operatiuni ADD COLUMN IF NOT EXISTS temei_307 text;'
DDL_DROP = 'ALTER TABLE "{s}".d301_operatiuni DROP COLUMN IF EXISTS d390_confirmat_local;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL_ADD.format(s=schema))
        cur.execute(DDL_DROP.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FILTER (WHERE column_name='temei_307') AS add, "
                    "count(*) FILTER (WHERE column_name='d390_confirmat_local') AS drop "
                    "FROM information_schema.columns WHERE table_schema=%s AND table_name='d301_operatiuni'",
                    (schema,))
        a, d = cur.fetchone()
        return a == 1 and d == 0


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
                    esec.append(s + " (verificare esuata)")
        except Exception as e:
            esec.append("%s (%s)" % (s, e))
    print("migrare_d301_temei_307: %d/%d OK" % (ok, len(scheme)))
    if esec:
        print("ESEC:", "; ".join(esec))


if __name__ == "__main__":
    _main()
