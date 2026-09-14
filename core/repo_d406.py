# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d406.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d406.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_firma_profil(cur):
    cur.execute("SELECT nume, cui, adresa, oras, cod_postal, platitor_tva, tip_decont "
                "FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def select_plan_conturi(cur):
    cur.execute("SELECT simbol, denumire, COALESCE(tip,'Bifunctional') AS tip, "
                "COALESCE(sold_debitor,0) AS sd, COALESCE(sold_creditor,0) AS sc "
                "FROM plan_conturi ORDER BY simbol")


def select_clienti(cur):
    cur.execute("SELECT id, nume, cui, oras FROM clienti ORDER BY id")


def select_furnizori(cur):
    cur.execute("SELECT id, nume, cui, oras FROM furnizori ORDER BY id")


def select_facturi(cur):
    cur.execute("SELECT tert_cui, tert_nume FROM facturi "
                "WHERE directie='emisa' ORDER BY id")


def select_facturi_2(cur):
    cur.execute("SELECT tert_cui, tert_nume FROM facturi "
                "WHERE directie='primita' ORDER BY id")


def select_inregistrari(cur, di, ds):
    cur.execute("SELECT i.id, i.data, i.descriere, i.sursa, l.cont_debit, l.cont_credit, "
                "l.suma, f.tert_cui, f.tert_nume "
                "FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                "LEFT JOIN facturi f ON f.id = i.factura_id "
                "WHERE i.status = 'validata' AND i.data >= %s AND i.data < %s "
                "ORDER BY i.id, l.id", (di, ds))


def select_factura_linii(cur, di, ds):
    cur.execute("SELECT factura_id, id, descriere, um, "
                "COALESCE(cantitate,0) AS cantitate, "
                "COALESCE(pret_unitar,0) AS pret_unitar, "
                "COALESCE(cota_tva,0) AS cota_tva "
                "FROM factura_linii WHERE factura_id IN "
                "(SELECT id FROM facturi WHERE data_emitere >= %s AND data_emitere < %s) "
                "ORDER BY factura_id, id", (di, ds))


def select_facturi_3(cur, di, ds):
    cur.execute("SELECT id, numar, data_emitere, tert_cui, tert_nume, "
                "COALESCE(total,0) AS total, COALESCE(tva,0) AS tva, "
                "COALESCE(taxare_inversa,false) AS ti, storno_din_id, directie "
                "FROM facturi WHERE data_emitere >= %s AND data_emitere < %s ORDER BY id", (di, ds))
    return cur.fetchall()
