# -*- coding: utf-8 -*-
"""core/migrare_lot13_salarii.py — schema salarizării din lotul 13 (comanda Costin 13.1). Mirror în tenant_template.sql.

1. [670 b] `diurna_excedent`: excedentul de diurnă al salariatului, pe lună — venit asimilat salariilor (CF art.76 alin.(2) lit.k),
   citit de statul de plată, D112 și nota salariilor. DDL-ul e în `core/diurna_salariat.py` (sursa unică).
1b. [684] `diurna_excedent.inregistrare_id` -> `inregistrari(id)` ON DELETE CASCADE: excedentul cade odată cu nota decontului, pe
   orice drum de ștergere. Datele existente: rândurile scrise de decont (`decont-deplasare:<nota>`) primesc nota; cele a căror notă a
   fost ștearsă înainte (orfanele defectului 684) se scot (`diurna_salariat.REPARA_LEGATURA`).
2. [679] `elemente_salariale.spor_procent`: sporul orelor suplimentare, din care aplicația calculează suma (ore × tariful orar al
   salariului de bază × (100% + spor)); se arată pe ecran și pe fluturaș. Rândurile vechi rămân cu spor_procent NULL: suma lor a
   fost scrisă de contabil și nu se rescrie (ecranul arată sporul care rezultă din ea).

Idempotent (IF NOT EXISTS). Tenanți NOI prin template; EXISTENȚI prin `python -m core.migrari_registru ruleaza core/migrare_lot13_salarii.py`.
"""
from core import db
from core import diurna_salariat as _ds

DDL_SPOR = ('ALTER TABLE "{s}".elemente_salariale ADD COLUMN IF NOT EXISTS spor_procent numeric(6,2) '
            'CHECK (spor_procent IS NULL OR spor_procent >= 0);')


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(_ds.DDL.format(s=schema))
        cur.execute(_ds.DDL_NOTA.format(s=schema))
        cur.execute(_ds.REPARA_LEGATURA.format(s=schema))
        cur.execute(DDL_SPOR.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ("%s.diurna_excedent" % schema,))
        if cur.fetchone()[0] is None:
            return False
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema = %s AND table_name = 'diurna_excedent' "
                    "AND column_name = 'inregistrare_id'", (schema,))
        if cur.fetchone() is None:
            return False
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema = %s AND table_name = 'elemente_salariale' "
                    "AND column_name = 'spor_procent'", (schema,))
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
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1
                    print("  OK  %s" % s)
                else:
                    esec.append(s)
                    print("  ESEC (verificare)  %s" % s)
        except Exception as e:   # noqa: BLE001 — o firmă eșuată se numără și se spune; rularea se oprește cu cod 1 la final
            esec.append(s)
            print("  ESEC %s: %s" % (s, e))
    print("lot13 salarii (diurna_excedent + legătura de notă, spor_procent): %d ok, %d esec" % (ok, len(esec)))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
