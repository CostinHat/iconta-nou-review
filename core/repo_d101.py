# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d101.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d101.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:829`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_firma_profil(cur):
    cur.execute("SELECT nume, cui, adresa, oras, judet, caen, "
                "declarant_nume, declarant_prenume, declarant_functie "
                "FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def select_inregistrari_linii(cur, _inc, _sf):
    cur.execute("SELECT "
                "COALESCE(SUM(CASE WHEN l.cont_credit LIKE '76%%' THEN l.suma ELSE 0 END),0) AS ven_fin, "
                "COALESCE(SUM(CASE WHEN l.cont_credit LIKE '7%%' AND l.cont_credit NOT LIKE '76%%' THEN l.suma ELSE 0 END),0) AS ven_expl, "
                "COALESCE(SUM(CASE WHEN l.cont_credit LIKE '70%%' THEN l.suma ELSE 0 END),0) AS cifra_afaceri, "
                "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '66%%' THEN l.suma ELSE 0 END),0) AS chelt_fin, "
                "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '6%%' AND l.cont_debit NOT LIKE '66%%' THEN l.suma ELSE 0 END),0) AS chelt_expl "
                "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND i.data >= %s AND i.data < %s", (_inc.isoformat(), _sf.isoformat()))
    return cur.fetchone()


def select_inregistrari_linii_2(cur, _sf):
    cur.execute("SELECT COALESCE(SUM(CASE WHEN l.cont_credit LIKE '1012%%' THEN l.suma ELSE 0 END),0) "
                "     - COALESCE(SUM(CASE WHEN l.cont_debit  LIKE '1012%%' THEN l.suma ELSE 0 END),0) AS capital "
                "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND i.data < %s", (_sf.isoformat(),))
    return cur.fetchone()


def select_inregistrari_linii_3(cur, _inc):
    cur.execute("SELECT COALESCE(SUM(CASE WHEN l.cont_credit LIKE '1061%%' THEN l.suma ELSE 0 END),0) "
                "     - COALESCE(SUM(CASE WHEN l.cont_debit  LIKE '1061%%' THEN l.suma ELSE 0 END),0) AS rez "
                "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND i.data < %s", (_inc.isoformat(),))
    return cur.fetchone()


def select_inregistrari_linii_4(cur, _inc, _sf):
    cur.execute("SELECT COALESCE(SUM(CASE WHEN l.cont_debit LIKE '691%%' THEN l.suma ELSE 0 END),0) AS imp "
                "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND i.data >= %s AND i.data < %s", (_inc.isoformat(), _sf.isoformat()))
    return cur.fetchone()
