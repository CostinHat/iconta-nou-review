# -*- coding: utf-8 -*-
"""core/migrare_d300_b1.py - campuri noi pe facturi pentru clasificarea/temporizarea D300 (B1).

Adauga TREI coloane pe facturi (OBLIGATORII de la inceput - NOT NULL cu DEFAULT sensibil, ca
randurile existente/seed sa ramana valide):

  - tert_tara            text    NOT NULL DEFAULT 'RO'   -- codul ISO 2 litere al partenerului
                         (IC/export: partener UE -> taxare inversa/livrare IC; non-UE -> export).
  - tip_operatiune       text    NOT NULL DEFAULT 'normal' -- {'normal','avans','regularizare_avans'}
                         distinge AVANSUL (exigibil la emiterea facturii, art.282 alin.2 lit.b) de
                         faptul generator (exigibil la COALESCE(data_faptului_generator,data_emitere)).
  - furnizor_tva_incasare boolean NOT NULL DEFAULT false  -- pe facturile PRIMITE: furnizorul aplica
                         TVA la incasare (mentiune de pe factura) -> deducerea se amana pana la PLATA
                         (art.297 alin.2), chiar daca firma proprie e in regim normal.

BACKFILL determinista a lui tert_tara pentru facturile straine deja existente: prefixul de 2 litere
al CUI-ului (format VIES, ex. DE136695976 -> DE, FR40303265045 -> FR) ESTE codul de tara. CUI-urile
numerice / RO12345678 / fara CUI raman 'RO'. Idempotent (se aplica doar peste 'RO', valoarea implicita).

Sursa UNICA a DDL-ului = mirror in tenant_template.sql (CREATE TABLE facturi). Idempotent
(ADD COLUMN IF NOT EXISTS). Se aplica: tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_d300_b1`.
"""
from core import db

_DDL = [
    "ALTER TABLE \"{s}\".facturi ADD COLUMN IF NOT EXISTS tert_tara text NOT NULL DEFAULT 'RO';",
    "ALTER TABLE \"{s}\".facturi ADD COLUMN IF NOT EXISTS tip_operatiune text NOT NULL DEFAULT 'normal';",
    "ALTER TABLE \"{s}\".facturi ADD COLUMN IF NOT EXISTS furnizor_tva_incasare boolean NOT NULL DEFAULT false;",
]
# backfill determinista: prefixul de 2 litere al CUI-ului = codul de tara (VIES). Doar peste 'RO' (implicit).
_BACKFILL = (
    "UPDATE \"{s}\".facturi SET tert_tara = upper(left(tert_cui, 2)) "
    "WHERE tert_cui ~ '^[A-Za-z]{{2}}' AND tert_tara = 'RO';"
)

_COLOANE = ("tert_tara", "tip_operatiune", "furnizor_tva_incasare")


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))
        cur.execute(_BACKFILL.format(s=schema))


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
                aplica(conn, s)
                conn.commit()
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1; print("  OK  %s" % s)
                else:
                    esec.append(s); print("  ESEC (verificare)  %s" % s)
        except Exception as e:  # noqa: BLE001
            esec.append(s); print("  ESEC %s: %s" % (s, e))
    print("migrare_d300_b1: %d ok, %d esec" % (ok, len(esec)))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
