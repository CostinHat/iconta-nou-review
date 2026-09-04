# -*- coding: utf-8 -*-
"""CURATENIA de dupa `proba_ecrane_formular.py` — si granita ei, scrisa.

DE UNDE VINE (lotul 11, 04.09.2026). Regula casei: *o proba care schimba starea portofoliului o
lasa schimbata* — deci curatenia se face, si se face **verificand starea**, nu constatand ca s-a
trimis cererea. Pana azi curatenia era de mana, si de doua ori la rand am aflat ce trebuie sters
citind iesirea sondei.

CE FACE: cauta semnatura probei (`«»@#$%`) in TOATE coloanele de text ale schemei si sterge
randurile care o poarta.

CE NU FACE, si e chiar granita clasei — **un INSERT se poate desface, un UPDATE nu.** Daca
semnatura sta intr-un rand care exista si INAINTE de proba (denumirea firmei, un camp al unui
document vechi), stergerea ar distruge date reale. Acolo instrumentul **NU sterge**: refuza,
numeste tabelul si coloana, si spune ca valoarea veche trebuie luata de la sursa. Instanta care a
nascut regula: sonda a redenumit firma in `public.tenants` si in `firma_profil`, iar numele vechi
s-a refacut citindu-l din D394-urile DEPUSE (`denP` pe CUI-ul firmei), nu din memorie.

Se ruleaza dupa fiecare rulare a sondei:
    PROBA_SCHEMA=tenant_003 ./venv/bin/python frontend_test/vizual/curata_proba_ecrane.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "..", "..")))

from core import db  # noqa: E402

SEMNATURA = "«»@#$%"
SCHEMA = os.environ.get("PROBA_SCHEMA", "tenant_003")
# Tabele in care semnatura NU poate insemna „rand adaugat de proba": randul e unic si preexistent,
# deci semnatura de acolo e o MODIFICARE. Se raporteaza, nu se sterge.
NU_SE_STERGE = {"firma_profil"}


def coloane_text(cur):
    cur.execute("""SELECT table_name, column_name FROM information_schema.columns c
                   WHERE table_schema = %s AND data_type IN ('text', 'character varying')
                     AND EXISTS (SELECT 1 FROM information_schema.tables t
                                 WHERE t.table_schema = c.table_schema
                                   AND t.table_name = c.table_name
                                   AND t.table_type = 'BASE TABLE')
                   ORDER BY 1, 2""", (SCHEMA,))
    return cur.fetchall()


def urme(conn):
    """[(tabel, coloana, cate)] — unde apare semnatura acum."""
    out = []
    with conn.cursor() as cur:
        for t, c in coloane_text(cur):
            try:
                cur.execute('SELECT count(*) FROM "%s"."%s" WHERE "%s" LIKE %%s'
                            % (SCHEMA, t, c), ("%" + SEMNATURA + "%",))
                n = cur.fetchone()[0]
                if n:
                    out.append((t, c, n))
            except Exception:  # noqa: BLE001
                conn.rollback()
    conn.rollback()
    return out


def main():
    db.init_pool()
    with db.get_conn() as conn:
        gasite = urme(conn)
        if not gasite:
            print("nicio urma a probei in %s — nimic de curatat" % SCHEMA)
            return 0
        for t, c, n in gasite:
            print("gasit  %s.%s  x%d" % (t, c, n))
        de_sters = [(t, c) for t, c, _ in gasite if t not in NU_SE_STERGE]
        with conn.cursor() as cur:
            for t, c in de_sters:
                cur.execute('DELETE FROM "%s"."%s" WHERE "%s" LIKE %%s' % (SCHEMA, t, c),
                            ("%" + SEMNATURA + "%",))
                print("sters  %s.%s  -> %d randuri" % (t, c, cur.rowcount))
        conn.commit()

        # SE VERIFICA STAREA, nu ca s-au trimis stergerile (capcana 10).
        ramase = urme(conn)
        modificari = [x for x in ramase if x[0] in NU_SE_STERGE]
        altele = [x for x in ramase if x[0] not in NU_SE_STERGE]
        if altele:
            print("NU S-A CURATAT: %s" % altele)
            return 2
        if modificari:
            print("\nNU SE POATE DESFACE AICI — semnatura sta intr-un rand PREEXISTENT:")
            for t, c, n in modificari:
                print("   %s.%s x%d" % (t, c, n))
            print("Un INSERT se sterge; o MODIFICARE cere valoarea veche, si ea se ia de la sursa "
                  "(declaratiile depuse, instantaneul ANAF), nu din memorie.")
            return 3
        print("STARE CURATA — nicio urma a probei in %s" % SCHEMA)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
