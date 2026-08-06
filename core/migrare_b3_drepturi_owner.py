# -*- coding: utf-8 -*-
"""Backfill B3: deblocheaza proprietarii de cabinet (admin_firma) existenti care au fost creati
fara drepturi operationale (poate_pregati/valida/depune=false). public.users, o singura data."""
from core import db


def main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE public.users SET poate_pregati=true, poate_valida=true, poate_depune=true "
                        "WHERE rol='admin_firma' AND NOT (poate_pregati AND poate_valida AND poate_depune)")
            n = cur.rowcount
    print("Backfill B3: %d proprietari admin_firma deblocati" % n)
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, poate_pregati, poate_valida, poate_depune FROM public.users WHERE rol='admin_firma'")
            for r in cur.fetchall():
                print("  admin_firma id=%s pregati=%s valida=%s depune=%s" % tuple(r))


if __name__ == "__main__":
    main()
