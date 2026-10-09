# -*- coding: utf-8 -*-
"""Scoaterea firmelor sintetice ale plasei de capăt la capăt — o singură definiție, folosită de `conftest.py` (la sfârșitul rulării) și
de `scripts/e2e_poarta.py` (DUPĂ oprirea aplicației: prins 09.10.2026 — aplicația își recalculează rezumatul firmei în fundal și scria
`firma_rezumat` / `firma_sursa_versiune` după ce firma fusese ștearsă, lăsând rânduri spre o firmă inexistentă)."""
import os

PREFIX_FIRMA = "E2E Probă"


def registru_firme():
    """Fișierul în care conftest notează firmele create (id, schemă), în directorul rulării."""
    return os.path.join(os.environ.get("E2E_TEMP", "/tmp/e2e_poarta"), "firme_create.txt")


def scoate(db, firme):
    """[(tenant_id, schemă)]: rândurile din tabelele publice cu `tenant_id`, rândul firmei, schema. Numai firmele probei (prefixul)."""
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT c.table_name FROM information_schema.columns c JOIN information_schema.tables t ON t.table_schema = "
                    "c.table_schema AND t.table_name = c.table_name AND t.table_type = 'BASE TABLE' WHERE c.table_schema = 'public' "
                    "AND c.column_name = 'tenant_id' AND c.table_name <> 'tenants'")
        tabele = [r[0] for r in cur.fetchall()]
        for tid, schema in firme:
            cur.execute("SELECT nume FROM public.tenants WHERE id = %s", (tid,))
            r = cur.fetchone()
            if r and not str(r[0]).startswith(PREFIX_FIRMA):
                continue                                   # nu e o firmă a probei: nu se atinge
            for t in tabele:
                cur.execute('DELETE FROM public."%s" WHERE tenant_id = %%s' % t, (tid,))
            cur.execute("DELETE FROM public.tenants WHERE id = %s", (tid,))
            if schema and schema.startswith("tenant_") and db.schema_valida(schema):
                cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % schema)
        c.commit()
