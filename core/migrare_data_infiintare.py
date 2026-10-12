# -*- coding: utf-8 -*-
"""core/migrare_data_infiintare.py — `firma_profil.data_infiintare` (deficiența 229, comanda Costin 12.10.2026, verbatim în DECIZII:
„dacă firma s-a înființat în anul bilanțului, coloana «An precedent» rămâne legal goală (primul exercițiu) și nu se cere completarea
manuală. Ține cont de data înființării.”).

Data înființării: din ANAF (`date_generale.data_inregistrare`, `anaf_surse/doc_WS_V9.txt`) la adăugarea firmei, editabilă în Date firmă.
NULL = necunoscută (bilanțul cere coloana „An precedent” ca până acum). Sursa UNICĂ (mirror în tenant_template.sql). Idempotentă.
`python3 -m core.migrari_registru ruleaza --productie core/migrare_data_infiintare.py`.
"""
from core import db

DDL_SCHEMA = ['ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS data_infiintare date;']


def aplica(conn, schema):
    """DDL-ul pe schema unei firme. False dacă schema n-are `firma_profil`."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='firma_profil'", (schema,))
        if not cur.fetchone():
            return False
        for d in DDL_SCHEMA:
            cur.execute(d.format(s=schema))
    return True


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants ORDER BY id")
            scheme = [x[0] for x in cur.fetchall()]
        ok = 0
        for s in scheme:
            try:
                ok += 1 if aplica(conn, s) else 0
                conn.commit()
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                print("  ESEC", s, e)
    print("firma_profil.data_infiintare: %d/%d scheme" % (ok, len(scheme)))


if __name__ == "__main__":
    _main()
