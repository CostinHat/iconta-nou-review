# -*- coding: utf-8 -*-
"""core/migrare_plan_conturi_omfp.py — conturile planului general OMFP 1802/2014 care lipsesc din planul fiecărei firme (deficiența 387,
comanda Costin 9.1, 19.10.2026: „Plan de conturi: lipsește 609 (Reduceri comerciale primite). Planul are 184 de conturi — compară-l integral
cu OMFP 1802/2014.”).

Planul firmelor noi (`tenant_template.sql`, „[p97_plan_seed]”) e acum planul întreg din ordin, generat (`scripts/plan_conturi_omfp.py` ->
`core/plan_conturi_omfp.PLAN`, 577 de conturi de gradul I și II). Firmele existente au pornit de la lista veche (184); aici primesc ce lipsește.

Adaugă numai ce lipsește (`ON CONFLICT DO NOTHING`): un cont pe care firma îl are deja — cu rulaje, cu o denumire din importul SAGA sau din
lista veche — rămâne neatins, la fel analiticele (`4428.01`, `401.05` …). Nu scrie în note și nu schimbă solduri. Toate firmele, ca
șablonul (și PFA-ul are planul în schemă, deși ecranele lui nu-l arată). Idempotentă.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_plan_conturi_omfp.py`.
"""
from core import db
from core.plan_conturi_omfp import PLAN


def aplica(conn, schema):
    """Câte conturi a adăugat; None dacă schema n-are plan de conturi (nu e o firmă)."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = %s AND table_name = 'plan_conturi'", (schema,))
        if cur.fetchone()[0] < 1:
            return None
        n = 0
        for simbol, (denumire, _functie) in PLAN.items():
            cur.execute('INSERT INTO "%s".plan_conturi (simbol, denumire, tip) VALUES (%%s, %%s, \'Bifunctional\') '
                        'ON CONFLICT (simbol) DO NOTHING' % schema, (simbol, denumire))
            n += cur.rowcount
    return n


def _main():
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE schema_name IS NOT NULL ORDER BY id")
        scheme = [r[0] for r in cur.fetchall()]
    total, atinse = 0, 0
    for s in scheme:
        with db.get_conn() as conn:
            n = aplica(conn, s)
            conn.commit()
        if n:
            total += n
            atinse += 1
    print("planul OMFP 1802/2014: %d conturi adăugate pe %d din %d scheme" % (total, atinse, len(scheme)))


if __name__ == "__main__":
    _main()
