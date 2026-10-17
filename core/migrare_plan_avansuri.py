# -*- coding: utf-8 -*-
"""core/migrare_plan_avansuri.py — conturile de avans 4092 / 4093 / 4094 în planul fiecărei firme (C48, găsită de Code la deficiența 312,
17.10.2026).

312 (comanda Costin 17.10.2026 7.2 pct.4, verbatim în DECIZII): „La 312: contul propus pentru 401 debitor e 4091 sau 4092, nu 409.”
Planul firmelor noi (`tenant_template.sql`, „[p97_plan_seed]”) avea 409 și 4091, dar nu 4092, 4093, 4094 — deși aplicația le folosește
singură pentru avansurile acordate (`core/avansuri.CONT_AVANS`: servicii 4092, imobilizări corporale 4093, necorporale 4094), iar o notă pe
un cont care nu e în planul firmei e refuzată (`core/cont_valid.py`). Denumirile, din planul de conturi OMFP 1802/2014
(`anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`): „4092. Furnizori - debitori pentru prestări de servicii”, „4093. Avansuri
acordate pentru imobilizări corporale”, „4094. Avansuri acordate pentru imobilizări necorporale”.

Adaugă numai ce lipsește (`ON CONFLICT DO NOTHING`): un cont pe care firma îl are deja (cu altă denumire, din importul SAGA) rămâne neatins.
Nu scrie în note. Idempotentă. Rulare: `python -m core.migrari_registru ruleaza --productie core/migrare_plan_avansuri.py`.
"""
from core import db

CONTURI = (("4092", "Furnizori - debitori pentru prestări de servicii"),
           ("4093", "Avansuri acordate pentru imobilizări corporale"),
           ("4094", "Avansuri acordate pentru imobilizări necorporale"))


def aplica(conn, schema):
    """Câte conturi a adăugat; None dacă schema n-are plan de conturi (nu e o firmă)."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = %s AND table_name = 'plan_conturi'", (schema,))
        if cur.fetchone()[0] < 1:
            return None
        n = 0
        for simbol, denumire in CONTURI:
            cur.execute('INSERT INTO "%s".plan_conturi (simbol, denumire, tip) VALUES (%%s, %%s, \'Bifunctional\') '
                        'ON CONFLICT (simbol) DO NOTHING' % schema, (simbol, denumire))
            n += cur.rowcount
    return n


def _main():
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE schema_name IS NOT NULL ORDER BY id")
        scheme = [r[0] for r in cur.fetchall()]
    total = 0
    for s in scheme:
        with db.get_conn() as conn:
            total += aplica(conn, s) or 0
            conn.commit()
    print("conturile de avans 4092 / 4093 / 4094: %d adăugate pe %d scheme" % (total, len(scheme)))


if __name__ == "__main__":
    _main()
