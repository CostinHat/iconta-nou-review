"""
core/migrare_nume_conturi_vechi.py — numele conturilor create cu formularul vechi de înregistrare, lipit la loc (deficiența 269; comanda
Costin 16.10.2026, „Lotul 5, comanda 4” pct.2b, verbatim în DECIZII: „269: faci migrarea numelor la conturile vechi.”).

Formularul „Înregistrează cabinetul tău” împărțea până la lotul 5 numele scris de om în două (`login.js` `separaNume`): ultimul cuvânt
în `prenume`, restul în `nume` — „Test 253” devenea nume „Test”, prenume „253”, iar salutul spunea „Salut, 253”. De la lotul 5 numele
se trimite întreg (`prenume` NULL). Aici, conturile create cu formularul vechi primesc numele întreg, în ordinea în care l-a scris omul:
`nume` = „nume prenume”, `prenume` = NULL.
CARE CONTURI: numai `admin_firma` (singurul rol creat de acel formular: `auth_api.inregistreaza_cabinet`), cu `prenume` completat,
create ÎNAINTE de `PANA_LA` (publicarea lotului 5). Asistenții, clienții și conturile create după nu se ating; un prenume scris după
aceea, separat, în Setări, rămâne. Limita, declarată: un administrator vechi care și-a corectat singur numele în Setări (nume și prenume
separat) primește și el numele lipit — tot numele lui întreg, în ordinea „nume prenume”; nu există urmă care să-l deosebească.
Idempotent (după rulare `prenume` e NULL, deci nu mai e ales). Se aplică prin
`python -m core.migrari_registru ruleaza [--productie] core/migrare_nume_conturi_vechi.py`.
Gard: core/test_migrare_nume_conturi_vechi.py.
"""
from core import db

#: publicarea lotului 5 (16.10.2026): conturile create înainte au trecut prin formularul care împărțea numele
PANA_LA = "2026-10-17 00:00:00+03"

_ALESE = ("FROM public.users WHERE rol = 'admin_firma' AND NULLIF(btrim(prenume), '') IS NOT NULL AND creat_la < %s::timestamptz")


def aplica(conn, pana_la=PANA_LA):
    """[id] ale conturilor reparate."""
    with conn.cursor() as cur:
        cur.execute("UPDATE public.users SET nume = concat_ws(' ', NULLIF(btrim(nume), ''), btrim(prenume)), prenume = NULL "
                    "WHERE id IN (SELECT id " + _ALESE + ") RETURNING id", (pana_la,))
        return sorted(r[0] for r in cur.fetchall())


def verifica(conn, pana_la=PANA_LA):
    """Câte conturi vechi mai au numele împărțit (0 după rulare)."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) " + _ALESE, (pana_la,))
        return cur.fetchone()[0]


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        ids = aplica(conn)
        conn.commit()
        print("migrare_nume_conturi_vechi: %d conturi cu numele lipit la loc (id %s); rămase împărțite: %d"
              % (len(ids), ids, verifica(conn)))


if __name__ == "__main__":
    _main()
