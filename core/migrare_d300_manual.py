# -*- coding: utf-8 -*-
"""core/migrare_d300_manual.py - tabel d300_manual (randuri manuale D300 persistate).

Randurile D300 pe care generatorul NU le deriva din facturi (scutiri R14/R15, regularizari
R16/R30, ajustari R29/R43/R44, cote istorice etc.) se introduc de contabil si trebuie sa
PERSISTE (nu efemer prin body.manual) - altfel calea de DEPUNERE (/coada regenereaza server-side
FARA body.manual) ar produce alt XML decat preview-ul. Geaman cu d301_operatiuni / d390_manual:
tabel propriu, generatorul il re-citeste din DB.

UNITATE: LEI intregi (bigint), aliniat cu d300.py care lucreaza tot in lei intregi (_int ->
Decimal.quantize la '1'). NU bani. baza=col.1 (valoare), tva=col.2; randurile fara col.2
(R1-R4/R13/R14/R15/R26) au tva=0.

Sursa UNICA a DDL-ului = mirror in tenant_template.sql (CREATE TABLE d300_manual). Idempotent
(CREATE TABLE IF NOT EXISTS). Se aplica: tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_d300_manual`. id SERIAL (ca d301_operatiuni) - zero drift.
"""
from core import db

_DDL = (
    'CREATE TABLE IF NOT EXISTS "{s}".d300_manual ('
    ' id SERIAL PRIMARY KEY,'
    ' an integer NOT NULL, luna integer NOT NULL,'
    ' rand text NOT NULL,'
    ' baza bigint NOT NULL DEFAULT 0,'
    ' tva bigint NOT NULL DEFAULT 0,'
    ' descriere text,'
    ' creat timestamp DEFAULT now(),'
    ' UNIQUE (an, luna, rand)'
    ');'
)


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(_DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='d300_manual' AND column_name = ANY(%s)",
                    (schema, ['an', 'luna', 'rand', 'baza', 'tva', 'descriere']))
        return cur.fetchone()[0] == 6


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
                conn.commit()
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1; print("  OK  %s" % s)
                else:
                    esec.append(s); print("  ESEC (verificare)  %s" % s)
        except Exception as e:  # noqa: BLE001
            esec.append(s); print("  ESEC %s: %s" % (s, e))
    print("migrare_d300_manual: %d ok, %d esec" % (ok, len(esec)))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
