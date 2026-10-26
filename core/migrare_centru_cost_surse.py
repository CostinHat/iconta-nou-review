# -*- coding: utf-8 -*-
"""core/migrare_centru_cost_surse.py — centrul de cost pe documentele din care se contează automat (lotul 13, deficiența 536).

DE CE — comanda Costin 13.1, 536, verbatim: „Centrul se pune doar pe notele manuale; tot ce se contează automat (facturi, NIR, salarii,
amortizare) iese «nealocat» — pe F2: Producție 0, nealocat cheltuieli 1.900 / venituri 5.000. Centrul se poate pune pe liniile facturilor,
NIR-urilor, salariilor și pe mijloacele fixe (amortizarea moștenește centrul activului). Adăugarea și raportul funcționează.”

CE ADAUGĂ (oglindit în `tenant_template.sql`), coloane goale, cu cheia străină spre `centre_cost`:
  - `factura_linii.centru_cost_id` — centrul liniei facturii (emisă sau primită); contarea îl pune pe rândul de venit / cheltuială al notei
    (`contare_facturi._note_pe_cote`);
  - `salariati.centru_cost_id` — centrul salariatului; nota statului de plată împarte cheltuielile cu personalul pe centre, după brutul
    fiecărui salariat (`salarii_contare.pe_centre`);
  - `mijloace_fixe.centru_cost_id` — centrul activului; rândurile de cheltuială ale notelor activului (amortizarea lunii, casarea,
    reevaluarea) îl moștenesc (`mf_note.adauga_linie`).

DATELE EXISTENTE: neafectate. Coloanele pornesc goale — alocarea se face de acum (o notă deja scrisă rămâne cum e; un centru pus azi pe un
salariat sau pe un activ se vede pe notele generate de acum încolo). Nicio notă contabilă nu se rescrie.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_centru_cost_surse.py`.
"""
import sys

from core import db

_TABELE = ("factura_linii", "salariati", "mijloace_fixe")

_DDL = ['ALTER TABLE "{s}".%s ADD COLUMN IF NOT EXISTS centru_cost_id integer REFERENCES "{s}".centre_cost(id);' % t for t in _TABELE]


def aplica_ddl(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def aplica(conn, schema):
    aplica_ddl(conn, schema)
    return {}


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema = %s AND column_name = 'centru_cost_id' "
                    "AND table_name = ANY(%s)", (schema, list(_TABELE)))
        return cur.fetchone()[0] == len(_TABELE)


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                aplica(conn, s)
                conn.commit()
            ok += 1
        except Exception as e:  # noqa: BLE001 — o firmă căzută nu le oprește pe celelalte; se raportează și ieșirea e 1
            esec.append((s, str(e)))
    print("migrare_centru_cost_surse: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        sys.exit(1)


if __name__ == "__main__":
    _main()
