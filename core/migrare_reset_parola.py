# -*- coding: utf-8 -*-
"""core/migrare_reset_parola.py — resetare parola cont cabinet ("Am uitat parola").

Sursa UNICA a DDL-ului. Idempotent (CREATE ... IF NOT EXISTS / ADD COLUMN IF NOT EXISTS).
Aplica pe existenti: `python3 -m core.migrare_reset_parola`.

Ce adauga:
  - public.reset_parola_token: tokenuri de resetare stocate HASH-UIT (sha256), single-use,
    expira 60 min. Index pe token_hash (cautat la fiecare validare). Curatarea expiratelor
    se face la fiecare scriere (core.reset_parola.cere_reset), tabelul nu creste la nesfarsit.
  - users.sesiuni_valide_de: dupa schimbarea parolei se seteaza now(); tokenurile emise INAINTE
    (iat < sesiuni_valide_de) sunt respinse la cere_cabinet -> sesiunile vechi mor.
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS public.reset_parola_token (
  id serial PRIMARY KEY,
  user_id integer NOT NULL,
  token_hash text NOT NULL,
  expira timestamptz NOT NULL,
  folosit boolean NOT NULL DEFAULT false,
  creat_la timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_reset_parola_token_hash ON public.reset_parola_token (token_hash);
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS sesiuni_valide_de timestamptz;
"""


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()
    print("migrare_reset_parola: OK")


if __name__ == "__main__":
    _main()
