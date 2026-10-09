# -*- coding: utf-8 -*-
"""core/migrare_asociati_istoric.py — structurile ANTERIOARE ale asociaților (cote de participare), cu data până la care au
fost valabile.

Sursa UNICĂ a DDL-ului (mirror în tenant_template.sql). [lot 19 pct.4e, 02.10.2026] D205 împărțea dividendele anului după
cotele ACTUALE din `asociati`, fără istoric: un asociat ieșit nu mai primea nimic din ce i se distribuise, iar unul intrat
lua o parte din dividendele de dinaintea lui. Temei: Legea 31/1990 art.67 alin.(2) — dividendele se distribuie
„proporțional cu cota de participare la capitalul social vărsat”; alin.(6) — „Dividendele care se cuvin după data
transmiterii acțiunilor aparțin cesionarului”. `asociati` rămâne structura CURENTĂ; aici se arhivează structura
înlocuită, la o cesiune înregistrată cu data ei (importul asociaților, `data_cesiune`).
Idempotent. Tenanți NOI prin template; EXISTENȚI prin `python3 -m core.migrare_asociati_istoric`."""
from core import db

DDL = ('CREATE TABLE IF NOT EXISTS "{s}".asociati_istoric ('
       ' id serial PRIMARY KEY,'
       ' cnp text NOT NULL,'
       ' nume text,'
       ' cota numeric NOT NULL,'
       ' valabil_pana_la date NOT NULL,'
       ' creat_la timestamp with time zone DEFAULT now() NOT NULL,'
       ' CONSTRAINT asociati_istoric_uniq UNIQUE (valabil_pana_la, cnp));')


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ("%s.asociati_istoric" % schema,))
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
    print("asociati_istoric: %d ok, %d esec" % (ok, len(esec)))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
