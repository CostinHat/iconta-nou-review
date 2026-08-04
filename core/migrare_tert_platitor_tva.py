# -*- coding: utf-8 -*-
"""core/migrare_tert_platitor_tva.py — camp facturi.tert_platitor_tva (boolean, nullable).

Statutul de platitor TVA al TERTULUI (furnizor/client), INGHETAT la momentul facturii = FAPT CONTABIL imutabil,
ca orice fapt de pe factura. clasifica_partener (D394, pct.216) il consulta in loc de euristica pe FORMA CUI-ului:
- True  -> partener inregistrat in scop TVA (RO -> tip_partener 1);
- False -> partener NEinregistrat (PJ neplatitor sau PF, chiar cu CUI valid) -> tip_partener 2 -> achizitie N;
- NULL  -> necunoscut (factura legacy, inainte de camp) -> fallback pe euristica de forma (limita scrisa in GARZI).
Corectitudine ISTORICA gratis: flag-ul inghetat pe fiecare factura da statutul de ATUNCI (o firma inregistrata
2020-2023 apoi radiata: factura 2022 -> True, factura 2025 -> False).

Sursa UNICA a DDL-ului = mirror in tenant_template.sql. Idempotent (ADD COLUMN IF NOT EXISTS).
Se aplica: tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_tert_platitor_tva`.
"""
from core import db

_DDL = [
    'ALTER TABLE "{s}".facturi ADD COLUMN IF NOT EXISTS tert_platitor_tva boolean;',
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='facturi' AND column_name='tert_platitor_tva'", (schema,))
        return cur.fetchone() is not None


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
            ok += 1
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_tert_platitor_tva: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))


if __name__ == "__main__":
    _main()
