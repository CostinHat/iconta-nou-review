"""
core/migrare_sanatate_load15.py — alerta de load pe media pe 15 minute, ținută, și niciodată din rulările de teste (comanda Costin
15.10.2026 noaptea, „Lotul 5 — comanda 3” pct.6b, verbatim în DECIZII: „Alerta de load pleacă doar dacă media pe 15 minute depășește un
prag calculat pe numărul de procesoare și rămâne așa; nu pleacă în timpul rulărilor tale de teste.”).

`public.metrici_sanatate` (un rând la 5 minute, scris de bucla de sănătate din `main.py`) primește:
- `load15` — media pe 15 minute a încărcării (`os.getloadavg()[2]`);
- `teste` — dacă la acel ciclu rula o probă / o suită de teste pe server (`core.rulari_teste.in_curs`).
Alerta se decide din istoric (`main._load_de_alertat`), nu dintr-o singură măsurătoare. Idempotent (ADD COLUMN IF NOT EXISTS). Se aplică
prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_sanatate_load15.py`.
"""
from core import db

DDL = """
ALTER TABLE public.metrici_sanatate ADD COLUMN IF NOT EXISTS load15 numeric;
ALTER TABLE public.metrici_sanatate ADD COLUMN IF NOT EXISTS teste boolean;
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 2 FROM information_schema.columns WHERE table_schema = 'public' "
                    "AND table_name = 'metrici_sanatate' AND column_name IN ('load15', 'teste')")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_sanatate_load15: coloanele %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
