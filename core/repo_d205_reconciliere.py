# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d205_reconciliere.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d205_reconciliere.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_inregistrari_linii(cur, inc, sf):
    cur.execute("SELECT COALESCE(SUM(l.suma),0) FROM inregistrari_linii l "
                "JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status='validata' AND l.cont_debit LIKE '457%%' "
                "AND i.data >= %s AND i.data < %s", (inc, sf))
    return cur.fetchone()


def select_asociati(cur):
    cur.execute("SELECT nume, cnp, cota FROM asociati WHERE cota > 0 ORDER BY nume")
    return cur.fetchall()


def select_457_miscari(cur, sf):
    """[A6] Mișcările 457 pe NOTĂ (credit=distribuire, debit=plată) cu DATA, din tot registrul până la
    `sf` (exclusiv), ordonate cronologic — recalcul INDEPENDENT pentru atribuirea FIFO plată->distribuire
    (cota după data distribuirii). SQL PROPRIU al căii 2 (nu importă repo-ul generatorului)."""
    cur.execute("SELECT i.data, "
                "COALESCE(SUM(CASE WHEN l.cont_credit LIKE '457%%' THEN l.suma ELSE 0 END),0) AS distribuit, "
                "COALESCE(SUM(CASE WHEN l.cont_debit  LIKE '457%%' THEN l.suma ELSE 0 END),0) AS platit "
                "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status='validata' "
                "AND (l.cont_credit LIKE '457%%' OR l.cont_debit LIKE '457%%') "
                "AND i.data < %s "
                "GROUP BY i.id, i.data ORDER BY i.data, i.id", (sf,))
    return cur.fetchall()
