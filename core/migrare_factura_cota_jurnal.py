# -*- coding: utf-8 -*-
"""core/migrare_factura_cota_jurnal.py — jurnalul cotei TVA alese pe linia facturii (decizia Costin 05.10.2026).

Decizia: „Cota TVA pe linie: … contabilul poate corecta cota; schimbarea rămâne consemnată (propus → ales, cine, când).” Un rând
pe fiecare linie emisă cu altă cotă decât cea propusă automat. Tabelul stă în schema FIRMEI (ca `firma_profil_jurnal`): o
factură se păstrează zece ani, iar `public.audit_log` se șterge după 12 luni. Sursa UNICĂ a DDL-ului (mirror în
tenant_template.sql). Idempotent. Pe ORICE schemă care are `facturi`.
Legătura cu factura e ON DELETE CASCADE, ca la `factura_linii`: o factură necontată se poate șterge, iar rândurile cotei sunt
atributul liniilor ei. Tabelele create în prima rulare (05.10.2026, fără CASCADE) primesc legătura refăcută.
Tenanți NOI prin template; EXISTENȚI prin `python3 -m core.migrare_factura_cota_jurnal`.
"""
from core import db

DDL = ('CREATE TABLE IF NOT EXISTS "{s}".factura_cota_jurnal ('
       ' id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,'
       ' factura_id integer NOT NULL REFERENCES "{s}".facturi(id) ON DELETE CASCADE,'
       ' linie_nr integer NOT NULL,'
       ' descriere text,'
       ' cota_propusa numeric(5,2) NOT NULL,'
       ' cota_aleasa numeric(5,2) NOT NULL,'
       ' user_id integer NOT NULL,'
       ' la timestamp with time zone NOT NULL DEFAULT now());')


_FK = ("SELECT conname, confdeltype FROM pg_constraint "
       "WHERE conrelid = %s::regclass AND contype = 'f' AND confrelid = %s::regclass")


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))
        cur.execute(_FK, ('"%s".factura_cota_jurnal' % schema, '"%s".facturi' % schema))
        for nume, regula in cur.fetchall():
            if regula != "c":
                cur.execute('ALTER TABLE "%s".factura_cota_jurnal DROP CONSTRAINT "%s"' % (schema, nume))
                cur.execute('ALTER TABLE "%s".factura_cota_jurnal ADD CONSTRAINT "%s" FOREIGN KEY (factura_id) '
                            'REFERENCES "%s".facturi(id) ON DELETE CASCADE' % (schema, nume, schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ('"%s".factura_cota_jurnal' % schema,))
        if cur.fetchone()[0] is None:
            return False
        cur.execute(_FK, ('"%s".factura_cota_jurnal' % schema, '"%s".facturi' % schema))
        return [r[1] for r in cur.fetchall()] == ["c"]


def scheme_cu_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables "
                    "WHERE table_name='facturi' ORDER BY 1")
        return [r[0] for r in cur.fetchall()]


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        scheme = scheme_cu_tabela(conn)
        ok, esec = 0, []
        for s in scheme:
            try:
                aplica(conn, s)
                conn.commit()
                ok += 1 if verifica(conn, s) else 0
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, str(e)))
        print("migrare factura_cota_jurnal: %d/%d ok" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
