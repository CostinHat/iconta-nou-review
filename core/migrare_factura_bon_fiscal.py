# -*- coding: utf-8 -*-
"""core/migrare_factura_bon_fiscal.py — factura EMISĂ PE BAZA BONULUI FISCAL (decizia Costin A, 02.10.2026).

Sursa UNICĂ a DDL-ului. Idempotent (ADD COLUMN IF NOT EXISTS / constrângere creată o dată).
Aplică pe existenți: `python3 -m core.migrare_factura_bon_fiscal`.

DE CE. HG 1/2016 pct.97 alin.(1): „Pe facturile emise și achitate pe bază de bonuri fiscale … fiind suficientă mențiunea
«conform bon fiscal nr./data»”. Fără marca asta, o factură eliberată clientului pentru un bon deja cuprins în raportul Z se
număra a doua oară: în D300 (facturile + Z), în D394 op2 Î1 („cu excepția celor pentru care s-au emis facturi”, OPANAF
2194/2025 lit.G) și în evidență (contarea automată `4111 = 707 + 4427` peste nota Z).

  - bon_fiscal_nr    text  — numărul bonului fiscal (cum e tipărit)
  - bon_fiscal_data  date  — data bonului (luna lui decide raportul Z din care se scade)
  - CHECK: amândouă sau niciuna (o marcă pe jumătate nu poate fi aplicată).
"""
from core import db

_DDL = [
    'ALTER TABLE "{s}".facturi ADD COLUMN IF NOT EXISTS bon_fiscal_nr text;',
    'ALTER TABLE "{s}".facturi ADD COLUMN IF NOT EXISTS bon_fiscal_data date;',
    'DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_constraint c JOIN pg_namespace n ON n.oid = c.connamespace '
    "WHERE n.nspname = '{s}' AND c.conname = 'facturi_bon_fiscal_complet') THEN "
    'ALTER TABLE "{s}".facturi ADD CONSTRAINT facturi_bon_fiscal_complet CHECK '
    "((bon_fiscal_nr IS NULL) = (bon_fiscal_data IS NULL) AND (bon_fiscal_nr IS NULL OR btrim(bon_fiscal_nr) <> '')); "
    'END IF; END $$;',
]

_COLOANE = ("bon_fiscal_nr", "bon_fiscal_data")


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='facturi' AND column_name = ANY(%s)", (schema, list(_COLOANE)))
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
                with conn.cursor() as cur:
                    cur.execute("SELECT to_regclass(%s)", ('%s.facturi' % s,))
                    if cur.fetchone()[0] is None:
                        continue
                aplica(conn, s)
                conn.commit()
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1
                else:
                    esec.append("%s: coloanele nu sunt acolo dupa aplicare" % s)
        except Exception as e:
            esec.append("%s: %r" % (s, e))
    print("migrare_factura_bon_fiscal: %d scheme OK" % ok)
    for e in esec:
        print("   ESEC", e)
    return 0 if not esec else 2


if __name__ == "__main__":
    raise SystemExit(_main())
