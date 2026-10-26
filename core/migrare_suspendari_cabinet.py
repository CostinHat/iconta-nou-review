"""
core/migrare_suspendari_cabinet.py — `public.suspendari_cabinet`: jurnalul suspendărilor unui cabinet (cine, când, motivul, nota internă,
emailul către administratorul cabinetului, reactivarea).

Comanda 13.1, deficiența 645 (decisă de Costin și arhitect pe 24.10.2026, verbatim în anexa comenzii): „motiv obligatoriu din listă fixă —
neplată, la cererea cabinetului, încălcarea termenilor, acces suspect / securitate, la cererea unei autorități — plus notă internă
opțională. La logare apare motivul ales, transparent, fără linie de contact; nota internă nu se arată. […] Email către administratorul
cabinetului la suspendare, cu același motiv. Cine, când, motivul și reactivarea rămân în jurnal.”

- `motiv`: mulțimea închisă din `core.uc_admin.MOTIVE_SUSPENDARE` (CHECK-ul de aici e aceeași listă — gard
  `core/test_lot13_admin_suspendare.py::test_check_ul_bazei_are_exact_motivele_din_cod`); NULL numai pe rândurile scrise de migrare;
- o singură suspendare deschisă pe cabinet (`reactivat_la IS NULL`, indexul unic parțial).

DATELE EXISTENTE: un cabinet suspendat ÎNAINTE de jurnal (`accounting_firms.activ = false`, fără rând aici) primește un rând deschis cu
motivul și data necunoscute (NULL) — la logare vede „Cabinetul este suspendat.” fără motiv (nu se inventează unul), iar reactivarea lui se scrie
pe același rând. Idempotent.
Se aplică prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_suspendari_cabinet.py`.
"""
from core import db

MOTIVE = ("neplata", "cerere_cabinet", "incalcare_termeni", "securitate", "autoritate")

DDL = """
CREATE TABLE IF NOT EXISTS public.suspendari_cabinet (
    id serial PRIMARY KEY,
    cabinet_id integer NOT NULL REFERENCES public.accounting_firms(id) ON DELETE CASCADE,
    motiv text CHECK (motiv IS NULL OR motiv IN (%s)),
    nota_interna text,
    suspendat_de integer REFERENCES public.users(id) ON DELETE SET NULL,
    suspendat_la timestamptz DEFAULT now(),
    emailuri_trimise integer,
    reactivat_de integer REFERENCES public.users(id) ON DELETE SET NULL,
    reactivat_la timestamptz
);
CREATE UNIQUE INDEX IF NOT EXISTS suspendari_cabinet_deschisa ON public.suspendari_cabinet (cabinet_id) WHERE reactivat_la IS NULL;
INSERT INTO public.suspendari_cabinet (cabinet_id, motiv, nota_interna, suspendat_la)
SELECT f.id, NULL, 'suspendat înainte de jurnalul suspendărilor (lotul 13): motivul și data nu s-au înregistrat', NULL
  FROM public.accounting_firms f
 WHERE f.activ = false
   AND NOT EXISTS (SELECT 1 FROM public.suspendari_cabinet s WHERE s.cabinet_id = f.id AND s.reactivat_la IS NULL);
""" % ", ".join("'%s'" % m for m in MOTIVE)


def aplica(conn):
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.suspendari_cabinet') IS NOT NULL")
        return bool(cur.fetchone()[0])


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
        conn.commit()
        print("migrare_suspendari_cabinet: tabela %s" % ("există" if verifica(conn) else "LIPSĂ"))


if __name__ == "__main__":
    _main()
