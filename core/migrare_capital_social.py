# -*- coding: utf-8 -*-
"""core/migrare_capital_social.py — forma juridică + capitalul social pe firma_profil (lot 19, defectul 12, 03.10.2026).

Legea 31/1990 art.74 alin.(3): factura unui SRL menționează capitalul social; a unui SA/SCA, capitalul subscris și pe
cel vărsat (v. core/capital_social.py). Coloanele sunt NULL implicit: o valoare inventată ar ajunge pe factură; lipsa
lor la o persoană juridică oprește emiterea, cu trimitere la Date firmă. Sursa UNICA a DDL-ului (mirror în
tenant_template.sql). Idempotent. Se aplică pe ORICE schemă care are firma_profil.
`python3 -m core.migrare_capital_social`.
"""
from core import db

DDL = [
    'ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS forma_juridica character varying(4);',
    'ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS capital_subscris numeric(18,2);',
    'ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS capital_varsat numeric(18,2);',
    'ALTER TABLE "{s}".firma_profil DROP CONSTRAINT IF EXISTS forma_juridica_valida;',
    'ALTER TABLE "{s}".firma_profil ADD CONSTRAINT forma_juridica_valida CHECK '
    "(forma_juridica IS NULL OR forma_juridica IN ('SRL', 'SA', 'SCA', 'SNC', 'SCS', 'ALTA'));",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for d in DDL:
            cur.execute(d.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name="
                    "'firma_profil' AND column_name IN ('forma_juridica','capital_subscris','capital_varsat')", (schema,))
        return cur.fetchone()[0] == 3


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables WHERE table_name='firma_profil' "
                        "ORDER BY 1")
            scheme = [r[0] for r in cur.fetchall()]
        ok, esec = 0, []
        for s in scheme:
            try:
                aplica(conn, s)
                conn.commit()
                ok += 1 if verifica(conn, s) else 0
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, str(e)))
        print("migrare capital_social: %d/%d ok" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
