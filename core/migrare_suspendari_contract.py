# -*- coding: utf-8 -*-
"""core/migrare_suspendari_contract.py — perioadele de SUSPENDARE a contractului individual de muncă (CFP / suspendare).

Sursa UNICĂ a DDL-ului (mirror în tenant_template.sql). [lot 19 pct.4c, 02.10.2026] Statul de plată și D112 nu proratau
brutul la concediul fără plată sau la suspendare, fiindcă perioada nu se înregistra NICĂIERI (pontajul e informativ —
DECIZII F135 —, iar fișa salariatului avea doar data angajării/încetării). Temei: Codul muncii art.49 alin.(2)
(„suspendarea contractului individual de muncă are ca efect suspendarea prestării muncii de către salariat și a plății
drepturilor de natură salarială de către angajator”), art.54 (CFP = suspendare prin acordul părților), art.153.
`tip`: `cfp` (concediu fără plată, art.54/153) | `suspendare` (altă suspendare FĂRĂ drepturi salariale, art.49 alin.(2)).
Suspendările plătite parțial (art.53 — întrerupere temporară, 75%) NU se înregistrează aici.
Idempotent (CREATE TABLE IF NOT EXISTS). Tenanți NOI prin template; EXISTENȚI prin `python3 -m core.migrare_suspendari_contract`."""
from core import db

DDL = ('CREATE TABLE IF NOT EXISTS "{s}".suspendari_contract ('
       ' id serial PRIMARY KEY,'
       ' salariat_id integer NOT NULL REFERENCES "{s}".salariati(id) ON DELETE CASCADE,'
       ' data_inceput date NOT NULL,'
       ' data_sfarsit date NOT NULL,'
       " tip text NOT NULL CONSTRAINT suspendari_contract_tip CHECK (tip IN ('cfp', 'suspendare')),"
       ' temei text,'
       ' creat_la timestamp with time zone DEFAULT now() NOT NULL,'
       ' CONSTRAINT suspendari_contract_interval CHECK (data_sfarsit >= data_inceput),'
       ' CONSTRAINT suspendari_contract_uniq UNIQUE (salariat_id, data_inceput));')


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ("%s.suspendari_contract" % schema,))
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
    print("suspendari_contract: %d ok, %d esec" % (ok, len(esec)))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
