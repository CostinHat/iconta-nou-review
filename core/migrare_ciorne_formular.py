"""
core/migrare_ciorne_formular.py — ciornele formularelor începute, pe server (deficiența 495, lotul 12, comanda 12.1, cu clasa ei).

Costin: „Factură: Ciorna facturii e salvată doar în browser; pe alt calculator nu se regăsește.” Ciorna stătea numai în `localStorage`
(`emitere_ecran.js`, cheia `iconta_ciorna_factura:<utilizator>:<firmă>`), deci pe alt calculator sau în alt browser formularul pornea
gol. Aceeași clasă: ciornele formularelor lungi de creare (`static/js/ciorna_formular.js`: salariatul nou, concediul medical).

- `public.ciorne_formular` — o ciornă pe UTILIZATOR + FIRMĂ + FORMULAR (cheia primară): ciorna unui utilizator nu apare la altul,
  nici la altă firmă (deficiența 65). `formular` = „factura”, „salariat_nou”, „concediu_medical:<id salariat>”; `continut` = formularul
  așa cum l-a lăsat omul, `salvat_la` = ultima scriere. Rândul se șterge la salvarea / emiterea documentului și la „Renunță”
  (`core/ciorne_formular.py`). Utilizatorul sau firma șterse își iau ciornele cu ele (ON DELETE CASCADE).

Datele existente: tabela pornește goală; ciornele rămase în browserul fiecăruia se urcă pe server la prima deschidere a formularului
(`emitere_ecran.js` `incarcaCiorna`, `ciorna_formular.js`). Idempotent (CREATE TABLE IF NOT EXISTS). Se aplică prin
`python -m core.migrari_registru ruleaza [--productie] core/migrare_ciorne_formular.py`.
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS public.ciorne_formular (
    user_id     integer NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    tenant_id   integer NOT NULL REFERENCES public.tenants(id) ON DELETE CASCADE,
    formular    varchar(60) NOT NULL CHECK (formular ~ '^[a-z][a-z0-9_]{0,40}(:[0-9]{1,12})?$'),
    continut    jsonb NOT NULL CHECK (jsonb_typeof(continut) = 'object'),
    salvat_la   timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, tenant_id, formular)
);
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.ciorne_formular') IS NOT NULL")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_ciorne_formular: tabela %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
