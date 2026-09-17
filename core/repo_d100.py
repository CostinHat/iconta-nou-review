# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d100.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d100.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
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
    # [A8, 17.09.2026] Veniturile micro/profit sunt din ORICE SURSĂ, nu doar din exploatare (70x).
    # Art. 53(1) / art. 19 CF: intră și 75x (alte venituri din exploatare) și 76x (venituri
    # financiare), iar 709 (reduceri comerciale acordate) SE SCADE (cont de venit cu sold debitor).
    # Până azi baza micro (cod 121) lua doar `cont_credit LIKE '70%'`, deci un venit financiar 766 sau
    # o dobândă 766 nu intrau, iar reducerile 709 nu se scădeau. `71x` (variația stocurilor) rămâne în
    # afară, deliberat: e o corecție de producție, nu venit din sursă (art. 53 nu o include în micro).
    cur.execute("SELECT COALESCE(SUM(CASE WHEN (l.cont_credit LIKE '70%%' OR l.cont_credit LIKE '75%%' "
                "        OR l.cont_credit LIKE '76%%') THEN l.suma ELSE 0 END),0) "
                "     - COALESCE(SUM(CASE WHEN l.cont_debit LIKE '709%%' THEN l.suma ELSE 0 END),0) AS venituri, "
                "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '6%%' THEN l.suma ELSE 0 END),0) AS cheltuieli "
                "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status='validata' AND i.data >= %s AND i.data < %s", (_inc.isoformat(), _sf.isoformat()))
    return cur.fetchone()


def select_facturi(cur, _inc, _sf):
    cur.execute("SELECT count(*) FROM facturi WHERE directie='emisa' "
                "AND data_emitere >= %s AND data_emitere < %s", (_inc.isoformat(), _sf.isoformat()))
    return cur.fetchone()
