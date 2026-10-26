# -*- coding: utf-8 -*-
"""Scoaterea firmelor sintetice ale plasei de capăt la capăt — o singură definiție, folosită de `conftest.py` (la sfârșitul rulării) și
de `scripts/e2e_poarta.py` (DUPĂ oprirea aplicației: prins 09.10.2026 — aplicația își recalculează rezumatul firmei în fundal și scria
`firma_rezumat` / `firma_sursa_versiune` după ce firma fusese ștearsă, lăsând rânduri spre o firmă inexistentă)."""
import os

PREFIX_FIRMA = "E2E Probă"


def registru_firme():
    """Fișierul în care conftest notează firmele create (id, schemă), în directorul rulării."""
    return os.path.join(os.environ.get("E2E_TEMP", "/tmp/e2e_poarta"), "firme_create.txt")


def scoate(db, firme, incercari=5):
    """[(tenant_id, schemă)]: rândurile din tabelele publice cu `tenant_id`, rândul firmei, schema. Numai firmele probei (prefixul).

    [15.10.2026, poarta a treia a lotului 3] O firmă pe tranzacția ei, reluată la DEADLOCK: `DROP SCHEMA … CASCADE` ia blocări
    exclusive pe toate tabelele schemei, iar o cerere a paginii încă deschise (aplicația citește aceeași firmă) le ia în altă ordine —
    Postgres oprește una din ele („deadlock detected”, la curățarea testului 243). Tranzacția anulată se reia întreagă; după
    `incercari` reluări eroarea urcă, vizibilă."""
    import time
    from psycopg2 import errors
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT c.table_name FROM information_schema.columns c JOIN information_schema.tables t ON t.table_schema = "
                    "c.table_schema AND t.table_name = c.table_name AND t.table_type = 'BASE TABLE' WHERE c.table_schema = 'public' "
                    "AND c.column_name = 'tenant_id' AND c.table_name <> 'tenants'")
        tabele = [r[0] for r in cur.fetchall()]
    tabele = sorted(tabele)
    for tid, schema in firme:
        for incercare in range(1, incercari + 1):
            try:
                _scoate_una(db, tabele, tid, schema)
                break
            except (errors.DeadlockDetected, errors.LockNotAvailable):
                # [C201, lotul 13] `LockNotAvailable`: `DROP SCHEMA` a așteptat peste `lock_timeout` (db.optiuni_sesiune) o cerere a
                # aplicației încă deschise; se reia ca deadlock-ul, în loc să aștepte la nesfârșit (blocajul de 38 de minute din C201)
                if incercare == incercari:
                    raise
                time.sleep(0.5 * incercare)


def _scoate_una(db, tabele, tid, schema):
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT nume FROM public.tenants WHERE id = %s", (tid,))
        r = cur.fetchone()
        if r and not str(r[0]).startswith(PREFIX_FIRMA):
            return                                         # nu e o firmă a probei: nu se atinge
        from core.tenant_stergere import ordinea_stergerii   # [lotul 11] contoarele derivate la urmă (altfel ștergerea unei surse le recrea)
        for t in ordinea_stergerii(tabele):
            cur.execute('DELETE FROM public."%s" WHERE tenant_id = %%s' % t, (tid,))
        cur.execute("DELETE FROM public.tenants WHERE id = %s", (tid,))
        if schema and schema.startswith("tenant_") and db.schema_valida(schema):
            cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % schema)
        c.commit()
