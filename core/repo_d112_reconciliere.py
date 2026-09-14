# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d112_reconciliere.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d112_reconciliere.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select(cur, schema, sid, data):
    cur.execute("SELECT salariu_brut FROM %s.salariu_istoric WHERE salariat_id=%%s AND valabil_din<=%%s "
                "ORDER BY valabil_din DESC LIMIT 1" % schema, (sid, data))
    return cur.fetchone()


def select_2(cur, schema, sid):
    cur.execute("SELECT salariu_brut FROM %s.salariati WHERE id=%%s" % schema, (sid,))
    return cur.fetchone()


def select_3(cur, schema, sid, luna_inc, luna_sf):
    cur.execute("SELECT COUNT(*) AS n FROM %s.salariu_istoric WHERE salariat_id=%%s "
                "AND valabil_din > %%s AND valabil_din <= %%s" % schema, (sid, luna_inc, luna_sf))
    return cur.fetchone()


def select_4(cur, schema, luna_inc):
    cur.execute("SELECT id, salariu_brut, part_time, scutit_contrib_minim, tichet_masa_valoare, "
                "data_angajare, data_incetare FROM %s.salariati "
                "WHERE (data_incetare IS NULL OR data_incetare >= %%s) ORDER BY id" % schema, (luna_inc,))
    return cur.fetchall()


def select_5(cur, schema, an, luna):
    cur.execute("SELECT DISTINCT salariat_id FROM %s.concedii_medicale WHERE an=%%s AND luna=%%s"
                % schema, (an, luna))
    return cur.fetchall()


def select_6(cur, schema, an, luna):
    cur.execute("SELECT DISTINCT salariat_id FROM %s.beneficii_lunare WHERE an=%%s AND luna=%%s"
                % schema, (an, luna))
    return cur.fetchall()
