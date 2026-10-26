"""
core/migrare_anunturi_trimiteri.py — anunțurile Panoului Admin ținute pe TRIMITERI, cu retragere; data publicării actului din propunerile
monitorului fiscal; retragerea unei invitații.

Comanda 13.1, deficiența 646 (anexa, verbatim): „(b) Propunerile monitorului fiscal nu au data publicării și data intrării în vigoare.
(c) Nu există lista anunțurilor trimise (către cine, citit sau nu, retragere). […] (e) Invitații: lipsesc «Copiază» lângă link și
retragerea unei invitații”.

- `anunturi_cabinet.lot`: trimiterea din care face parte rândul (un anunț trimis la N cabinete = N rânduri, același `lot` = id-ul
  primului rând); `trimis_de`: superadminul care l-a trimis; `retras_la`: anunțul retras nu se mai arată cabinetelor care nu l-au citit;
- `alerte_fiscale.data_publicarii`: data publicării actului (monitorul o cere în analiză, lângă `data_vigoare`);
- `invitatii_cabinet.retrasa_la`: invitația retrasă nu mai creează cont (`core.invitatii.stare` -> RETRASA).

DATELE EXISTENTE: rândurile vechi de anunț primesc `lot` după trimiterea din care au venit — același mesaj, scris în aceeași tranzacție
(`creat_la` = ora tranzacției, `now()`), deci aceeași pereche (mesaj, creat_la) = aceeași trimitere; `trimis_de` rămâne necunoscut (NULL).
Alertele vechi au `data_publicarii` NULL (ecranul spune „nu apare în sursă”, nu inventează). Idempotent.
Se aplică prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_anunturi_trimiteri.py`.
"""
from core import db

DDL = """
ALTER TABLE public.anunturi_cabinet ADD COLUMN IF NOT EXISTS lot integer;
ALTER TABLE public.anunturi_cabinet ADD COLUMN IF NOT EXISTS trimis_de integer;
ALTER TABLE public.anunturi_cabinet ADD COLUMN IF NOT EXISTS retras_la timestamptz;
UPDATE public.anunturi_cabinet a SET lot = g.primul
  FROM (SELECT id, MIN(id) OVER (PARTITION BY mesaj, creat_la) AS primul FROM public.anunturi_cabinet) g
 WHERE g.id = a.id AND a.lot IS NULL;
CREATE INDEX IF NOT EXISTS anunturi_cabinet_lot ON public.anunturi_cabinet (lot);
ALTER TABLE public.alerte_fiscale ADD COLUMN IF NOT EXISTS data_publicarii date;
ALTER TABLE public.invitatii_cabinet ADD COLUMN IF NOT EXISTS retrasa_la timestamptz;
"""


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) = 5 FROM information_schema.columns WHERE table_schema = 'public' AND "
                    "((table_name = 'anunturi_cabinet' AND column_name IN ('lot', 'trimis_de', 'retras_la')) OR "
                    " (table_name = 'alerte_fiscale' AND column_name = 'data_publicarii') OR "
                    " (table_name = 'invitatii_cabinet' AND column_name = 'retrasa_la'))")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_anunturi_trimiteri: coloanele %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
