# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d301.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d301.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:829`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_firma_profil(cur):
    cur.execute("SELECT nume, cui, adresa, oras, judet, banca, iban, "
                "declarant_nume, declarant_prenume, declarant_functie, inreg_art317 "
                "FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def select_d301_operatiuni(cur, an, luna):
    cur.execute("SELECT tip, nr_doc, data_doc, val_valuta, tip_valuta, curs, tva "
                "FROM d301_operatiuni WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
    return cur.fetchall()
