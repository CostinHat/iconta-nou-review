# -*- coding: utf-8 -*-
"""core/migrare_decizii_0810_s6.py — partea de bază a lotului „Deciziile 08.10 §6” (comanda Costin, verbatim în DECIZII 08.10.2026).

  · §6 pct.3  analiticul de ACHIZIȚIE al lui 4428 (`nir_legare.CONT_TVA_NIR` = 4428.01, „TVA neexigibilă — achiziții fără factură
              (NIR)”) în planul de conturi al fiecărei firme: TVA-ul NIR-ului fără factură stă acolo până la factură.
  · §6 pct.4  `firma_profil.luna_preluare` (prima zi a lunii): luna preluării, editabilă în Date firmă (NULL = propunerea dedusă).
Sursa UNICĂ (mirror în tenant_template.sql). Idempotentă. `python3 -m core.migrare_decizii_0810_s6`.
"""
from core import db

DDL_SCHEMA = [
    """INSERT INTO "{s}".plan_conturi (simbol, denumire, tip) VALUES ('4428.01', 'TVA neexigibilă — achiziții fără factură (NIR)',
       'Bifunctional') ON CONFLICT (simbol) DO NOTHING;""",
    'ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS luna_preluare date;',
]


def aplica(conn, schema):
    """DDL-ul pe schema unei firme. False dacă schema n-are `plan_conturi`."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='plan_conturi'", (schema,))
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
    print("4428.01 + firma_profil.luna_preluare: %d/%d scheme" % (ok, len(scheme)))


if __name__ == "__main__":
    _main()
