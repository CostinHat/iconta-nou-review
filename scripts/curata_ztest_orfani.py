# -*- coding: utf-8 -*-
"""[Faza 0, Sesiunea B] Curatare one-shot a tenantilor de TEST ORFANI (`ztest_*`, fara cabinet).

Context: dupa stergerea celor 55 de cabinete de test (gdpr_sterge), au ramas 19 randuri `tenants`
+ scheme `ztest_%` cu `accounting_firm_id IS NULL` — reziduu din rulari de test, fara cabinet.

GARD DE SCOP (hard): sterge EXCLUSIV tenants cu `schema_name LIKE 'ztest\\_%'` SI
`accounting_firm_id IS NULL`. Orice tenant real (cu cabinet) sau cu alta schema NU e atins — un
`assert` opreste inainte de orice stergere daca tinta nu respecta ambele conditii. Idempotent:
daca nu mai sunt orfani, e no-op. Foloseste calea canonica `tenant_stergere.sterge` (R72:
cele 13 tabele cu tenant_id + DROP SCHEMA + fisiere disc), apoi sterge randul din public.tenants.
"""
import os as _os
import sys as _sys

# Self-contained: radacina repo pe path + incarca ~/.iconta/db.env, ca sa poata fi rulat printr-o
# comanda SIMPLA (`./venv/bin/python scripts/curata_ztest_orfani.py`) sub o regula de permisiune ingusta.
_RAD = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _RAD not in _sys.path:
    _sys.path.insert(0, _RAD)
_ENV = _os.path.expanduser("~/.iconta/db.env")
if _os.path.exists(_ENV):
    for _ln in open(_ENV, encoding="utf-8"):
        _ln = _ln.strip()
        if _ln.startswith("export "):
            _ln = _ln[len("export "):]
        if "=" in _ln and not _ln.startswith("#"):
            _k, _, _v = _ln.partition("=")
            _os.environ.setdefault(_k.strip(), _v.strip())

from core import db, tenant_stergere


def orfani(cur):
    """Tenants de test orfani: schema ztest_ SI fara cabinet. Doar acestia sunt tinta."""
    cur.execute(r"""SELECT id, schema_name FROM public.tenants
                    WHERE schema_name LIKE 'ztest\_%' AND accounting_firm_id IS NULL
                    ORDER BY id""")
    return cur.fetchall()


def scheme_orfane(cur):
    """Scheme `ztest_%` FARA niciun rand in public.tenants (reziduu de test pur, fara entitate).
    Doar prefixul `ztest_` e tinta — nicio schema `tenant_%` sau alta nu intra aici."""
    cur.execute(r"""SELECT schema_name FROM information_schema.schemata
                    WHERE schema_name LIKE 'ztest\_%'
                      AND schema_name NOT IN (SELECT schema_name FROM public.tenants WHERE schema_name IS NOT NULL)
                    ORDER BY 1""")
    return [r[0] for r in cur.fetchall()]


def main():
    db.init_pool()
    with db.get_conn() as c:
        with c.cursor() as cur:
            tinte = orfani(cur)
    sterse = 0
    if not tinte:
        print("niciun tenant ztest_ orfan (randuri) — trec la scheme orfane")
    for tid, sch in tinte:
        # GARD: reconfirma, pe fiecare, ca e chiar ztest_ orfan INAINTE de a-l atinge
        with db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT schema_name, accounting_firm_id FROM public.tenants WHERE id=%s", (tid,))
                r = cur.fetchone()
                assert r is not None, "tenant %s disparut intre listare si stergere" % tid
                assert r[0] and r[0].startswith("ztest_") and r[1] is None, \
                    "STOP: tenant %s NU e ztest_ orfan (schema=%r firm_id=%r) — refuz" % (tid, r[0], r[1])
            tenant_stergere.sterge(c, tid, "gdpr_cabinet", 1)
            with c.cursor() as cur:
                cur.execute("DELETE FROM public.tenants WHERE id=%s", (tid,))
            c.commit()
        if sch:
            tenant_stergere.sterge_fisiere(sch)
        sterse += 1
    print("tenants ztest_ orfani stersi:", sterse)

    # Scheme `ztest_%` pur orfane (fara rand tenant) — DROP direct, cu gard de prefix.
    # Commit per schema: un singur DROP CASCADE pe o schema cu ~100 tabele consuma multe lock-uri;
    # 18 intr-o tranzactie depasesc max_locks_per_transaction.
    with db.get_conn() as c:
        with c.cursor() as cur:
            scheme = scheme_orfane(cur)
    drop = 0
    for s in scheme:
        assert s.startswith("ztest_"), "STOP: schema %r nu incepe cu ztest_ — refuz DROP" % s
        with db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % s)
            c.commit()
        drop += 1
    print("scheme ztest_ pur orfane dropate:", drop)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
