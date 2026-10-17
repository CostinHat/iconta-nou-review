# -*- coding: utf-8 -*-
"""core/migrare_poveste_amprenta.py — amprenta cifrelor pe care s-a aprobat povestea lunii (deficiența 314, comanda Costin 17.10.2026 7.2
pct.7, verbatim în DECIZII: „314: povestea aprobată se marchează depășită și Trimite se oprește dacă cifrele lunii s-au schimbat după
aprobare.”).

`public.pachet_povestea.cifre_amprenta` — scrisă la aprobare (`pachete_api.amprenta_cifre`: venituri, cheltuieli, rezultat, declarațiile
depuse ale lunii). O poveste aprobată înainte de coloană n-are amprentă: nu se poate ști pe ce cifre s-a aprobat, deci e depășită până la o
nouă aprobare. Idempotentă. Rulare: `python -m core.migrari_registru ruleaza --productie core/migrare_poveste_amprenta.py`.
"""
from core import db

DDL = "ALTER TABLE public.pachet_povestea ADD COLUMN IF NOT EXISTS cifre_amprenta text;"


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
    print("migrare_poveste_amprenta: aplicată")


if __name__ == "__main__":
    _main()
