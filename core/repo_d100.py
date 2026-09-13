# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d100.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d100.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:808`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_firma_profil(cur):
    cur.execute("SELECT nume, cui, adresa, oras, judet, regim_fiscal, "
                "declarant_nume, declarant_prenume, declarant_functie "
                "FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def select_inregistrari_linii(cur, _inc, _sf):
    cur.execute("SELECT COALESCE(SUM(CASE WHEN l.cont_credit LIKE '70%%' THEN l.suma ELSE 0 END),0) AS venituri, "
                "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '6%%' THEN l.suma ELSE 0 END),0) AS cheltuieli "
                "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status='validata' AND i.data >= %s AND i.data < %s", (_inc.isoformat(), _sf.isoformat()))
    return cur.fetchone()


def select_facturi(cur, _inc, _sf):
    cur.execute("SELECT count(*) FROM facturi WHERE directie='emisa' "
                "AND data_emitere >= %s AND data_emitere < %s", (_inc.isoformat(), _sf.isoformat()))
    return cur.fetchone()
