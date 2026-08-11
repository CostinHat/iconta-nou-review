# -*- coding: utf-8 -*-
"""core/migrare_bun_venit.py — flag "pagina de bun-venit vazuta" per user.

Sursa UNICA a DDL-ului. Idempotent (ADD COLUMN IF NOT EXISTS).
Aplica pe existenti: `python3 -m core.migrare_bun_venit`.

Ce adauga:
  - users.bun_venit_vazut_la: timestamptz. NULL = userul n-a vazut inca prezentarea de
    ansamblu la prima logare -> se afiseaza o data, apoi se seteaza now() si nu mai apare.
    Prezentarea ramane accesibila oricand prin semnul "?" general din bara de stare.
"""
from core import db

DDL = """
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS bun_venit_vazut_la timestamptz;
"""


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()
    print("migrare_bun_venit: OK")


if __name__ == "__main__":
    _main()
