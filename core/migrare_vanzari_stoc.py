# -*- coding: utf-8 -*-
"""core/migrare_vanzari_stoc.py — vânzarea în regim de marjă și livrarea de aur de investiții DIN STOC (lotul 13, deficiența 548).

DE CE — comanda Costin 13.1, 548, verbatim: „Vânzarea nu descarcă bunul din gestiune (607 = 371 / costul aurului) și nu cere clientul;
profitul iese mai mare cu tot costul bunului, stocul rămâne umflat. Prețul de cumpărare se scrie de mână în loc să vină din bunul aflat în
stoc (511). Jurnalul special al vânzărilor în regim de marjă (F248) nu are ecran.”

CE ADAUGĂ (oglindit în `tenant_template.sql`, peticul `l13_petice/ops_template.json`):
  - `vanzari_din_stoc` — vânzarea (nota din Operațiuni, cu clientul pe 4111) și ieșirea ei din stoc (`miscari_stoc`, nota ei 607 = 371 la
    CMP, scrisă de `stocuri_cv_api.iesire` ca orice ieșire pe articol): prețul de cumpărare al marjei = valoarea ieșirii, nu un număr scris;
    jurnalul vânzărilor în regim de marjă (`uc_tenants.jurnal_marja`) citește de aici prețul de vânzare, prețul de cumpărare, marja și TVA;
  - triggerul `trg_vanzare_stoc_sterge` (înaintea ștergerii notei vânzării): o vânzare a cărei ieșire din stoc e încă vie nu se șterge —
    altfel bunul ar rămâne ieșit din gestiune fără vânzare; refuzul (`REGULA_CONTABILA:`, 409) spune unde se anulează ieșirea.

DATELE EXISTENTE: vânzările în regim de marjă dinainte (nota „… (art. 312)”, fără ieșire din stoc) rămân cum sunt — nu au ieșire de
legat, iar prețul lor de cumpărare nu e în evidență (era scris numai în calcul); jurnalul le arată din notă, cu prețul de cumpărare „—”.
Nimic de mutat; tabelul pornește gol.
"""
import sys

from core import db

_DDL = [
    'CREATE TABLE IF NOT EXISTS "{s}".vanzari_din_stoc ('
    ' inregistrare_id integer PRIMARY KEY REFERENCES "{s}".inregistrari(id) ON DELETE CASCADE,'
    " fel text NOT NULL CHECK (fel IN ('marja', 'aur')),"
    ' miscare_id integer REFERENCES "{s}".miscari_stoc(id) ON DELETE SET NULL,'
    ' nota_iesire_id integer REFERENCES "{s}".inregistrari(id) ON DELETE SET NULL,'
    ' articol_id integer,'
    ' cantitate numeric(12,3) NOT NULL CHECK (cantitate > 0),'
    ' pret_vanzare numeric(14,2) NOT NULL,'
    ' pret_cumparare numeric(14,2) NOT NULL,'
    ' tva numeric(14,2) NOT NULL,'
    ' client_cui text,'
    ' client_nume text NOT NULL,'
    ' document text);',
    'CREATE OR REPLACE FUNCTION "{s}".vanzare_stoc_sterge() RETURNS trigger AS $$\n'
    'DECLARE doc text;\n'
    'BEGIN\n'
    '  SELECT m.document INTO doc FROM "{s}".vanzari_din_stoc v JOIN "{s}".miscari_stoc m ON m.id = v.miscare_id\n'
    '   WHERE v.inregistrare_id = OLD.id AND m.anuleaza_id IS NULL\n'
    '     AND NOT EXISTS (SELECT 1 FROM "{s}".miscari_stoc r WHERE r.anuleaza_id = m.id);\n'
    '  IF FOUND THEN\n'
    "    RAISE EXCEPTION 'REGULA_CONTABILA: Vânzarea a scos bunul din stoc (ieșirea „%”). Anulează întâi ieșirea (respinge-i nota din "
    "„De validat”), apoi șterge nota vânzării — altfel bunul ar rămâne ieșit din gestiune fără vânzare.', doc;\n"
    '  END IF;\n'
    '  RETURN OLD;\n'
    'END $$ LANGUAGE plpgsql;',
    'DROP TRIGGER IF EXISTS trg_vanzare_stoc_sterge ON "{s}".inregistrari;',
    'CREATE TRIGGER trg_vanzare_stoc_sterge BEFORE DELETE ON "{s}".inregistrari '
    'FOR EACH ROW EXECUTE FUNCTION "{s}".vanzare_stoc_sterge();',
]


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
        cur.execute("SELECT to_regclass(%s) IS NOT NULL AND EXISTS (SELECT 1 FROM pg_trigger t JOIN pg_class c ON c.oid = t.tgrelid "
                    "JOIN pg_namespace ns ON ns.oid = c.relnamespace WHERE ns.nspname = %s AND t.tgname = 'trg_vanzare_stoc_sterge')",
                    ('"%s".vanzari_din_stoc' % schema, schema))
        return bool(cur.fetchone()[0])


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
    print("migrare_vanzari_stoc: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        sys.exit(1)


if __name__ == "__main__":
    _main()
