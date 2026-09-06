# -*- coding: utf-8 -*-
"""core/migrare_plata_referinte.py — R43: referința de plată își știe FIRMA, iar plata simulată o spune.

Sursa UNICA a DDL-ului. Idempotent. Aplică pe existenți: `python3 -m core.migrare_plata_referinte`.

CE ADAUGĂ, și de ce fiecare:

  - **`public.plata_referinte`** — `ref` → firma care l-a emis. Până azi,
    `POST /public/plata/{ref}/confirma` **parcurgea toate schemele** din `public.tenants` și încerca
    un `UPDATE` în fiecare, până la prima potrivire. O rută neautentificată care scrie prin toate
    firmele nu e o validare lipsă, e o suprafață: nu scurge date (răspunsul e doar `{ok}`, iar `ref`
    e de 128 de biți), dar **nu există nicio barieră structurală** care să oprească o referință dintr-o
    firmă să atingă alta.
    `ref` e **PRIMARY KEY**, deci coliziunea între firme devine **imposibilă prin construcție**, nu
    doar improbabilă — iar ruta pleacă de la firmă, nu o caută.

  - **`facturi.plata_confirmata_de`** — CINE a confirmat plata. Pe calea `mock` valoarea e `'mock'`,
    adică **o simulare**, și se vede în evidență. Condiția lui R43 o cere textual: *„se închide
    parțial dacă `platita_la` scris pe calea mock poartă o marcă de simulare care se vede în
    evidență"*. Fără ea, `platita_la` e o afirmație despre bani pe care nimic n-o distinge de un
    buton apăsat.

CE NU ÎNCHIDE, declarat: confirmarea tot **nu vine de la un procesator real, semnată** — aia cere
chei de la Costin (`cine deblochează: EXTERN`). R43 rămâne deschisă pe partea aia.

BACKFILL: niciunul necesar. Măsurat 06.09.2026, pe toate cele 20 de firme: **0 facturi cu
`plata_ref`**, deci nicio referință existentă de mapat. Se scrie aici ca să nu se creadă, peste un
an, că migrarea a uitat trecutul.
"""
from core import db

DDL_PUBLIC = """
CREATE TABLE IF NOT EXISTS public.plata_referinte (
  ref         text PRIMARY KEY,
  tenant_id   integer NOT NULL,
  schema_name text NOT NULL,
  factura_id  integer NOT NULL,
  creat_la    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_plata_referinte_tenant ON public.plata_referinte (tenant_id);
"""

DDL_SCHEMA = """
ALTER TABLE {schema}.facturi ADD COLUMN IF NOT EXISTS plata_confirmata_de character varying(20);
"""


def aplica(conn, scheme=None):
    """Aplică DDL-ul public + coloana pe fiecare schemă de firmă. Întoarce numărul de scheme atinse."""
    with conn.cursor() as cur:
        cur.execute(DDL_PUBLIC)
        if scheme is None:
            cur.execute("SELECT schema_name FROM public.tenants ORDER BY id")
            scheme = [r[0] for r in cur.fetchall()]
        for s in scheme:
            cur.execute(DDL_SCHEMA.format(schema=s))
    conn.commit()
    return len(scheme)


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        n = aplica(conn)
    print("migrare_plata_referinte: OK · %d scheme de firmă" % n)


if __name__ == "__main__":
    _main()
