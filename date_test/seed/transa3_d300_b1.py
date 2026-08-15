#!/usr/bin/env python3
"""Seed B1 (D300 model + generator) - cazuri noi care exercita campurile adaugate pe facturi:

  - tip_operatiune='avans'      -> factura de AVANS, exigibila la EMITERE (art.282 alin.2 lit.b),
                                    chiar daca data_faptului_generator e ulterioara (aici: fapt in
                                    septembrie, dar avansul apare in decontul lunii de emitere - iulie).
  - furnizor_tva_incasare=true  -> PRIMITA de la furnizor care aplica TVA la incasare: deducerea se
                                    amana pana la PLATA (art.297 alin.2), chiar daca firma proprie e
                                    in regim normal. Se adauga si plata validata (401=5121) in iulie,
                                    ca deducerea sa devina exigibila pe calea de plata.

Tinta: P1 (Distributie Profit IC SRL, cui 95275466) - profit, platitor, lunar, regim normal. Iulie
2026 nu are alte facturi la P1, deci cifrele sunt curate. Idempotent (nu dubleaza facturi/note).

Rulare: venv/bin/python3 date_test/seed/transa3_d300_b1.py
"""
import sys
sys.path.insert(0, ".")
from core import db

CAB_NUME = "Cabinet Contabil Prisma SRL"
P1_CUI = "95275466"

# facturi noi: (numar, data_emitere, data_fapt, directie, tert_cui, tert_nume, net, tva, cota,
#               tip_operatiune, furnizor_tva_incasare)
FACTURI = [
    # AVANS: emisa in iulie, fapt generator abia in septembrie -> exigibil la EMITERE (iulie).
    ("B1-AVANS", "2026-07-05", "2026-09-15", "emisa", "95141537", "Comert Micro TVA SRL",
     1000, 210, 21, "avans", False),
    # FURNIZOR LA INCASARE: primita in iulie, furnizor aplica TVA la incasare -> deducere amanata la plata.
    ("B1-FTI", "2026-07-10", None, "primita", "95363126", "Constructii Profit Trim SRL",
     2000, 420, 21, "normal", True),
]
# plata facturii B1-FTI (401=5121) validata in iulie -> deducerea devine exigibila pe calea de plata.
PLATA_FTI = ("B1-FTI", "2026-07-20", 2420)


def _incarca_db_env():
    import os
    cale = os.path.expanduser("~/.iconta/db.env")
    if not os.path.exists(cale):
        return
    for linie in open(cale, encoding="utf-8"):
        linie = linie.strip()
        if linie and not linie.startswith("#") and "=" in linie:
            k, v = linie.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _schema_p1(conn):
    with conn.cursor() as c:
        c.execute("SELECT id FROM public.accounting_firms WHERE nume=%s", (CAB_NUME,))
        fid = c.fetchone()[0]
        c.execute("SELECT schema_name FROM public.tenants WHERE cui=%s AND accounting_firm_id=%s",
                  (P1_CUI, fid))
        return c.fetchone()[0]


def _factura_exista(conn, schema, numar, directie):
    with conn.cursor() as c:
        c.execute('SELECT id FROM "%s".facturi WHERE numar=%%s AND directie=%%s' % schema,
                  (numar, directie))
        r = c.fetchone()
        return r[0] if r else None


def seed(conn, schema):
    rap = []
    ids = {}
    for (numar, data, fapt, directie, tcui, tnume, net, tva, cota, tipop, fti) in FACTURI:
        fid = _factura_exista(conn, schema, numar, directie)
        if fid:
            ids[numar] = fid
            rap.append((numar, "deja prezent")); continue
        total = net + tva
        with conn.cursor() as c:
            c.execute(
                'INSERT INTO "%s".facturi (numar, serie, data_emitere, data_faptului_generator, directie, '
                'tert_cui, tert_nume, total, tva, moneda, tip, tert_tara, tip_operatiune, '
                'furnizor_tva_incasare, tert_platitor_tva) '
                'VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s) RETURNING id' % schema,
                (numar, "B1", data, fapt, directie, tcui, tnume, total, tva, "RON", "factura",
                 "RO", tipop, fti, True))
            fid = c.fetchone()[0]
            c.execute(
                'INSERT INTO "%s".factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) '
                'VALUES (%%s,%%s,%%s,%%s,%%s,%%s)' % schema,
                (fid, "seed B1", "buc", 1, net, cota))
        ids[numar] = fid
        rap.append((numar, "inserata id=%d" % fid))
    # plata facturii furnizor la incasare (401=5121) validata -> exigibilitate deducere pe plata
    numar, data_p, suma = PLATA_FTI
    fid = ids.get(numar) or _factura_exista(conn, schema, numar, "primita")
    with conn.cursor() as c:
        c.execute('SELECT id FROM "%s".inregistrari WHERE factura_id=%%s AND data=%%s AND status=%%s'
                  % schema, (fid, data_p, "validata"))
        if c.fetchone():
            rap.append(("plata %s" % numar, "deja prezent"))
        else:
            c.execute('INSERT INTO "%s".inregistrari (data, descriere, factura_id, sursa, status) '
                      'VALUES (%%s,%%s,%%s,%%s,%%s) RETURNING id' % schema,
                      (data_p, "[SEED-B1] plata furnizor la incasare", fid, "banca", "validata"))
            nid = c.fetchone()[0]
            c.execute('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) '
                      'VALUES (%%s,%%s,%%s,%%s)' % schema, (nid, "401", "5121", suma))
            rap.append(("plata %s" % numar, "inserata nota id=%d (401=5121 %d lei)" % (nid, suma)))
    return rap


def main():
    _incarca_db_env()
    db.init_pool()
    with db.get_conn() as conn:
        schema = _schema_p1(conn)
        print("P1 schema=%s" % schema)
        for (n, act) in seed(conn, schema):
            print("  %-14s %s" % (n, act))
        print("OK.")


if __name__ == "__main__":
    main()
