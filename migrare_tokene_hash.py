# -*- coding: utf-8 -*-
"""migrare_tokene_hash.py — tokene_activare: token in CLAR -> DOAR hash sha256 (magic-link + activare).

Idempotent. Securitate: un dump/backup nu mai permite impersonarea (tokenul in clar traieste doar in link).
ACTIVE la migrare = 0 -> tokenurile vechi se INVALIDEAZA (nu se hash-uiesc); niciun link valid nu moare.
Ruleaza cu env sourcat:  set -a; . ~/.iconta/db.env; set +a; python3 migrare_tokene_hash.py
"""
from core import db

DDL = [
    "ALTER TABLE public.tokene_activare ADD COLUMN IF NOT EXISTS token_hash text",
    # invalideaza tokenurile vechi (in clar) — 0 active azi, deci niciun link valid nu moare
    "DELETE FROM public.tokene_activare WHERE token_hash IS NULL",
    "ALTER TABLE public.tokene_activare DROP CONSTRAINT IF EXISTS tokene_activare_pkey",
    "ALTER TABLE public.tokene_activare DROP COLUMN IF EXISTS token",
    "CREATE UNIQUE INDEX IF NOT EXISTS ix_tokene_activare_token_hash ON public.tokene_activare(token_hash)",
]


def main():
    db.init_pool()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT count(*) FROM public.tokene_activare WHERE NOT folosit AND expira > now()")
        print("ACTIVE inainte de migrare:", cur.fetchone()[0])
        for stmt in DDL:
            cur.execute(stmt)
            print("OK:", stmt[:70])
        c.commit()
        cur.execute("SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema='public' AND table_name='tokene_activare' ORDER BY ordinal_position")
        print("coloane dupa:", [r[0] for r in cur.fetchall()])
        cur.execute("SELECT indexdef FROM pg_indexes WHERE tablename='tokene_activare'")
        print("indexuri dupa:", [r[0] for r in cur.fetchall()])


if __name__ == "__main__":
    main()
