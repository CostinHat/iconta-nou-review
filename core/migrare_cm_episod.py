# -*- coding: utf-8 -*-
"""
core/migrare_cm_episod.py — model de EPISOD pentru concediile medicale (reparatie calcul fiscal).

Indemnizatia CM se calculeaza LEGAL pe EPISOD (OUG 158/2005 art.17(1): "raportat la fiecare episod de
boala"), nu pe certificat izolat. Certificatele de continuare apartin aceluiasi episod ca certificatul
initial. Coloane noi (toate NULLABLE / cu default):
  - serie_initiala / numar_initial: cheia episodului = seria+numarul certificatului INITIAL (transcris
    de contabil de pe certificatul de continuare; nu se deduce automat).
  - este_continuare: certificatul e o continuare (procentul se ia pe durata EPISODULUI, diminuarea si
    zilele-angajator NU se re-aplica - deja pe initial).
  - data_certificat_initial: data de start a episodului -> selectia formei art.17(1) (art.XI L141/2025).
  - venituri_6_luni / zile_6_luni: baza stocata, ca un certificat sa fie RE-calculabil cand episodul creste.
Backfill: fiecare rand existent devine PROPRIUL episod (initial = el insusi) -> zile_episod = zilele lui =
comportamentul de azi -> ZERO re-calcul de valori. Sursa UNICA a DDL-ului (mirror in tenant_template.sql).
"""
from core import db

DDL = """
ALTER TABLE "{s}".concedii_medicale ADD COLUMN IF NOT EXISTS serie_initiala text;
ALTER TABLE "{s}".concedii_medicale ADD COLUMN IF NOT EXISTS numar_initial text;
ALTER TABLE "{s}".concedii_medicale ADD COLUMN IF NOT EXISTS este_continuare boolean DEFAULT false;
ALTER TABLE "{s}".concedii_medicale ADD COLUMN IF NOT EXISTS data_certificat_initial date;
ALTER TABLE "{s}".concedii_medicale ADD COLUMN IF NOT EXISTS venituri_6_luni numeric;
ALTER TABLE "{s}".concedii_medicale ADD COLUMN IF NOT EXISTS zile_6_luni integer;
UPDATE "{s}".concedii_medicale SET
    serie_initiala = COALESCE(serie_initiala, serie),
    numar_initial = COALESCE(numar_initial, numar),
    data_certificat_initial = COALESCE(data_certificat_initial, data_inceput),
    este_continuare = COALESCE(este_continuare, false)
WHERE serie_initiala IS NULL OR data_certificat_initial IS NULL;
"""

_COLS = ["serie_initiala", "numar_initial", "este_continuare", "data_certificat_initial",
         "venituri_6_luni", "zile_6_luni"]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='concedii_medicale' AND column_name = ANY(%s)", (schema, _COLS))
        are_col = cur.fetchone()[0] == len(_COLS)
        # backfill: niciun rand fara episod
        cur.execute('SELECT count(*) FROM "%s".concedii_medicale WHERE serie_initiala IS NULL '
                    'OR data_certificat_initial IS NULL' % schema)
        fara_orfani = cur.fetchone()[0] == 0
    return are_col and fara_orfani


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                aplica(conn, s)
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1; print("  OK  %s" % s)
                else:
                    esec.append(s); print("  ESEC (verificare)  %s" % s)
        except Exception as e:
            esec.append(s); print("  ESEC %s: %s" % (s, e))
    print("Migrare cm_episod: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
