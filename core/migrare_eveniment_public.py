# -*- coding: utf-8 -*-
"""Migrare: tabela public.eveniment_public — analytics public FARA date personale.

Stocheaza DOAR evenimentul: ce (tip), de unde (pagina proprie), cand (creat_la).
NU are: ip, user_agent, cookie/session, user_id, amprenta browser - nimic care sa identifice o persoana.
Din acest motiv NU exista obligatie de consimtamant (fara date personale). Idempotent (IF NOT EXISTS).
Rulare: venv/bin/python3 -m core.migrare_eveniment_public
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS public.eveniment_public (
  id       bigserial PRIMARY KEY,
  tip      text NOT NULL,          -- ce: tip eveniment din lista alba (validat server-side)
  pagina   text,                   -- de unde: calea/slug-ul propriei pagini (landing / slug de ghid)
  creat_la timestamptz NOT NULL DEFAULT now()   -- cand
);
CREATE INDEX IF NOT EXISTS ix_eveniment_public_creat_la ON public.eveniment_public (creat_la);
CREATE INDEX IF NOT EXISTS ix_eveniment_public_tip ON public.eveniment_public (tip);
"""


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()
    print("migrare_eveniment_public: OK")


if __name__ == "__main__":
    _main()
