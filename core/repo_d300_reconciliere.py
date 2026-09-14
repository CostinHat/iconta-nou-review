# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d300_reconciliere.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d300_reconciliere.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:829`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def sql(cur, q, inceput, sfarsit):
    cur.execute(q, (inceput.isoformat(), sfarsit.isoformat()))
    return cur.fetchall()


def select_inregistrari(cur, inceput, sfarsit):
    cur.execute("SELECT 1 FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                "JOIN facturi f ON f.id = i.factura_id "
                "WHERE i.status = 'validata' AND f.directie = 'primita' "
                "AND COALESCE(f.furnizor_tva_incasare, false) = true AND l.cont_debit = '401' "
                "AND i.data >= %s AND i.data < %s LIMIT 1", (inceput.isoformat(), sfarsit.isoformat()))
    return cur.fetchone()
