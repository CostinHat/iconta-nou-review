"""
core/migrare_spv_citiri.py — `public.spv_cui_acoperit`: ultima citire SPV a fiecărei firme (CUI) pe tokenul cabinetului.

Comanda Costin 16.10.2026, „Lotul 6, comanda 1” pct.7a (273), verbatim în DECIZII: „Ecranul spune dacă firma e conectată la SPV și când s-a
verificat ultima dată”; a treia completare pct.2b („când rulează citirea automată pentru o firmă nou adăugată”). Tabela exista
(`spv_conector_ddl_v1.sql`, ARHITECTURA_SPV.md: „spv_cui_acoperit se populează EMPIRIC — apel per CIF la listaMesajeFactura”), dar n-o
scria nimeni. Acum o scrie `spv_receive.citeste_firma` la fiecare citire: `verificat_la`, `are_drept` (din textul ANAF), plus coloanele noi
`eroare` (răspunsul ANAF), `mesaje` (câte la ultima citire), `ultima_reusita` (prima citire reușită pe token cuprinde 60 de zile).
Idempotent (ADD COLUMN IF NOT EXISTS). Se aplică prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_spv_citiri.py`.
"""
from core import db

DDL = """
ALTER TABLE public.spv_cui_acoperit ADD COLUMN IF NOT EXISTS eroare text;
ALTER TABLE public.spv_cui_acoperit ADD COLUMN IF NOT EXISTS mesaje integer;
ALTER TABLE public.spv_cui_acoperit ADD COLUMN IF NOT EXISTS ultima_reusita timestamptz;
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 3 FROM information_schema.columns WHERE table_schema = 'public' "
                    "AND table_name = 'spv_cui_acoperit' AND column_name IN ('eroare', 'mesaje', 'ultima_reusita')")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_spv_citiri: coloanele %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
